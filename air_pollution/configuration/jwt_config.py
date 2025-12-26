from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from exceptions.exceptions import AppException
from constants.error_codes import ErrorCodes
from air_pollution_be.models.user import User
from utils.utils import Utils


class JwtConfig:
    @staticmethod
    def generate(user):
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)

        return {
            "token": token,
            "refresh_token": str(refresh),
            "redis_key": Utils.hash_lib_sha(token),
        }

    @staticmethod
    def validate(request):
        token = Utils.get_token_from_header(request)
        return {"token": token, "redis_key": Utils.hash_lib_sha(token)}

    @staticmethod
    def refresh(refresh_token):
        refresh_token_obj = RefreshToken(refresh_token)
        user_id = refresh_token_obj.payload.get("user_id")
        
        if not user_id:
            raise AppException(ErrorCodes.USER_NOT_FOUND)  

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AppException(ErrorCodes.USER_NOT_FOUND)

        access_token = str(refresh_token_obj.access_token)

        return {
            "token": access_token,
            "refresh_token": str(refresh_token_obj),
            "user": user,
            "redis_key": Utils.hash_lib_sha(access_token),
        }


    @staticmethod
    def generate_token(key, value, time):
        token = AccessToken()
        token[key] = value
        token.set_exp(lifetime=timedelta(minutes=time))
        return str(token)

    @staticmethod
    def get_from_token(key, token_str):
        try:
            token = AccessToken(token_str)
            return token.get(key)
        except:
            return None
        