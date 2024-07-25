from django_filters import rest_framework as filters
from .models import Author, Book, Genre


class AuthorFilter(filters.FilterSet):
    first_name = filters.CharFilter(field_name='first_name', lookup_expr='startswith')
    last_name = filters.CharFilter(field_name='last_name', lookup_expr='startswith')

    class Meta:
        model = Author
        fields = ['first_name', 'last_name']


class GenreFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Genre
        fields = ['name']


class BookFilter(filters.FilterSet):
    date_publish_min = filters.DateFilter(field_name="date_publish", lookup_expr='gte')
    date_publish_max = filters.DateFilter(field_name="date_publish", lookup_expr='lte')
    genre = filters.CharFilter(field_name='genre__name', lookup_expr='icontains')
    author = filters.CharFilter(field_name='author__last_name', lookup_expr='icontains')

    class Meta:
        model = Book
        fields = ['date_publish_min', 'date_publish_max', 'genre', 'author']
