from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def auto_schema_post(serializer_class=None, security=None):
    def decorator(func):
        return swagger_auto_schema(
            method='post',
            request_body=serializer_class,
            security=security,  # <--- dòng mới
        )(func)
    return decorator

def auto_schema_put(serializer_class=None, security=None):
    def decorator(func):
        return swagger_auto_schema(method='put', request_body=serializer_class, security=security)(func)

    return decorator

def auto_schema_patch(serializer_class=None, security=None):
    def decorator(func):
        return swagger_auto_schema(method='patch', request_body=serializer_class, security=security)(func)

    return decorator

def auto_schema_delete(serializer_class=None, security=None):
    def decorator(func):
        return swagger_auto_schema(method='delete', request_body=serializer_class, security=security)(func)

    return decorator


def auto_schema_get(serializer_class=None, security=None, many=True):
    def decorator(func):
        responses = {200: serializer_class(many=many)} if serializer_class else None
        return swagger_auto_schema(method='get', responses=responses, security=security)(func)
    return decorator


# Excel schema decorators
flexible_filter_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "template_name": openapi.Schema(type=openapi.TYPE_STRING),
        "filter_rules": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "field": openapi.Schema(type=openapi.TYPE_STRING),
                    "option": openapi.Schema(type=openapi.TYPE_STRING),
                    "value": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        oneOf=[
                            openapi.Schema(type=openapi.TYPE_STRING),
                            openapi.Schema(type=openapi.TYPE_INTEGER),
                            openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                            openapi.Schema(type=openapi.TYPE_OBJECT),
                        ],
                        description="Any valid JSON: string, number, list, or object"
                    ),
                },
            )
        ),
    },
    required=["template_name", "filter_rules"]
)

