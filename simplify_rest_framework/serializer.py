from rest_framework.serializers import ModelSerializer


def create_new_serializer_class(super_self):
    class FactorySerializer(ModelSerializer):
        class Meta:
            model = super_self.model
            fields = super_self.get_fields()
            depth = super_self.serializer_depth
            read_only_fields = super_self.readonly_fields
            extra_kwargs = super_self.get_extra_kwargs()

        def validate(self, attrs):
            if super_self.auto_user_field:
                if self.context.get('request').user.is_authenticated:
                    attrs[super_self.auto_user_field] = self.context['request'].user
            return super().validate(attrs)

        def create(self, validated_data):
            if callable(super_self.create_instance):
                return super_self.create_instance(self, validated_data)
            return super().create(validated_data)

        def update(self, instance, validated_data):
            if callable(super_self.update_instance):
                return super_self.update_instance(self, instance, validated_data)
            return super().update(instance, validated_data)

    return FactorySerializer


def create_new_serializer(super_self, extra_attributes=None):
    if extra_attributes is None:
        extra_attributes = {}

    factory_serializer = create_new_serializer_class(super_self)

    attributes = {
        **extra_attributes,
    }
    return type('FactorySerializer', (factory_serializer,), attributes)


def create_simple_serializer(model, fields):
    new_model = model
    all_fields = fields

    class Meta:
        model = new_model
        fields = all_fields

    dct = {
        'Meta': Meta,
    }
    return type('FactorySerializer', (ModelSerializer,), dct)
