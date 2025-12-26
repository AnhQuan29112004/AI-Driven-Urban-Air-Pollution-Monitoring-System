from rest_framework import serializers
from constants.querying_option_choices import OptionChoices
from django.db.models import Model
from django.core.exceptions import FieldError
from constants.error_codes import ErrorCodes


class FilterItemSerializer(serializers.Serializer):
    field = serializers.CharField(default="")
    option = serializers.ChoiceField(
        choices=[(choice.value, choice.label) for choice in OptionChoices]
    )
    value = serializers.JSONField(default="")

    def __init__(self, *args, model: Model = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

    def validate(self, data):
        field = data.get("field")
        option = data.get("option")
        value = data.get("value")

        if (
            self.model
            and field is not None
            and field.strip() != ""
            and option is not None
            and value is not None
        ):
            # Kiểm tra trường liên quan nhiều cấp
            try:
                current_model = self.model
                parts = field.split('__')
                for part in parts:
                    try:
                        field_info = current_model._meta.get_field(part)
                        if field_info.is_relation:
                            current_model = field_info.related_model
                    except FieldError:
                        # Kiểm tra trường có phải là related_name của mối quan hệ ngược
                        for f in current_model._meta.get_fields():
                            if f.is_relation and f.related_name == part:
                                current_model = f.related_model
                                break
                        else:
                            raise serializers.ValidationError(
                                ErrorCodes.INVALID_FILTER_FIELD_CHOICE, {"field_not_exist": field}
                            )
            except FieldError:
                raise serializers.ValidationError(
                    ErrorCodes.INVALID_FILTER_FIELD_CHOICE, {"field_not_exist": field}
                )

            if option not in [choice.value for choice in OptionChoices]:
                raise serializers.ValidationError(
                    ErrorCodes.INVALID_FILTER_OPTION_CHOICE
                )

        return data