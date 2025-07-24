from django.db import models
from django.contrib.auth.models import User

# Choices for event types
EVENT_TYPE_CHOICES = [
    ('birthday', 'Birthday'),
    ('marriage', 'Marriage'),
    ('party', 'Party'),
    ('private_movie', 'Private Movie'),
    ('other', 'Other'),
]

class Hall(models.Model):
    name = models.CharField(max_length=200)  # Hall name
    cover_photo = models.ImageField(upload_to='hall_images/', blank=True, null=True, verbose_name='Cover Photo')
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)  # Price per hour
    capacity = models.PositiveIntegerField()  # Seating capacity
    location = models.CharField(max_length=255)  # Hall location
    description = models.TextField()  # Hall description
    event_types = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)  # Supported event types
    created_at = models.DateTimeField(auto_now_add=True)  # Date added

    def __str__(self):
        return self.name

# Booking model for hall reservations
class Booking(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, default='Booked')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hall.name} booked by {self.user.username} on {self.event_date}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'hall')

    def __str__(self):
        return f"{self.user.username} favorited {self.hall.name}"

class HallImage(models.Model):
    hall = models.ForeignKey(Hall, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='hall_images/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.hall.name}" if self.hall else "Hall Image"
