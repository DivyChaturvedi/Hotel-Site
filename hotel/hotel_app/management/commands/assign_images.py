import os
from django.core.management.base import BaseCommand
from hotel_app.models import Hotel, Room

class Command(BaseCommand):
    help = 'Assign downloaded images to Hotels and Rooms'

    def handle(self, *args, **kwargs):
        # Folders
        hotel_img_folder = "media/hotels"
        room_img_folder = "media/rooms"

        # ---------- Hotels ----------
        for hotel in Hotel.objects.all():
            slug_hotel = hotel.name.lower().replace(" ", "_")
            img_path = os.path.join(hotel_img_folder, f"{slug_hotel}_1.jpg")
            if os.path.exists(img_path):
                hotel.image.name = f"hotels/{slug_hotel}_1.jpg"  # ImageField path
                hotel.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Assigned image to Hotel: {Hotel.Name}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠ Image not found for Hotel: {hotel.name}"))

        # ---------- Rooms ----------
        for room in Room.objects.all():
            slug_hotel = room.hotel.name.lower().replace(" ", "_")
            slug_room = room.room_type.lower().replace(" ", "_")
            img_path = os.path.join(room_img_folder, f"{slug_hotel}_{slug_room}_1.jpg")
            if os.path.exists(img_path):
                room.image.name = f"rooms/{slug_hotel}_{slug_room}_1.jpg"  # ImageField path
                room.save()
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Assigned image to Room: {room.hotel.name} - {room.room_type}"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"⚠ Image not found for Room: {room.hotel.name} - {room.room_type}"
                ))

        self.stdout.write(self.style.SUCCESS("🎉 All available images assigned!"))
