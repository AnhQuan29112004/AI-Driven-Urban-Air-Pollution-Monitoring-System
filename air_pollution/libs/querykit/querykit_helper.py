from django.db.models import CharField
from django.db.models.expressions import RawSQL, Func, Value, F
from django.db.models.functions import Lower


class QuerykitHelper:
    @staticmethod
    def transform_json_queryset(queryset, json_field, json_to_find, alias):
        return queryset.annotate(**{
            alias: RawSQL(
                f"LOWER(JSON_UNQUOTE(JSON_EXTRACT({json_field}, %s)))",
                [f'$.{json_to_find}']
            )
        })

        # def transform_json_queryset(queryset, json_field, json_to_find, alias):
    #     return queryset.annotate(**{
    #         alias: RawSQL(f"JSON_UNQUOTE(JSON_EXTRACT({json_field}, %s))", [f"$.{json_to_find}"]).lower()
    #     })
