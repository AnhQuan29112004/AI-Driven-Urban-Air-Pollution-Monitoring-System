from rest_framework import serializers

class ChatBotRequest(serializers.Serializer):
    question = serializers.CharField(max_length = 1000)

class ChatBotResponse(serializers.Serializer):
    response = serializers.CharField()