import warnings
from collections import OrderedDict

import coreapi
import coreschema
from django.db import models
from django.utils.encoding import force_str
from rest_framework import serializers, exceptions
from rest_framework.schemas import AutoSchema


class BaseAutoSchema(AutoSchema):
    @classmethod
    def remove_content_object(cls, fields, content_type='content_type', object_id='object_id'):
        for field in [f for f in fields if f.name in (content_type, object_id)]:
            fields.remove(field)
        return fields

    def get_serializer_fields(self, path, method):
        """
        Return a list of `coreapi.Field` instances corresponding to any
        request body input, as determined by the serializer class.
        """
        view = self.view

        if method not in ('PUT', 'PATCH', 'POST'):
            return []

        if not hasattr(view, 'get_serializer'):
            return []

        try:
            serializer = view.get_serializer()
        except exceptions.APIException:
            serializer = None
            warnings.warn('{}.get_serializer() raised an exception during '
                          'schema generation. Serializer fields will not be '
                          'generated for {} {}.'
                          .format(view.__class__.__name__, method, path))

        if isinstance(serializer, serializers.ListSerializer):
            return [
                coreapi.Field(
                    name='data',
                    location='body',
                    required=True,
                    schema=coreschema.Array()
                )
            ]

        if not isinstance(serializer, serializers.Serializer):
            return []

        fields = []
        for field in serializer.fields.values():
            if field.read_only or isinstance(field, serializers.HiddenField):
                continue

            required = field.required and method != 'PATCH'
            field = coreapi.Field(
                name=field.field_name,
                location='form',
                required=required,
                schema=field_to_schema(field)
            )
            fields.append(field)

        return fields


def field_to_schema(field):
    """rest_framework.schemas.coreapi.field_to_schemaはあるんですけど、
    ここでカスタマイズする原因はCharFieldに対して、Max Length情報がないからです。
    """
    title = force_str(field.label) if field.label else ''
    description = force_str(field.help_text) if field.help_text else ''

    if isinstance(field, (serializers.ListSerializer, serializers.ListField)):
        child_schema = field_to_schema(field.child)
        return coreschema.Array(
            items=child_schema,
            title=title,
            description=description
        )
    elif isinstance(field, serializers.DictField):
        return coreschema.Object(
            title=title,
            description=description
        )
    elif isinstance(field, serializers.Serializer):
        return coreschema.Object(
            properties=OrderedDict([
                (key, field_to_schema(value))
                for key, value
                in field.fields.items()
            ]),
            title=title,
            description=description
        )
    elif isinstance(field, serializers.ManyRelatedField):
        related_field_schema = field_to_schema(field.child_relation)

        return coreschema.Array(
            items=related_field_schema,
            title=title,
            description=description
        )
    elif isinstance(field, serializers.PrimaryKeyRelatedField):
        schema_cls = coreschema.String
        model = getattr(field.queryset, 'model', None)
        if model is not None:
            model_field = model._meta.pk
            if isinstance(model_field, models.AutoField):
                schema_cls = coreschema.Integer
        return schema_cls(title=title, description=description)
    elif isinstance(field, serializers.RelatedField):
        return coreschema.String(title=title, description=description)
    elif isinstance(field, serializers.MultipleChoiceField):
        return coreschema.Array(
            items=coreschema.Enum(enum=list(field.choices)),
            title=title,
            description=description
        )
    elif isinstance(field, serializers.ChoiceField):
        return coreschema.Enum(
            enum=list(field.choices),
            title=title,
            description=description
        )
    elif isinstance(field, serializers.BooleanField):
        return coreschema.Boolean(title=title, description=description)
    elif isinstance(field, (serializers.DecimalField, serializers.FloatField)):
        return coreschema.Number(title=title, description=description)
    elif isinstance(field, serializers.IntegerField):
        return coreschema.Integer(title=title, description=description)
    elif isinstance(field, serializers.DateField):
        # yyyy-mm-dd を追加する
        return coreschema.String(
            title=title,
            description='{}\nyyyy-mm-dd'.format(description) if description else 'yyyy-mm-dd',
            format='date'
        )
    elif isinstance(field, serializers.DateTimeField):
        return coreschema.String(
            title=title,
            description=description,
            format='date-time'
        )
    elif isinstance(field, serializers.JSONField):
        return coreschema.Object(title=title, description=description)

    if field.style.get('base_template') == 'textarea.html':
        return coreschema.String(
            title=title,
            description=description,
            format='textarea'
        )

    # max_length=field.max_length を追加する
    return coreschema.String(title=title, max_length=field.max_length, description=description)


