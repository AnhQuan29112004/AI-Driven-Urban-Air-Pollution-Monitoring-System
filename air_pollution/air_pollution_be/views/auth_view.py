import datetime

from django.conf import settings
from utils.swagger_decorators import auto_schema_post
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny,IsAuthenticated
from libs.response_handle import AppResponse
from air_pollution_be.models.user import User
from rest_framework.decorators import api_view
from constants.success_codes import SuccessCodes
from configuration.jwt_config import JwtConfig
from air_pollution_be.serializers.user_serializer import UserSerializer
from django.contrib.auth import authenticate
from constants.error_codes import ErrorCodes
from django.contrib.auth.models import update_last_login
from libs.Redis import RedisWrapper
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

@auto_schema_post(UserSerializer)
@permission_classes([AllowAny])
@api_view(['POST'])
def login(request, username=None, password=None):
    try:
        taiKhoan = request.data.get('username')
        password = request.data.get('password')
        print(taiKhoan, password)
        user = authenticate(username=taiKhoan, password=password)
        print("DATA USER: ",user)
        if not user:
            return AppResponse.error("Fail login", "Sai thông tin tài khoản hoặc mật khẩu")
        jwt_token = JwtConfig.generate(user)
        token = {"access_token": jwt_token["token"], "refresh_token": jwt_token["refresh_token"]}
        first_login = user.last_login is None
        update_last_login(None, user)
        
        return AppResponse.success("login successfully", data={'token':token, 'user':UserSerializer(user, context = {"request": request}).data, 'isFisrtLogin' : first_login})
    except:
        print("LOI DANG NHAP")
        return AppResponse.error("Fail login", "Invalid password or username")
        

@auto_schema_post(UserSerializer)
@permission_classes([AllowAny])
@api_view(['POST'])
def register(request):
    try:
        taiKhoan = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get("email")
        phone = request.data.get("phone")
        address = request.data.get("address_line")
        gender = request.data.get("gender")
        full_name = request.data.get("full_name")
        birthday = datetime.strptime(request.data.get("birthday"), "%Y-%m-%d").date() if request.data.get("birthday") else None
        keycloak_id = request.data.get("sub")
        
        serializer = UserSerializer(
            data={
                "username": taiKhoan,
                "email": email,
                "phone": phone,
                "gender": gender,
                "full_name" :full_name,
                "birthday": birthday,
                "address": address,
                "status": 1,  # Assuming 1 is the default active status
            },
            context={
                "request": request
            }
        )
        if not serializer.is_valid():
            return AppResponse.error(
                ErrorCodes.VALIDATION_ERROR,
                errors=serializer.errors
            )
        try:
            
            user = serializer.save()
        except Exception as e:
            return AppResponse.error(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                errors=str(e)
            )
        user.set_password(password)
        user.save()
        return AppResponse.success(SuccessCodes.REGISTER, data=UserSerializer(user).data)
    except Exception as e:
        return AppResponse.error("Fail register", str(e))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    user = request.user
    key_redis = f"user:{user.id}"
    is_remove_cache = RedisWrapper.remove(key_redis)
    if(is_remove_cache):
        return AppResponse.success(SuccessCodes.LOGOUT)
    else:
        return AppResponse.error(ErrorCodes.LOGOUT_FAIL)
    

@auto_schema_post()
@permission_classes([AllowAny])
@api_view(['POST'])
def refresh_token(request):
    try:
        refresh_token = request.data.get('refresh_token')
        jwt = JwtConfig.refresh(refresh_token)
        return AppResponse.success(SuccessCodes.REFRESH_TOKEN, data={'token':jwt['token'], 'refresh_token':jwt['refresh_token']})
    except Exception as e:
        return AppResponse.error(ErrorCodes.REFRESH_TOKEN_ERROR, str(e))
    
@api_view(['POST'])
def google_auth(request):
    token = request.data.get('id_token')
    if not token:
        return AppResponse.error(ErrorCodes.AUTHENTICATION_FAILED)

    try:
        # VERIFY token với Google
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)

        # idinfo chứa: 'sub' (google id), 'email', 'email_verified', 'name', 'picture', ...
        if not idinfo.get('email_verified'):
            return AppResponse.error(ErrorCodes.NOT_VERIFY_EMAIL_GOOGLE)

        email = idinfo.get('email')
        google_sub = idinfo.get('sub')
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')

        # Tạo hoặc lấy user
        user, created = User.objects.get_or_create(email=email, defaults={
            'username': email.split('@')[0],
            'full_name': name,
            'avatar': picture
        })
        # (tuỳ chọn) lưu google_sub vào profile/model nếu muốn

        # Tạo JWT (SimpleJWT)
        jwt_token = JwtConfig.generate(user)
        token = {"access_token": jwt_token["token"], "refresh_token": jwt_token["refresh_token"]}
        update_last_login(None, user)
        
        return AppResponse.success(SuccessCodes.LOGIN, data={'token':token, 'user':UserSerializer(user, context = {"request": request}).data})
    except Exception as e:
        return AppResponse.error(ErrorCodes.LOGIN_TOO_MANY_ATTEMPTS, str(e))
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    try:
        current_password: str = request.data.get("current_password")
        new_password: str = request.data.get("new_password")

        if not current_password:
            return AppResponse.error(
                error_code=ErrorCodes.CURRENT_PASSWORD_REQUIRED,
                errors=["Old password is required"]
            )

        if not new_password:
            return AppResponse.error(
                error_code=ErrorCodes.NEW_PASSWORD_REQUIRED,
                errors=["New password is required"]
            )

        user: User = request.user
        
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return AppResponse.error(
                error_code=ErrorCodes.VALIDATION_NEW_PASSWORD,
                errors=e.messages
            )

        with transaction.atomic():
            user.set_password(new_password)
            user.save()


        return AppResponse.success(success_code=SuccessCodes.CHANGE_PASSWORD)

    except Exception as e:
        return AppResponse.error(
            error_code=ErrorCodes.CANNOT_CHANGE_PASSWORD,
            errors=str(e)
        )