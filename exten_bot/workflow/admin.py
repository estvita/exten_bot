from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Dify


@admin.register(Dify)
class DifyAdmin(GuardedModelAdmin):
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
