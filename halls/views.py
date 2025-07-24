from django.shortcuts import render, get_object_or_404, redirect
from .models import Hall, Booking, Favorite
from .forms import BookingForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
#from django.conf import settings
#import razorpay  # Temporarily commented out for migrations
from django.utils import timezone
from django.db import models

# Create your views here.

# Homepage view: list all halls as cards, with search and filter
def hall_list(request):
    halls = Hall.objects.all()
    q = request.GET.get('q', '')
    name = request.GET.get('name', '')
    location = request.GET.get('location', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_capacity = request.GET.get('min_capacity', '')
    max_capacity = request.GET.get('max_capacity', '')
    event_type = request.GET.get('event_type', '')

    if q:
        halls = halls.filter(
            models.Q(name__icontains=q) |
            models.Q(location__icontains=q) |
            models.Q(event_types__icontains=q)
        )
    if name:
        halls = halls.filter(name__icontains=name)
    if location:
        halls = halls.filter(location__icontains=location)
    if min_price:
        halls = halls.filter(price_per_hour__gte=min_price)
    if max_price:
        halls = halls.filter(price_per_hour__lte=max_price)
    if min_capacity:
        halls = halls.filter(capacity__gte=min_capacity)
    if max_capacity:
        halls = halls.filter(capacity__lte=max_capacity)
    if event_type:
        halls = halls.filter(event_types=event_type)

    # Pass favorite hall IDs for the logged-in user
    if request.user.is_authenticated:
        favorite_hall_ids = set(request.user.favorite_set.values_list('hall_id', flat=True))
    else:
        favorite_hall_ids = set()

    event_types = [
        ('birthday', '🎂', 'Birthday'),
        ('marriage', '💍', 'Marriage'),
        ('party', '🎉', 'Party'),
        ('private_movie', '🎬', 'Private Movie'),
    ]

    static_hall_images = [
        "Hall 1.jpeg", "Hall 2.jpeg", "Hall 3.jpeg", "Hall 4.jpeg", "Hall 5.jpg", "Hall 6.jpg"
    ]

    # Zip halls and images: assign static image if available, else None
    halls_list = list(halls)
    halls_with_images = []
    for i, hall in enumerate(halls_list):
        if i < len(static_hall_images):
            halls_with_images.append((hall, static_hall_images[i], None))
        elif hall.image:
            halls_with_images.append((hall, None, hall.image.url))
        else:
            halls_with_images.append((hall, None, None))

    promotion_images = ["promotion 1.jpg", "promotion 2.jpg"]
    return render(request, 'halls/hall_list.html', {
        'halls': halls,
        'filters': {
            'q': q,
            'name': name,
            'location': location,
            'min_price': min_price,
            'max_price': max_price,
            'min_capacity': min_capacity,
            'max_capacity': max_capacity,
            'event_type': event_type,
        },
        'favorite_hall_ids': favorite_hall_ids,
        'event_types': event_types,
        'promotion_images': promotion_images,
    })

# Hall detail view: show full details and booking option
@login_required(login_url='/accounts/login/')
def hall_detail(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    form = BookingForm()
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = hall.favorite_set.filter(user=request.user).exists()
    gallery_images = hall.images.all()
    return render(request, 'halls/hall_detail.html', {
        'hall': hall,
        'form': form,
        'is_favorite': is_favorite,
        'gallery_images': gallery_images,
    })

@login_required(login_url='/accounts/login/')
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-event_date', '-start_time')
    return render(request, 'halls/my_bookings.html', {'bookings': bookings})

@login_required(login_url='/accounts/login/')
def favorite_hall(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, hall=hall)
    if not created:
        # Already favorited, so unfavorite
        favorite.delete()
        favorited = False
    else:
        favorited = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'favorited': favorited})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/accounts/login/')
def unfavorite_hall(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    Favorite.objects.filter(user=request.user, hall=hall).delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'favorited': False})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/accounts/login/')
def my_favorites(request):
    favorite_halls = Hall.objects.filter(favorite__user=request.user)
    return render(request, 'halls/my_favorites.html', {'favorite_halls': favorite_halls})

@login_required(login_url='/accounts/login/')
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'Paid':
        messages.info(request, 'This booking is already paid.')
        return redirect('my_bookings')

    #client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = int(booking.hall.price_per_hour * 100)  # Razorpay expects amount in paise
    #order = client.order.create({
    #    'amount': amount,
    #    'currency': 'INR',
    #    'payment_capture': '1'
    #})
    context = {
        'booking': booking,
        #'order_id': order['id'],
        #'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount,
    }
    return render(request, 'halls/payment.html', context)

@login_required(login_url='/accounts/login/')
def book_now(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    # For demo, use current date and a default time slot
    event_date = timezone.now().date()
    start_time = timezone.now().time().replace(second=0, microsecond=0)
    end_time = (timezone.now() + timezone.timedelta(hours=1)).time().replace(second=0, microsecond=0)
    # Prevent double-booking for the same hall/date/time
    conflict = Booking.objects.filter(
        hall=hall,
        event_date=event_date,
        start_time__lt=end_time,
        end_time__gt=start_time
    ).exists()
    if conflict:
        messages.error(request, 'This hall is already booked for the selected date and time.')
        return redirect('hall_list')
    # Create a pending booking
    booking = Booking.objects.create(
        hall=hall,
        user=request.user,
        event_date=event_date,
        start_time=start_time,
        end_time=end_time,
        status='Pending'
    )
    messages.success(request, 'Booking created! Please complete your payment from My Bookings.')
    return redirect('my_bookings')

def hall_booked_dates(request, pk):
    """Return a JSON list of booked dates for a given hall (pk)."""
    bookings = Booking.objects.filter(hall_id=pk).values_list('event_date', flat=True)
    booked_dates = [date.strftime('%Y-%m-%d') for date in bookings]
    return JsonResponse({'booked_dates': booked_dates})
