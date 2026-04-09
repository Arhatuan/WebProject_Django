from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F

from .models import Event, Participant, Registration
        
        
class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ["id", "username", "password", "email", 
                  "first_name", "last_name",
                  "email", "phone", "is_staff"]
        write_only_fields = ["password"] # only in HTTP requests, never in HTTP responses
        read_only_fields = ["is_staff"]

    # To automatically generate a token for the new user
    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user) # create a unique token for the user
        return user
    

# Serializer with minimum attributes necessary for viewing participants without getting personnal data
class MinimumParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ["id", "username", "email"]
    

class EventSerializer(serializers.ModelSerializer):
    registered_count = serializers.IntegerField(read_only=True)
    available_slots = serializers.IntegerField(read_only=True)
    price = serializers.DecimalField(max_digits=8, decimal_places=2, coerce_to_string=True)
    
    class Meta:
        model = Event
        fields = ["id", "title", "description",
                  "start_date", "end_date", "price", "status", "location",
                  "max_participants",
                  "registered_count", "available_slots"]
        read_only_fields = ["registered_count", "available_slots"]
    

# Event serializer with the participants to that event
class EventWithParticipantsSerializer(EventSerializer):
    participants = MinimumParticipantSerializer(many=True, read_only=True)

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ["participants"]

        
class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ["id", "event_id", "user_id", "registered_at"]
        read_only_fields = ['user_id']

    # Check if the event is already full (otherwise the user can't register to it)
    def create(self, validated_data):
        with transaction.atomic():
            event = Event.objects.select_for_update().get(
                id=validated_data['event_id'].id
            )
            
            if event.registrations.count() >= event.max_participants:
                raise serializers.ValidationError("The event is already full.")
            registration = Registration.objects.create(**validated_data)
            return registration
        
