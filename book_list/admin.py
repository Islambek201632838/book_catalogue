from django.contrib import admin
from .models import *

for model in [Genre, Author, Book, BookDescription, Favourite]:
    admin.site.register(model)

