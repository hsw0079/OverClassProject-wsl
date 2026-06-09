from rest_framework import serializers
from apps.campus_nav.models import CampusLocation


class CampusLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusLocation
        fields = '__all__'