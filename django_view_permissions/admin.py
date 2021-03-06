from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets
from django.forms import fields_for_model


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

    def is_savable(self, request, obj):
        """
        If you want to customize saving you can do it here.
        """
        return not self.is_readonly(request, obj)

    def hide_save_buttons(self, request, obj, context):
        """ Customize hiding save buttons """
        return not self.is_savable(request, obj)

    def _changeable_fields(self, request, obj):
        """ When result is True get_fields and get_readonly_fields simply returns super
        """
        return not obj or not self.is_readonly(request, obj)

    def get_fields(self, request, obj=None):
        if self._changeable_fields(request, obj):
            return super(ReadonlyModeMixin, self).get_fields(request, obj)

        if self.fields is not None:
            return self.fields

        fields = None
        if hasattr(self.form, '_meta'):
            fields = getattr(self.form._meta, 'fields', None)

        exclude = self.exclude
        if exclude is None and hasattr(self.form, '_meta'):
            exclude = getattr(self.form._meta, 'exclude', None)

        fields = fields_for_model(self.model, fields, exclude)

        return fields

    def get_readonly_fields(self, request, obj=None):
        if self._changeable_fields(request, obj):
            return super(ReadonlyModeMixin, self).get_readonly_fields(request, obj)

        readonly_fields = flatten_fieldsets(self.get_fieldsets(request, obj))

        return readonly_fields

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if change and self.hide_save_buttons(request, obj, context):
            extra_context = {'hide_save_buttons': True,
                             'is_readonly': self.is_readonly(request, obj)
                             }

            add = False
            change = False
            self.save_as = True

            context.update(extra_context)

        return super(ReadonlyModeMixin, self).render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        if not change or self.is_savable(request, obj):
            super(ReadonlyModeMixin, self).save_model(request, obj, form, change)


class ReadonlyMixin(ReadonlyModeMixin):
    """
        Mixin which displays models in readonly mode.
    """
    def is_readonly(self, request, obj):
        return True


class ReadonlyAdmin(ReadonlyMixin, admin.ModelAdmin):
    pass
