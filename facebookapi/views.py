from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout as auth_logout
# Allauth
from allauth.socialaccount import  providers
from allauth.socialaccount.models import SocialToken, SocialApp, SocialLogin
from allauth.socialaccount.providers.facebook.views import fb_complete_login
from allauth.socialaccount.helpers import complete_social_login
# Custome method
from .serializers import EverybodyCanAuthentication
import logging
from commonfriends.helper import FacebookManager


logger = logging.getLogger(__name__)


# Using Facepy fto obtain data from facebook
# curl -X GET -H 'Authorization: Token f386ccc6c18ffe7863cd705340c3f138967033f3' http://localhost:8000/api/facepy/
class FacePy (APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		user = request.user
		fb = FacebookManager(user)
		allfriends = fb.get_user_friends()
		return Response (status=status.HTTP_200_OK, data= allfriends)				


# API to allow mobile to login
# Example to request login
# curl --dump-header - -H "Content-Type: application/json" -X POST -d '{"access_token":"xxxxxxxx"}' http://localhost:8000/rest/facebook-login/
# Actual Login
# curl -H "Content-Type: application/json" -X POST -d '{"access_token":"EAAOYwyCLF9oBABpLTdOTkZAvQPsHeFRJ4LCdIkrBXAJz1ZAWljjb67NRFeGc2ZC7BVn3QZCEGTaL7wM0RCM8HNdrjZArdMzkla726svHHFMOJceQoutCRJBnXfnZAkUAPjtltq9KDsr3IWXrhBW99xg1PlqjL3ZBONvhVfjdNhZAqjtLDuvAH0ZC6KI57wR7buM8JzqSU394ZAaoijoyAogwpnFHr0H7zSWNdCSlfUS2WRovjVEBdYHjwVlunylLlO05ZB5jZCkJgsci4wZDZD"}' http://localhost:8000/api/login/facebook/
# Path /api/login/facebook
class RestFacebookLogin (APIView):
	permission_classes = (AllowAny,)
	authentication_classes = (EverybodyCanAuthentication,)

	def dispatch(self, *args, **kwargs):
		return super(RestFacebookLogin, self).dispatch(*args, **kwargs)
	def post (self,request):
		
		original_request = request._request
		data = JSONParser().parse(request)
		access_token = data.get('access_token', '')

		try:
			app = SocialApp.objects.get(provider='facebook')
			fb_auth_token = SocialToken(app=app, token=access_token)

			login = fb_complete_login(original_request, app, fb_auth_token)
			login.token = fb_auth_token
			login.state = SocialLogin.state_from_request(original_request)

			complete_social_login(original_request, login)
			token, _ = Token.objects.get_or_create(user=original_request.user)

			
			data_response ={
			'username': original_request.user.username,
			'objectId': original_request.user.pk,
			'firstName': original_request.user.first_name,
			'lastName': original_request.user.last_name,
			'email': original_request.user.email,
			'sessionToken': token.key,
			}
			return Response(status=status.HTTP_200_OK, data=data_response)
		except:
			return Response(status=status.HTTP_401_UNAUTHORIZED,data={
				'detail': 'Bad Access Token',
				})

# API to allow mobile app to logout 
# Example for the request 
# curl -X POST -H 'Authorization: Token Xyour token goes hereX' http://localhost:8000/api/logout/facebook/
#Actual Example
# curl -X POST -H 'Authorization: Token f386ccc6c18ffe7863cd705340c3f138967033f3' http://localhost:8000/api/logout/facebook/
# /api/logout/facebook/
class RestFacebookLogout (APIView):
	def dispatch(self, *args, **kwargs):
		return super(RestFacebookLogout, self).dispatch(*args, **kwargs)
	def post(self, request):
		original_request = request._request
		if original_request.user.is_authenticated():
			auth_logout(original_request)
			request.user.auth_token.delete()
		return Response (status=status.HTTP_200_OK, data= {'status': status.HTTP_200_OK })