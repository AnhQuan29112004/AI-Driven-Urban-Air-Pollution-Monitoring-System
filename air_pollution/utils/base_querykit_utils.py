

from exceptions.exceptions import AppException
from constants.error_codes import ErrorCodes
from django.db.models import QuerySet

from constants.querying_option_choices import OptionChoices

class BaseQuerykitUtils:
    @staticmethod
    def extract_filteritems_from_request(request, queryset: QuerySet):
        # Lazy import: prevent circular import
        from libs.querykit.querykit import FilterItem
        from libs.querykit.filter_item_serializer import FilterItemSerializer
        
        filter_items = []
        model = queryset.model # IMPORTANT: get the model

        # Extract filter rules from request data
        # If 'filter_rules' is not provided, use an empty list
        rules_list = request.data.get('filter_rules') or []
        
        for rules in rules_list:
            filter_item_serializer = FilterItemSerializer(data=rules, model=model)
            if filter_item_serializer.is_valid():
                data = filter_item_serializer.validated_data
                field = data.get('field')
                option = data.get('option')
                value = data.get('value')
                filter_items.append(FilterItem(field=field, option=option, value=value))
            else:
                raise AppException(ErrorCodes.INVALID_FILTER_FIELD_CHOICE, filter_item_serializer.errors)
        return filter_items
    
    @staticmethod
    def extract_searchitem_from_request(request, queryset: QuerySet):
        # Lazy import: prevent circular import
        from libs.querykit.querykit_serializer import SearchItemSerializer
        from libs.querykit.querykit import SearchItem
        
        model = queryset.model
        search_rule_data = request.data.get('search_rule')
        if not search_rule_data:
            return []  # Return an empty list if no search rule is provided
        search_item_serializer = SearchItemSerializer(data=search_rule_data, model=model)
        if search_item_serializer.is_valid():
            data = search_item_serializer.validated_data
            fields = data.get('fields')
            option = data.get('option')
            value = data.get('value')
            search_item = SearchItem(fields=fields, option=option, value=value)
        else:
            raise AppException(ErrorCodes.INVALID_FILTER_FIELD_CHOICE, search_item_serializer.errors)
        return search_item
    
    @staticmethod
    def extract_sortitem_from_request(request, queryset: QuerySet):
        # Lazy import: prevent circular import
        from libs.querykit.querykit_serializer import SortItemSerializer
        from libs.querykit.querykit import SortItem

        model = queryset.model
        # Extract sort rule from request data
        # If 'sort_rule' is not provided, use an empty dict
        sort_rule = request.data.get('sort_rule')
        if not sort_rule:
            return None
        sort_item_serializer = SortItemSerializer(data=request.data.get('sort_rule'), model=model)
        if sort_item_serializer.is_valid():
            data = sort_item_serializer.validated_data
            field = data.get('field')
            option = data.get('option')
            sort_item = SortItem(field=field, option=option)
        else:
            raise AppException(ErrorCodes.INVALID_FILTER_FIELD_CHOICE, sort_item_serializer.errors)
        return sort_item

    @staticmethod
    def get_filter_options_map():
        return {
            OptionChoices.EXACT: "",
            OptionChoices.CONTAINS: "icontains",
            OptionChoices.IN: "in",
            OptionChoices.GREATER_THAN: "gt",
            OptionChoices.GREATER_OR_EQUALS: "gte",
            OptionChoices.LESS_THAN: "lt",
            OptionChoices.LESS_OR_EQUALS: "lte",
            OptionChoices.STARTS_WITH: "istartswith",
            OptionChoices.ENDS_WITH: "iendswith",
            OptionChoices.RANGE: "range",
            OptionChoices.IS_NULL: "isnull",
            OptionChoices.IS_NOT_NULL: "isnull",  # will handle value as False
        }
        
    @staticmethod
    def get_search_options_map():
        return {
            OptionChoices.CONTAINS: "icontains"
        }

