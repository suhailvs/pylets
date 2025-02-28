from rest_framework import viewsets  # import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, F, BooleanField, Case, When
from django.contrib.auth import get_user_model
from django.db import transaction
from coinapp.models import Listing, Transaction
from .serializers import (
    ListingModelSerializer,
    ListingDetailSerializer,
    TransactionSerializer,
    UserSerializer,
)

User = get_user_model()


class ListingModelViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    # queryset = Listing.objects.all()
    def get_queryset(self):
        user = self.request.user
        qs = Listing.objects.filter(user__exchange=user.exchange)
        # c = Listing.listing_type.field.choices[0][0]
        if self.action == "list":
            qs = qs.filter(listing_type=self.request.GET.get("type", "O"))
        return qs

    def get_serializer_class(self):
        """Return different serializers for list and detail views"""
        if self.action == "list":
            return ListingModelSerializer
        return ListingDetailSerializer


class GetUserBalance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response(request.user.amount)


class Transactions(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = self.request.user
        qs = (
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
        serializer = TransactionSerializer(qs, many=True)  # Serialize orders
        return Response(serializer.data)

    def post(self, request):
        transaction_type = "buyer"  # request.data["transaction_type"] # buyer or seller
        amt = request.data["amount"]
        desc = request.data["message"]
        # default is seller transaction(receive money)
        seller = request.user
        buyer = User.objects.get(id=request.data["user"])
        if seller == buyer:
            msg = "You cannot send money to you own account"
            return Response(msg,status=status.HTTP_400_BAD_REQUEST)

        if transaction_type == "buyer":
            # send money
            seller, buyer = buyer, seller
        with transaction.atomic():
            seller.amount = F("amount") + amt
            buyer.amount = F("amount") - amt
            seller.save(update_fields=["amount"])
            buyer.save(update_fields=["amount"])
            txn = Transaction.objects.create(
                seller=seller,
                buyer=buyer,
                description=desc,
                amount=amt,
            )
            serializer = TransactionSerializer(txn)
            return Response(serializer.data)


class GetUsers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        qs = (
            User.objects.exclude(id=request.user.id)
            .filter(exchange=request.user.exchange)
            .order_by("first_name")
        )
        serializer = UserSerializer(qs, many=True)  # Serialize orders
        return Response(serializer.data)
