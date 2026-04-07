from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
    
# 'Participant' extends the 'Users' table in the admin panel
class Participant(AbstractUser):
    email = models.EmailField(max_length=100, unique=True) # unique
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    # role -> 'is_staff' attribute (boolean)
    # status -> 'is_active' attribute (boolean)
    
    phone = PhoneNumberField(max_length=30, blank=True) # optional
    
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def created_at(self):
        return self.date_joined # already existing attribute

    def __str__(self):
        return f"{self.username}"
    

class Event(models.Model):
    # 'id' created automatically
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True) # optional
    date = models.DateTimeField()

    STATUSES = {
        "upcoming": "upcoming",
        "ongoing": "ongoing",
        "completed": "completed",
        "cancelled": "cancelled"
    }
    status = models.CharField(max_length=9, choices=STATUSES)
    location = models.CharField(max_length=200, blank=True) # optional
    max_participants = models.IntegerField(default=2)
    #participants_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-many relationship between Participant and Event via Registration
    participants = models.ManyToManyField(
        Participant,
        through="Registration",
        related_name="events"
    )

    def __str__(self):
        return self.title
    

    
class Registration(models.Model):
    event_id = models.ForeignKey(Event, related_name="registrations", on_delete=models.CASCADE)
    user_id = models.ForeignKey(Participant, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"'{self.event_id.title}' attended by '{self.user_id.username}'"
    
    # constraint : unique tuple [event_id, user_id] (there can't be another exact tupic)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event_id', 'user_id'],
                                    name='unique_registration')
        ]
