from rest_framework import viewsets # import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from coinapp.models import Listing
from .serializers import ListingModelSerializer, ListingDetailSerializer

class ListingModelViewSet(viewsets.ReadOnlyModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Listing.objects.all()
    # serializer_class = ListingModelSerializer
    def get_serializer_class(self):
        """Return different serializers for list and detail views"""
        if self.action == 'list':
            return ListingModelSerializer
        return ListingDetailSerializer
    