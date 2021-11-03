from typing import Type

from django.db.models import QuerySet, Model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings
from rest_framework.utils import model_meta

from .serializer import create_new_serializer


class ModelFactory:
    # For ModelViewSet
    authentication_classes: list = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    disabled_actions: list = []  # ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']
    filterset_fields = []
    filter_backends: list = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    get_object: callable = None
    http_method_names: list = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    lookup_field = 'pk'
    lookup_url_kwarg = None
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
    queryset: QuerySet | None = None
    renderer_classes: list = api_settings.DEFAULT_RENDERER_CLASSES
    search_fields: list = []
    serializer_class: Type[ModelSerializer] | None = None
    # For ModelSerializer
    auto_user_field: str | None = None  # Which field to use for auto-populating the user
    create_instance: callable = None  # Which function to use for creating the model instance
    excluded_fields: list | None = None  # Which fields to exclude from the api
    extra_kwargs: dict = {}  # Extra kwargs to pass to the serializer
    fields: list | None = None  # Which fields to include in the api
    readonly_fields: list = []  # Which fields to make readonly
    serializer_depth: int = 0  # How deep the serializer should be
    update_instance: callable = None  # Which function to use for updating the model instance
    write_only_fields: list = []  # Which fields to make write only
    # Others
    model: Type[Model] = None  # Which model to use

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_extra_kwargs(self):
        if self.extra_kwargs and type(self.extra_kwargs) != dict:
            raise ValueError('extra_kwargs must be a dict')
        for field in self.write_only_fields:
            if field in self.extra_kwargs:
                field_extra = {**self.extra_kwargs[field], 'write_only': True}
                self.extra_kwargs[field] = field_extra
            else:
                self.extra_kwargs[field] = {'write_only': True}
        return self.extra_kwargs

    def get_fields(self):
        # Validate required attributes
        if model_meta.is_abstract_model(self.model):
            raise ValueError('Abstract model can not be used')
        if self.fields and self.excluded_fields:
            raise ValueError('fields and excluded fields can not be same time')
        if self.fields and type(self.fields) != list:
            raise ValueError('fields must be a list')
        if self.excluded_fields and type(self.excluded_fields) != list:
            raise ValueError('excluded_fields must be a list')
        # Return fields name
        if self.fields:
            return self.fields
        all_fields = list(model_meta.get_field_info(self.model).fields.keys())
        if self.excluded_fields:
            all_fields = [field for field in all_fields if field not in self.excluded_fields]
        return all_fields

    def get_serializer_class(self) -> Type[ModelSerializer]:
        super_self = self
        if self.serializer_class and not issubclass(self.serializer_class, ModelSerializer):
            raise ValueError('serializer class must be model serializer')

        if self.serializer_class:
            return self.serializer_class
        return create_new_serializer(super_self)

    def get_queryset(self) -> QuerySet:
        if self.queryset and type(self.queryset) != QuerySet:
            raise ValueError('queryset must be queryset')
        if self.queryset:
            return self.queryset
        return self.model.objects.all()