def get_add_member_base_fields(basic_fields=None):
    """社員追加時の共通項目

    :param basic_fields:
    :return:
    """
    fields = [
        coreapi.Field(
            "basic_info",
            required=True,
            location="form",
            schema=coreschema.Object(
                title="基本情報",
                description="社員の基本情報、中身の詳しい情報は下記basic_info[〇〇〇]にてご確認"
            ),
        ),
        coreapi.Field(
            "basic_info[duplication]",
            required=False,
            location="form",
            schema=coreschema.Object(
                title="社員の重複情報",
                description="社員追加時、同じ名前持つ要員が契約社員または個人事業主に登録済の場合"
            ),
        ),
        coreapi.Field(
            "basic_info[duplication][content_type_id]",
            required=False,
            location="form",
            schema=coreschema.Object(
                title="重複登録済要員の種別",
                description="選択肢は 社員／協力社員／個人事業主"
            ),
        ),
        coreapi.Field(
            "basic_info[duplication][object_id]",
            required=False,
            location="form",
            schema=coreschema.Object(
                title="重複登録済要員のID",
            ),
        ),
        coreapi.Field(
            "organization",
            required=True,
            location="form",
            schema=coreschema.Object(
                title="所属情報",
                description="社員の所属、中身の詳しい情報は下記organization[〇〇〇]にてご確認"
            ),
        ),
        coreapi.Field(
            "organization[organization]",
            required=True,
            location="form",
            schema=coreschema.Integer(
                title="組織ID",
                description="組織データは「GET /api/org/organizations/」より取得できる。"
            ),
        ),
        coreapi.Field(
            "organization[start_date]",
            required=True,
            location="form",
            schema=coreschema.String(
                title="所属開始日",
                description="YYYY-MM-DD",
            ),
        ),
        coreapi.Field(
            "organization[end_date]",
            required=True,
            location="form",
            schema=coreschema.String(
                title="所属終了日",
                description="YYYY-MM-DD",
            ),
        ),
    ]
    if basic_fields is None:
        basic_fields = []
    for i, f in enumerate(basic_fields):
        fields.insert(i + 1, coreapi.Field(
            'basic_info[{}]'.format(f.name),
            required=f.required,
            location=f.location,
            schema=f.schema,
        ))
    return fields


def get_fields_from_serializer(method, serializer, name_prefix=None, excludes=None):
    """Serializerを自動的に読み込んで、項目を作成する。

    :param method: http 方法
    :param serializer: Serializerのインスタンス
    :param name_prefix: 項目名称の先頭文字
    :param excludes: 除外項目名称のリスト
    :return:
    """
    if excludes is None:
        excludes = []
    fields = []
    for field in serializer.fields.values():
        if field.read_only or isinstance(field, serializers.HiddenField):
            continue
        elif field.field_name in excludes:
            continue

        required = field.required and method != 'PATCH'
        field = coreapi.Field(
            name='{}[{}]'.format(name_prefix, field.field_name) if name_prefix else field.field_name,
            location='form',
            required=required,
            schema=field_to_schema(field)
        )
        fields.append(field)
    return fields


