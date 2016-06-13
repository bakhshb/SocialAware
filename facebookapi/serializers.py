from rest_framework.authentication import SessionAuthentication


class EverybodyCanAuthentication(SessionAuthentication):
    def authenticate(self, request):
        return None