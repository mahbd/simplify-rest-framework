from copy import deepcopy
from typing import Type

from django.db.models import QuerySet, Model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.fields import SerializerMethodField
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings
from rest_framework.utils import model_meta

from .serializer import create_new_serializer, create_simple_serializer


def generate_method_for_many_relation(key, db_field, serializer):
    def get_new_field(self, instance):
        children = getattr(instance, db_field).all()
        return serializer(children, many=True).data

    get_new_field.__name__ = f'get_{key}'
    return get_new_field


class ModelFactory:
    # *******************************************************************
    # ****** Keep each attribute in both init and property to avoid *****
    # ****** Cache problem and get autocomplete in IDE ******************
    # *******************************************************************
    def __init__(self):
        # For ModelViewSet
        self.authentication_classes: list = api_settings.DEFAULT_AUTHENTICATION_CLASSES
        self.disabled_actions: list = []  # ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']
        self.filterset_fields = []
        self.filter_backends: list = [DjangoFilterBackend, SearchFilter, OrderingFilter]
        self.get_object: callable = None
        self.http_method_names: list = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
        self.lookup_field = 'pk'
        self.lookup_url_kwarg = None
        self.pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        self.permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
        self.queryset: QuerySet | None = None
        self.renderer_classes: list = api_settings.DEFAULT_RENDERER_CLASSES
        self.search_fields: list = []
        self.serializer_class: Type[ModelSerializer] | None = None
        # For ModelSerializer
        self.auto_user_field: str | None = None  # Which field to use for auto-populating the user
        self.create_instance: callable = None  # Which function to use for creating the model instance
        self.excluded_fields: list | None = None  # Which fields to exclude from the api
        self.extra_kwargs: dict = {}  # Extra kwargs to pass to the serializer
        self.extra_serializer_attrs: dict = {}
        self.fields: list | None = None  # Which fields to include in the api
        self.readonly_fields: list = []  # Which fields to make readonly
        self.serializer_depth: int = 0  # How deep the serializer should be
        self.update_instance: callable = None  # Which function to use for updating the model instance
        self.write_only_fields: list = []  # Which fields to make write only
        # Others
        self.model: Type[Model] | None = None  # Which model to use

    def get_permissions(self, self2):
        if self.permission_classes and type(self.permission_classes) != list:
            raise ValueError('permission_classes must be a list')
        permission_objs = []
        permission_classes = deepcopy(self.permission_classes) # To avoid making changes in the original list
        for permission in permission_classes:
            if type(permission) == dict:
                p = permission.get('class')
                permission.pop('class')
                permission_objs.append(p(**permission))
            else:
                permission_objs.append(permission())
        return permission_objs

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
            raise ValueError(f'fields must be a list. currently {type(self.fields)}')
        if self.excluded_fields and type(self.excluded_fields) != list:
            raise ValueError('excluded_fields must be a list')
        # Return fields name
        all_fields = model_meta.get_field_info(self.model)
        fields = list(all_fields.fields.keys())
        foreign_fields = [(field, all_fields.relations[field].related_model) for field in all_fields.relations if
                          not all_fields.relations[field].to_many and not all_fields.relations[field].reverse]
        many_fields = [(field, all_fields.relations[field].related_model) for field in all_fields.relations if
                       all_fields.relations[field].to_many and not all_fields.relations[field].reverse]
        reverse_many_fields = [(field, all_fields.relations[field].related_model) for field in all_fields.relations if
                               all_fields.relations[field].to_many and all_fields.relations[field].reverse]
        fields = [*fields, *[field for field, _ in foreign_fields], *[field for field, _ in many_fields]]
        if self.fields:
            tem_fields = deepcopy(self.fields)
            for field in self.fields:
                if type(field) == str:
                    if field not in fields:
                        raise ValueError('field {} not found in model {}'.format(field, self.model))
                elif type(field) == tuple:
                    # ToDo: Implement foreign fields
                    pass
                elif type(field) == dict:
                    if field['db_field'] in [qvg for qvg, _ in foreign_fields]:
                        print(field)
                    elif field['db_field'] in [qvg for qvg, _ in [*many_fields, *reverse_many_fields]]:
                        field_name = field['field']
                        db_field = field['db_field']
                        model = None
                        for fn, model in [*reverse_many_fields, *many_fields]:
                            if db_field == fn:
                                model = model
                                break
                        serializer = create_simple_serializer(model, field["fields"])
                        self.extra_serializer_attrs[field_name] = SerializerMethodField()
                        self.extra_serializer_attrs[f'get_{field_name}'] = generate_method_for_many_relation(
                            field_name, db_field, serializer)
                        tem_fields.append(field_name)
                        tem_fields.remove(field)
                    else:
                        tem_fields.remove(field)
            # print([qvg for qvg, _ in [*many_fields, *reverse_many_fields]])
            return tem_fields
        if self.excluded_fields:
            fields = [field for field in fields if field not in self.excluded_fields]
        return fields

    def get_serializer_class(self, self2) -> Type[ModelSerializer]:
        super_self = self
        if self.serializer_class and not issubclass(self.serializer_class, ModelSerializer):
            raise ValueError('serializer class must be model serializer')

        if self.serializer_class:
            return self.serializer_class
        return create_new_serializer(super_self, self.extra_serializer_attrs)

    def get_queryset(self, self2) -> QuerySet:
        if self.queryset and type(self.queryset) != QuerySet:
            raise ValueError('queryset must be queryset')
        if self.queryset:
            return self.queryset
        return self.model.objects.all()
