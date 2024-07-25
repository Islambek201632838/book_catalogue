from django.db import models
from django.core.validators import MaxValueValidator
from auth_user.models import CustomUser


class Genre(models.Model):
    name = models.CharField(max_length=20, blank=False)

    def __str__(self):
        return self.name


class Author(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    first_name = models.CharField(max_length=30, blank=False, db_index=True)
    last_name = models.CharField(max_length=30, blank=False, db_index=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=True, db_index=True)
    age = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(150)])
    user = models.ForeignKey(CustomUser, null=True, default=None, blank=True, related_name='authors',
                             on_delete=models.CASCADE)
    bio = models.CharField(max_length=1000, blank=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    name = models.CharField(max_length=20, blank=False)
    genre = models.ForeignKey(Genre, null=False, blank=False, on_delete=models.CASCADE, related_name='books')
    author = models.ForeignKey(Author, null=False, blank=False, on_delete=models.CASCADE, related_name='books')
    date_publish = models.DateField(null=False, blank=False)

    def __str__(self):
        return self.name

    def average_rating(self):
        comments = self.comments_set.all()
        if comments.exists():
            return comments.aggregate(models.Avg('rating'))['rating__avg']
        return None


class BookDescription(models.Model):
    book = models.OneToOneField(Book, null=False, blank=False, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000, blank=False)


class Favourite(models.Model):
    user = models.ForeignKey(CustomUser, null=False, blank=False, related_name='favourites', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, null=False, blank=False, on_delete=models.CASCADE, related_name='favourites')

    def __str__(self):
        return f"{self.user} likes {self.book}"
