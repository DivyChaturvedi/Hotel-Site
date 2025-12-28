from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse
from django.conf import settings
import os



from .models import Hotel, Room, Booking

def home(request):
    q = request.GET.get('q')
    hotels = Hotel.objects.all()
    if q:
        hotels = hotels.filter(Q(name__icontains=q) | Q(city__icontains=q))
    return render(request, 'hotel_app/home.html', {
        'hotels': hotels,
        'MEDIA_URL': settings.MEDIA_URL
    })


def faq(request):
    return render(request,'hotel_app/faq.html')

def terms(request):
    return render(request,'hotel_app/terms.html')

def privacy(request):
    return render(request,'hotel_app/privacy.html')

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    rooms = hotel.rooms.all()
    return render(request, 'hotel_app/hotel_detail.html', {'hotel': hotel, 'rooms': rooms})



@login_required(login_url='/login/')
def book_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        guests = int(request.POST.get('guests', 1))

    
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


from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import send_mail
import random

from .models import EmailOTP

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST.get('email','')
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_active=False   
        )

    
        otp = str(random.randint(100000, 999999))

        EmailOTP.objects.create(user=user, otp=otp)
        send_mail(
    'Email Verification OTP',
    f'Your OTP for account verification is {otp}',
    settings.EMAIL_HOST_USER,
    [email],
)
        request.session['user_id'] = user.id
        messages.success(request, "OTP sent to your email")
        return redirect('verify_otp')

    return render(request, 'hotel_app/register.html')



def verify_otp(request):
    if request.method == "POST":
        otp_input = request.POST['otp']
        user_id = request.session.get('user_id')

        user = User.objects.get(id=user_id)
        otp_obj = EmailOTP.objects.get(user=user)

        if otp_obj.otp == otp_input:
            user.is_active = True
            user.save()
            otp_obj.delete()
            messages.success(request, "Email verified successfully")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'hotel_app/verify_otp.html')




# ---------------- Login ----------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request,"Logged in Successfully")
            return redirect('home')
        
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'hotel_app/login.html')

# ---------------- Logout ----------------
def logout_view(request):
    logout(request)
    return redirect('home')


# from django.core.mail import send_mail
from django.conf import settings

@login_required
def payment_simulation(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

    total_days = (booking.check_out - booking.check_in).days
    if total_days < 1:
        total_days = 1
    total_amount = booking.room.price * total_days

#     if request.method == 'POST':
#         booking.is_paid = True
#         booking.save()

#         subject = "✅ Room Booking Confirmed – Demo Payment Successful"

#         message = f"""
# Hello {booking.user.first_name or booking.user.username},

# Your room booking has been successfully confirmed.

# 🏨 Booking Details
# Booking ID: {booking.id}
# Hotel: {booking.room.hotel.name}
# Room Type: {booking.room.get_room_type_display()}
# Check-in: {booking.check_in}
# Check-out: {booking.check_out}
# Total Nights: {total_days}

# 💳 Payment Details
# Payment Status: Successful (Demo)
# Amount Paid: ₹{total_amount}
# Transaction ID: DEMO-{booking.id}

# Thank you for booking with us.
# Have a pleasant stay 😊

# Hotel Booking Team
# """

        # send_mail(
        #     subject,
        #     message,
        #     settings.EMAIL_HOST_USER,
        #     [booking.user.email],
        #     fail_silently=False,
        # )

        # messages.success(request, "Payment successful! Confirmation email sent.")
        # return redirect('my_bookings')

    return render(request, 'hotel_app/payment_simulation.html', {
        'booking': booking,
        'total_amount': total_amount
    })



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


from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings

def support(request):
    success = False

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        full_message = f"""
        Name: {name}
        Email: {email}

        Message:
        {message}
        """

        send_mail(
            subject="New Contact Message - HotelBooking",
            message=full_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],  #  EMAIL
            fail_silently=False,
        )
        send_mail(
    "We received your message",
    "Thank you for contacting Hotel Booking Support. We will get back to you shortly.",
    settings.DEFAULT_FROM_EMAIL,
    [email],
)


        success = True
        messages.success(request,"Your mail Sent Successfully")

    return render(request, "hotel_app/support.html", {"success": success})


