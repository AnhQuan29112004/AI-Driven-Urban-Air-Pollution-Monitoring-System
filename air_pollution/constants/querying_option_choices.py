from django.db import models


# Querying option choices, contains all constants about Filter, Pagination, Search, Sort, ...

class OptionChoices(models.TextChoices):
    EXACT = 'exact', 'Equals (==)'
    CONTAINS = 'contains', 'Case-insensitive contains'
    IN = 'in', 'In a list'
    GREATER_THAN = 'gt', 'Greater than'
    GREATER_OR_EQUALS = 'gte', 'Greater than or equal to'
    LESS_THAN = 'lt', 'Less than'
    LESS_OR_EQUALS = 'lte', 'Less than or equal to'
    STARTS_WITH = 'startswith', 'Case-insensitive starts with'
    ENDS_WITH = 'endswith', 'Case-insensitive ends with'
    RANGE = 'range', 'Range of values'
    IS_NULL = 'isnull', 'Is NULL'
    IS_NOT_NULL = 'isnotnull', 'Is NOT NULL'


class SearchOptionChoices(models.TextChoices):
    CONTAINS = 'contains', 'Case-insensitive contains'
    EXACT = 'exact', 'Equals (==)'


class SortOptionChoices(models.TextChoices):
    ASCENDING = 'asc', 'Ascending'
    DESCENDING = 'desc', 'Descending'
