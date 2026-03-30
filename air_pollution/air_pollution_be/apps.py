from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'air_pollution_be'

    def ready(self):
        import air_pollution_be.signal
        import os
        from air_pollution_be.service.mqtt_service import MQTTServiceClass

        # CHÚ THÍCH & GIẢI THÍCH (Dành cho ASGI/Uvicorn):
        # Vì bạn chạy môi trường thông qua ASGI Uvicorn (hoặc gunicorn),
        # những application server này không sử dụng biến môi trường 'RUN_MAIN' giống Django Dev Server.
        # Ở môi trường Uvicorn, quá trình khởi tạo ứng dụng thường nằm mượt mà trên worker process
        # và đã được an toàn thông qua Thread Lock ở bên trong MQTTServiceClass.
        #
        # QUAN TRỌNG:
        # Celery worker/beat cũng load Django app => nếu bật listener ở đây cho mọi process
        # thì sẽ tạo nhiều MQTT client trùng client_id và bị "session taken over".
        # Chỉ bật listener khi container/process có chủ đích (ví dụ: service backend).
        if os.getenv("START_MQTT_LISTENER", "0") == "1":
            MQTTServiceClass.start_listening()