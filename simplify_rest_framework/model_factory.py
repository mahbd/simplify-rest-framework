from copy import deepcopy
from typing import Type

from django.db.models import QuerySet, Model, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.fields import SerializerMethodField
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings
from rest_framework.utils import model_meta

from .serializer import create_new_serializer, create_simple_serializer


def method_for_relation(key, db_field, serializer, many=True):
    def get_new_field(self, instance):
        children = getattr(instance, db_field).all()
        return serializer(children, many=many).data

    get_new_field.__name__ = f'get_{key}'
    return get_new_field


def method_for_field(key):
    def get_new_field(self, instance):
        return getattr(instance, key)

    get_new_field.__name__ = f'get_{key}'
    return get_new_field


class ModelFactory:
    # *******************************************************************
    # ****** Keep each attribute in both init and property to avoid *****
    # ****** Cache problem and get autocomplete in IDE ******************
    # *******************************************************************
    def __init__(self):
        # For ModelViewSet
        self.annotated_fields: dict = {}
        self.authentication_classes: list = api_settings.DEFAULT_AUTHENTICATION_CLASSES
        self.disabled_actions: list = []  # ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']
        self.extra_field_to_query = set()
        self.filterset_fields = []
        self.filter_backends: list = [DjangoFilterBackend, SearchFilter, OrderingFilter]
        self.get_object: callable = None
        self.http_method_names: list = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
        self.lookup_field = 'pk'
        self.lookup_url_kwarg = None
        self.pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        self.permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
        self.prefetch_related = set()
        self.queryset: QuerySet | None = None
        self.renderer_classes: list = api_settings.DEFAULT_RENDERER_CLASSES
        self.search_fields: list = []
        self.select_related = set()
        self.serializer_class: Type[ModelSerializer] | None = None
        # For ModelSerializer
        self.auto_user_field: str | None = None  # Which field to use for auto-populating the user
        self.create_instance: callable = None  # Which function to use for creating the model instance
        self.excluded_fields: list = []  # Which fields to exclude from the api
        self.extra_kwargs: dict = {}  # Extra kwargs to pass to the serializer
        self.extra_serializer_attrs: dict = {}
        self.fields: list = []  # Which fields to include in the api
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
        # Avoid making changes in the original list
        for permission in deepcopy(self.permission_classes):
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
        relations = [(field, info.related_model, info.to_many, info.reverse) for field, info in
                     all_fields.relations.items()]
        fields = [*fields, *[field for field, _, _, reverse in relations if not reverse]]
        if hasattr(deepcopy(self.model)(), 'id'):  # include **id** if id is primary key
            fields.append('id')
        if self.fields:
            tem_fields = deepcopy(self.fields)
            for field in self.fields:
                if type(field) == str:
                    if field not in fields:
                        raise ValueError('field {} not found in model {}'.format(field, self.model))
                elif type(field) == tuple and len(field) == 2:
                    self.extra_serializer_attrs[field[0]] = SerializerMethodField()
                    self.extra_serializer_attrs[f'get_{field[0]}'] = method_for_field(field[0])
                    self.annotated_fields[field[0]] = F(field[1])
                    tem_fields.remove(field)
                    tem_fields.append(field[0])
                elif type(field) == tuple and len(field) == 3:
                    if field[1] in [qvg for qvg, _, _, _ in relations]:
                        for fn, model, many, reverse in relations:
                            if field[1] == fn:
                                break
                        serializer = create_simple_serializer(model, field[2])
                        self.extra_serializer_attrs[field[0]] = SerializerMethodField()
                        self.extra_serializer_attrs[f'get_{field[0]}'] = method_for_relation(
                            field[0], field[1], serializer, many)
                        tem_fields.append(field[0])
                        tem_fields.remove(field)
                        if many:
                            self.prefetch_related.add(field[1])
                        else:
                            self.select_related.add(field[1])
                    else:
                        tem_fields.remove(field)
                elif type(field) == tuple and (len(field) == 4 or len(field) == 5):
                    self.extra_serializer_attrs[field[0]] = SerializerMethodField()
                    self.extra_serializer_attrs[f'get_{field[0]}'] = field[3]
                    for inr in field[1]:
                        self.extra_field_to_query.add(inr)
                    for inr in field[2]:
                        self.prefetch_related.add(inr)
                    if len(field) == 5:
                        for inr in field[4]:
                            self.select_related.add(inr)
                else:
                    raise ValueError(f'field must be a string or tuple. Your\'s {field}')
            return tem_fields
        if self.excluded_fields:
            fields = [field for field in fields if field not in self.excluded_fields]
        return fields

    def get_fields_to_query(self):
        all_fields = model_meta.get_field_info(self.model)
        fields = list(all_fields.fields.keys())
        fields = [*fields, *[field for field, info in all_fields.relations.items() if not info.reverse]]
        fields_to_query = set()
        for field in self.extra_field_to_query:
            fields_to_query.add(field)
        for field in self.fields:
            if type(field) == str:
                fields_to_query.add(field)
            elif type(field) == tuple and (len(field) == 2 or len(field) == 3):
                if field[1] in fields:
                    fields_to_query.add(field[1])
            elif type(field) == tuple and (len(field) == 4 or len(field) == 5):
                for qqq in field[1]:
                    fields_to_query.add(qqq)
        return fields_to_query

    def validate(self, self2, attrs):
        return attrs

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
        self.get_fields()
        fields = self.get_fields_to_query()
        queryset = self.queryset or self.model.objects
        queryset = queryset.annotate(**self.annotated_fields).prefetch_related(*self.prefetch_related).select_related(
            *self.select_related).only(*fields)
        return queryset.all()
