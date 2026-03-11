from django.db.models import Q
from rest_framework import serializers

from constants.constants import Constants
from validators.validator import Validator

class DashboardSerializer(serializers.Serializer):
    test = serializers.CharField(max_length=20)
    