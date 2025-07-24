from django.urls import path
from . import views

urlpatterns = [
    path('', views.hall_list, name='hall_list'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('favorites/', views.my_favorites, name='my_favorites'),
    path('pay/<int:booking_id>/', views.payment_view, name='payment_view'),
    path('book-now/<int:pk>/', views.book_now, name='book_now'),
    path('<int:pk>/', views.hall_detail, name='hall_detail'),
    path('favorite/<int:pk>/', views.favorite_hall, name='favorite_hall'),
    path('unfavorite/<int:pk>/', views.unfavorite_hall, name='unfavorite_hall'),
    path('booked-dates/<int:pk>/', views.hall_booked_dates, name='hall_booked_dates'),
] 