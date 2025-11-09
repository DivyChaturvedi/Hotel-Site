# import_rooms.py
import os
import django
import csv

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_booking_site.settings")
django.setup()

from hotel_app.models import Hotel, Room

CSV_FILE = "rooms.csv"  # tumhara CSV file path

with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        hotel_name = row['hotel_name'].strip()
        try:
            hotel = Hotel.objects.get(name=hotel_name)
        except Hotel.DoesNotExist:
            print(f"Hotel {hotel_name} does not exist. Skipping row.")
            continue
        except Hotel.MultipleObjectsReturned:
            print(f"Multiple hotels found with name {hotel_name}. Using first one.")
            hotel = Hotel.objects.filter(name=hotel_name).first()

        room_type = row['room_type'].strip()
        price = float(row['price'])
        quantity = int(row['quantity'])
        description = row['description'].strip()
        image_name = row['image_name'].strip()

        # Create Room object
        room, created = Room.objects.get_or_create(
            hotel=hotel,
            room_type=room_type,
            defaults={
                'price': price,
                'quantity': quantity,
                'description': description,
                'image': f"rooms/{image_name}" if image_name else None
            }
        )
        if not created:
            # Update existing room if already exists
            room.price = price
            room.quantity = quantity
            room.description = description
            room.image = f"rooms/{image_name}" if image_name else None
            room.save()

        print(f"Imported room: {hotel_name} - {room_type}")

print("Rooms import complete!")