def get_contract_basic_fields(prefix):
    fields = [
        coreapi.Field(
            "{}[company_content_type]".format(prefix) if prefix else 'company_content_type',
            required=True,
            location="form",
            schema=coreschema.Integer(
                title="所属会社種別",
            ),
        ),
        coreapi.Field(
            "{}[company_object_id]".format(prefix) if prefix else 'company_object_id',
            required=True,
            location="form",
            schema=coreschema.Integer(
                title="所属会社ID",
            ),
        ),
        coreapi.Field(
            "{}[content_type]".format(prefix) if prefix else 'content_type',
            required=True,
            location="form",
            schema=coreschema.Integer(
                title="契約対象種別",
                description="社員／案件メンバー／案件（一括の場合）",
            ),
        ),
        coreapi.Field(
            "{}[object_id]".format(prefix) if prefix else 'object_id',
            required=True,
            location="form",
            schema=coreschema.Integer(
                title="契約対象ID",
            ),
        ),
        coreapi.Field(
            "{}[contract_no]".format(prefix) if prefix else 'contract_no',
            required=True,
            location="form",
            schema=coreschema.String(
                title="契約番号",
                description="15桁の文字列、先頭文字は会社コード、続いては作成時の年月と社員コード、最後は連番です。"
            ),
        ),
        coreapi.Field(
            "{}[contract_date]".format(prefix) if prefix else 'contract_date',
            required=True,
            location="form",
            schema=coreschema.String(
                title="契約日",
            ),
        ),
        coreapi.Field(
            "{}[contract_type]".format(prefix) if prefix else 'contract_type',
            required=True,
            location="form",
            schema=coreschema.String(
                title="契約形態",
                description="社員契約時の選択肢 0001:正社員、0002:正社員（試用期間）、0010:契約社員、0011:パート、0012:アルバイト、"
                            "0020:個人事業者、0021:他社技術者\n"
                            "案件契約時の選択肢 0101:業務委託、0102:準委任、0103:派遣、0104:一括、0111:出向（在籍）、0112:出向（完全）、0190:その他"
            ),
        ),
        coreapi.Field(
            "{}[start_date]".format(prefix) if prefix else 'start_date',
            required=True,
            location="form",
            schema=coreschema.String(
                title="契約開始日",
            ),
        ),
        coreapi.Field(
            "{}[end_date]".format(prefix) if prefix else 'end_date',
            required=True,
            location="form",
            schema=coreschema.String(
                title="契約終了日",
                description="正社員の場合は9999-12-31とする。"
            ),
        ),
        coreapi.Field(
            "{}[is_auto_update]".format(prefix) if prefix else 'is_auto_update',
            required=True,
            location="form",
            schema=coreschema.Boolean(
                title="自動更新フラグ",
                description="正社員の場合は無視する。"
            ),
        ),
        coreapi.Field(
            "{}[auto_update_period]".format(prefix) if prefix else 'auto_update_period',
            required=False,
            location="form",
            schema=coreschema.Integer(
                title="自動更新期間",
                description="単位（月）、正社員以外の場合は必須です。"
            ),
        ),
        coreapi.Field(
            "{}[organization]".format(prefix) if prefix else 'organization',
            required=False,
            location="form",
            schema=coreschema.Integer(
                title="所属部署",
                description="雇用契約書出力用、実際の社員所属は変更しません。"
            ),
        ),
        coreapi.Field(
            "{}[status]".format(prefix) if prefix else 'status',
            required=True,
            location="form",
            schema=coreschema.String(
                title="ステータス",
                description="デフォルト：01（01:登録済み、10:自動更新、90:廃棄）"
            ),
        ),
        coreapi.Field(
            "{}[member_is_loan]".format(prefix) if prefix else 'member_is_loan',
            required=False,
            location="form",
            schema=coreschema.Boolean(
                title="出向フラグ",
                description="デフォルト：False、現在サポートしません、今後実装予定。"
            ),
        ),
        coreapi.Field(
            "{}[member_calculate_type]".format(prefix) if prefix else 'member_calculate_type',
            required=False,
            location="form",
            schema=coreschema.String(
                title="時間計算種類",
                description="最小と最大時間を設定します、この時間以外だったら、欠勤または残業が発生します。\n"
                            "01:固定１６０時間、02:営業日数 × ８、03:営業日数 × ７.９、04:営業日数 × ７.７５、\n"
                            "10:固定金額、11:時給、90:その他（任意）"
            ),
        ),
        coreapi.Field(
            "{}[has_employment_insurance]".format(prefix) if prefix else 'has_employment_insurance',
            required=False,
            location="form",
            schema=coreschema.Boolean(
                title="雇用保険加入フラグ",
                description="デフォルト：False"
            ),
        ),
        coreapi.Field(
            "{}[has_health_insurance]".format(prefix) if prefix else 'has_health_insurance',
            required=False,
            location="form",
            schema=coreschema.Boolean(
                title="健康保険加入フラグ",
                description="デフォルト：False"
            ),
        ),
        coreapi.Field(
            "{}[has_employee_pension]".format(prefix) if prefix else 'has_employee_pension',
            required=False,
            location="form",
            schema=coreschema.Boolean(
                title="厚生年金加入フラグ",
                description="デフォルト：False"
            ),
        ),
        coreapi.Field(
            "{}[has_injury_insurance]".format(prefix) if prefix else 'has_injury_insurance',
            required=False,
            location="form",
            schema=coreschema.Boolean(
                title="労災保険加入フラグ",
                description="デフォルト：False"
            ),
        ),
    ]
    if prefix:
        fields.insert(0, coreapi.Field(
            prefix,
            required=False,
            location="form",
            schema=coreschema.Object(
                title="契約基本情報",
                description="空白でない場合は、ステップフォームで契約情報が分かれています。\n"
                            "空白の場合は、すべての契約情報は1つのフォームにまとめています。"
            ),
        ))
    return fields


