from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import TemplateHTMLRenderer
from django.core.exceptions import ObjectDoesNotExist
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
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		user = request.user
		# Make Sure User Logged in With Social Account
		try:
			social_access_token = SocialToken.objects.get(account__user=user, account__provider='facebook')
		except ObjectDoesNotExist:
			content = {'detail':'Authentication with social account required'}
			return Response(content, status=status.HTTP_428_PRECONDITION_REQUIRED)

		if social_access_token != None:
			graph = facebook.GraphAPI(access_token= social_access_token, version='2.2')
			# Get Frineds
			friends = graph.get_connections(id='me', connection_name='taggable_friends')

			allfriends =[]
			# Wrap this block in a while loop so we can keep paginating requests until
			# finished.
			while (True):
				try:
					for friend in friends['data']:
						allfriends.append({'name':friend['name']})
					# Attempt to make a request to the next page of data, if it exists.
					friends=requests.get(friends['paging']['next']).json()
				except KeyError:
					# When there are no more pages (['paging']['next']), break from the
			        # loop and end the script.
					break

			return Response (allfriends)



class FacePy (APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		user = request.user
		try:
			social_access_token = SocialToken.objects.get(account__user=user, account__provider='facebook')
		except ObjectDoesNotExist:
			content = {'detail':'Authentication with social account required'}
			return Response(content, status=status.HTTP_428_PRECONDITION_REQUIRED)

		if social_access_token != None:
			graph = GraphAPI(social_access_token)
			# Get Frineds
			friends= graph.get('me/invitable_friends')
			allfriends = []

			# Wrap this block in a while loop so we can keep paginating requests until
			# finished.
			while(True):
			    try:
			        for friend in friends['data']:
			            allfriends.append({'name':friend['name']})
			        # Attempt to make a request to the next page of data, if it exists.
			        friends=requests.get(friends['paging']['next']).json()
			    except KeyError:
			        # When there are no more pages (['paging']['next']), break from the
			        # loop and end the script.
			        break
			return Response (allfriends)				


class URLLib (APIView):
	permission_classes = (AllowAny,)
	def get(self, request, format=None):
		# Get application access token 
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
		# Extract all messages & append them into new json
		post_id = {'message':[]}
		for post in json_fbposts:
			post_id ['message'].append({'message': post['message']})

		return Response (post_id ['message'])