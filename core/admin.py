
from django.contrib import admin
from .models import Hospital, BloodStock


# =========================
# HOSPITAL ADMIN
# =========================

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'hospital_id',
        'city',
        'district',
        'state',
        'is_verified',
        'is_active',
    )

    list_filter = (
        'state',
        'district',
        'is_verified',
        'is_active',
    )

    search_fields = (
        'name',
        'hospital_id',
        'city',
        'district',
        'contact_number',
    )

    list_editable = (
        'is_verified',
        'is_active',
    )

    ordering = (
        '-is_verified',
        'name',
    )


# =========================
# BLOOD STOCK ADMIN
# =========================

@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):

    list_display = (
        'hospital',
        'blood_group',
        'available_units',
        'last_updated',
    )

    list_filter = (
        'blood_group',
        'hospital',
    )

    search_fields = (
        'hospital__name',
        'hospital__hospital_id',
        'hospital__city',
    )

    ordering = (
        'hospital',
        'blood_group',
    )