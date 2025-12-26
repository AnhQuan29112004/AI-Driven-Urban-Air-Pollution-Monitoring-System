import json
import asyncio
from django.http import StreamingHttpResponse
from django.views.decorators.http import require_GET
from redis.asyncio import Redis

# from libs.Redis import RedisUtils

# async def async_event_stream(session_id: str):
#     # Kết nối Redis async
#     exists, ttl = RedisUtils.check_session(session_id)
#     if not exists and ttl == 0:
#         print("check data before: ", f'{exists} {ttl}')
#         yield f"data: {json.dumps({'exist': exists, 'ttl': ttl})}\n\n"
#         return 
#     redis = await Redis.from_url("redis://redis_hotel:6379/1")
#     pubsub = redis.pubsub()
#     await pubsub.subscribe("session_status_channel")

#     last_heartbeat = asyncio.get_event_loop().time()

#     while True:
#         # Lấy message từ Redis async
#         message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

#         if message is not None:
#             data = json.loads(message["data"])
#             if str(data.get("session_id")) == str(session_id):
#                 yield f"data: {json.dumps(data)}\n\n"

#                 last_heartbeat = asyncio.get_event_loop().time()

#         # Heartbeat 10s
#         if asyncio.get_event_loop().time() - last_heartbeat > 10:
            
#             last_heartbeat = asyncio.get_event_loop().time()

#         await asyncio.sleep(0.1)  # tránh busy loop

# @require_GET
# def sse_view(request, session_id):
#     """
#     Lưu ý: Django ASGI sẽ tự convert generator async thành StreamingHttpResponse
#     """
#     response = StreamingHttpResponse(
#         async_event_stream(session_id),
#         content_type="text/event-stream"
#     )
#     response["Cache-Control"] = "no-cache, no-transform"
#     response["X-Accel-Buffering"] = "no"
#     response["Connection"] = "keep-alive"
#     return response
