import re
from typing import List

from django.db.models.expressions import RawSQL

from exceptions.exceptions import AppException
from constants.querying_option_choices import (
    OptionChoices,
    SearchOptionChoices,
    SortOptionChoices,
)
from rest_framework.request import Request
from rest_framework.fields import DateTimeField
from datetime import datetime, timedelta

from constants.error_codes import ErrorCodes
from libs.querykit.querykit_helper import QuerykitHelper
from utils.base_querykit_utils import BaseQuerykitUtils
# from validators.validator import Validator
from django.core.paginator import Paginator
from django.db.models import QuerySet, Q
from django.db import models
from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__name__)


class FilterItem:
    OPTION_CHOICES = OptionChoices

    # Remember : use FilterItemSerializer first, then use this class FilterItem !
    def __init__(self, field, option, value):
        if option not in self.OPTION_CHOICES:
            raise AppException(ErrorCodes.INVALID_FILTER_OPTION_CHOICE)

        self.field = field
        self.option = option
        self.value = value

    def __str__(self):
        return f"{self.field} - {self.option} - {self.value}"

    # Apply self.filter to the queryset.
    # We do all the field and option validation (check) in Serializer.
    # Classes will be used only to compute and handle queryset.
    def apply_filter(self, queryset):
        print(f"[DEBUG] Filtering: field={self.field}, option={self.option}, value={self.value}")
        lookup_map = BaseQuerykitUtils.get_filter_options_map()
        lookup = lookup_map.get(self.option)

        field_lookup = f"{self.field}__{lookup}" if lookup else self.field
        
        if self.value is None:
            return queryset  # hoặc raise AppException nếu bạn muốn bắt buộc phải có value

        # Lấy thông tin về field từ model
        model = queryset.model
        try:
            field_info = model._meta.get_field(self.field)
            is_text_field = isinstance(field_info, (models.CharField, models.TextField, models.SlugField))
            is_number_field = isinstance(field_info, (models.IntegerField, models.BigIntegerField, models.SmallIntegerField, models.PositiveIntegerField, models.PositiveSmallIntegerField))
            is_date_field = isinstance(field_info, (models.DateTimeField, models.DateField))
            print(f"[DEBUG] Field Info: is_text_field={is_text_field}, is_number_field={is_number_field}, is_date_field={is_date_field}")
        except:
            # Nếu không lấy được field info, mặc định là text field
            is_text_field = True
            is_number_field = False
            is_date_field = False
            print(f"[DEBUG] Field Info: Defaulting to is_text_field={is_text_field}")
            
        # XỬ LÝ RANGE (ngày, số, timestamp, ...)
        if self.option == OptionChoices.RANGE:
            if not isinstance(self.value, list) or len(self.value) != 2:
                raise AppException(ErrorCodes.INVALID_FILTER_FIELD_CHOICE)

            def parse_value(v, is_end=False):
                """Tự động parse kiểu dữ liệu cho RANGE."""
                # Nếu là số (int/float) → dùng trực tiếp
                if isinstance(v, (int, float)):
                    return v

                # Nếu là dạng số nhưng kiểu string → convert
                if isinstance(v, str) and re.fullmatch(r"^-?\d+(\.\d+)?$", v):
                    return float(v) if "." in v else int(v)

                # Nếu là ngày YYYY-MM-DD
                if isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                    dt = datetime.strptime(v, "%Y-%m-%d").date() # Lấy Date object
                    
                    # Nếu field là DateField, trả về Date object luôn
                    if is_date_field and isinstance(field_info, models.DateField):
                        if is_end:
                            dt = dt + timedelta(days=1)
                        return dt
                    
                    # Nếu là DateTimeField hoặc default, convert sang timestamp (hoặc datetime)
                    # Logic cũ dùng timestamp cho DateTime
                    dt_full = datetime.combine(dt, datetime.min.time())
                    if is_end:
                        dt_full = dt_full + timedelta(days=1)
                    return dt_full.timestamp()

                # Nếu là datetime ISO 2025-11-15T10:20:30
                try:
                    if isinstance(v, str):
                        dt = datetime.fromisoformat(v)
                        return dt.timestamp()
                except:
                    pass

                raise AppException(ErrorCodes.INVALID_FILTER_FIELD_CHOICE, detail=f"Invalid RANGE value: {v}")

            try:
                start = parse_value(self.value[0], is_end=False)
                end = parse_value(self.value[1], is_end=True)

            except Exception as e:
                # Log error thật để debug
                import traceback
                print(traceback.format_exc())
                raise AppException(ErrorCodes.INVALID_FILTER_FIELD_CHOICE, detail=str(e))

            return queryset.filter(**{f"{self.field}__range": (start, end)})

        # Xử lý giá trị dựa trên loại option
        if self.option in [OptionChoices.IN]:
            # Với option "in", giá trị phải là list
            print(f"[DEBUG] Processing 'in' option with value: {self.value}")
            if not isinstance(self.value, list):
                self.value = [self.value]
        else:
            print(f"[DEBUG] Processing option '{self.option}' with value: {self.value}")
            # Với các option khác, sử dụng giá trị gốc
            if isinstance(self.value, list) and len(self.value) == 1:
                self.value = self.value[0]
            elif isinstance(self.value, list) and len(self.value) > 1:
                # Nếu có nhiều giá trị nhưng không phải option "in", chỉ lấy giá trị đầu tiên
                self.value = self.value[0]

        # Chỉ chuyển thành lowercase cho các trường text
        if is_text_field and isinstance(self.value, str):
            print(f"[DEBUG] Lowercasing value for text field: {self.value}")
            if isinstance(self.value, list):
                self.value = [str(v).lower() for v in self.value]
            else:
                self.value = str(self.value).lower()

        # For JSONField only, for example: "data__customer_name"
        if re.fullmatch(r".+__.+", self.field):
            print(f"[DEBUG] Applying JSONField filter for field: {self.field}")
            json_result_value = "json_result_value"
            json_field, json_to_find = str(self.field).split("__", 1)
            print(f"[DEBUG] JSON field: {json_field}, to find: {json_to_find}")
            # Lower field checking
            # queryset = QuerykitHelper.transform_json_queryset(
            #     queryset, json_field, json_to_find, json_result_value
            # )
            print(f"[DEBUG] Transformed queryset for JSONField.")
            json_lookup = f"{self.field}__{lookup}" if lookup else json_field
            print(f"[DEBUG] Applying filter: {json_lookup} = {self.value}")
            return queryset.filter(**{json_lookup: self.value}).distinct()
        print(f"[DEBUG] Applying filter: {field_lookup} = {self.value}")
        return queryset.filter(**{field_lookup: self.value})


