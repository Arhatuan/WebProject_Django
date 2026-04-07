from rest_framework.viewsets import ModelViewSet
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action, api_view
from django.db import IntegrityError
from django.db.models import Count, F
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, time
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware

from .models import Event, Participant, Registration
from .serializers import EventSerializer, ParticipantSerializer, RegistrationSerializer, EventWithParticipantsSerializer
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdminOrCreateOnly, IsOwnerOrAdminOrCreateOnlyForRegistration

# Create your views here.
class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    http_method_names = ['get', 'post', 'put', 'delete'] # removes 'PATCH'
    permission_classes = [IsAdminOrReadOnly]
    authentication_classes = [TokenAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"] # filtering by ?status=...
            # We don't filter by date here, but we do it manually, to not have to compare by time

    # Return queryset with automatically computed 'registered_count' and 'available_slots' (only on read operations)
    def get_queryset(self):
        queryset = Event.objects.all()

        # Filter on date (and not hours)
        date = self.request.query_params.get("date")
        if date:
            queryset = queryset.filter(date__date=date)
        
        if self.action in ["list", "retrieve"]:
            queryset = queryset.annotate(
                registered_count = Count('registrations')
            ).annotate(
                available_slots = F('max_participants') - F('registered_count')
            )
            if self.action == "retrieve":
                queryset = queryset.prefetch_related("participants")
        return queryset
    
    # Only the 'retrieve' method (and not 'list') gets the event's participants
    def get_serializer_class(self):
        if self.action == "retrieve":
            return EventWithParticipantsSerializer
        return EventSerializer
    
    def list(self, request, *args, **kwargs):
        test = super().list(request, *args, **kwargs)
        print("test", test.data)
        return test

    # Show a message when destroying (by default, there is no message)
    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        event.delete()
        return Response({"message": f"The event '{event.title}' was deleted."},
                        status=status.HTTP_200_OK)



class ParticipantViewSet(ModelViewSet):
    serializer_class = ParticipantSerializer
    permission_classes = [IsOwnerOrAdminOrCreateOnly]
    authentication_classes = [TokenAuthentication]

    # A participant can only see its own informations
    # Admins can see everyone's informations
    def get_queryset(self):
        user = self.request.user
        queryset = Participant.objects.filter(is_active=True) # only if the user is still active
        if user.is_staff:
            return queryset
        return queryset.filter(username=user.username)
    
    # Deactivate the user
    def destroy(self, request, *args, **kwargs):
        self.request.user.is_active = False
        self.request.user.save()
        return Response({"message": f"User '{self.request.user.username}' deactivated."}, 
                        status=status.HTTP_200_OK)

    # Create the URL 'api/participants/{user_id}/events/
    #   that gives the events which the user participes in
    @action(detail=True, methods=['get'], url_path='events')
    def events(self, request, pk=None):
        user = self.get_object()
        events = Event.objects.filter(participants=user)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)



class RegistrationViewSet(ModelViewSet):
    serializer_class = RegistrationSerializer
    http_method_names = ['get', 'post', 'delete'] # removes 'POST' and 'PATCH'
    permission_classes = [IsOwnerOrAdminOrCreateOnlyForRegistration]
    authentication_classes = [TokenAuthentication]

    # A participant can only see its own informations
    # Admins can see everyone's informations
    def get_queryset(self):
        user = self.request.user
        queryset = Registration.objects.filter(user_id__is_active=True) # only if the user is still active
        if user.is_staff:
            return queryset
        return queryset.filter(user_id__username=user.username)
    
    # Catch the error when trying to create a row with the 2 foreign keys already existing
    def perform_create(self, serializer):
        try:
            serializer.save(user_id=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError("Already registered.")
        
    # Show a message when destroying (by default, there is no message)
    def destroy(self, request, *args, **kwargs):
        registration = self.get_object()
        registration.delete()

        return Response(
            {"message": f"Registration by user '{registration.user_id}' for the event '{registration.event_id}' has been deleted."},
            status=status.HTTP_200_OK
        )




@api_view(["GET"])
def dashboard(request):
    nb_events = Event.objects.count()
    nb_participants = Participant.objects.count()
    nb_registrations = Registration.objects.count()

    upcoming_events = Event.objects.filter(status="upcoming").count()
    completed_events = Event.objects.filter(status="completed").count()
    cancelled_events = Event.objects.filter(status="cancelled").count()

    data = {
        "nb_events": nb_events,
        "nb_participants": nb_participants,
        "nb_registrations": nb_registrations,
        "upcoming_events": upcoming_events,
        "completed_events": completed_events,
        "cancelled_events": cancelled_events,
    }

    return Response(data, status=status.HTTP_200_OK)