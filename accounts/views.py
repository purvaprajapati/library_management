import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from .models import UserProfile
from members.models import Member
from .decorators import login_required_custom, unauthenticated_required

@unauthenticated_required
def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'member') # default to member

        # Validation
        if not name or not username or not email or not password:
            messages.error(request, "All required fields must be filled.")
            return render(request, 'accounts/register.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html')

        if UserProfile.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'accounts/register.html')

        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'accounts/register.html')

        # Create user profile
        hashed_pw = make_password(password)
        user = UserProfile.objects.create(
            name=name,
            username=username,
            email=email,
            phone=phone,
            password=hashed_pw,
            role=role if role in ['admin', 'member'] else 'member'
        )

        # If role is member, create Member object
        if user.role == 'member':
            membership_id = f"LIB-{timezone.now().year}-{random.randint(1000, 9999)}"
            while Member.objects.filter(membership_id=membership_id).exists():
                membership_id = f"LIB-{timezone.now().year}-{random.randint(1000, 9999)}"
            
            Member.objects.create(
                user=user,
                membership_id=membership_id,
                address=""
            )

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'accounts/register.html')


@unauthenticated_required
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'accounts/login.html')

        try:
            user = UserProfile.objects.get(username=username)
            if check_password(password, user.password):
                # Set Session
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['user_role'] = user.role
                messages.success(request, f"Welcome back, {user.name}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        except UserProfile.DoesNotExist:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required_custom
def profile_view(request):
    user = request.user_profile
    member_profile = None
    if user.is_member():
        member_profile = getattr(user, 'member_profile', None)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not name or not email:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Name and Email are required.'})
            messages.error(request, "Name and Email are required.")
            return redirect('profile')

        # Check unique email excluding current user
        if UserProfile.objects.filter(email=email).exclude(id=user.id).exists():
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Email is already used by another account.'})
            messages.error(request, "Email is already used by another account.")
            return redirect('profile')

        user.name = name
        user.email = email
        user.phone = phone
        user.save()

        if user.is_member() and member_profile:
            member_profile.address = address
            member_profile.save()

        request.session['user_name'] = user.name

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Profile updated successfully.'})

        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return render(request, 'accounts/profile.html', {
        'user_profile': user,
        'member_profile': member_profile
    })


@login_required_custom
def change_password_view(request):
    user = request.user_profile

    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not current_password or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, 'accounts/change_password.html')

        if not check_password(current_password, user.password):
            messages.error(request, "Current password is incorrect.")
            return render(request, 'accounts/change_password.html')

        if new_password != confirm_password:
            messages.error(request, "New password and confirmation do not match.")
            return render(request, 'accounts/change_password.html')

        user.password = make_password(new_password)
        user.save()

        request.session.flush()
        messages.success(request, "Password changed successfully. Please log in with your new password.")
        return redirect('login')

    return render(request, 'accounts/change_password.html')


@unauthenticated_required
def forgot_password_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not identifier or not new_password:
            messages.error(request, "Please enter your username/email and new password.")
            return render(request, 'accounts/forgot_password.html')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/forgot_password.html')

        try:
            user = UserProfile.objects.get(username=identifier)
        except UserProfile.DoesNotExist:
            try:
                user = UserProfile.objects.get(email=identifier)
            except UserProfile.DoesNotExist:
                messages.error(request, "No user found with that username or email.")
                return render(request, 'accounts/forgot_password.html')

        user.password = make_password(new_password)
        user.save()

        messages.success(request, "Password reset successfully! Please log in.")
        return redirect('login')

    return render(request, 'accounts/forgot_password.html')
