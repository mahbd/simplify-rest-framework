from django.contrib import admin

from .models import *
# register UserProfile model with admin
admin.site.register(UserProfile)