from django.shortcuts import render

def about(request):
    return render(request, 'hotel_app/about.html')



from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        full_message = f"""
        New Contact Message from HotelBooking Website

        Name: {name}
        Email: {email}

        Message:
        {message}
        """

        send_mail(
            subject="New Contact Message - HotelBooking",
            message=full_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],  # TERA EMAIL
            fail_silently=False,
        )

        return render(request, 'hotel_app/contact.html', {'success': True})

    return render(request, 'hotel_app/contact.html')




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking



@login_required

def my_bookings(request):
    bookings = request.user.bookings.all().order_by('-booked_at')
    return render(request, 'hotel_app/my_bookings.html', {'bookings': bookings})




from django.http import JsonResponse
import pandas as pd
import os

def chatbot_response(request):
    user_message = request.GET.get('message', '').lower()

    csv_path = os.path.join('hotel_app', 'data', 'hotels.csv')

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return JsonResponse({'reply': 'Sorry, I could not access hotel data.'})


    reply = "Sorry, I didn’t understand. Try asking about available hotels."


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






# from django.http import HttpResponse
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from datetime import datetime
# from reportlab.lib.utils import ImageReader
# import qrcode
# from io import BytesIO
# from reportlab.lib.utils import ImageReader

# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont


# @login_required
# def booking_receipt(request, booking_id):
#     from .models import Booking
#     booking = get_object_or_404(Booking, id=booking_id, user=request.user)

#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="Booking_Receipt_{booking.id}.pdf"'

#     p = canvas.Canvas(response, pagesize=A4)
#     width, height = A4

#     font_path = os.path.join(settings.BASE_DIR, 'hotel_app/static/fonts/DejaVuSans.ttf')
#     pdfmetrics.registerFont(TTFont('DejaVu', font_path))



#     p.setFillColor(colors.HexColor("#1F3C88"))
#     p.rect(0, height-110, width, 110, fill=True, stroke=False)

#     logo_path = os.path.join(
#     settings.BASE_DIR,
#     "hotel_app",
#     "static",
#     "images",
#     "hotel_logo.png"
#     )

#     p.drawImage(
#     logo_path,
#     width - 110,
#     height - 95,
#     width=70,
#     height=70,
#     mask='auto'
#     )



#     p.setFillColor(colors.white)
#     p.setFont("DejaVu", 26)
#     p.drawString(50, height-60, "Hotel Booking Invoice")

#     p.setFont("DejaVu", 12)
#     p.drawString(50, height-85, "Official Payment Receipt")

#     p.setFillColor(colors.whitesmoke)
#     p.roundRect(40, height-520, width-80, 380, 12, fill=True, stroke=False)

#     p.setFillColor(colors.black)
#     p.setFont("DejaVu", 14)
#     p.drawString(60, height-160, "Booking Details")

#     p.line(60, height-170, width-60, height-170)

#     p.setFont("DejaVu", 12)

#     left_x = 70
#     right_x = 350
#     y = height - 200
#     gap = 25

#     p.drawString(left_x, y, "Booking ID:")
#     p.drawString(right_x, y, str(booking.id))

#     y -= gap
#     p.drawString(left_x, y, "Customer Name:")
#     p.drawString(right_x, y, booking.user.username)

#     y -= gap
#     p.drawString(left_x, y, "Hotel Name:")
#     p.drawString(right_x, y, booking.room.hotel.name)

#     y -= gap
#     p.drawString(left_x, y, "Room Type:")
#     p.drawString(right_x, y, booking.room.get_room_type_display())

#     y -= gap
#     p.drawString(left_x, y, "Price per Night:")
#     p.drawString(right_x, y, f"₹ {booking.room.price}")

#     y -= gap
#     p.drawString(left_x, y, "Check-in Date:")
#     p.drawString(right_x, y, booking.check_in.strftime('%d-%m-%Y'))

#     y -= gap
#     p.drawString(left_x, y, "Check-out Date:")
#     p.drawString(right_x, y, booking.check_out.strftime('%d-%m-%Y'))


