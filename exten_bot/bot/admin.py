from django.contrib import admin
from django.db.models import Q
from guardian.admin import GuardedModelAdmin

from django import forms
from openai import OpenAI

from exten_bot.workflow.models import Dify

from .models import Bot
from .models import Domain
from .models import Function
from .models import Model
from .models import Voice


def check_openai_key(api_key):
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()
        return True
    except Exception as e:
        return str(e)


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_per_page = 50


@admin.register(Voice)
class VoiceAdmin(admin.ModelAdmin):
    list_display = ("voice",)
    list_per_page = 50


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "owner")
    list_per_page = 50


@admin.register(Function)
class FunctionAdmin(GuardedModelAdmin):
    def get_list_display(self, request):
        base = ["name", "privacy"]
        if request.user.is_superuser:
            base.insert(1, "owner")
        return base

    def get_fields(self, request, obj=None):
        fields = ["name", "description"]
        if request.user.is_superuser:
            fields += ["owner", "privacy"]
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(Q(owner=request.user) | Q(privacy="public")).distinct()

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.owner = request.user
        obj.save()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.privacy == "public" and obj.owner != request.user:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.privacy == "public" and obj.owner != request.user:
            return False
        return super().has_delete_permission(request, obj)


class BotAdminForm(forms.ModelForm):
    class Meta:
        model = Bot
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['token'].widget = forms.PasswordInput(render_value=True)

    def clean_token(self):
        token = self.cleaned_data.get("token")
        if token:
            result = check_openai_key(token)
            if result is not True:
                raise forms.ValidationError(f"OpenAI key validation error: {result}")
        return token

@admin.register(Bot)
class BotAdmin(GuardedModelAdmin):
    form = BotAdminForm
    def get_list_display(self, request):
        base = ["id", "expiration_date", "username", "domain", "model", "voice"]
        if request.user.is_superuser:
            base.insert(1, "owner")
        return base

    def get_fields(self, request, obj=None):
        fields = [
            "username",
            "password",
            "domain",
            "expiration_date",
            "token",
            "model",
            "voice",
            "dify",
            "instruction",
            "welcome_msg",
            "transfer_uri",
            "functions",
            "temperature",
            "max_tokens",
        ]
        if request.user.is_superuser:
            fields.insert(0, "owner")
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "functions":
            if request.user.is_superuser:
                kwargs["queryset"] = Function.objects.all()
            else:
                kwargs["queryset"] = Function.objects.filter(
                    Q(owner=request.user) | Q(privacy="public")
                ).distinct()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "dify":
            if request.user.is_superuser:
                kwargs["queryset"] = Dify.objects.all()
            else:
                kwargs["queryset"] = Dify.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        base = ["username", "password"]
        if not request.user.is_superuser:
            base.append("expiration_date")
        return base

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.owner = request.user
        obj.save()