def get_contract_items_fields(prefix):
    fields = [
        coreapi.Field(
            "{}[code]".format(prefix) if prefix else 'code',
            required=False,
            location="form",
            schema=coreschema.Number(
                title="項目コード",
                description="使用できる選択肢は「GET /api/master/contract-items/」で取得できる",
            ),
        ),
        coreapi.Field(
            "{}[name]".format(prefix) if prefix else 'name',
            required=False,
            location="form",
            schema=coreschema.String(
                title="項目名称",
                description="50文字以内です。",
            ),
        ),
        coreapi.Field(
            "{}[content]".format(prefix) if prefix else 'content',
            required=False,
            location="form",
            schema=coreschema.String(
                title="契約内容",
            ),
        ),
    ]
    if prefix:
        fields.insert(0, coreapi.Field(
            prefix,
            required=False,
            location="form",
            schema=coreschema.Object(
                title="契約条件リスト",
            ),
        ))
    return fields


def get_contract_calculate_hours_fields(prefix):
    fields = [
        coreapi.Field(
            "{}[code]".format(prefix) if prefix else 'code',
            required=False,
            location="form",
            schema=coreschema.Number(
                title="時間計算種類",
                description="0000:下限時間、0001:上限時間、0010:計算用下限時間、0011:計算用上限時間",
            ),
        ),
        coreapi.Field(
            "{}[name]".format(prefix) if prefix else 'name',
            required=False,
            location="form",
            schema=coreschema.String(
                title="時間計算名称",
                description="50文字以内です。",
            ),
        ),
        coreapi.Field(
            "{}[hours]".format(prefix) if prefix else 'hours',
            required=False,
            location="form",
            schema=coreschema.Number(
                title="時間",
            ),
        ),
    ]
    if prefix:
        fields.insert(0, coreapi.Field(
            prefix,
            required=False,
            location="form",
            schema=coreschema.String(
                title="契約計算用時間リスト",
            ),
        ))
    return fields


def get_contract_allowances_fields(prefix):
    fields = [
        coreapi.Field(
            "{}[code]".format(prefix) if prefix else 'code',
            required=False,
            location="form",
            schema=coreschema.Number(
                title="手当コード",
                description="使用できる選択肢は「GET /api/master/contract-allowances/」で取得できる",
            ),
        ),
        coreapi.Field(
            "{}[name]".format(prefix) if prefix else 'name',
            required=False,
            location="form",
            schema=coreschema.String(
                title="手当名称",
                description="50文字以内です。",
            ),
        ),
        coreapi.Field(
            "{}[amount]".format(prefix) if prefix else 'amount',
            required=False,
            location="form",
            schema=coreschema.Integer(
                title="金額",
            ),
        ),
        coreapi.Field(
            "{}[unit]".format(prefix) if prefix else 'unit',
            required=False,
            location="form",
            schema=coreschema.String(
                title="金額",
                description="01:円/月、02:円/年、03:円/時間、04:円/日、05:円"
            ),
        ),
    ]
    if prefix:
        fields.insert(0, coreapi.Field(
            prefix,
            required=False,
            location="form",
            schema=coreschema.Object(
                title="契約手当リスト",
            ),
        ))
    return fields


def get_save_attendance_fields():
    return [
        coreapi.Field(
            'project_id',
            required=False,
            location="form",
            schema=coreschema.Integer(
                title="案件ID",
                description="案件に参加してない場合はnullを移送"
            ),
        ),
        coreapi.Field(
            'total_hours',
            required=True,
            location="form",
            schema=coreschema.Number(
                title="合計時間",
                description="小数2桁まで入力可能、0.5は30分とする"
            ),
        ),
        coreapi.Field(
            'total_days',
            required=False,
            location="form",
            schema=coreschema.Integer(
                title="勤務日数",
            ),
        ),
        coreapi.Field(
            'night_days',
            required=False,
            location="form",
            schema=coreschema.Integer(
                title="深夜日数",
            ),
        ),
    ]
