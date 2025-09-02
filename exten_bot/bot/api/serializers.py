from rest_framework import serializers


class FunctionSerializer(serializers.Serializer):
    url = serializers.URLField()
    token = serializers.CharField(allow_null=True)
    function = serializers.JSONField()
    input_schema = serializers.JSONField(allow_null=True)


class McpServerSerializer(serializers.Serializer):
    url = serializers.URLField()
    api_key = serializers.CharField(allow_null=True)
    label = serializers.CharField(allow_null=True)
    require_approval = serializers.CharField(allow_null=False)

class BotResponseContentSerializer(serializers.Serializer):
    model = serializers.CharField()
    key = serializers.CharField(allow_null=True)
    voice = serializers.CharField(allow_null=True)
    instructions = serializers.CharField()
    welcome_message = serializers.CharField(allow_null=True)
    transfer_to = serializers.CharField(allow_null=True)
    temperature = serializers.FloatField()
    max_tokens = serializers.IntegerField()
    functions = FunctionSerializer(many=True, required=False, allow_null=True)
    mcp_servers = McpServerSerializer(many=True, required=False, allow_null=True)


class BotResponseSerializer(serializers.Serializer):
    flavor = serializers.CharField(default="openai")
    openai = BotResponseContentSerializer()
