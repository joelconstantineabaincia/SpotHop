from apps.home.models import User

def auth_user_processor(request):
    user_id = request.session.get('user_id')
    current_user = None
    if user_id:
        try:
            current_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            current_user = None
    
    is_authenticated = current_user is not None
    dark_mode = current_user.dark_mode if current_user else request.session.get('dark_mode', False)
    return {
        'current_user': current_user,
        'is_authenticated': is_authenticated,
        'dark_mode': dark_mode,
    }
