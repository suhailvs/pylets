from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import BooleanField, Case, F, Q, When
from rest_framework import viewsets  # import ModelViewSet
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.serializers import ValidationError
from coinapp.models import Listing, Transaction

from .serializers import (
    ListingCreateSerializer,
    ListingDetailSerializer,
    ListingListSerializer,
    TransactionSerializer,
    UserSerializer,
    UserCreateSerializer,
)

User = get_user_model()


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        # serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            # check for inactive users
            inactive_user = User.objects.filter(username=request.data['username']).first()
            if inactive_user:
                if inactive_user.check_password(request.data['password']):
                    # user is inactive
                    return Response({'is_active':False, 'message':'Verification is pending.'})
            raise ValidationError(serializer.errors)
        
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "key": token.key,
                "user_id": user.pk,
                "username": user.username,
                "exchange": user.exchange_id,
            }
        )

class CreateUserView(CreateAPIView):

    model = User
    # permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer


class GetUserBalance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response(request.user.balance)


class GetUsers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        qs = (
            User.objects.exclude(id=request.user.id)
            .filter(exchange=request.user.exchange)
            .order_by("first_name")
        )
        serializer = UserSerializer(qs, many=True)
        return Response(serializer.data)


class ListingModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    # queryset = Listing.objects.all()
    def get_queryset(self):
        user = self.request.user
        qs = Listing.objects.filter(user__exchange=user.exchange)
        # c = Listing.listing_type.field.choices[0][0]
        if self.action == "list":
            qs = qs.filter(listing_type=self.request.GET.get("type", "O"))
            print("requests:", self.request.GET)
        return qs.order_by("-created_at")

    def get_serializer_class(self):
        """Return different serializers for list, create and detail views"""
        if self.action == "list":
            return ListingListSerializer
        if self.action == "create":
            return ListingCreateSerializer
        return ListingDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



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
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        if transaction_type == "buyer":
            # send money
            seller, buyer = buyer, seller
        with transaction.atomic():
            seller.balance = F("balance") + amt
            buyer.balance = F("balance") - amt
            seller.save(update_fields=["balance"])
            buyer.save(update_fields=["balance"])
            txn = Transaction.objects.create(
                seller=seller,
                buyer=buyer,
                description=desc,
                amount=amt,
            )
            serializer = TransactionSerializer(txn)
            return Response(serializer.data)

