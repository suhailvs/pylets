from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from coinapp.models import Listing, Transaction, Exchange

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "balance", "last_login", "username"]

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            "first_name",
            "username",
            "password",
            "government_id",
            "date_of_birth",
            "exchange",
        ]

    def validate(self, attrs):       
        user = User(**attrs)
        password = attrs.get("password")
        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError({"password": serializer_error})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user


class ListingDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nest the entire Category object

    class Meta:
        model = Listing
        fields = "__all__"


class ListingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ("id", "category", "title", "image")


class ListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = (
            "id",
            "category",
            "title",
            "description",
            "rate",
            "listing_type",
            "image",
        )


class TransactionSerializer(serializers.ModelSerializer):
    is_received = serializers.BooleanField(default=False)
    seller_name = serializers.ReadOnlyField(source="seller.first_name")
    buyer_name = serializers.ReadOnlyField(source="buyer.first_name")

    class Meta:
        model = Transaction
        fields = "__all__"
