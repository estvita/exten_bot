from django.contrib import admin
from django import forms
from guardian.admin import GuardedModelAdmin

from .models import Mcp


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
