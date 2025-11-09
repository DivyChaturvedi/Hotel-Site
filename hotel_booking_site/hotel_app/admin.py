from django.contrib import admin
from .models import Hotel, Room, Booking

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'rating', 'price','image')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('hotel','room_type','price','quantity','image')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id','user','room','check_in','check_out','is_paid','booked_at')
    list_filter = ('is_paid',)