class FilterOnlyCondition:
    def __init__(self, filter_rules: List[FilterItem] = None):
        self.filter_rules = filter_rules if filter_rules else []

    def add_filter(self, filter_item: FilterItem):
        if isinstance(filter_item, FilterItem):
            self.filter_rules.append(filter_item)

    def add_multi_filters(self, filter_items: List[FilterItem]):
        for item in filter_items:
            self.filter_rules.append(item)

    def apply_filters(self, queryset: QuerySet) -> QuerySet:
        for filter_item in self.filter_rules:
            queryset = filter_item.apply_filter(queryset)
        return queryset


# A single SearchItem used for searching with multiple fields.
class SearchItem:
    OPTION_CHOICES = SearchOptionChoices

    def __init__(self, fields: list, option, value):
        if option not in self.OPTION_CHOICES:
            raise AppException(ErrorCodes.INVALID_FILTER_OPTION_CHOICE)

        self.fields = fields
        self.option = option
        self.value = value

    def __str__(self):
        return f"{self.fields} - {self.option} - {self.value}"

    # Apply search to our Search queryset.
    # We do all the field and option validation (check) in Serializer.
    # Classes will be used only to compute and handle queryset.
    def apply_search(self, queryset):
        q_object = Q()
        lookup_map = BaseQuerykitUtils.get_search_options_map()
        lookup = lookup_map.get(self.option)

        if (
            not self.fields
            or len(self.fields) == 0
            or not self.option
            or not self.value
        ):
            return queryset

        # Lower value passed in
        self.value = str(self.value).lower()

        # For JSONField only, for example: "data__customer_name"
        for index, field in enumerate(self.fields):
            is_json_field = False
            if "__" in field:
                parts = str(field).split("__", 1)
                first_part = parts[0]
                try:
                    field_info = queryset.model._meta.get_field(first_part)
                    if isinstance(field_info, models.JSONField):
                        is_json_field = True
                except Exception:
                    pass

            if is_json_field:
                json_result_value = f"json_result_value_{index}"
                json_field, json_to_find = str(field).split("__", 1)

                # Lower field to check
                queryset = QuerykitHelper.transform_json_queryset(
                    queryset, json_field, json_to_find, json_result_value
                )

                json_lookup = f"{json_result_value}__{lookup}" if lookup else json_field

                q_object |= Q(**{json_lookup: self.value})

            else:
                field_lookup = f"{field}__{lookup}" if lookup else field
                q_object |= Q(**{field_lookup: self.value})

        # Remember: apply q_object only ONCE to the queryset !
        queryset = queryset.filter(q_object)
        return queryset


