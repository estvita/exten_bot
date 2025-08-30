from django.contrib import admin
from django import forms
from guardian.admin import GuardedModelAdmin

from .models import Mcp, Function


class McpAdminForm(forms.ModelForm):
    class Meta:
        model = Mcp
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['api_key'].widget = forms.PasswordInput(render_value=True)


@admin.register(Mcp)
class McpAdmin(GuardedModelAdmin):
    form = McpAdminForm
    
    def get_list_display(self, request):
        base = ["id", "base_url", "owner"]
        if request.user.is_superuser:
            return base
        return ["id", "base_url"]

    def get_fields(self, request, obj=None):
        fields = ["base_url", "api_key"]
        if request.user.is_superuser:
            fields.insert(0, "owner")
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def get_readonly_fields(self, request, obj=None):
        return []

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.owner = request.user
        obj.save()


class FunctionAdminForm(forms.ModelForm):
    class Meta:
        model = Function
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поле owner только для чтения для обычных пользователей
        if not kwargs.get('instance') or not self.instance.pk:
            # Для новых записей
            if not self.current_user.is_superuser and 'owner' in self.fields:
                self.fields['owner'].widget = forms.HiddenInput()
                self.fields['owner'].initial = self.current_user


@admin.register(Function)
class FunctionAdmin(GuardedModelAdmin):
    form = FunctionAdminForm
    search_fields = ["url", "owner__email"]
    
    def get_list_display(self, request):
        base = ["id", "name", "url"]
        if request.user.is_superuser:
            base.insert(3, "owner")
        return base

    def get_fields(self, request, obj=None):
        fields = ["name", "url", "token", "json_schema", "input_schema"]
        if request.user.is_superuser:
            fields.insert(0, "owner")
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if not request.user.is_superuser and obj:
            # Обычные пользователи не могут изменять владельца существующих записей
            readonly_fields.append("owner")
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.owner = request.user
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form
