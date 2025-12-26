from rest_framework import serializers
from libs.querykit.filter_item_serializer import FilterItemSerializer
class FilterOnlyConditionSerializer(serializers.Serializer):
    filter_rules = serializers.ListField(
        child=FilterItemSerializer(),
        required=False,
        default=[],
        allow_null=True
    )