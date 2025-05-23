from django.conf import settings


def admin_url(request):
    return {"ADMIN_URL": settings.ADMIN_URL}


def installed_apps(request):
    return {"INSTALLED_APPS": settings.INSTALLED_APPS}
