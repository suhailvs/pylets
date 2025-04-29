import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from coinapp.models import Listing, Transaction
from .fields import HyperlinkedSorlImageField

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name","last_login", "username","is_active", "balance",
            'phone','government_id','date_of_birth','exchange']
        read_only_fields = fields

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            "first_name",
            'email',
            "phone",
            "password",
            "government_id",
            "date_of_birth",
            "exchange",
            'username',
        ]
        read_only_fields = ['username']

    def generate_username(self, exchange):
        PREFIX = exchange.code
        latest_user = User.objects.filter(username__startswith=PREFIX).order_by('-username').first()
        if latest_user:
            # Extract the numeric part
            match = re.search(r'(\d+)$', latest_user.username)
            if match:
                number = int(match.group(1)) + 1
            else:
                number = 1
        else:
            number = 1

        return f"{PREFIX}{str(number).zfill(3)}"  # 3-digit number with leading zeros

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
        validated_data['username'] = self.generate_username(validated_data['exchange'])
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
        fields = ("id", "category", "title", "image",'rate','thumbnail')
    # https://github.com/dessibelle/sorl-thumbnail-serializer-field/tree/master#example-usage
    thumbnail = HyperlinkedSorlImageField(
        '128x128',
        options={"crop": "center"},
        source='image',
        read_only=True
    )


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
    is_received = serializers.ReadOnlyField(default=False)
    seller_name = serializers.ReadOnlyField(source="seller.first_name")
    buyer_name = serializers.ReadOnlyField(source="buyer.first_name")

    class Meta:
        model = Transaction
        fields = "__all__"
