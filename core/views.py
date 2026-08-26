from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Hospital, BloodStock
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum


# =========================
# HOME PAGE
# =========================

def home(request):
    return render(request, 'core/home.html')
    # =========================
# HOSPITAL REGISTRATION
# =========================

def hospital_register(request):

    if request.method == 'POST':

        hospital_name = request.POST.get('hospital_name')
        hospital_id = request.POST.get('hospital_id')
        contact_number = request.POST.get('contact_number')

        state = request.POST.get('state')
        district = request.POST.get('district')
        city = request.POST.get('city')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Password check
        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

            return render(
                request,
                'core/hospital_register.html'
            )

        # Hospital ID already exists
        if User.objects.filter(username=hospital_id).exists():

            messages.error(
                request,
                'Hospital ID already exists.'
            )

            return render(
                request,
                'core/hospital_register.html'
            )

        # Create User
        user = User.objects.create_user(
            username=hospital_id,
            password=password
        )

        # Create Hospital
        Hospital.objects.create(
            user=user,
            name=hospital_name,
            hospital_id=hospital_id,
            contact_number=contact_number,
            state=state,
            district=district,
            city=city,
            address=address,
            latitude=latitude or None,
            longitude=longitude or None,
            is_verified=False,
            is_active=False
        )

        messages.success(
            request,
            'Registration submitted successfully. '
            'Your account will be activated after admin verification.'
        )

        return redirect('hospital_login')

    return render(
        request,
        'core/hospital_register.html'
    )


# =========================
# HOSPITAL LOGIN
# =========================

def hospital_login(request):

    if request.method == 'POST':

        hospital_id = request.POST.get('hospital_id')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=hospital_id,
            password=password
        )

        if user is not None:

            if hasattr(user, 'hospital'):

                hospital = user.hospital

                if hospital.is_verified and hospital.is_active:

                    login(request, user)

                    return redirect('hospital_dashboard')

                messages.error(
                    request,
                    'Hospital account is not verified or active.'
                )

            else:

                messages.error(
                    request,
                    'Hospital account is not properly configured.'
                )

        else:

            messages.error(
                request,
                'Invalid Hospital ID or Password.'
            )

    return render(
        request,
        'core/hospital_login.html'
    )


# =========================
# HOSPITAL DASHBOARD
# =========================


@login_required
def hospital_dashboard(request):

    if not hasattr(request.user, 'hospital'):

        messages.error(
            request,
            'Hospital account is not properly configured.'
        )

        return redirect('hospital_login')

    hospital = request.user.hospital

    blood_stocks = BloodStock.objects.filter(
        hospital=hospital
    )

    # =========================
    # DASHBOARD STATISTICS
    # =========================

    total_units = sum(
        stock.available_units
        for stock in blood_stocks
    )

    available_groups = blood_stocks.filter(
        available_units__gt=0
    ).count()

    low_stock_groups = blood_stocks.filter(
        available_units__gt=0,
        available_units__lte=5
    ).count()

    out_of_stock_groups = blood_stocks.filter(
        available_units=0
    ).count()

    return render(
        request,
        'core/hospital_dashboard.html',
        {
            'hospital': hospital,
            'blood_stocks': blood_stocks,

            'total_units': total_units,
            'available_groups': available_groups,
            'low_stock_groups': low_stock_groups,
            'out_of_stock_groups': out_of_stock_groups,
        }
    )


# =========================
# HOSPITAL LOGOUT
# =========================

@login_required
def hospital_logout(request):

    logout(request)

    return redirect('hospital_login')


# =========================
# BLOOD SEARCH
# =========================

def blood_search(request):

    hospitals = []

    blood_group = request.GET.get('blood_group')
    state = request.GET.get('state')
    district = request.GET.get('district')
    city = request.GET.get('city')

    if blood_group and state and district and city:

        hospitals = BloodStock.objects.filter(
            blood_group=blood_group,
            available_units__gt=0,
            hospital__state__iexact=state,
            hospital__district__iexact=district,
            hospital__city__iexact=city,
            hospital__is_verified=True,
            hospital__is_active=True
        ).select_related('hospital')

    return render(
        request,
        'core/blood_search.html',
        {
            'hospitals': hospitals,
            'selected_blood': blood_group,
            'selected_state': state,
            'selected_district': district,
            'selected_city': city,
        }
    )


@login_required
def update_blood_stock(request):

    if not hasattr(request.user, 'hospital'):
        messages.error(
            request,
            'Hospital account is not properly configured.'
        )
        return redirect('hospital_login')

    hospital = request.user.hospital

    if request.method == 'POST':

        blood_group = request.POST.get('blood_group')
        available_units = request.POST.get('available_units')

        if blood_group and available_units:

            try:
                available_units = int(available_units)

                if available_units < 0:
                    raise ValueError

                stock, created = BloodStock.objects.get_or_create(
                    hospital=hospital,
                    blood_group=blood_group
                )

                stock.available_units = available_units
                stock.save()

                messages.success(
                    request,
                    f'{blood_group} stock updated successfully.'
                )

            except ValueError:

                messages.error(
                    request,
                    'Please enter a valid number of units.'
                )

    return redirect('hospital_dashboard')

# =========================
# ADMIN DASHBOARD
# =========================

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum


