from django.contrib import admin
from django.urls import path
from core import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path(
        'hospital/login/',
        views.hospital_login,
        name='hospital_login'
    ),
    
path(
    'hospital/forgot-password/',
    views.forgot_password,
    name='forgot_password'
),

    path(
    'hospital/register/',
    views.hospital_register,
    name='hospital_register'
),

    path(
        'hospital/dashboard/',
        views.hospital_dashboard,
        name='hospital_dashboard'
    ),

    path(
        'hospital/logout/',
        views.hospital_logout,
        name='hospital_logout'
    ),
    path(
    'search/',
    views.blood_search,
    name='blood_search'
),
path(
    'hospital/update-stock/',
    views.update_blood_stock,
    name='update_blood_stock'
),

path(
    'admin-dashboard/',
    views.admin_dashboard,
    name='admin_dashboard'
),

path(
    'admin-dashboard/pending-hospitals/',
    views.pending_hospitals,
    name='pending_hospitals'
),

path(
    'admin-dashboard/approve-hospital/<int:hospital_id>/',
    views.approve_hospital,
    name='approve_hospital'
),
path(
    'hospital/reset-password/<int:hospital_id>/',
    views.reset_password,
    name='reset_password'
),

path(
    'admin-dashboard/hospitals/',
    views.manage_hospitals,
    name='manage_hospitals'
),

path(
    'admin-dashboard/hospitals/<int:hospital_id>/',
    views.hospital_detail,
    name='hospital_detail'
),

path(
    'admin-dashboard/hospitals/<int:hospital_id>/toggle-status/',
    views.toggle_hospital_status,
    name='toggle_hospital_status'
),



]