from rest_framework.exceptions import MethodNotAllowed
from rest_framework.viewsets import ModelViewSet


def create_view_set(factory_class):
    class FactoryViewSet(ModelViewSet):
        authentication_classes = factory_class.authentication_classes
        filterset_fields = factory_class.filterset_fields
        filter_backends = factory_class.filter_backends
        http_method_names = factory_class.http_method_names
        lookup_field = factory_class.lookup_field
        lookup_url_kwarg = factory_class.lookup_url_kwarg
        pagination_class = factory_class.pagination_class
        renderer_classes = factory_class.renderer_classes
        search_fields = factory_class.search_fields

        def get_permissions(self):
            if callable(factory_class.get_permissions):
                return factory_class.get_permissions(self)
            return super().get_permissions()

        def get_serializer_class(self):
            if callable(factory_class.get_serializer_class):
                return factory_class.get_serializer_class(self)
            return super().get_serializer_class()

        def get_object(self):
            if callable(factory_class.get_object):
                return factory_class.get_object(self)
            return super().get_object()

        def get_queryset(self):
            if callable(factory_class.get_queryset):
                return factory_class.get_queryset(self)
            return super().get_queryset()

        # ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']
        def list(self, request, *args, **kwargs):
            if 'list' in factory_class.disabled_actions:
                # raise method not allowed drf
                raise MethodNotAllowed(request.method)
            return super().list(request, *args, **kwargs)

        def retrieve(self, request, *args, **kwargs):
            if 'retrieve' in factory_class.disabled_actions:
                raise MethodNotAllowed(request.method)
            return super().retrieve(request, *args, **kwargs)

        def create(self, request, *args, **kwargs):
            if 'create' in factory_class.disabled_actions:
                raise MethodNotAllowed(request.method)
            return super().create(request, *args, **kwargs)

        def update(self, request, *args, **kwargs):
            if 'update' in factory_class.disabled_actions:
                raise MethodNotAllowed(request.method)
            return super().update(request, *args, **kwargs)

        def partial_update(self, request, *args, **kwargs):
            if 'partial_update' in factory_class.disabled_actions:
                raise MethodNotAllowed(request.method)
            return super().partial_update(request, *args, **kwargs)

        def destroy(self, request, *args, **kwargs):
            if 'destroy' in factory_class.disabled_actions:
                raise MethodNotAllowed(request.method)
            return super().destroy(request, *args, **kwargs)

    return FactoryViewSet
