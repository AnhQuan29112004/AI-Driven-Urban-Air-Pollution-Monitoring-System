import datetime
import json
from utils.swagger_decorators import auto_schema_post, auto_schema_get, auto_schema_put, auto_schema_delete, auto_schema_patch
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from django.db import transaction
from rest_framework.permissions import AllowAny,IsAuthenticated, IsAdminUser
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
from libs.querykit.querykit import Querykit
from libs.querykit.querykit_serializer import (
    QuerykitSerializer,
)
from django.db.models import Count
from validators.validator import Validator
from constants.constants import Constants
from django.utils import timezone

@auto_schema_get(UserSerializer)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def current_user_infor(request):
    try:
        user = request.user
        cache_key = f"user:{user.id}"
        cached_user = RedisWrapper.get(cache_key)
        if(cached_user):
            data=cached_user
            print(data)
        else:
            data = UserSerializer(user).data
        return AppResponse.success(SuccessCodes.USER_INFOR,data=data)
    except Exception as e:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND, str(e))
            
            
@auto_schema_post(QuerykitSerializer)
@permission_classes([IsAdminUser])
@api_view(['POST'])
def list_user(request):
    try:
        list_user = User.objects.filter(is_deleted=0)
        print(list_user)
        paginated_user, total = Querykit.apply_filter_paginate_search_sort(request=request, queryset=list_user).values()
        print(paginated_user)
        status_display = {
            1: "active",
            2: "inactive"
        }
        serializer = UserSerializer(instance=paginated_user, many=True)
        status_counts = User.objects.values("status").annotate(count=Count("id"))
        status_count_dict = {item["status"]: item["count"] for item in status_counts}
        status_summary = {
        label: status_count_dict.get(code, 0) for code, label in status_display.items()
        }

        return AppResponse.success(SuccessCodes.LIST_USER, data = {"users": serializer.data,
                "total_user": total,
                "status_summary": status_summary,})
    except Exception as e:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND, str(e))
    
@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def get_all_user(request):
    print('request ne: ', request.data)
    if "search_rule" in request.data and request.data["search_rule"]:
        print('request ne: ', request)
        qk = Querykit()
        users = qk.apply_search(User.objects.all(), request)
    else:
        users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return AppResponse.success(SuccessCodes.LIST_USER, 
                                data=serializer.data)

