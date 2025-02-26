from rest_framework import viewsets # import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, F, BooleanField, Case, When
from coinapp.models import Listing, Transaction
from .serializers import ListingModelSerializer, ListingDetailSerializer, TransactionSerializer

class ListingModelViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Listing.objects.all()
    def get_serializer_class(self):
        """Return different serializers for list and detail views"""
        if self.action == 'list':
            return ListingModelSerializer
        return ListingDetailSerializer

class GetUserBalance(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        return Response(request.user.amount)

class TransactionModelViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    def get_queryset(self):
        user = self.request.user
        return (
            Transaction.objects.filter(Q(seller=user) | Q(buyer=user))
            .select_related("seller", "buyer")
            .annotate(
                is_received=Case(
                    When(Q(seller=user), then=True),
                    default=False,
                    output_field=BooleanField(),
                )
            )
            .order_by("-created_at")
        )