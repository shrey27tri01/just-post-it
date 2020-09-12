from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Tweet, Profile, FollowerRelation

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Tweet)
admin.site.register(Profile)
admin.site.register(FollowerRelation)