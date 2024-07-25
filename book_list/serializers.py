from rest_framework import serializers
from book_list.models import Genre, Author, Book, Favourite, BookDescription


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class AuthorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'gender', 'age', 'user', 'bio']


class AuthorShortSerializer(AuthorSerializer):
    class Meta(AuthorSerializer.Meta):
        fields = ['id', 'first_name', 'last_name']


class BookDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookDescription
        fields = ['text']


class BookSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()
    author = AuthorShortSerializer()
    average_rating = serializers.SerializerMethodField()
    description = BookDescriptionSerializer(source='bookdescription', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'name', 'genre', 'author', 'average_rating', 'description']

    def get_average_rating(self, obj):
        return obj.average_rating()


class BookShortSerializer(BookSerializer):
    class Meta(BookSerializer.Meta):
        fields = ['id', 'name', 'genre', 'author', 'average_rating']


class FavouriteSerializer(serializers.ModelSerializer):
    book = BookShortSerializer()

    class Meta:
        model = Favourite
        fields = ['id', 'book']
