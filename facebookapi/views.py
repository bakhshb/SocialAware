from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
import logging
#facebook sdk
import facebook
import requests
#facepy 
from facepy import GraphAPI
#urllib
import urllib
import json
from allauth.socialaccount.models import SocialToken, SocialApp


logger = logging.getLogger(__name__)

class FacebookSDK (APIView):

	def get(self, request, format=None):
		if request.user.is_authenticated():
			user = request.user
			social_access_token = SocialToken.objects.get(account__user=user, account__provider='facebook')
			if social_access_token != None:
				graph = facebook.GraphAPI(access_token= social_access_token, version='2.2')
				post = graph.get_object(id='me', connection_name='pokes')
				friends = graph.get_connections(id='me', connection_name='invitable_friends')
				general = graph.get_connections(id='me', connection_name='friends')
				return Response (general)
		return Response (status=status.HTTP_401_UNAUTHORIZED)



class FacePy (APIView):
	def get(self, request, format=None):
		
		if request.user.is_authenticated():
			user = request.user
			social_access_token = SocialToken.objects.get(account__user=user, account__provider='facebook')
			if social_access_token != None:
				graph = GraphAPI(social_access_token)
				# Get my latest posts
				post= graph.get('me/invitable_friends')
				return Response (post)
		return Response (status=status.HTTP_401_UNAUTHORIZED)

class URLLib (APIView):


	def get(self, request, format=None):
		#get access token 
		client_id = SocialApp.objects.values_list('client_id').get(name='commonfriends')
		client_secret = SocialApp.objects.values_list('secret').get(name='commonfriends')
		payload = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
		file = requests.post('https://graph.facebook.com/oauth/access_token?', params = payload)
		print (file.text)
		result = file.text.split("=")[1]

		
		list_companies = ["walmart", "cisco", "pepsi", "facebook"]
		graph_url = "https://graph.facebook.com/walmart/posts/?key=value&access_token="
			
		web_response = urllib.request.urlopen(graph_url+ result)
		readable_page = web_response.read()
		json_postdata = json.loads(str(readable_page,'utf-8','strict'))
		json_fbposts = json_postdata['data']
		#Extract all messages and append them into new json
		post_id = {'message':[]}
		for post in json_fbposts:
			post_id ['message'].append({'message': post['message']})

		return Response (post_id ['message'])