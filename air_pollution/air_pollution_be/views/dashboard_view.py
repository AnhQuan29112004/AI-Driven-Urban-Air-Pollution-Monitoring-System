from air_pollution_be.service.dashboard_service import DashboardService
from constants.error_codes import ErrorCodes
from constants.success_codes import SuccessCodes
from libs.response_handle import AppResponse
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny,IsAuthenticated, IsAdminUser

@permission_classes([AllowAny])
@api_view(["GET"])
def get_latest(request):
    data = DashboardService.get_latest_data()
    return AppResponse.success(SuccessCodes.DEFAULT, data=data)

@permission_classes([AllowAny])
@api_view(["GET"])
def get_history(request):
    data = DashboardService.get_history_24h()
    return AppResponse.success(SuccessCodes.DEFAULT, data=data)