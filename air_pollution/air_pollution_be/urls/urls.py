from django.urls import path
from air_pollution_be.views.auth_view import *
from air_pollution_be.views.user_view import *
from air_pollution_be.views.dashboard_view import *


urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/',logout,name="logout"),
    path('refresh/', refresh_token,name="refresh_token"),
    path('infor/', current_user_infor,name="user_infor"),
    path('all/', list_user, name="list_user"),
    path('auth/google/', google_auth, name='google-auth'),
    path("update/", update_profile),
    path("upload-avatar/", upload_avatar),
    path("all/", list_user),
    path("users/", get_all_user),
    path("register/user/", register_user),
    path("update/user/<int:id>/", update_user_profile),
    path("delete/user/<int:id>/", delete_user),
    path('upload-image/', upload_image),
    path('change-password/', change_password),
    path('dashboard/latest/', get_latest),
    path('dashboard/history/', get_history)
]
