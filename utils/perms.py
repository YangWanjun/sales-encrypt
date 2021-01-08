import datetime

from django.db.models import Model

from rest_framework import exceptions
from rest_framework.permissions import DjangoModelPermissions, DjangoObjectPermissions

from utils import constants


class SalesModelPermission(DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        return super(SalesModelPermission, self).has_permission(request, view)


class ContractPermission(SalesModelPermission):
    """契約に紐付き基本給・諸手当と契約条件を変更時、独自の権限ではなく、親のContract権限を使う
    """
    perms_map = {
        'GET': ['%(app_label)s.view_contract'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_contract'],
        'PUT': ['%(app_label)s.change_contract'],
        'PATCH': ['%(app_label)s.change_contract'],
        'DELETE': ['%(app_label)s.delete_contract'],
    }


class ProjectMemberContractPermission(SalesModelPermission):

    def get_required_permissions(self, method, model_cls):
        kwargs = {
            'app_label': 'project',
            'model_name': 'projectmembercontract',
        }
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]


class PartnerCompanyPermission(SalesModelPermission):

    def get_required_permissions(self, method, model_cls):
        kwargs = {
            'app_label': 'partner',
            'model_name': 'partnercompany',
        }
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]


class PartnerMemberContractPermission(SalesModelPermission):

    def get_required_permissions(self, method, model_cls):
        kwargs = {
            'app_label': 'partner',
            'model_name': 'partnermembercontract',
        }
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]


class ProjectBlanketContractPermission(SalesModelPermission):

    def get_required_permissions(self, method, model_cls):
        kwargs = {
            'app_label': 'project',
            'model_name': 'projectcontract',
        }
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]


class SalesObjectPermission(DjangoObjectPermissions):

    def has_permission(self, request, view):
        pass


def get_encrypt_objects(user, object_list, perms, fields=None):
    """付与した権限により、見せない項目を暗号化する。

    permsに下記のデータが必要となります
    view_amount_all:　全件を参照できる権限
    view_amount_org_only:　所属部署の権限（課長、部長、事業部長など）
    view_amount_salesperson_only: 営業している案件など

    :param user: ログインユーザー
    :param object_list: 表示する対象一覧
    :param perms: 必要な権限一覧
    :param fields: 暗号化する項目リスト、Noneの場合見せる権限のないレコードを外す
    :return:
    """
    if user.is_superuser:
        # スーパーユーザーの場合は暗号化しない。
        return object_list
    allowed_perms = list(set(perms) & set(user.get_all_permissions()))
    if not hasattr(user, 'member') or not allowed_perms:
        # 紐づきの社員が存在しない場合、または必要とする権限がない場合、暗号化したデータを返す。
        return encrypt_objects(object_list, fields) if fields else []
    elif 'view_amount_all' in [i.split('.')[1] for i in allowed_perms if i.find('.') >= 0]:
        # 全件を参照できる権限
        return object_list
    member = user.member
    if hasattr(member, 'salesperson'):
        salesperson = member.salesperson
    else:
        salesperson = None
    qs_position_ship = member.get_position_ships()
    own_org = [o.organization.pk for o in qs_position_ship if o.position in ('10', '11', '20', '21', '30', '31')]
    if not salesperson and not own_org:
        # 部門長でなし、かつ営業でない場合は空白を戻す。
        return encrypt_objects(object_list, fields) if fields else []
    has_org_only = len([i for i in allowed_perms if i.endswith('_org_only')]) > 0
    has_salesperson_only = len([i for i in allowed_perms if i.endswith('_salesperson_only')]) > 0
    results = []
    for obj in object_list:
        if has_org_only and obj.get('organization_id') in own_org:
            results.append(obj)
        elif has_salesperson_only and salesperson and obj.get('salesperson_id') == salesperson.pk:
            results.append(obj)
        elif fields:
            results.append(encrypt_objects(obj, fields))
    return results


def encrypt_objects(obj_or_list, fields):
    if isinstance(obj_or_list, (tuple, list)):
        for obj in obj_or_list:
            for field in fields:
                if field in obj:
                    obj[field] = constants.ENCRYPT_DISPLAY_VALUE
                    obj['has_permission'] = False
    else:
        for field in fields:
            if field in obj_or_list:
                obj_or_list[field] = constants.ENCRYPT_DISPLAY_VALUE
                obj_or_list['has_permission'] = False
    return obj_or_list


def has_permission(user, organization, salesperson, perms):
    """指定ユーザーに権限あるかどうかをチェック

    permsに下記のデータが必要となります
    view_amount_all:　全件を参照できる権限
    view_amount_org_only:　所属部署の権限（課長、部長、事業部長など）
    view_amount_salesperson_only: 営業している案件など

    :param user: ログインユーザー
    :param organization: 検証対象の所属組織
    :param salesperson: 検証対象の営業
    :param perms: 必要な権限一覧
    :return:
    """
    if user.is_superuser:
        return True
    elif not hasattr(user, 'member'):
        return False
    if not organization:
        organization = 0
    elif isinstance(organization, Model):
        organization = organization.pk
    if not salesperson:
        salesperson = 0
    elif isinstance(salesperson, Model):
        salesperson = salesperson.pk
    member = user.member
    perm_all, perm_org, perm_salesperson = perms
    all_perms = user.get_all_permissions()
    if perm_all in all_perms:
        # 全件を参照できる権限を持つ
        return True
    if hasattr(member, 'salesperson') and salesperson == member.salesperson.pk and perm_salesperson in all_perms:
        # 営業担当している権限を持つ
        return True
    qs_position_ship = member.get_position_ships()
    own_org = [o.organization.pk for o in qs_position_ship if o.position in ('10', '11', '20', '21', '30', '31')]
    if perm_org in all_perms and organization in own_org:
        return True
    return False
