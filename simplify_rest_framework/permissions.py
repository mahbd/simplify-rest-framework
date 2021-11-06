from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `user` attribute or pass owner_field
    """

    def __init__(self, owner_fields=None):
        if owner_fields is None:
            owner_fields = ['user']
        self.owner_fields = owner_fields
        self.unauthorized_readonly = True

    def has_object_permission(self, request, view, obj):
        if self.unauthorized_readonly and request.method in permissions.SAFE_METHODS:
            return True
        owners = []
        for field in self.owner_fields:
            owner_field_value = getattr(obj, field, None)
            if owner_field_value and hasattr(owner_field_value, 'all'):
                field_owners = owner_field_value.all()
            elif owner_field_value:
                field_owners = [owner_field_value]
            else:
                continue
            if field_owners and isinstance(field_owners[0], User):
                owners.extend(field_owners)
        return request.user in owners or getattr(request.user, 'is_superuser', False)


class IsOwner(IsOwnerOrReadOnly):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute or pass owner_field
    """

    def __init__(self, owner_fields=None):
        super().__init__(owner_fields=owner_fields)
        self.unauthorized_readonly = False


class HasContestOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in [*permissions.SAFE_METHODS, 'PUT', 'PATCH'] or
                    (request.user and request.user.is_staff))

    def has_object_permission(self, request, view, obj, safe_deny=False):
        related_users = [user.id for user in obj.writers.all()]
        if request.method in ['PUT', 'PATCH'] or safe_deny:
            return bool(request.user and (request.user.is_staff or request.user.id in related_users))
        if request.method in permissions.SAFE_METHODS:
            return True
        return False
