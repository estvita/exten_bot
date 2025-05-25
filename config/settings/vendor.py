from .production import *

INSTALLED_APPS = [
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.simple_translation",
    "django.contrib.sitemaps",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.locales",
    "wagtail",
    "modelcluster",
    "taggit",
    "wagtailcodeblock",
    "exten_bot.website",
    "exten_bot.billing",
] + INSTALLED_APPS

MIDDLEWARE = MIDDLEWARE + [
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

WAGTAIL_SITE_NAME = "exten.bot"
WAGTAILADMIN_BASE_URL = "https://exten.bot"
WAGTAILEMBEDS_RESPONSIVE_HTML = True
WAGTAILDOCS_EXTENSIONS = [
    "csv",
    "docx",
    "key",
    "odt",
    "pdf",
    "pptx",
    "rtf",
    "txt",
    "xlsx",
    "zip",
]
WAGTAIL_CMS_URL = env("WAGTAIL_CMS_URL", default="cms/")
WAGTAIL_I18N_ENABLED = True

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('en', "English"),
    ('ru', "Russian"),
]