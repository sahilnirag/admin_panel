from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        dt = {"email": kwargs.get("email", kwargs.get("username"))}

        try:
            user = User.objects.get(**dt)
        except User.DoesNotExist:
            return None
        if user.check_password(kwargs.get("password")):
            return user
        return None
