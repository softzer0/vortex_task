from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet, BooleanFilter, NumericRangeFilter


class OwnFilter(FilterSet):
    own = BooleanFilter(label=_("Own"), field_name='user', method='filter_own')

    def filter_own(self, queryset, name, value):
        return queryset.filter(user=self.request.user) if value else queryset


class RecipeFilter(OwnFilter):
    ingredients = NumericRangeFilter(label=_("Number of ingredients between"),
                                     field_name='ingredients', method='filter_ingredients')

    def filter_ingredients(self, queryset, name, value):
        filters = {}
        if value.start:
            filters['ingredients_count__gte'] = value.start
        if value.stop:
            filters['ingredients_count__lte'] = value.stop
        return queryset.annotate(ingredients_count=Count('ingredients')).filter(**filters)
