from rest_framework import serializers
from django.contrib.auth.models import User
from apps.vehicle_mgmt.models import VisitorAppointment, QRPassToken


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'username': {'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class VisitorAppointmentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    has_qr = serializers.SerializerMethodField()

    class Meta:
        model = VisitorAppointment
        fields = '__all__'
        read_only_fields = ('user', 'status', 'approver', 'created_at', 'updated_at')

    def get_has_qr(self, obj):
        return hasattr(obj, 'qr_token') and obj.qr_token is not None and obj.qr_token.is_valid()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class QRTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRPassToken
        fields = ('id', 'token', 'expires_at', 'used_at', 'created_at')