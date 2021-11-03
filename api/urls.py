from django.urls import path, include

from simplify_rest_framework import factories

urlpatterns = [
    path('', include(factories.get_urls())),
]
