from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.utils import timezone

from exten_bot.bot.models import Bot

from config.permissions import IsOwnerOrTrustedIp
from .serializers import BotResponseSerializer


class BotInfoViewSet(GenericViewSet):
    permission_classes = [IsOwnerOrTrustedIp]
    serializer_class = BotResponseSerializer
    http_method_names = ["get"]

    @extend_schema(
        parameters=[OpenApiParameter(
            "bot", str, OpenApiParameter.QUERY, required=True, description="Bot username"
        )],
        responses={
            200: BotResponseSerializer,
            400: None,
            402: None,
            404: None,
        },
    )
    def list(self, request, *args, **kwargs):
        username = request.query_params.get("bot")
        if not username:
            return Response(
                {"error": "Bot parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            bot = (
                Bot.objects.select_related("model", "voice")
                .prefetch_related("functions")
                .get(username=username)
            )
        except Bot.DoesNotExist:
            return Response(
                {"error": "Bot not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # self.check_object_permissions(request, bot)

        now = timezone.now()
        if bot.expiration_date and bot.expiration_date < now:
            return Response(
                {"error": "Payment required."},
                status=status.HTTP_402_PAYMENT_REQUIRED
            )

        flavor = "openai"

        tools = [func.description for func in bot.functions.all()]
        response = {
            "flavor": flavor,
            flavor: {
                "model": bot.model.name if bot.model else None,
                "key": bot.token if bot.token else None,
                "voice": bot.voice.voice if bot.voice else None,
                "instructions": bot.instruction,
                "welcome_message": bot.welcome_msg,
                "tools": tools,
                "transfer_uri": bot.transfer_uri,
                "temperature": float(bot.temperature)
                if bot.temperature is not None
                else None,
                "max_tokens": bot.max_tokens,
            },
        }
        if bot.dify:
            response[flavor]["dify_url"] = bot.dify.base_url
            response[flavor]["dify_key"] = bot.dify.api_key

        response_serializer = BotResponseSerializer(response)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
