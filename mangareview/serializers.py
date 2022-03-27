from rest_framework import serializers
from .models import Series, Review
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    liked = serializers.ReadOnlyField(source='liked.count')
    # likes= serializers.ReadOnlyField(source='likes.count')

    class Meta:
        model = User
        fields = ['id','liked','username', 'email']
        # extra_kwargs = {
        #     'first_name': {'required': False},
        #     'last_name': {'required': False}
        # }

class RegisterSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id','username', 'password', 'password2', 'email')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        if validated_data['password'] != validated_data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
       
        else:
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
            )

            user.set_password(validated_data['password'])
            user.save()

        return user

class ReviewSerializer(serializers.ModelSerializer):
    # series = serializers.CharField(source='series.title')
    reviewer = serializers.ReadOnlyField(source='reviewer.username')
    likes= serializers.ReadOnlyField(source='likes.count')
    series= serializers.ReadOnlyField(source='series.title')
    date=serializers.ReadOnlyField()
   
    class Meta:
        model = Review
        fields = "__all__"
     
class SeriesSerializer(serializers.ModelSerializer):
    # reviews = ReviewSerializer(many=True,read_only=True)
    rating = serializers.ReadOnlyField()
    number_of_reviews = serializers.ReadOnlyField(source='reviews.count')
    
    class Meta:
        model = Series
        fields = "__all__"
        # exclude =["reviews"]
        # extra_kwargs = {
        #     'chapters': {'required': False},
        #     'volumes': {'required': False}
        # }
        #depth=1
  