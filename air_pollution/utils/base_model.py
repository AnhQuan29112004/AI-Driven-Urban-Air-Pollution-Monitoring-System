from django.db import models
import time
from datetime import datetime, timezone
from django.db.models.signals import class_prepared

class BaseModel(models.Model):
    created_by = models.ForeignKey(
        "air_pollution_be.User",  # 👉 thay "A" bằng tên app thật của bạn
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by"
    )
    updated_by = models.ForeignKey(
        "air_pollution_be.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by"
    )
    created_at = models.BigIntegerField(editable=False)
    updated_at = models.BigIntegerField(null=True)
    def save(self, *args, **kwargs):
        now_time = int(time.time())
        if(self.created_at is None):
           self.created_at = now_time
        self.updated_at = now_time
        super().save(*args, **kwargs) # Call the real save() method
    @property
    def created_datetime(self):
        """Convert unix -> datetime (UTC)"""
        return datetime.fromtimestamp(self.created_at, tz=timezone.utc)

    @property
    def updated_datetime(self):
        """Convert unix -> datetime (UTC)"""
        return datetime.fromtimestamp(self.updated_at, tz=timezone.utc) if self.updated_at else None

    class Meta:
        abstract = True

# 🔧 Tự động đổi related_name cho created_by & updated_by    
def update_related_names(sender, **kwargs):
    if issubclass(sender, BaseModel) and sender is not BaseModel:
        model_name = sender.__name__.lower()

        for field_name in ["created_by", "updated_by"]:
            field = sender._meta.get_field(field_name)
            field.remote_field.related_name = f"{model_name}_{field_name}"

class_prepared.connect(update_related_names)