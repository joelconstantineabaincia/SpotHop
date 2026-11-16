from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from apps.home.models import User

def login_user(request, user):
    request.session['user_id'] = user.id
    request.session['username'] = user.username
    request.session['dark_mode'] = user.dark_mode

def logout_user(request):
    request.session.flush()

def get_logged_in_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect(f"{reverse('login:login')}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
