from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from exten_bot.bot.api.views import BotInfoViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# router.register("users", UserViewSet)
router.register("bots", BotInfoViewSet, basename="bots")


app_name = "api"
urlpatterns = router.urls
