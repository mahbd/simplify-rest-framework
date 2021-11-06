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
            if callable(super_self.validate):
                attrs = super_self.validate(self, attrs)
            return super().validate(attrs)

        def create(self, validated_data):
            if callable(super_self.create_instance):
                obj = super_self.create_instance(self, validated_data)
            else:
                obj = super().create(validated_data)
            for new_field, field in super_self.annotated_fields.items():
                value = get_annotated_attrs(obj, field.name)
                setattr(obj, new_field, value)
            return obj

        def update(self, instance, validated_data):
            if callable(super_self.update_instance):
                return super_self.update_instance(self, instance, validated_data)
            return super().update(instance, validated_data)

    return FactorySerializer


def get_annotated_attrs(obj, name, pos=0):
    if len(name.split('__')) > pos + 1:
        return get_annotated_attrs(getattr(obj, name.split('__')[pos]), name, pos + 1)
    elif len(name.split('__')) > pos:
        return getattr(obj, name.split('__')[pos])


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
