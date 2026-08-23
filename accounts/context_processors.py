from .models import UserProfile

def user_profile_context(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            profile = UserProfile.objects.get(id=user_id)
            return {'current_user': profile}
        except UserProfile.DoesNotExist:
            pass
    return {'current_user': None}
