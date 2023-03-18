from django_filters import CharFilter, FilterSet, NumberFilter
from reviews.models import Title


class TitleFilters(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    year = NumberFilter(field_name='year', lookup_expr='icontains')
    category = CharFilter(field_name='category__slug', lookup_expr='icontains')
    genre = CharFilter(field_name='genre__slug', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre',)
