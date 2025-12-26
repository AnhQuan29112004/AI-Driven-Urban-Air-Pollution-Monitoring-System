import time
from air_pollution_be.serializers.user_serializer import UserSerializer
from constants.redis_keys import Rediskeys
import jwt
from rest_framework.authentication import BaseAuthentication
from constants.error_codes import ErrorCodes
from air_pollution_be.models.user import User
# from services.web_portal.models.classification import Classification
from utils.utils import Utils
from django.conf import settings
from libs.Redis import RedisWrapper
from exceptions.exceptions import AppException
from rest_framework.permissions import AllowAny


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
      
        if getattr(request, "permission_classes", None) == [AllowAny]:
            return None
        try:
            token = Utils.get_token_from_header(request)
           
            if not token:
                return None
            id = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]).get(
                "user_id"
            )
           
            if not id:
                raise AppException(ErrorCodes.AUTHENTICATION_FAILED)
            cache_key = Rediskeys.USER(id)
            user_data = RedisWrapper.get(cache_key)
            print("User data:", user_data)
            if user_data:
                user = User.objects.get(id=id)
            else:
                user = User.objects.get(id=id)
                exp = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]).get("exp")
                if exp:
                    ttl = exp - int(time.time())
                    if ttl > 0:
                        RedisWrapper.save(cache_key, UserSerializer(user).data, ttl)
                    else:
                        raise AppException(ErrorCodes.TOKEN_EXPIRED)
                else:
                    raise AppException(ErrorCodes.INVALID_TOKEN)
            
           
           
        except jwt.ExpiredSignatureError:
            raise AppException(ErrorCodes.TOKEN_EXPIRED)
        except jwt.InvalidTokenError:
            raise AppException(ErrorCodes.INVALID_TOKEN)
        except User.DoesNotExist:
            raise AppException(ErrorCodes.AUTHENTICATION_FAILED)
        return (user, token)
