from rest_framework import serializers
from django.contrib.auth import get_user_model
from coinapp.models import Listing

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ListingDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nest the entire Category object
    class Meta:
        model = Listing
        fields = '__all__'

class ListingModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ("id", "category", "heading")