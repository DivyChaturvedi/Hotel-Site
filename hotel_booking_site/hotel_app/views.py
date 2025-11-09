from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse

from .models import Hotel, Room, Booking

# ---------------- Home Page ----------------
def home(request):
    q = request.GET.get('q')
    hotels = Hotel.objects.all()
    if q:
        hotels = hotels.filter(Q(name__icontains=q) | Q(city__icontains=q))
    return render(request, 'hotel_app/home.html', {
        'hotels': hotels,
        'MEDIA_URL': settings.MEDIA_URL
    })

# ---------------- Hotel Detail ----------------
def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    rooms = hotel.rooms.all()
    return render(request, 'hotel_app/hotel_detail.html', {'hotel': hotel, 'rooms': rooms})


# ---------------- Book Room ----------------
@login_required(login_url='/login/')
def book_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        guests = int(request.POST.get('guests', 1))

        # parse dates safely
        try:
            d1 = datetime.strptime(check_in, "%Y-%m-%d").date()
            d2 = datetime.strptime(check_out, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid dates.")
            return redirect('hotel_detail', hotel_id=room.hotel.hotel_id)

        booking = Booking.objects.create(
            user=request.user,
            room=room,
            check_in=d1,
            check_out=d2,
            guests=guests
        )
        return redirect('payment_simulation', booking_id=booking.id)

    return render(request, 'hotel_app/book_room.html', {'room': room})

# ---------------- My Bookings ----------------

# ---------------- Register ----------------
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST.get('email','')
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username taken")
            return redirect('register')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created. Please log in.")
            return redirect('login')

    return render(request, 'hotel_app/register.html')

# ---------------- Login ----------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'hotel_app/login.html')

# ---------------- Logout ----------------
def logout_view(request):
    logout(request)
    return redirect('home')

# ---------------- Payment Simulation ----------------
@login_required
def payment_simulation(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if request.method == 'POST':
        booking.is_paid = True
        booking.save()
        messages.success(request, "Payment successful! Booking confirmed.")
        return redirect('my_bookings')
    return render(request, 'hotel_app/payment_simulation.html', {'booking': booking})

# ---------------- Search Hotels (AJAX/JSON) ----------------
def search_hotels(request):
    q = request.GET.get('q', '')
    if q:
        hotels = Hotel.objects.filter(Q(name__icontains=q) | Q(city__icontains=q))
    else:
        hotels = Hotel.objects.none()

    data = []
    for hotel in hotels:
        data.append({
            'id': hotel.id,
            'name': hotel.name,
            'city': hotel.city,
            'image': hotel.image.url if hotel.image else '/static/hotel_app/default_hotel.jpg'
        })
    return JsonResponse({'hotels': data})


def support(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        # Optionally send email or save message
        messages.success(request, "Your message has been sent successfully!")
    return render(request, 'hotel_app/support.html')


from django.shortcuts import render

def about(request):
    return render(request, 'hotel_app/about.html')

def contact(request):
    return render(request, 'hotel_app/contact.html')




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking



@login_required

def my_bookings(request):
    bookings = request.user.bookings.all().order_by('-booked_at')
    return render(request, 'hotel_app/my_bookings.html', {'bookings': bookings})








# hotel_app/views.py
from django.http import JsonResponse
import pandas as pd
import os

def chatbot_response(request):
    user_message = request.GET.get('message', '').lower()

    # Apni CSV file ka path (update kar lena)
    csv_path = os.path.join('hotel_app', 'data', 'hotels.csv')

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return JsonResponse({'reply': 'Sorry, I could not access hotel data.'})

    # Default reply
    reply = "Sorry, I didn’t understand. Try asking about available hotels."

    # Check if user is asking about hotel availability
    if 'available' in user_message or 'hotel' in user_message:
        found_hotels = []
        for hotel in df['name']:
            if hotel.lower() in user_message:
                found_hotels.append(hotel)

        if found_hotels:
            reply = f"Yes ✅ {', '.join(found_hotels)} is available!"
        else:
            reply = "Sorry ❌, that hotel is not available in our list."

    elif 'hello' in user_message or 'hi' in user_message:
        reply = "Hello 👋! How can I assist you with hotel booking?"

    elif 'price' in user_message or 'cost' in user_message:
        reply = "Our hotels start from ₹1200 per night."

    elif 'room' in user_message:
        reply = "We have deluxe, standard, and suite rooms available."

    return JsonResponse({'reply': reply})


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime

def booking_receipt(request, booking_id):
    from .models import Booking
    booking = Booking.objects.get(id=booking_id)

    # 🧾 Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Booking_Receipt_{booking.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # 🎨 Header Design
    p.setFillColor(colors.HexColor("#007ACC"))
    p.rect(0, height - 100, width, 100, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(150, height - 60, "HOTEL BOOKING RECEIPT")

    # 🏨 Hotel Info Box
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 12)
    p.roundRect(50, height - 350, 500, 230, 10, stroke=1, fill=0)

    p.drawString(70, height - 130, f"Booking ID: {booking.id}")
    p.drawString(70, height - 150, f"Customer Name: {booking.user.username}")
    p.drawString(70, height - 170, f"Hotel Name: {booking.room.hotel.name}")
    p.drawString(70, height - 190, f"Room Type: {booking.room.get_room_type_display()}")
    p.drawString(70, height - 210, f"Price per Night: Rs.{booking.room.price}")
    p.drawString(70, height - 230, f"Check-in Date: {booking.check_in.strftime('%d-%m-%Y')}")
    p.drawString(70, height - 250, f"Check-out Date: {booking.check_out.strftime('%d-%m-%Y')}")

    # 📅 Calculate total amount
    total_days = (booking.check_out - booking.check_in).days
    total_amount = float(booking.room.price) * total_days
    p.setFont("Helvetica-Bold", 12)
    p.drawString(70, height - 280, f"Total Nights: {total_days}")
    p.drawString(70, height - 300, f"Total Amount: Rs.{total_amount:.2f}")

    # 💰 Payment Status
    p.setFillColor(colors.green if booking.is_paid else colors.red)
    p.roundRect(400, height - 180, 120, 30, 8, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 12)
    status_text = "PAID" if booking.is_paid else "UNPAID"
    p.drawCentredString(460, height - 168, status_text)
    p.setFillColor(colors.black)

    # 🕓 Footer
    p.setFont("Helvetica", 10)
    p.drawString(70, 130, f"Booking Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    p.line(50, 120, 550, 120)
    p.drawString(70, 100, "Thank you for booking with us! We hope you enjoy your stay.")
    p.drawString(70, 80, "Hotel Booking System © Divy Chaturvedi | ")
    p.drawString(400, 60, "Authorized Sign: Divy")

    # ✅ Save and Return
    p.showPage()
    p.save()
    return response



import uuid
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone

@require_http_methods(["GET", "POST"])
def demo_payment_view(request, booking_id):
    # Fetch booking in your usual way (example)
    from .models import Booking
    booking = Booking.objects.get(id=booking_id)

    if request.method == 'POST':
        # Read minimal fields. DO NOT store real card/cvv in production.
        method = request.POST.get('pay_method', 'card')

        # Create a demo transaction id
        demo_txn = f"DEMO-{uuid.uuid4().hex[:10].upper()}"

        # For demo behaviour: accept anything and mark success
        # But do not persist sensitive details - log only safe fields or mark sanitised
        demo_record = {
            "booking_id": booking.id,
            "method": method,
            "txn_id": demo_txn,
            "amount": float(booking.total_price),
            "time": timezone.now().isoformat(),
        }

        # If you want to keep a local demo audit, store only non-sensitive info.
        # Example: save demo transaction to a DemoPayment model (if you create one).
        # Otherwise just show success.

        # Flash message (optional)
        messages.success(request, f"Payment simulated successfully. Transaction ID: {demo_txn}")

        # Optionally mark booking as paid in demo mode (only if you want)
        # booking.is_demo_paid = True
        # booking.save()

        # Redirect to success page
        return render(request, 'payment_success.html', {"booking": booking, "demo": demo_record})

    # GET
    return render(request, 'payment.html', {"booking": booking})



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking
from django.contrib import messages
@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    messages.success(request, "Booking deleted successfully!")
    return redirect('my_bookings')  # ye tera mybookings page ka name hoga
