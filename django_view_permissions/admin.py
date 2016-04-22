from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets


class ReadonlyModeMixin(object):
    """
        Mixin which enables model admin to work in readonly mode. By default it has no effect.
        To customize behaviour override is_readonly and/or is_unsavable methods.
    """
    change_form_template = 'admin/readonly_change_form.html'

    def is_readonly(self, request, obj):
        """
        :return: True - all fields readonly
                 False - default readonly fields(calls super)
        """
        return False

    def is_unsavable(self, request, obj, context=None):
        """
        If you want to customize saving you can do it here
        :return: True - disable saving, hide save buttons
                 False - enable saving, show save buttons
        """
        return self.is_readonly(request, obj)

    def get_fields(self, request, obj=None, call_super=True):
        fields = []
        if call_super:
            fields = super(ReadonlyModeMixin, self).get_fields(request, obj)
        return fields

    def get_readonly_fields(self, request, obj=None):
        if not obj or not self.is_readonly(request, obj):
            return super(ReadonlyModeMixin, self).get_readonly_fields(request, obj)

        declared_fieldsets = None
        if self.fieldsets:
            declared_fieldsets = self.fieldsets
        elif self.fields:
            fields = list(self.fields) + list(self.get_fields(request, obj, call_super=False))
            declared_fieldsets = [(None, {'fields': fields})]

        if declared_fieldsets:
            return flatten_fieldsets(declared_fieldsets)
        else:
            all_fields = self.model._meta.get_fields()
            exclude = self.exclude or []

            readonly_fields = [f.name for f in all_fields
                               if not f.auto_created and
                               f.name not in exclude
                               ]
            return readonly_fields

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if change and self.is_unsavable(request, obj, context):
            extra_context = {'is_unsavable': True,
                             'is_readonly': self.is_readonly(request, obj)
                             }

            add = False
            change = False
            self.save_as = True

            context.update(extra_context)

        return super(ReadonlyModeMixin, self).render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        if change or not self.is_unsavable(request, obj):
            super(ReadonlyModeMixin, self).save_model(request, obj, form, change)


class ReadonlyMixin(ReadonlyModeMixin):
    """
        Mixin which displays models in readonly mode.
    """
    def is_readonly(self, request, obj):
        return True


class ReadonlyAdmin(ReadonlyMixin, admin.ModelAdmin):
    pass
