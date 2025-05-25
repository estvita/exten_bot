from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from django import forms

from .models import Dify

class DifyAdminForm(forms.ModelForm):
    class Meta:
        model = Dify
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['api_key'].widget = forms.PasswordInput(render_value=True)


@admin.register(Dify)
class DifyAdmin(GuardedModelAdmin):
    form = DifyAdminForm
    def get_list_display(self, request):
        base = ["id", "base_url"]
        if request.user.is_superuser:
            base.insert(1, "owner")
        return base

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def get_fields(self, request, obj=None):
        fields = ["base_url", "api_key"]
        if request.user.is_superuser:
            fields.insert(0, "owner")
        return fields

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.owner = request.user
        obj.save()
