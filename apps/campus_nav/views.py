from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from apps.campus_nav.models import CampusLocation
from apps.campus_nav.serializers import CampusLocationSerializer


class CampusLocationViewSet(viewsets.ModelViewSet):
    """校内地点 CRUD"""
    queryset = CampusLocation.objects.all()
    serializer_class = CampusLocationSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]