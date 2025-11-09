import csv
import random
import re

# 100 hotel names from previous CSV
hotels = [
    "Hotel Sunshine","Hotel Lakeview","Hotel Mountain Mist","City Palace Inn","Hotel Blue Ocean",
    "Green Valley Resort","Hotel Royal Orchid","The River Edge","Hotel Coral Sands","Desert Pearl",
    "Hotel Snow Peak","Hotel Golden Star","Blue Lagoon Resort","The Palm Retreat","Hotel Sky Tower",
    "Hotel Silver Leaf","Hotel Maple Leaf","The Banyan Tree","Hotel Grand Plaza","Hotel Harmony",
    "Hotel Paradise","Hotel Dreamland","The Sapphire","Hotel Red Rose","Hotel Silver Star",
    "The Royal Crown","The Fern Residency","Hotel Sea Breeze","Hotel Sunrise","Hotel Pine View",
    "Hotel Bluebell","Hotel White Pearl","The Metro Grand","Hotel City Heart","Hotel Crystal Inn",
    "Hotel River View","Hotel Coral Inn","Hotel Ocean Park","The Heritage Palace","Hotel Royal Stay",
    "Hotel Hill View","Hotel Silver Nest","Hotel Bloom","The Lake Resort","Hotel Coral Tree",
    "Hotel Ganga Palace","Hotel Morning Star","Hotel Blue Lotus","Hotel Desert View","Hotel Grand River",
    "Hotel Lavender","The Maple Resort","Hotel Blueberry","Hotel Golden Leaf","Hotel Royal Heights",
    "Hotel Diamond Plaza","Hotel Ocean Pearl","Hotel Hill Palace","Hotel Blossom","Hotel Pearl View",
    "Hotel Elite","Hotel Palm View","Hotel Pine Woods","Hotel Midtown","Hotel Comfort Inn",
    "Hotel Regal Heights","Hotel Sunrise Point","Hotel Serenity","Hotel Ocean Bay","Hotel White Orchid",
    "Hotel Pearl Palace","Hotel Green Hills","Hotel Blue Horizon","Hotel Sunflower","Hotel City Bay",
    "Hotel Grand Orchid","Hotel Pine Valley","Hotel Lotus Crown","Hotel Royal Nest","Hotel Paradise Inn",
    "Hotel Coral Bay","Hotel Dream Palace","Hotel Sunrise Residency","Hotel Blue Moon","Hotel Emerald Hills",
    "Hotel White Cloud","Hotel Golden Nest","Hotel Bliss","Hotel Pine Shade","Hotel Ocean Sky",
    "Hotel Shree Palace","Hotel Golden Palm","Hotel Sapphire View","Hotel Misty Valley","Hotel Grand Vista",
    "Hotel Silver Oak","Hotel Riverstone","Hotel Blue Lagoon","Hotel Royal Bay","Hotel Lake Pearl"
]

# Room types
room_types = ["Standard","Deluxe","Suite"]

# Sample cities
cities = ["Goa","Udaipur","Manali","Jaipur","Mumbai","Munnar","Bangalore","Rishikesh","Pondicherry","Jaisalmer"]

# Helper to make filenames safe
def slugify(text):
    text = text.lower()
    text = re.sub(r'\s+','_',text)
    text = re.sub(r'[^a-z0-9_]', '', text)
    return text

# ------------------- Generate hotels.csv -------------------
with open("hotels.csv","w",newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name","city","address","description","hotel_images"])
    for hotel in hotels:
        city = random.choice(cities)
        address = f"{random.randint(1,200)} {city} Street"
        description = f"{hotel} is a beautiful hotel located in {city}."
        slug = slugify(hotel)
        num_images = random.randint(1,3)
        images = [f"{slug}_{i}.jpg" for i in range(1,num_images+1)]
        writer.writerow([hotel, city, address, description, ";".join(images)])

# ------------------- Generate rooms.csv -------------------
with open("rooms.csv","w",newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["hotel_name","room_type","price","quantity","description","image_name"])
    for hotel in hotels:
        slug_hotel = slugify(hotel)
        for rtype in room_types:
            price = random.randint(2000,6000)
            quantity = random.randint(2,5)
            description = f"{rtype} room with all modern amenities."
            num_images = random.randint(1,2)
            slug_room = slugify(rtype)
            images = [f"{slug_hotel}_{slug_room}_{i}.jpg" for i in range(1,num_images+1)]
            writer.writerow([hotel, rtype, price, quantity, description, ";".join(images)])

print("✅ hotels.csv and rooms.csv with unique image names generated successfully!")
