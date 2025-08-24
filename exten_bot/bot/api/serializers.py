from rest_framework import serializers


class BotResponseContentSerializer(serializers.Serializer):
    model = serializers.CharField()
    key = serializers.CharField(allow_null=True)
    voice = serializers.CharField(allow_null=True)
    instructions = serializers.CharField()
    welcome_message = serializers.CharField(allow_null=True)
    transfer_to = serializers.CharField(allow_null=True)
    temperature = serializers.FloatField()
    max_tokens = serializers.IntegerField()
    mcp_url = serializers.CharField(allow_null=True)
    mcp_key = serializers.CharField(allow_null=True)


class BotResponseSerializer(serializers.Serializer):
    flavor = serializers.CharField(default="openai")
    openai = BotResponseContentSerializer()
