import csv
from django.core.management.base import BaseCommand
from hotel_app.models import Hotel, Room

class Command(BaseCommand):
    help = "Import rooms from CSV file safely"

    def handle(self, *args, **options):
        try:
            with open("rooms.csv", newline='', encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.stdout.write(f"Room CSV headers: {reader.fieldnames}")

                for row in reader:
                    hotel_name = row['hotel_name'].strip()
                    room_type = row['room_type'].strip()

                    # Find the hotel
                    try:
                        hotel = Hotel.objects.get(name=hotel_name)
                    except Hotel.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"❌ Hotel not found: {hotel_name}"))
                        continue

                    # Update existing room or create new
                    room, created = Room.objects.update_or_create(
                        hotel=hotel,
                        room_type=room_type,
                        defaults={
                            'price': row['price'],
                            'quantity': row['quantity'],
                            'description': row['description'],
                            'image': row['image_name'],  # make sure Room model has ImageField or CharField
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"✅ Room added: {hotel_name} - {room_type}"))
                    else:
                        self.stdout.write(self.style.NOTICE(f"↻ Room updated: {hotel_name} - {room_type}"))

            self.stdout.write(self.style.SUCCESS("🎉 All rooms imported successfully!"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("rooms.csv not found!"))
