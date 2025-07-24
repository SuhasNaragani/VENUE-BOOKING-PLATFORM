from django.contrib import admin
from .models import Hall, Booking, Favorite, HallImage

class HallImageInline(admin.TabularInline):
    model = HallImage
    extra = 1

class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "cover_photo", "location", "price_per_hour", "capacity", "event_types", "created_at")
    search_fields = ("name", "location")
    list_filter = ("event_types", "location")
    fieldsets = (
        (None, {
            'fields': ("name", "cover_photo", "price_per_hour", "capacity", "location", "event_types", "description")
        }),
        ("Meta", {
            'fields': ("created_at",),
            'classes': ("collapse",),
        }),
    )
    readonly_fields = ("created_at",)
    inlines = [HallImageInline]

admin.site.register(Hall, HallAdmin)
admin.site.register(Booking)
admin.site.register(Favorite)
