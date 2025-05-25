from django import template
from wagtail.models import Site, Locale

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    return Site.find_for_request(context["request"]).root_page


@register.simple_tag
def get_menuitem_translation(menuitem, language_code):
    try:
        locale = Locale.objects.get(language_code=language_code)
    except Locale.DoesNotExist:
        return menuitem
    if hasattr(menuitem, "get_translation"):
        translation = menuitem.get_translation(locale)
        if translation and translation.live:
            return translation
    return menuitem
