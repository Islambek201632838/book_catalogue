from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from .filters import AuthorFilter, BookFilter, GenreFilter


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class AuthorListView(generics.ListAPIView):
    queryset = Author.objects.all().order_by('id')
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuthorFilter


class GenreListView(generics.ListAPIView):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = GenreFilter


class BookListView(generics.ListAPIView):
    queryset = Book.objects.all().order_by('id')
    serializer_class = BookShortSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter
    pagination_class = StandardResultsSetPagination


class FavouriteListView(generics.ListAPIView):
    serializer_class = FavouriteSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favourite.objects.filter(user=self.request.user)