#     total_days = (booking.check_out - booking.check_in).days
#     if total_days < 1:
#         total_days = 1 
#     total_amount = booking.room.price * ((booking.check_out - booking.check_in).days or 1)


#     qr_data = f"""
#     Booking ID: {booking.id}
#     Customer: {booking.user.username}
#     Hotel: {booking.room.hotel.name}
#     Amount: ₹{total_amount}
#     """


#     qr = qrcode.make(qr_data)
#     qr_buffer = BytesIO()
#     qr.save(qr_buffer)
#     qr_buffer.seek(0)

#     p.drawImage(ImageReader(qr_buffer), 50, 140, width=90, height=90)







#     y -= 40
#     p.setFont("DejaVu", 13)
#     p.drawString(left_x, y, "Total Nights:")
#     p.drawString(right_x, y, str(total_days))

#     y -= gap
#     p.drawString(left_x, y, "Total Amount:")
#     p.drawString(right_x, y, f"₹ {total_amount:.2f}")

#     # ===== Payment Status Badge =====
#     p.setFillColor(colors.green if booking.is_paid else colors.red)
#     p.roundRect(width-200, height-180, 140, 35, 10, fill=True, stroke=False)

#     p.setFillColor(colors.white)
#     p.setFont("DejaVu", 14)
#     status = "PAID" if booking.is_paid else "UNPAID"
#     p.drawCentredString(width-130, height-168, status)

#     # ===== Footer =====
#     p.setFillColor(colors.black)
#     p.setFont("DejaVu", 10)
#     p.line(40, 120, width-40, 120)

#     p.drawString(50, 95, f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
#     p.drawRightString(width-50, 95, "Authorized Signature")

#     p.setFont("Helvetica-Bold", 10)
#     p.drawRightString(width-50, 80, "Hotel Booking")

#     p.setFont("Helvetica", 10)
#     p.drawCentredString(width/2, 55, "Thank you for choosing our hotel. We wish you a pleasant stay!")

#     p.showPage()
#     p.save()





#     return response



import uuid
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone

@login_required
@require_http_methods(["GET", "POST"])
def demo_payment_view(request, booking_id):
    from .models import Booking
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        
        method = request.POST.get('pay_method', 'card')

        
        demo_txn = f"DEMO-{uuid.uuid4().hex[:10].upper()}"

     
        demo_record = {
            "booking_id": booking.id,
            "method": method,
            "txn_id": demo_txn,
            "amount": float(booking.total_price),
            "time": timezone.now().isoformat(),
        }


    
        messages.success(request, f"Payment simulated successfully. Transaction ID: {demo_txn}")


        return render(request, 'payment_success.html', {"booking": booking, "demo": demo_record})

    return render(request, 'payment.html', {"booking": booking})


from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking
from django.contrib import messages
@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    messages.success(request, "Booking deleted successfully!")
    return redirect('my_bookings')  # ye tera mybookings page ka name hoga


from django.shortcuts import render
from .models import Hotel

def search_hotels(request):
    query = request.GET.get('q', '')

    hotels = Hotel.objects.filter(
        city__icontains=query
    )

    return render(request, 'search_results.html', {
        'hotels': hotels,
        'query': query
    })





from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def edit_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.save()

        profile.phone = request.POST.get("phone")
        profile.city = request.POST.get("city")

        if request.FILES.get("image"):
            profile.image = request.FILES.get("image")

        profile.save()

        messages.success(request, "Profile updated successfully ✅")
        return redirect("my_profile")

    return render(request, "hotel_app/edit_profile.html", {
        "user": user,
        "profile": profile
    })




from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard(request):
    return render(request, 'hotel_app/dashboard.html')



from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def my_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    bookings = Booking.objects.filter(user=request.user).order_by("-id")

    return render(request, "hotel_app/my_profile.html", {
        "profile": profile,
        "bookings": bookings
    })



from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 🔥 VERY IMPORTANT
            messages.success(request, "Password changed successfully!")
            return redirect("my_profile")  # ya jahan bhejna ho
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "hotel_app/change_password.html", {"form": form})
