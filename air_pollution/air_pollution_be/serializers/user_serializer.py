from django.db.models import Q
from rest_framework import serializers

from constants.constants import Constants
from validators.validator import Validator
from utils.utils import Utils
from air_pollution_be.models.user import User

# from air_pollution.constants.constants import Constants

class UserSerializer(serializers.ModelSerializer):
    total_nights = serializers.SerializerMethodField()
    username = serializers.CharField(
        required=True,
        validators=[]  # 🔥 loại bỏ UniqueValidator
    )
    class Meta:
        model = User
        exclude = ['groups', 'user_permissions','password']
        
    def get_total_nights(self,obj):
        from air_pollution_be.service.booking_service import BookingService

        total_nights = BookingService.caculate_nights_user(obj.email)
        return total_nights
        
    def create(self, validated_data):
        request = self.context.get("request")
        is_first_user = not User.objects.exists()
        print(f"Is first user: {is_first_user}")
        created_by = request.user if request and request.user.is_authenticated else None

         # Dữ liệu cơ bản
        email = validated_data.get("email")
        username = validated_data.get("username")

        # Tìm user bị soft-delete theo email hoặc username
        soft_deleted_user = User.all_objects.filter(
             Q(username=username),
            is_deleted=True
        ).first() 

        if soft_deleted_user:
        # Khôi phục user cũ & cập nhật dữ liệu mới
            for attr, value in validated_data.items():
                setattr(soft_deleted_user, attr, value)

            soft_deleted_user.restore()  # bỏ is_deleted, set delete_at = None
            soft_deleted_user.updated_at = Utils.get_current_datetime()
            created_by = request.user if request and request.user.is_authenticated else soft_deleted_user
            soft_deleted_user.created_by = created_by
            soft_deleted_user.role = 1 if is_first_user else validated_data.get('role',3)

            if is_first_user:
                soft_deleted_user.is_superuser = True
                soft_deleted_user.is_staff = True

            soft_deleted_user.save()
            return soft_deleted_user

        user = User.objects.create(
            **validated_data,
            is_superuser=is_first_user,
            is_staff=is_first_user,
        )
        created_by = request.user if request.user.is_authenticated else user
        user.created_by = created_by
        
        
        # if is_first_user:
        #     user.role = 1
        # else:
        #     user.role = 3

        user.save()
        return user

    def update(self, instance, validated_data):
        request = self.context.get("request")
        password = request.data.get('password', '')
        if request and request.user.is_authenticated and request.user.id != instance.id:
            instance.updated_by = request.user
        instance.updated_at = Utils.get_current_datetime()
        if self.context.get(Constants.REGISTER, False):
            instance.status = 1

        if password:
            instance.set_password(password)


        if "groups" in validated_data:
            groups = validated_data.pop("groups")
            instance.groups.set(groups)

        for attr, value in validated_data.items():
            if attr in ["created_at"]:   
                continue
            setattr(instance, attr, value)
        
            
        # Đảm bảo các trường is_staff, is_superuser đã đúng trước khi gán role
        #instance.refresh_from_db()
        
        if instance.is_superuser:
            instance.role = 1  # admin
        elif instance.is_staff:
            instance.role = 2  # mod
        else:
            instance.role = 3  # user
        
        instance.save()
        return instance

    def validate(self, data):
        errors = {}
        if self.instance is None:


            if self.context.get(Constants.ADMIN_REGISTER_USER, False):
                if not data.get("email"):
                    errors["email"] = "Email field is required."
                if not data.get("username"):
                    errors["username"] = "Username field is required."
             

        else:
            if self.context.get(Constants.REGISTER, False):
                if not data.get("password") :
                    errors["password"] = "Password field is required."
                # if not data.get("fullname"):
                #     errors["fullname"] = "Fullname field is required."
                # if not data.get("phone"):
                #     errors["phone"] = "Phone field is required."



        if errors:
            raise serializers.ValidationError(errors)

        return data
    def validate_username(self, value):
        # Khi đang tạo user
        if self.instance is None:
            # Tìm user trùng username nhưng bị soft-delete
            soft_deleted = User.all_objects.filter(username=value, is_deleted=True).first()

            # Nếu user bị soft-delete → cho phép → để restore trong create()
            if soft_deleted:
                return value

            # Nếu user tồn tại không soft-delete → báo lỗi
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("Username already exists.")
        
        return value
    def validate_avatar(self, value):
        # avatar không bắt buộc
        if not value:
            return None
        if isinstance(value, str):
            if value.startswith('data:image/'):  # Nếu là base64
                return Validator.validate_avatar_base64(value)
            else:  # Nếu là URL
                return Validator.validate_avatar(value)
        else:  # Nếu là file upload
            return Validator.validate_avatar_file(value)
    
    def validate_email(self, value):
        if value:
            return Validator.validate_email(value)
        return value
    
    def validate_phone(self, value):
        if value:
            return Validator.validate_phone(value)
        return value
    
    def to_representation(self, instance):
        data = super().to_representation(instance)   # data là dict
        
        return data