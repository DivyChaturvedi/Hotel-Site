import csv
import random

# Read hotels from hotels.csv
with open("mp_hotels.csv", newline='', encoding="utf-8") as file:
    reader = csv.DictReader(file)
    print("Detected Headers:", reader.fieldnames)
    hotels = list(reader)

# Create rooms.csv
with open("rooms.csv", "w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["hotel_name", "room_type", "price", "quantity", "description", "image_name"])

    for hotel in hotels:
        hotel_name = hotel["Name"].strip()
        base_price = int(float(hotel["Price (INR)"]))  # take price from CSV
        total_rooms = int(hotel["Rooms vailable"]) if hotel["Rooms vailable"].isdigit() else 10

        rooms_data = [
            ("single", base_price, random.randint(1, max(2, total_rooms // 3))),
            ("double", int(base_price * 1.4), random.randint(1, max(2, total_rooms // 2))),
            ("suite", int(base_price * 1.8), random.randint(1, max(2, total_rooms))),
        ]

        for room_type, price, qty in rooms_data:
            description = f"{room_type.capitalize()} room at {hotel_name} with modern amenities and comfort."
            image_name = f"{hotel_name.lower().replace(' ', '_')}_{room_type}.jpg"
            writer.writerow([hotel_name, room_type, price, qty, description, image_name])

print("✅ rooms.csv generated successfully based on hotels.csv!")
