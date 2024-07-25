from django.urls import path
from .views import AuthorListView, GenreListView, BookListView, FavouriteListView

urlpatterns = [
    path('authors/', AuthorListView.as_view(), name='author-list'),
    path('genres/', GenreListView.as_view(), name='genre-list'),
    path('books/', BookListView.as_view(), name='book-list'),
    path('favourites/', FavouriteListView.as_view(), name='favourite-list'),
]

