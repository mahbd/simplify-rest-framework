from rest_framework.serializers import ModelSerializer


def create_new_serializer(super_self):
    class FactorySerializer(ModelSerializer):
        class Meta:
            model = super_self.model
            fields = super_self.get_fields()
            depth = super_self.serializer_depth
            read_only_fields = super_self.readonly_fields
            extra_kwargs = super_self.get_extra_kwargs()

        def validate(self, attrs):
            if super_self.auto_user_field:
                attrs[super_self.auto_user_field] = self.context['request'].user
            return super().validate(attrs)

        def create(self, validated_data):
            if callable(super_self.create_instance):
                return super_self.create_instance(validated_data)
            return super().create(validated_data)

        def update(self, instance, validated_data):
            if callable(super_self.update_instance):
                return super_self.update_instance(instance, validated_data)
            return super().update(instance, validated_data)
    return FactorySerializer
