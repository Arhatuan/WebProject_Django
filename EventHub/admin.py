from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Event, Participant, Registration

# customize how the admin panel sees the 'Users' table (with the additionnal fields)
class CustomUser(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'phone', 'is_staff', 'is_active', 'created_at', 'updated_at')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('phone',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('phone',)}),
    )

# Register your models here.
admin.site.register(Event)
admin.site.register(Participant, CustomUser) # the 'Participant' table serves in place of the 'Users' table
admin.site.register(Registration)
