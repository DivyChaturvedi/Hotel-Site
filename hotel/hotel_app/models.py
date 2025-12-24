from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Hotel(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.TextField()
    rating = models.FloatField(null=True, blank=True)
    price = models.CharField(max_length=50, null=True, blank=True)
    rooms_available = models.IntegerField(default=0)
    amenities = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='hotels/',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ ye line add kar

    def __str__(self):
        return f"{self.name} ({self.city})"

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    ROOM_TYPE = (
        ('single','Single'),
        ('double','Double'),
        ('suite','Suite'),
    )
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type} - ₹{self.price}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    booked_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking {self.id} by {self.user.username} - {self.room}"

    @property
    def nights(self):
        return (self.check_out - self.check_in).days or 1

    @property
    def total_price(self):
        return self.nights * self.room.price
    



class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='hotel_images/')


    def __str__(self):
        return self.hotel.name
    


# models.py
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return self.user.username





from django.db import models
from django.contrib.auth.models import User

class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)




