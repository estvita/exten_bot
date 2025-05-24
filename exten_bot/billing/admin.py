from django.contrib import admin
from .models import Tariff, Trial

# Register your models here.
@admin.register(Trial)
class TrialAdmin(admin.ModelAdmin):
    list_display = ("id", "owner")
    list_per_page = 50

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_filter = ("trial", )
    list_display = ("duration", "period", "price", "currency", "trial")
    list_per_page = 50