@staff_member_required
def admin_dashboard(request):

    total_hospitals = Hospital.objects.count()

    pending_hospitals = Hospital.objects.filter(
        is_verified=False
    ).count()

    verified_hospitals = Hospital.objects.filter(
        is_verified=True
    ).count()

    active_hospitals = Hospital.objects.filter(
        is_active=True
    ).count()

    total_blood_units = (
        BloodStock.objects.aggregate(
            total=Sum('available_units')
        )['total'] or 0
    )

    out_of_stock = BloodStock.objects.filter(
        available_units=0
    ).count()

    low_stock = BloodStock.objects.filter(
        available_units__gt=0,
        available_units__lte=2
    ).count()

    return render(
        request,
        'core/admin_dashboard.html',
        {
            'total_hospitals': total_hospitals,
            'pending_hospitals': pending_hospitals,
            'verified_hospitals': verified_hospitals,
            'active_hospitals': active_hospitals,
            'total_blood_units': total_blood_units,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
        }
    )

# =========================
# PENDING HOSPITALS
# =========================

@staff_member_required
def pending_hospitals(request):

    hospitals = Hospital.objects.filter(
        is_verified=False
    ).order_by('-created_at')

    return render(
        request,
        'core/pending_hospitals.html',
        {
            'hospitals': hospitals,
        }
    )


# =========================
# APPROVE HOSPITAL
# =========================

@staff_member_required
def approve_hospital(request, hospital_id):

    if request.method == 'POST':

        try:
            hospital = Hospital.objects.get(
                id=hospital_id
            )

            hospital.is_verified = True
            hospital.is_active = True
            hospital.save()

            messages.success(
                request,
                f'{hospital.name} has been approved successfully.'
            )

        except Hospital.DoesNotExist:

            messages.error(
                request,
                'Hospital not found.'
            )

    return redirect('pending_hospitals')
    
# =========================
# HOSPITAL FORGOT PASSWORD
# =========================

def forgot_password(request):

    if request.method == 'POST':

        hospital_id = request.POST.get('hospital_id')
        contact_number = request.POST.get('contact_number')

        try:

            hospital = Hospital.objects.get(
                hospital_id=hospital_id,
                contact_number=contact_number
            )

            return redirect(
                'reset_password',
                hospital_id=hospital.id
                
            )

        except Hospital.DoesNotExist:

            messages.error(
                request,
                'Hospital ID or registered mobile number is incorrect.'
            )

    return render(
        request,
        'core/forgot_password.html'
    )
    
# =========================
# RESET HOSPITAL PASSWORD
# =========================

def reset_password(request, hospital_id):

    try:

        hospital = Hospital.objects.get(
            id=hospital_id
        )

    except Hospital.DoesNotExist:

        messages.error(
            request,
            'Hospital not found.'
        )

        return redirect('forgot_password')


    if request.method == 'POST':

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')


        # Password match check

        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

            return render(
                request,
                'core/reset_password.html',
                {
                    'hospital': hospital
                }
            )


        # Password length check

        if len(password) < 6:

            messages.error(
                request,
                'Password must be at least 6 characters long.'
            )

            return render(
                request,
                'core/reset_password.html',
                {
                    'hospital': hospital
                }
            )


        # Change Django User password

        hospital.user.set_password(password)

        hospital.user.save()


        messages.success(
            request,
            'Password changed successfully. You can now login with your new password.'
        )

        return redirect('hospital_login')


    return render(
        request,
        'core/reset_password.html',
        {
            'hospital': hospital
        }
    )
    
# =========================
# MANAGE HOSPITALS
# =========================

@staff_member_required
def manage_hospitals(request):

    hospitals = Hospital.objects.all().order_by('-created_at')

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()

    # Search
    if search:

        hospitals = hospitals.filter(
            name__icontains=search
        ) | hospitals.filter(
            hospital_id__icontains=search
        ) | hospitals.filter(
            city__icontains=search
        )


    # Status filter

    if status == 'pending':

        hospitals = hospitals.filter(
            is_verified=False
        )

    elif status == 'verified':

        hospitals = hospitals.filter(
            is_verified=True
        )

    elif status == 'active':

        hospitals = hospitals.filter(
            is_active=True
        )

    elif status == 'inactive':

        hospitals = hospitals.filter(
            is_active=False
        )


    return render(
        request,
        'core/manage_hospitals.html',
        {
            'hospitals': hospitals,
            'search': search,
            'status': status,
        }
    )


# =========================
# HOSPITAL DETAILS
# =========================

@staff_member_required
def hospital_detail(request, hospital_id):

    try:

        hospital = Hospital.objects.get(
            id=hospital_id
        )

    except Hospital.DoesNotExist:

        messages.error(
            request,
            'Hospital not found.'
        )

        return redirect('manage_hospitals')


    blood_stocks = BloodStock.objects.filter(
        hospital=hospital
    ).order_by('blood_group')


    return render(
        request,
        'core/hospital_detail.html',
        {
            'hospital': hospital,
            'blood_stocks': blood_stocks,
        }
    )


# =========================
# ACTIVATE / DEACTIVATE
# =========================

@staff_member_required
def toggle_hospital_status(request, hospital_id):

    if request.method != 'POST':

        return redirect('manage_hospitals')


    try:

        hospital = Hospital.objects.get(
            id=hospital_id
        )

    except Hospital.DoesNotExist:

        messages.error(
            request,
            'Hospital not found.'
        )

        return redirect('manage_hospitals')


    # Only verified hospitals can be activated

    if not hospital.is_verified:

        messages.error(
            request,
            'Hospital must be verified before activation.'
        )

        return redirect('manage_hospitals')


    hospital.is_active = not hospital.is_active

    hospital.save()


    if hospital.is_active:

        messages.success(
            request,
            f'{hospital.name} has been activated.'
        )

    else:

        messages.success(
            request,
            f'{hospital.name} has been deactivated.'
        )


    return redirect('manage_hospitals')



