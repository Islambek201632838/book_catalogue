from django.contrib import admin
from .models import *

for model in (Like, Dislike, Comments, Reply):
    admin.site.register(model)
