import re
from typing import Any, Type
from collections import Counter
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password as django_validate_password
import requests
import utils.utils
from exceptions.exceptions import AppException
from django.db import models
from django.db.models import Model
from constants.error_codes import ErrorCodes
from constants.constants import Constants
from air_pollution_be.models.user import User
from utils.utils import Utils

class MultifieldValidator:
    @staticmethod
    def try_validate_multifields(cls, fields: list, data):
        errors = {}
        for field in fields:
            method_name = f"try_validate_{field}"
            if hasattr(cls, method_name):
                method = getattr(cls, method_name)
                err = method(data.get(field), return_message_only=True)
                Utils.logger().info(f"Error try validate multi: {err}")
                if isinstance(err, dict):
                    errors.update(err)
            else:
                errors[field] = f"Invalid field: {field}. No corresponding validation method found for field: {field}, in class: {str(cls)}. This field: {field} will be marked as invalid."
        print(f"Error: {errors}")
        return errors if errors else None

class Validator: 
    # Validate if "model" is a subclass of django.db.models.Model or not.
    @staticmethod
    def validate_model(model: Type[Any], error_code=ErrorCodes):
        if model is None or not isinstance(model, type):
            raise AppException(error_code, f"The model cannot be None and must be a class. Got: {type(model)}")
        if not issubclass(model, models.Model):
            raise AppException(error_code, f"The model {model.__name__} must be a subclass of django.db.models.Model.")
        return model   
    
    # Validate subclass. The required_subclass must be a class, not its instance. Pass class -> ok. Pass instance -> error
    @staticmethod
    def validate_args_subclass(args: Type[Any], expected_superclass: tuple[type, ...], error_code: ErrorCodes, error_message :str=None):
        if not isinstance(args, type):
            raise AppException(f"Argument must be a class type, got {type(args).__name__} - {error_code}")
        if not issubclass(args, expected_superclass):
            expected = ', '.join(t.__name__ for t in expected_superclass)
            raise AppException(f"Invalid class: expected subclass of {expected}, got {args.__name__} - {error_code}")
        return args

    @staticmethod
    def validate_args_type(args: Type[Any], expected_type: tuple[type, ...], error_code: ErrorCodes, error_message :str=None):
        if not isinstance(expected_type, tuple):
            # Convert expected_type to a tuple, if not
            expected_type = (expected_type,)
        if not isinstance(args, expected_type):
            expected = ", ".join([typ.__name__ for typ in expected_type])
            raise AppException(error_code, {'type_error' : f"Expected types : {expected}. Got type : {type(args).__name__}"}, error_message)
        return args
        
    @staticmethod
    def validate_email(email):
        if email is None:
            raise AppException(ErrorCodes.MISSING_REQUIRED_FIELD)
        # Check for Blank
        if not email.strip():
            raise AppException(ErrorCodes.BLANK_NOT_ALLOWED)
        # Django's validate_email does not check for None / blank / empty
        try:
            django_validate_email(email)
        except ValidationError:
            raise AppException(ErrorCodes.INVALID_EMAIL)
        
        return email

    @staticmethod
    def validate_phone(phone):
        # Check for None
        # if phone is None:
        #     raise AppException(ErrorCodes.MISSING_REQUIRED_FIELD)

        # # Check for blank
        # if not phone.strip():
        #     raise AppException(ErrorCodes.BLANK_NOT_ALLOWED)

        pattern = r'\+?(84|0)(2|3|5|7|8|9)[0-9]{8}\b'
        if not re.fullmatch(pattern, phone):
            raise AppException(ErrorCodes.INVALID_PHONE)

        # Length validation
        if len(phone) > 20:
            raise AppException(ErrorCodes.MAX_LENGTH_EXCEEDED)

        return phone
    
    @staticmethod
    def validate_name_destination(name):
        if name is None:
            raise AppException(ErrorCodes.MISSING_REQUIRED_FIELD)
        if not name.strip():
            raise AppException(ErrorCodes.BLANK_NOT_ALLOWED)
        if len(name) > 100:
            raise AppException(ErrorCodes.MAX_LENGTH_EXCEEDED)
        if len(name) < 3:
            raise AppException(ErrorCodes.MIN_LENGTH_NOT_MET)

        # Cho phép chữ cái tiếng Việt (có dấu), số, khoảng trắng và một số dấu câu
        pattern = r'^[\w\sÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂÊÔƠưăêôơ\-]+$'

        if not re.fullmatch(pattern, name, re.UNICODE):
            raise AppException(ErrorCodes.INVALID_NAME)

        return name

    @staticmethod
    def validate_username(username):
        # Check for None
        if username is None:
            raise AppException(ErrorCodes.MISSING_REQUIRED_FIELD)

        # Check for blank
        if not username.strip():
            raise AppException(ErrorCodes.BLANK_NOT_ALLOWED)

        # Length validation
        if len(username) > 150:
            raise AppException(ErrorCodes.MAX_LENGTH_EXCEEDED)
        if len(username) < 3:
            raise AppException(ErrorCodes.MIN_LENGTH_NOT_MET)

        # SRS : allow number, characters, '-', '@', '_'
        pattern = r'^[a-zA-Z0-9@_-]+$'
        if not re.fullmatch(pattern, username):
            raise AppException(ErrorCodes.INVALID_USERNAME)
        return username

    @staticmethod

    def validate_avatar(avatar):
        try:
            response = requests.head(avatar, allow_redirects=True, timeout=5)
            if response.status_code != 200:
                # Thử lại bằng GET nếu HEAD bị chặn
                if response.status_code in (403, 405):
                    response = requests.get(avatar, stream=True, timeout=5)
                else:
                    raise ValidationError(f"Không thể truy cập ảnh từ liên kết đã cung cấp (HTTP {response.status_code}).")
            content_type = response.headers.get("Content-Type", "")
            content_length = int(response.headers.get("Content-Length", 0))
            # print('Avatar URL:', avatar)
            # print('Response:', response)
            # print('Content-Type:', content_type)
            # print('Content-Length:', content_length)
            if content_type not in Constants.ALLOWED_AVATAR_TYPES:
                raise ValidationError("Chỉ chấp nhận ảnh jpg, png, gif, bmp, tiff, webp.")
            max_size = Constants.MAX_AVATAR_SIZE_MB * 1024 * 1024
            if content_length > max_size:
                raise ValidationError("Ảnh vượt quá dung lượng cho phép (tối đa 5MB).")
        except requests.exceptions.RequestException:
            raise ValidationError("Không thể truy cập ảnh từ liên kết đã cung cấp.")
        return avatar

    @staticmethod
    def validate_password(password):
        # Check for None
        if password is None:
            raise AppException(ErrorCodes.MISSING_REQUIRED_FIELD)

        # Check for blank
        if not password.strip():
            raise AppException(ErrorCodes.BLANK_NOT_ALLOWED)

        # Length validation
        if len(password) < 8:
            raise AppException(ErrorCodes.MIN_LENGTH_NOT_MET)

        # Max length = 128 is the max password length after hashing,
        # not the max length of password input.
        
        # Password validation
        # django_validate_password does not handle None/blank password
        try:
            django_validate_password(password)
        except ValidationError:
            raise AppException(ErrorCodes.WEAK_PASSWORD)

        return None
    
    
    # TRY - EXCEPT validators. Usually used for Serializers with built-in [try-except] to handle exceptions gracefully and prevent unintentional shutdowns of codeflow.
    @staticmethod
    def try_validate_email(email, return_message_only=False):
        """
        Validate the provided email address using a try-except block.
        Email: NotNull


        - Args:
            - email (str): The email address to validate.
            - return_message_only (bool): Default False.
                If True, returns only the error message inside a list.
                If False, returns a detailed error dictionary inside a list.
                Examples:
                    - If return_message_only is True:
                        {"email": ["Invalid email format."]}
                    - If return_message_only is False:
                        {"email": [{"code": 1103, "message": "Invalid email format."}]}

        - Raises:
            - All exceptions are handled internally.

        - Returns:
            - str or dict: The validated email string or an error dictionary.
        """
        errors = {}
        try:
            if email is None:
                raise AppException(ErrorCodes.MISSING_REQUIRED_FIELD)
            if not email.strip():
                raise AppException(ErrorCodes.BLANK_NOT_ALLOWED)
            django_validate_email(email)
        except AppException as ea:
            details = ea.get_full_details()
            errors["email"] = [details.get("message")] if return_message_only else [details]
            return errors
        except ValidationError as ev:
            errors["email"] = [str(ev.args[0])]
            return errors
        except Exception as e:
            errors["email"] = [str(e)] if return_message_only else [{"code": 0000, "message": f"Error: {str(e)}"}]
            return errors
        return email

    @staticmethod
    def try_validate_phone(phone, return_message_only=False):
        """
        Validate the provided phone number using a try-except block.
        Phone: Nullable

        - Args:
            - phone (str): The phone number to validate.
            - return_message_only (bool): Default False.
                If True, returns only the error message inside a list.
                If False, returns a detailed error dictionary inside a list.
                Examples:
                    - If return_message_only is True:
                        {"phone": ["Invalid phone number format."]}
                    - If return_message_only is False:
                        {"phone": [{"code": 1104, "message": "Invalid phone number format."}]}

        - Raises:
            - All exceptions are handled internally.

        - Returns:
            - str or dict: The validated phone string or an error dictionary.
        """
        errors = {}
        if phone is None:
            return phone
        try:
            if not phone.strip():
                raise AppException(ErrorCodes.BLANK_NOT_ALLOWED)
            pattern = r'\+?(84|0)(3|5|7|8|9)[0-9]{8}\b'
            if not re.fullmatch(pattern, phone):
                raise AppException(ErrorCodes.INVALID_PHONE)
            if len(phone) > 20:
                raise AppException(ErrorCodes.MAX_LENGTH_EXCEEDED)
        except AppException as ea:
            details = ea.get_full_details()
            errors["phone"] = [details.get("message")] if return_message_only else [details]
            return errors
        except Exception as e:
            errors["phone"] = [str(e)] if return_message_only else [{"code": 0000, "message": f"Error: {str(e)}"}]
            return errors
        return phone

    @staticmethod
    def try_validate_username(username, return_message_only=False):
        """
        Validate the provided username using a try-except block.
        Username: NotNull

        - Args:
            - username (str): The username to validate.
            - return_message_only (bool): Default False.
                If True, returns only the error message inside a list.
                If False, returns a detailed error dictionary inside a list.
                Examples:
                    - If return_message_only is True:
                        {"username": ["Username must be at least 3 characters long."]}
                    - If return_message_only is False:
                        {"username": [{"code": 1105, "message": "Username must be at least 3 characters long."}]}

        - Raises:
            - All exceptions are handled internally.

        - Returns:
            - str or dict: The validated username string or an error dictionary.
        """

        errors = {}
        try:
            if username is None:
                raise AppException(ErrorCodes.MISSING_REQUIRED_FIELD)
            if not username.strip():
                raise AppException(ErrorCodes.BLANK_NOT_ALLOWED)
            if len(username) > 150:
                raise AppException(ErrorCodes.MAX_LENGTH_EXCEEDED)
            if len(username) < 3:
                raise AppException(ErrorCodes.MIN_LENGTH_NOT_MET)
            pattern = r'^[a-zA-Z0-9@_-]+$'
            if not re.fullmatch(pattern, username):
                raise AppException(ErrorCodes.INVALID_USERNAME)
        except AppException as ea:
            details = ea.get_full_details()
            errors["username"] = [details.get("message")] if return_message_only else [details]
            return errors
        except Exception as e:
            errors["username"] = [str(e)] if return_message_only else [{"code": 0000, "message": f"Error: {str(e)}"}]
            return errors
        return username

    @staticmethod
    def try_validate_password(password, return_message_only=False):
        """
        Validate the provided password using a try-except block.
        Password: Nullable

        - Args:
            - password (str): The password to validate.
            - return_message_only (bool): Default False.
                If True, returns only the error message inside a list.
                If False, returns a detailed error dictionary inside a list.
                Examples:
                    - If return_message_only is True:
                        {"password": ["Password must be at least 8 characters long."]}
                    - If return_message_only is False:
                        {"password": [{"code": 1106, "message": "Password must be at least 8 characters long."}]}

        - Raises:
            - All exceptions are handled internally.

        - Returns:
            - str or dict: The validated password string or an error dictionary.
        """
        
        errors = {}
        try:
            if not password.strip():
                raise AppException(ErrorCodes.BLANK_NOT_ALLOWED)
            if len(password) < 8:
                raise AppException(ErrorCodes.MIN_LENGTH_NOT_MET)
            django_validate_password(password)
        except AppException as ea:
            details = ea.get_full_details()
            errors["password"] = [details.get("message")] if return_message_only else [details]
            return errors
        except Exception as e:
            errors["password"] = [str(e)] if return_message_only else [{"code": 0000, "message": f"Error: {str(e)}"}]
            return errors
        return password
    
    
    # Validator functions for uniqueness validate only.
    @staticmethod
    def validate_email_unique(email):
        if User.objects.filter(email=email).exists():
            raise AppException(ErrorCodes.EMAIL_ALREADY_EXISTS)
        return email
        
    @staticmethod
    def validate_phone_unique(phone):
        if User.objects.filter(phone=phone).exists():
            raise AppException(ErrorCodes.PHONE_ALREADY_EXISTS)
        return phone
    
    @staticmethod
    def validate_username_unique(username):
        if User.objects.filter(username=username).exists():
            raise AppException(ErrorCodes.USERNAME_ALREADY_EXISTS)
        return username

    @staticmethod
    def validate_avatar_file(avatar_file):
        # if not avatar_file:
        #     raise ValidationError("Không tìm thấy file ảnh.")
            
        # Kiểm tra content type
        content_type = avatar_file.content_type
        if content_type not in Constants.ALLOWED_AVATAR_TYPES:
            raise ValidationError("Chỉ chấp nhận ảnh jpg, png, gif, bmp, tiff, webp.")
            
        # Kiểm tra kích thước file
        max_size = Constants.MAX_AVATAR_SIZE_MB * 1024 * 1024
        if avatar_file.size > max_size:
            raise ValidationError("Ảnh vượt quá dung lượng cho phép (tối đa 5MB).")
            
        return avatar_file

    @staticmethod
    def validate_avatar_base64(avatar_base64):
        if not avatar_base64:
            raise ValidationError("Không tìm thấy dữ liệu ảnh.")
            
        # Kiểm tra định dạng base64
        if not avatar_base64.startswith('data:image/'):
            raise ValidationError("Định dạng base64 không hợp lệ.")
            
        # Tách content type và dữ liệu base64
        try:
            content_type, base64_data = avatar_base64.split(',', 1)
            content_type = content_type.split(':')[1].split(';')[0]
        except:
            raise ValidationError("Định dạng base64 không hợp lệ.")
            
        # Kiểm tra content type
        if content_type not in Constants.ALLOWED_AVATAR_TYPES:
            raise ValidationError("Chỉ chấp nhận ảnh jpg, png, gif, bmp, tiff, webp.")
            
        # Kiểm tra kích thước
        import base64
        try:
            image_data = base64.b64decode(base64_data)
            max_size = Constants.MAX_AVATAR_SIZE_MB * 1024 * 1024
            if len(image_data) > max_size:
                raise ValidationError("Ảnh vượt quá dung lượng cho phép (tối đa 5MB).")
        except:
            raise ValidationError("Dữ liệu base64 không hợp lệ.")
            
        return avatar_base64



