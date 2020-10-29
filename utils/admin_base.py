from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):

    class Media:
        css = {
            'all': ('/static/css/base.css',)
        }

    def get_actions(self, request):
        actions = super(BaseModelAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class BaseTabularInline(admin.TabularInline):

    def has_delete_permission(self, request, obj=None):
        if obj:
            return request.user.has_perm('{app_label}.delete_{model_name}'.format(
                app_label=obj._meta.app_label,
                model_name=obj._meta.model_name,
            ))
        else:
            return False


class BaseAdminChangeOnly(BaseModelAdmin):

    def get_actions(self, request):
        actions = super(BaseAdminChangeOnly, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BaseAdminReadOnly(BaseAdminChangeOnly):

    class Media:
        js = (
            '/static/js/readonly.js',
        )
        css = {
            'all': ('/static/css/readonly.css',)
        }

    def get_readonly_fields(self, request, obj=None):
        return list(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        )
