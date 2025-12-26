import hashlib
from django.utils import timezone
import os
from django.conf import settings
import pytz
import importlib
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
import re
from django.contrib.contenttypes.models import ContentType
import logging
from constants.error_codes import ErrorCodes
import difflib
import datetime
from datetime import time, datetime
import holidays
import requests
from datetime import datetime
from django.conf import settings
import random
import string
import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect



class Utils:
    @staticmethod
    def get_token_from_header(request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]
        return None

    @staticmethod
    def hash_lib_sha(val):
        return hashlib.sha256(val.encode()).hexdigest()

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def get_current_datetime():
        vie_tz = pytz.timezone("Asia/Ho_Chi_Minh")
        return timezone.now().astimezone(vie_tz)

    @staticmethod
    def validate_uidb64(uidb64):
        return force_str(urlsafe_base64_decode(uidb64))

    @staticmethod
    def get_setting(key, default=None, cast_type=None):
        value = getattr(settings, key, os.getenv(key, default))
        if value in [None, ""]:
            return default
        if cast_type:
            try:
                return cast_type(value)
            except (ValueError, TypeError):
                return default
        return value

    # Logging utils
    @staticmethod
    def get_class_with_importlib(module_path: str, wanted_class: str):
        module = importlib.import_module(module_path)
        return getattr(module, wanted_class)

    @staticmethod
    def logger():
        return logging.getLogger(__name__)

    @staticmethod
    def extract_content_type(value):
        if not value:
            raise ValueError(ErrorCodes.CONTENT_TYPE_NOT_FOUND)
        special_case_map = {
            "auth.user": "user.user",
            "django.user": "user.user",
            "default.user": "user.user",
        }
        user_field_keywords = {"created_by", "updated_by", "assigned_by", "modified_by"}
        if any(keyword in value.lower() for keyword in user_field_keywords):
            user_cts = ContentType.objects.filter(model="user")
            if not user_cts.exists():
                raise ValueError(ErrorCodes.CONTENT_TYPE_NOT_FOUND)
            for ct in user_cts:
                if ct.app_label == "user":
                    return ct
            return user_cts.first()

        if "." in value:
            try:
                app_label, model_name = value.strip().split(".")
                app_model = f"{app_label.lower()}.{model_name.lower()}"
                mapped_model = special_case_map.get(app_model, app_model)
                app_label, model_name = mapped_model.split(".")
                return ContentType.objects.get(app_label=app_label, model=model_name)
            except (ValueError, ContentType.DoesNotExist):
                pass

        value_lower = value.lower()
        words = re.findall(r"\b\w+\b", value_lower)
        all_model_paths = []
        model_path_map = {}

        for ct in ContentType.objects.all():
            full_model_path = f"{ct.app_label}.{ct.model}"
            all_model_paths.append(full_model_path)
            model_path_map[full_model_path] = ct

        joined = " ".join(words)
        close_matches = difflib.get_close_matches(
            joined, all_model_paths, n=1, cutoff=0.3
        )

        if close_matches:
            best_match = close_matches[0]
            mapped_match = special_case_map.get(best_match, best_match)
            return model_path_map.get(mapped_match)

        raise ValueError(ErrorCodes.CONTENT_TYPE_NOT_FOUND)
    
    @staticmethod
    def get_path_from_url(url: str) -> str:
        """
        Extracts the file path from a given URL by removing the MEDIA_URL prefix.
        """
        if not url:
            return ""
        if url.startswith('http'):
            url = url.split(settings.MEDIA_URL, 1)[-1]
            url = settings.MEDIA_URL + url
            return url
        
    @staticmethod
    def upload_thumnail(request, field):
        from air_pollution_be.serializers.hotel_serializer import ThumbnailSerializer

        try:
            if f'{field}' in request.data:
                file = request.data[f'{field}']
                serializer = ThumbnailSerializer(data={'file': file}, context={'request': request, 'field': field})
                
                if serializer.is_valid():
                    path_file = serializer.save()
                    return path_file
            
            
        except Exception as e:
            raise e
        
    
    