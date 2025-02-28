from rest_framework import serializers
from django.contrib.auth import get_user_model
from coinapp.models import Listing, Transaction

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name','amount','last_login','username'] # ,'phone']#'__all__'

class ListingDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nest the entire Category object
    class Meta:
        model = Listing
        fields = '__all__'

class ListingModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ("id", "category", "heading","img")
    
class TransactionSerializer(serializers.ModelSerializer):
    is_received = serializers.BooleanField(default=False)
    seller_name = serializers.ReadOnlyField(source='seller.first_name')
    buyer_name = serializers.ReadOnlyField(source='buyer.first_name')
    class Meta:
        model = Transaction
        fields = '__all__'