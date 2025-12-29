from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers


class CustomJWTLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Add user info to the response
        data['user'] = {
            "pk": user.pk,
            "email": user.email,
            "username": user.username
        }

        return data


class UserSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    email = serializers.EmailField()
    username = serializers.CharField()

class JWTLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()

class JWTLoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)