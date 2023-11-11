"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework import routers
from . import views
router = routers.SimpleRouter()
app_name = "backend"

router.register(
    "user-register" , views.CreateUser ,basename="CreateUser"
)
router.register(
    "my-details",views.GetMydetails, basename="GetMydetails"
)
router.register(
    "CreateAuthUser",views.CreateAuthUser,basename="CreateAuthUser"
)
router.register(
    "attendance-punch",views.AttendancePunching,basename="AttendancePunching"
)
router.register(
    "user-login",views.UserSessionLogin,basename="UserSessionLogin"
)
router.register(
    "leave-details",views.LeaveDetails,basename="LeaveDetails"
)
router.register(
    "attendance-details",views.AttendanceDetails,basename="AttendanceDetails"
)
router.register(
    "event-details",views.EventDetails,basename="EventDetails"
)
router.register(
    "leave-apply",views.LeaveApply,basename="LeaveApply"
)
router.register(
    "leave-approval",views.LeaveApproval,basename="LeaveApproval"
)
router.register(
    "attendance-regularize",views.AttendanceRegularize,basename="AttendanceRegularize"
)
router.register(
    "apply/attendance-regularize",views.ApplyAttendanceRegularize,basename="ApproveAttendanceRegularize"
)
router.register(
    "list/attendance-regularize",views.ListAttendanceRegularize,basename="ListAttendanceRegularize"
)
router.register(
    "approve/attendance-regularize",views.ApproveAttendanceRegularize,basename="ApproveAttendanceRegularize"
)
router.register(
    "apply/resignation",views.ApplyResignation,basename="ApplyResignation"
)
router.register(
    "all-resignation",views.AllResignations,basename="AllResignations"
)


from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # ...
]

# urlpatterns = [
#     path('', include(router.urls)),
# ]