class SortItem:
    OPTION_CHOICES = SortOptionChoices

    def __init__(self, field, option):
        if option not in self.OPTION_CHOICES:
            raise AppException(ErrorCodes.INVALID_FILTER_OPTION_CHOICE)

        self.field = field
        self.option = option

    def __str__(self):
        return f"{self.field} - {self.option}"

    # Apply sorting option to our queryset.
    # We do all the field and option validation (check) in Serializer.
    # Classes will be used only to compute and handle queryset.
    def apply_sort(self, queryset):
        if not self.field or not self.option:
            return queryset

        # Not using the sort_map. Use base if - else
        sort_direction = ""
        if self.option == SortOptionChoices.ASCENDING:
            sort_direction = ""
        elif self.option == SortOptionChoices.DESCENDING:
            sort_direction = "-"

        # if re.fullmatch(r".+__.+", self.field):
        #     json_result_value = "json_result_value"
        #     json_field, json_to_find = str(self.field).split("__", 1)
        #     queryset = QuerykitHelper.transform_json_queryset(
        #         queryset, json_field, json_to_find, json_result_value
        #     )

        #     queryset = queryset.order_by(f"{sort_direction}{json_result_value}")

        # else:
        queryset = queryset.order_by(f"{sort_direction}{self.field}")

        return queryset


class Querykit:
    def __init__(
        self,
        page_index=1,
        page_size=10,
        filter_rules: List[FilterItem] = None,
        search_rule: SearchItem = None,
        sort_rule: SortItem = None,
    ):
        self.page_index = page_index
        if page_size is None or page_size <= 0:
            self.page_size = None
        else:
            self.page_size = page_size
        self.filter_rules = filter_rules if filter_rules else []
        self.search_rule = search_rule if search_rule else None
        self.sort_rule = sort_rule if sort_rule else None

    def add_filter(self, filter_item: FilterItem):
        if isinstance(filter_item, FilterItem):
            self.filter_rules.append(filter_item)

    def add_multi_filters(self, filter_items: List[FilterItem]):
        for item in filter_items:
            self.filter_rules.append(item)

    def apply_filters(self, queryset: QuerySet) -> QuerySet:
        for filter_item in self.filter_rules:
            queryset = filter_item.apply_filter(queryset)
        return queryset

    def apply_search(self, queryset: QuerySet, request=None) -> QuerySet:
    # Nếu truyền request vào, parse search_rule từ request
        if request is not None and self.search_rule is None:
            self.search_rule = BaseQuerykitUtils.extract_searchitem_from_request(request, queryset)

        # Chạy search nếu có search_rule
        if self.search_rule is not None:
            queryset = self.search_rule.apply_search(queryset)

        return queryset


    def apply_sort(self, queryset: QuerySet) -> QuerySet:
        if self.sort_rule is not None:
            queryset = self.sort_rule.apply_sort(queryset)
        return queryset

    # Queryset passed to this function must have .order_by() to prevent inconsistent pagination result.
    def get_paginated_data(self, queryset: QuerySet):
        if self.page_size is None:
            return {
                "queryset": queryset,
                "count": queryset.count()
            }
        if not queryset.query.order_by:
            queryset = queryset.order_by("-created_at")  # 'id': ASC ; '-id': DESC (reverse)
        paginator = Paginator(queryset, self.page_size)
        count = paginator.count
        page = paginator.get_page(self.page_index)
        return {"page": page, "count": count}

    def get_paginated_queryset(self, queryset: QuerySet):
        # Không phân trang khi page_size is None
        if self.page_size is None:
            return {
                "page": queryset,      # trả full queryset
                "count": queryset.count()
            }

        if not queryset.query.order_by:
            queryset = queryset.order_by("-created_at")

        start = (self.page_index - 1) * self.page_size
        end = start + self.page_size

        return {
            "queryset": queryset[start:end],
            "count": queryset.count()
        }

    # Accept QuerySet only.
    # queryset: the initial queryset (usually like, ModelClass.objects.all())
    @staticmethod
    def apply_filter_paginate_search_sort(request, queryset: QuerySet, return_queryset_only=False):
        from .querykit_serializer import QuerykitSerializer
        
        filter_items = BaseQuerykitUtils.extract_filteritems_from_request(
            request, queryset
        )
       
        search_item = BaseQuerykitUtils.extract_searchitem_from_request(request, queryset)
      
        sort_item = BaseQuerykitUtils.extract_sortitem_from_request(request, queryset)
        
        # Use Serializer to check valid for those fields : page_index, page_size, filter_rules
        # The filter_rules checked in this code line, is from request, not 'filter_items'
        serializer = QuerykitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Convert to Querykit instance
        condition = Querykit(
            page_index=data.get("page_index"),
            page_size=data.get("page_size"),
            filter_rules=filter_items,
            search_rule=search_item,
            sort_rule=sort_item,
        )

        # IMPORTANT: start paginating only if all filters have been applied !
        # Return the queryset which applied pagination (start:end), and the count - queryset.count()
        if return_queryset_only:
            query_result = condition.get_paginated_queryset(
                condition.apply_sort(
                    condition.apply_filters(condition.apply_search(queryset))
                )
            )

        # Return the fully paginated data, with count.
        else:
            query_result = condition.get_paginated_data(
                condition.apply_sort(
                    condition.apply_filters(condition.apply_search(queryset))
                )
            )

        return query_result

