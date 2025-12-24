from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),  # hotel list
    path('hotel/<str:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('mybookings/', views.my_bookings, name='my_bookings'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('payment-sim/<str:booking_id>/', views.payment_simulation, name='payment_simulation'),
    path('search-hotels/', views.search_hotels, name='search_hotels'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('support/', views.support, name='support'),
    path('chatbot-response/', views.chatbot_response, name='chatbot_response'),
    path('chatbot/', views.chatbot_response, name='chatbot_response'),
    path('receipt/<int:booking_id>/', views.booking_receipt, name='booking_receipt'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('search/', views.search_hotels, name='search_hotels'),
    path('faq/', views.faq, name='faq'),
    path('terms/', views.terms, name='terms'),
    path('privacy/',views.privacy,name='privacy'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path("my-profile/", views.my_profile, name="my_profile"),
    path('change-password/', views.change_password, name='change_password'),

    path('verify-otp/', views.verify_otp, name='verify_otp'),
  
    

    
   
    
  
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)