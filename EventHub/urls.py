from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import EventViewSet, ParticipantViewSet, RegistrationViewSet, dashboard, CustomAuthToken

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="events")
router.register(r"participants", ParticipantViewSet, basename="participants")
router.register(r"registrations", RegistrationViewSet, basename="registrations")

urlpatterns = router.urls + [
    # sign up : reference to the 'POST' method of ParticipantViewSet
    path('auth/signup/', ParticipantViewSet.as_view({'post': 'create'}), name='signup'),
    # login : already existing view to automatically get a token
    path('auth/login/', CustomAuthToken.as_view(), name='login'),
    # dashboard
    path('dashboard/', dashboard, name="dashboard")
]
