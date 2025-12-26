import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    try:
        UntypedToken(token)
        decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_data.get('user_id')
        if user_id:
            return User.objects.get(id=user_id)
    except (InvalidToken, TokenError, jwt.DecodeError):
        return None
    return None


class JWTAuthMidderwareSocket(BaseMiddleware):
    """
    Custom middleware cho Django Channels để gắn user vào scope.
    """

    async def __call__(self, scope, receive, send):
        # Lấy token từ query string
        query_string = parse_qs(scope["query_string"].decode())
        token = None
        scope["user"] = AnonymousUser()

        if "token" in query_string:
            token = query_string["token"][0]

        if not token:
            # fallback: lấy từ header nếu có
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", None)
            if auth_header:
                try:
                    token = auth_header.decode().split("Bearer ")[1]
                except IndexError:
                    pass

        if token:
            user = await get_user_from_token(token)
            if user:
                scope["user"] = user

        return await super().__call__(scope, receive, send)