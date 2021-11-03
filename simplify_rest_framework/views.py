from typing import Type

from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import Model
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet

from .model_factory import ModelFactory
from .view_set import create_view_set


def simplify_model_name(name: str) -> str:
    """
    Converts upper case to lower case and appends '-'

    :param name: Model name
    :return: Simplified model name
    """
    final_name = name[0].lower()
    for char in name[1:]:
        if char.isupper():
            final_name += f'-{char.lower()}'
        else:
            final_name += char
    return final_name


class ModelFactoryContainer:
    def __init__(self):
        self._registered_model_factories = {}

    def register(self, model: Type[Model], factory_class: Type[ModelFactory] = None, **options) -> None:
        """
        Register a model factory

        :param model: Subclass of django.db.models.Model
        :param factory_class: Subclass of ModelFactory
        :param options:
        :return: None
        """
        factory_class = factory_class or ModelFactory
        factory_class = factory_class()
        factory_class.model = model
        if not issubclass(model, Model):
            raise TypeError('Only model can be registered')
        if model._meta.abstract:
            raise ImproperlyConfigured(
                f'The model {model.__name__} is abstract, so it cannot be registered with factory.'
            )
        self._registered_model_factories[f'{model.__name__}.{factory_class.__class__.__name__}'] = factory_class

    def get_urls(self) -> list:
        """
        Return all registered urls

        :return: list of urls
        """
        router = DefaultRouter()
        view_sets = self.get_view_sets()
        for name, view_set in view_sets.items():
            router.register(name, view_set, basename=name)
        return router.urls

    def get_view_sets(self) -> dict[str, Type[ModelViewSet]]:
        """
        Return all registered view sets

        :return: dict of view sets
        """
        view_sets = {}
        for factory_class in self._registered_model_factories.values():
            view_set = create_view_set(factory_class)

            view_sets[simplify_model_name(factory_class.model.__name__)] = view_set
        return view_sets

    def unregister(self, model: Type[Model], factory_class: Type[ModelFactory]) -> None:
        """
        Unregister a model factory.

        :param model: Subclass of django.db.models.Model
        :param factory_class: Subclass of ModelFactory
        :return: None
        """
        factory_class = factory_class()
        factory_class.model = model
        factory_key = f'{model.__name__}.{factory_class.__class__.__name__}'
        if factory_key in self._registered_model_factories:
            del self._registered_model_factories[factory_key]
        else:
            raise ValueError(f'{factory_key} is not registered')


factories = ModelFactoryContainer()


def register(model: Type[Model]):
    """
    Register model factory to automatically generate api for model

    :param model: Subclass of django.db.models.Model
    :return: None
    """

    def _model_admin_wrapper(factory_class):
        if not model:
            raise ValueError('You must pass a model to register')
        if not issubclass(factory_class, ModelFactory):
            raise ValueError('Wrapped class must subclass ModelFactory.')
        factories.register(model, factory_class)
        return factory_class

    return _model_admin_wrapper


def unregister(model: Type[Model], factory_class: Type[ModelFactory]) -> None:
    """
    Unregister model factory

    :param model: Subclass of django.db.models.Model
    :param factory_class: Subclass of ModelFactory
    :return: None
    """
    if not model:
        raise ValueError('You must pass a model to register')
    if not issubclass(factory_class, ModelFactory):
        raise ValueError('Wrapped class must subclass ModelAdmin.')
    factories.unregister(model, factory_class)
