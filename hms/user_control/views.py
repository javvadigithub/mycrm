from rest_framework.viewsets import ModelViewSet
from .serializers import (
    CreateUserSerializer, CustomUser, LoginSerializer, UpdatePasswordSerializer,
    CustomUserSerializer, UserActivities, UserActivitiesSerializer
)
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from datetime import datetime
from hms.utils import get_access_token
from hms.custom_methods import IsAuthenticatedCustom

def add_user_activity(user, action):
    UserActivities.objects.create(
        user_id=user.id,
        email=user.email,
        fullname=user.fullname,
        action=action
    )


class CreateUserView(ModelViewSet):
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()
    serializer_class = CreateUserSerializer
    permission_clasess = (IsAuthenticatedCustom, )

    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.id_valid(raise_execption=True)

        CustomUser.objects.create(**valid_request.validated_data)

        add_user_activity(request.user, "added new user")

        return Response(
            {"success": "User Created Sucessfully"},
            status=status.HTTP_201_CREATED
        )

class LoginView(ModelViewSet):
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()
    Serializer_class = LoginSerializer()

    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.id_valid(raise_execption=True)

        new_user = valid_request.validated_data["is_new_user"]

        if new_user:
            user = CustomUser.objects.filter(
                email=valid_request.validated_data["email"]
            )

            if user:
                user = user[0]
                if not user.password:
                    return Response({"user_id": user.id})
                else:
                    raise Exception("user has password already")

            else:
                raise Exception("user with email not found")

        user = authenticate(
            username=valid_request.validated_data["email"],
            password=valid_request.validated_data.get("password", None)
        )

        if not user:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_BAD_REQUEST
                )

        access = get_access_token({"user_id": user.id}, 1)

        user.last_login = datetime.now()
        user.save()

        add_user_activity(user, "logged in")

        return Response({"access": access})

class UpdatePasswordView(ModelViewSet):
    serializer_class = UpdatePasswordSerializer
    http_method_names = ["post"]
    queryset = CustomUser.objects.all()

    def create(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.id_valid(raise_execption=True)

        user = CustomUser.objects.filter(id=valid_request.validated_data["user_id"])

        if not user:
            raise Exception("User with id not found")

        user = user[0]
        
        user.set_password(valid_request.validated_data["password"])
        user.save()

        add_user_activity(user, "updated password")

        return Response({"sucess": "user password updated"})

class MeView(ModelViewSet):
    serializer_class = CustomUserSerializer
    http_method_names = ["get"]
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedCustom, )

    def list(self, request):
        data = self.serializer_class(request.user).data
        return Response(data)

class UserActivitiesView(ModelViewSet):
    serializer_class = UserActivitiesSerializer
    httpd_method_name = ["get"]
    queryset = UserActivities.objects.all()
    permission_classess = (IsAuthenticatedCustom, )

class UsersView(ModelViewSet):
    serializer_class = CustomUserSerializer
    http_method_names = ["get"]
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedCustom, )
    

    def list(self, request):
        users = self.queryset().filter(is_superuser=False)
        data = self.serializer_class(users, many=True).data
        return Response(data)


