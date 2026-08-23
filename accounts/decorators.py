from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile

def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.warning(request, "Please log in to access this page.")
            return redirect('login')
        try:
            request.user_profile = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            request.session.flush()
            messages.error(request, "Session expired or invalid user. Please log in again.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.warning(request, "Please log in to access this page.")
            return redirect('login')
        try:
            user_profile = UserProfile.objects.get(id=user_id)
            if not user_profile.is_admin():
                messages.error(request, "Access denied. Admin/Librarian permissions required.")
                return redirect('dashboard')
            request.user_profile = user_profile
        except UserProfile.DoesNotExist:
            request.session.flush()
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def member_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.warning(request, "Please log in to access this page.")
            return redirect('login')
        try:
            user_profile = UserProfile.objects.get(id=user_id)
            if not user_profile.is_member():
                messages.error(request, "Access denied. Member permissions required.")
                return redirect('dashboard')
            request.user_profile = user_profile
        except UserProfile.DoesNotExist:
            request.session.flush()
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def unauthenticated_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_id'):
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
