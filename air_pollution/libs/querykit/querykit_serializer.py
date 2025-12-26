from rest_framework import serializers
from constants.error_codes import ErrorCodes
from constants.querying_option_choices import  SearchOptionChoices, SortOptionChoices
from django.db.models import Model
from django.core.exceptions import FieldError


class SearchItemSerializer(serializers.Serializer):
    fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=[]
    )
    option = serializers.ChoiceField(choices=[(choice.value, choice.label) for choice in SearchOptionChoices],
                                     default=SearchOptionChoices.CONTAINS)
    value = serializers.CharField(required=False, default="")

    # May cause error if model is not passed
    def __init__(self, *args, model: Model = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        # Exceptions inside a "validate" function, in a Serializer, should be serializers.ValidationError()

    def validate(self, data):
        fields = data.get('fields', [])
        option = data.get('option')
        value = data.get('value')

        if self.model and fields is not None and len(fields) > 0 and option is not None and value is not None:
            not_exist_fields = []
            
            for field in fields:
                field_valid = True
                try:
                    current_model = self.model
                    parts = field.split('__')
                    for part in parts:
                        try:
                            field_info = current_model._meta.get_field(part)
                            if field_info.is_relation:
                                current_model = field_info.related_model
                        except FieldError:
                            # Check reverse relation related_name
                            found_reverse = False
                            for f in current_model._meta.get_fields():
                                if f.is_relation and f.related_name == part:
                                    current_model = f.related_model
                                    found_reverse = True
                                    break
                            
                            if not found_reverse:
                                field_valid = False
                                break
                except Exception:
                    field_valid = False
                
                if not field_valid:
                    not_exist_fields.append(field)

            if not_exist_fields:
                raise serializers.ValidationError(ErrorCodes.INVALID_FILTER_FIELD_CHOICE,
                                                  {'not_exist_fields': not_exist_fields})
            if option not in SearchOptionChoices:
                raise serializers.ValidationError(ErrorCodes.INVALID_FILTER_OPTION_CHOICE)

        return data


class SortItemSerializer(serializers.Serializer):
    field = serializers.CharField(required=False, default="")
    option = serializers.ChoiceField(choices=[(choice.value, choice.label) for choice in SortOptionChoices],
                                     default=SortOptionChoices.ASCENDING)

    # May cause error if model is not passed
    def __init__(self, *args, model: Model = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

    # Exceptions inside a "validate" function, in a Serializer, should be serializers.ValidationError()
    def validate(self, data):
        field = data.get('field')
        option = data.get('option')

        if self.model and field is not None and field.strip() != "" and option is not None:
            field_valid = True
            try:
                current_model = self.model
                parts = field.split('__')
                for part in parts:
                    try:
                        field_info = current_model._meta.get_field(part)
                        if field_info.is_relation:
                            current_model = field_info.related_model
                    except FieldError:
                        # Check reverse relation related_name
                        found_reverse = False
                        for f in current_model._meta.get_fields():
                            if f.is_relation and f.related_name == part:
                                current_model = f.related_model
                                found_reverse = True
                                break
                        
                        if not found_reverse:
                            field_valid = False
                            break
            except Exception:
                field_valid = False
            
            if not field_valid:
                raise serializers.ValidationError(ErrorCodes.INVALID_FILTER_FIELD_CHOICE,
                                                  {'field_not_exist': field})
            if option not in SortOptionChoices:
                raise serializers.ValidationError(ErrorCodes.INVALID_FILTER_OPTION_CHOICE)

        return data


class QuerykitSerializer(serializers.Serializer):
    page_index = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=10)
    from libs.querykit.filter_item_serializer import FilterItemSerializer
    filter_rules = serializers.ListField(
        child=FilterItemSerializer(),
        required=False,
        default=[],
        allow_null=True
    )

    search_rule = SearchItemSerializer(required=False, allow_null=True)
    sort_rule = SortItemSerializer(required=False, allow_null=True)