@auto_schema_post(UserSerializer)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    user = request.user
    avatar = request.data.get("avatar")
    try:
        Validator.validate_avatar(avatar)
    except Exception as e:
        return AppResponse.error(ErrorCodes.VALIDATION_ERROR, message=str(e))
    user.avatar = avatar
    user.save()
    return AppResponse.success(
        SuccessCodes.UPLOAD_AVATAR,
        data={"avatar": user.avatar}
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_username(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND)

    return AppResponse.success(
        SuccessCodes.GET_USER,
        data={"username": user.username},
    )
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_infor(request):
 
    user = request.user
    userUpdated = User.objects.get(id = user.id)
    count = userUpdated.created_news.count()
    user_data_response = {
        "user": {**UserSerializer(userUpdated).data, "total_post": count},
      
    }
    # token = Utils.get_token_from_header(request)
    # cache_key = Rediskeys.USER(user.id)
    # user_data = RedisWrapper.get(cache_key)
    # if user_data:
    #     user = User(**user_data)
    # else:
    #     user = User.objects.get(id=user.id)
    #     exp = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]).get("exp")
    #     if exp:
    #         ttl = exp - int(time.time())
    #         if ttl > 0:
    #             RedisWrapper.save(cache_key, UserSerializer(user).data, ttl)
    #         else:
    #             raise AppException(ErrorCodes.TOKEN_EXPIRED)
    #     else:
    #         raise AppException(ErrorCodes.INVALID_TOKEN)
    
    return AppResponse.success(
        success_code=SuccessCodes.USER_INFOR,
        data=user_data_response,
    )
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_info_by_id(request, id):
    user = User.objects.get(id = id)
    serializer = UserSerializer(instance = user)
    data = serializer.data
    
    return AppResponse.success(
        success_code=SuccessCodes.USER_INFOR,
        data=data
    )



@auto_schema_put(UserSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile information."""
    try:
        key = f"user:{request.data.get('id')}"
        RedisWrapper.remove(key)
        serializer = UserSerializer(
            instance = request.user,
            data=request.data,
            partial=True,
            context={
                "request": request
            },
        )

        if not serializer.is_valid():
            return AppResponse.error(ErrorCodes.VALIDATION_ERROR, errors=serializer.errors)

        serializer.save()
      

        return AppResponse.success(SuccessCodes.UPDATE_USER, data=serializer.data)

    except Exception as e:
        return AppResponse.error(ErrorCodes.UPDATE_PROFILE_FAIL, message=str(e))



@api_view(["GET"])
@permission_classes([AllowAny])
def admin_infor(request):
    try:
        get_admin = User.objects.all().filter(role=1).order_by('created_at')[:1]
        serializer = UserSerializer(instance=get_admin, many=True)
        admin_infor = serializer.data
        return AppResponse.success(SuccessCodes.ADMIN_INFOR,{
            'admin_infor': admin_infor
        })
    except Exception as e:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND)

@auto_schema_post(UserSerializer)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def register_user(request):
    
    try:
        password = request.data.get('password')
        with transaction.atomic():
            serializer = UserSerializer(
                data=request.data,
                context={
                    "request": request,
                    Constants.ADMIN_REGISTER_USER: True,
                },
            )

            if not serializer.is_valid():
                print("[VALIDATION ERROR]", serializer.errors)
                return AppResponse.error(
                    ErrorCodes.VALIDATION_ERROR,
                    errors=serializer.errors,
                )

            # Lưu vào PostgreSQL
            user = serializer.save()

            print(f"[REGISTER] Created user: {user.username} ({user.email})")
            user.set_password(password)
            user.save()

        return AppResponse.success(SuccessCodes.ADMIN_CREATE_USER)

    except Exception as e:
        print(f"[REGISTER ERROR] {e}")
        return AppResponse.error(ErrorCodes.ERROR_REGISTER_USER, detail=str(e))



@auto_schema_put(UserSerializer)
@api_view(["PUT"])
@permission_classes([IsAdminUser, IsAuthenticated])
def update_user_profile(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND)
    
    serializer = UserSerializer(
        user,
        data=request.data,
        partial=True,
        context={
            "request": request,
            Constants.EDIT_USER_PROFILE: True,
        },
    )

    if not serializer.is_valid():
        print(f"Validation errors: {serializer.errors}")
        return AppResponse.error(ErrorCodes.VALIDATION_ERROR, errors=serializer.errors)

    try:
        with transaction.atomic():
            # 1. Lưu vào DB trước
            serializer.save()

            # 2. Lấy dữ liệu mới đã được cập nhật
            updated_user = serializer.instance
           
            

    except Exception as e:
       
        return AppResponse.error(ErrorCodes.KEYCLOAK_UPDATE_FAILED, errors=str(e))

    return AppResponse.success(SuccessCodes.UPDATE_USER_PROFILE)



@api_view(["DELETE"])
@permission_classes([IsAdminUser, IsAuthenticated])
def delete_user(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return AppResponse.error(ErrorCodes.USER_NOT_FOUND)

    if user.is_superuser:
        return AppResponse.error(ErrorCodes.CAN_NOT_DELETE_SUPER_UER)

    try:
        with transaction.atomic():
            user.soft_delete()
           
      
        return AppResponse.success(SuccessCodes.DELETE_USER)

    except Exception as e:
        # Có thể log lỗi chi tiết ở đây nếu muốn
        import traceback
        traceback.print_exc() 
        return AppResponse.error(ErrorCodes.INTERNAL_SERVER_ERROR, errors=str(e))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    import uuid
    import os
    from django.conf import settings
    try:
        file = request.FILES.get('image')
        if not file:
            return AppResponse.error(ErrorCodes.INVALID_REQUEST, errors="No image file provided")
            
        # allowed_types =  ["image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff", "image/webp"]
        if file.content_type not in Constants.ALLOWED_AVATAR_TYPES:
            return AppResponse.error(ErrorCodes.INVALID_REQUEST, errors="Invalid file type. Only JPEG, PNG, GIF, BMP and WEBP are allowed")
            
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'stores')
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"{uuid.uuid4()}_{file.name}"
        filepath = os.path.join(upload_dir, filename)
        
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
                
        image_url = f"{settings.MEDIA_URL}uploads/stores/{filename}"
       
        return AppResponse.success(SuccessCodes.UPLOAD_IMAGE, data={"url": image_url})
        
    except Exception as e:
        return AppResponse.error(ErrorCodes.UNKNOWN_ERROR, errors=str(e))
