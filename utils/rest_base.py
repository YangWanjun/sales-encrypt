import traceback

from django.db import transaction
from django.db.models.deletion import ProtectedError

from rest_framework import status as rest_status
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView, exception_handler
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CharField
from rest_framework.validators import UniqueTogetherValidator, qs_exists

from middleware.request import get_request
from utils import constants, common
from utils.app_base import check_file_size_limit, \
    log_action_for_add, \
    log_action_for_delete, \
    log_action_for_change
from utils.errors import CustomException
from utils.perms import SalesModelPermission
from utils.schema_base import BaseAutoSchema

logger = common.get_system_logger()


class BaseApiView(APIView):
    pass


class BaseApiRetrieveView(BaseApiView):

    def get_context_data(self, **kwargs):
        pass

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return Response(context)


class ListApiMixin(object):

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        count = queryset.count()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'count': count,
                'results': serializer.data,
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': count,
            'results': serializer.data,
        })


class BaseListAPIView(ListApiMixin, ListAPIView):
    pass


class BaseModelViewSet(ListApiMixin, ModelViewSet):
    permission_classes = [SalesModelPermission]
    schema = BaseAutoSchema()

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        # 削除のログを保存
        instance = self.get_object()
        log_action_for_delete(request.user, instance)
        return super(BaseModelViewSet, self).destroy(request, *args, **kwargs)


class BaseReadOnlyModelViewSet(ListApiMixin, ReadOnlyModelViewSet):
    permission_classes = [SalesModelPermission]


class BaseModelSerializer(ModelSerializer):

    @transaction.atomic
    def save(self, **kwargs):
        log = kwargs.pop('log', None)
        existed_uuids = dict()
        if self.instance:
            is_add = False
            for name, field in self.fields.items():
                if isinstance(field, UUIDFileField):
                    existed_uuids[name] = getattr(self.instance, name)
            # 変更前のデータを取得
            if log is not False:
                original_data = self.__class__(self.instance).data
            else:
                original_data = None
        else:
            # 追加の場合
            is_add = True
            original_data = None
        instance = super(BaseModelSerializer, self).save(**kwargs)
        from master.models import Attachment
        for name, field in self.fields.items():
            data = self.initial_data.get(name)
            if isinstance(field, UUIDFileField) and common.is_base64_string(data):
                Attachment.save_from_base64(
                    instance,
                    data,
                    self.data.get(name),
                    existed_uuids.get(name)
                )
        # 操作ログを保存
        request = get_request()
        if request and log is not False:
            if is_add:
                log_action_for_add(request.user, instance)
            elif is_add is False:
                # 変更の場合
                changed_data = self.get_changed_message(original_data)
                log_action_for_change(request.user, instance, changed_data)
        return instance

    def get_changed_message(self, original_data):
        """変更メッセージを取得する

        :param original_data: 変更前のデータ
        :return:
        """
        changed_data = []
        for key in self.validated_data:
            old_value = original_data.get(key)
            # validated_dataから取得したら、Python型に変更済みのデータになってします。
            new_value = self.data.get(key)
            if old_value != new_value:
                changed_data.append('{} を {} から {} に変更しました。'.format(
                    self.fields.get(key).label,
                    old_value if old_value != '' else None,
                    new_value if new_value != '' else None,
                ))
        return changed_data


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        logger.error(traceback.format_exc())
        response.data['status_code'] = response.status_code
    elif isinstance(exc, CustomException):
        json = {'detail': exc.message}
        if exc.data:
            json.update(exc.data)
        response = Response(json, status=rest_status.HTTP_400_BAD_REQUEST)
    elif isinstance(exc, ProtectedError):
        msg, qs = exc.args
        response = Response({'detail': constants.ERROR_DELETE_PROTECTED.format(
            name=qs.model._meta.verbose_name
        )}, status=rest_status.HTTP_400_BAD_REQUEST)
    elif hasattr(exc, 'args') and len(exc.args) == 2:
        logger.error(traceback.format_exc())
        code, msg = exc.args
        if code == 1062:
            # 一意制約違反
            pass
        response = Response(
            {'detail': msg, 'status_code': 500},
            status=rest_status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    elif hasattr(exc, 'args') and len(exc.args) == 1:
        logger.error(traceback.format_exc())
        msg, = exc.args
        response = Response({'detail': msg}, status=rest_status.HTTP_400_BAD_REQUEST)

    return response


class BaseUniqueTogetherValidator(UniqueTogetherValidator):

    def __init__(self, queryset, fields, message=None, error_field=None):
        super(BaseUniqueTogetherValidator, self).__init__(queryset, fields, message)
        self.error_field = error_field

    def __call__(self, attrs, serializer):
        self.enforce_required_fields(attrs, serializer)
        queryset = self.queryset
        queryset = self.filter_queryset(attrs, queryset, serializer)
        queryset = self.exclude_current_instance(attrs, queryset, serializer.instance)

        # Ignore validation if any field is None
        checked_values = [
            value for field, value in attrs.items() if field in self.fields
        ]
        if None not in checked_values and qs_exists(queryset):
            field_names = ', '.join(self.fields)
            message = self.message.format(field_names=field_names)
            if self.error_field:
                detail = dict()
                detail[self.error_field] = [message]
            else:
                detail = message
            raise ValidationError(detail, code='unique')


class UUIDFileField(CharField):
    file_ext = None

    def to_internal_value(self, data):
        if isinstance(data, bool) or not isinstance(data, (str, int, float,)):
            self.fail('invalid')

        if common.is_base64_string(data):
            self.file_ext = common.get_ext_from_base64(data)
            return common.get_default_file_uuid()
        else:
            return str(data)


class UUIDImageField(UUIDFileField):

    def run_validators(self, value):
        super(UUIDImageField, self).run_validators(value)
        req = self.context.get('request')
        if req:
            data = req.data.get(self.field_name)
            try:
                check_file_size_limit(data)
            except CustomException as ex:
                raise ValidationError(ex.message)
        valid_ext = ['.pdf', '.jpg', '.jpeg', '.png']
        if self.file_ext and self.file_ext.lower() not in valid_ext:
            raise ValidationError(constants.ERROR_INVALID_IMAGE_EXT.format(ext=", ".join(valid_ext)))
