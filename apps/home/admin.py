from django.contrib import admin
from .models import User, StudySpot, SpotAmenity, Review, CheckIn, SavedSpot

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'full_name', 'dark_mode', 'created_at')
    search_fields = ('username', 'email', 'full_name')

@admin.register(StudySpot)
class StudySpotAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price_tier', 'opening_time', 'closing_time')
    list_filter = ('category', 'price_tier')
    search_fields = ('name', 'address')

@admin.register(SpotAmenity)
class SpotAmenityAdmin(admin.ModelAdmin):
    list_display = ('spot', 'avg_wifi_speed_mbps', 'outlet_density', 'predominant_noise', 'last_recalculated_at')
    list_filter = ('outlet_density', 'predominant_noise')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'spot', 'user', 'overall_rating', 'noise_level', 'outlet_rating', 'download_speed_mbps')
    list_filter = ('overall_rating', 'noise_level')

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'spot', 'checked_in_at', 'is_active')
    list_filter = ('is_active',)

@admin.register(SavedSpot)
class SavedSpotAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'spot', 'saved_at')
