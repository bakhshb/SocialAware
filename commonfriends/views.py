from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ObjectDoesNotExist
import logging
from socialawareness.settings import BASE_DIR
from owlready import *
#facepy 
from facepy import GraphAPI
import requests
#allauth
from allauth.socialaccount.models import SocialToken, SocialApp, SocialLogin
from .models import onto

logger = logging.getLogger(__name__)


class OwlReadyOntology (APIView):
	permission_classes = (IsAuthenticated,)

	def get (self, request, format=None):
		user = request.user
		if not onto.instances:
			logger.info("Filling the ontology with Facebook data for the first time loggin")
			onto_user = self.create_user ( name= str(user))
			
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
				        for friend in iter(friends['data']):
				            allfriends.append({'name':friend['name']})
				            #print(friend['picture']['data']['url'])
				            onto_user.has_friend.append(self.create_friendlist(name=friend['name']))
				        # Attempt to make a request to the next page of data, if it exists.
				        friends=requests.get(friends['paging']['next']).json()
				    except KeyError:
				        # When there are no more pages (['paging']['next']), break from the
				        # loop and end the script.
				        break
				onto.save('facebook.owl')

				
				return Response (status=status.HTTP_200_OK, data= allfriends)
		else:
			# This data from ontology
			logger.info("Getting the data from ontology")

			allfriends = self.get_facebook_data(user)

			if not allfriends:
				content = {'detail':'Authentication with social account required'}
				return Response(content, status=status.HTTP_428_PRECONDITION_REQUIRED)
				
			for onto_user in onto.User.instances():
				if str(onto_user) == str(user):
					friendlist=[]
					for onto_friend in onto_user.has_friend:
						friendlist.append(str(onto_friend.has_name).replace("['",'').replace("']",''))
					for friend in allfriends:
						if not friend in friendlist:
							logger.info("Add a new friend")
							onto_user.has_friend.append(self.create_friendlist(name=friend))
						else:
							logger.info("No new friend found")
					return Response(status=status.HTTP_200_OK, data= friendlist)
				

	def create_friendlist (self, **kwargs):
		logger.info("Calling Friendlist Method")
		friendList = onto.Friend(kwargs['name'].replace(" ","_"))
		friendList.has_name.append(kwargs['name'])
		return friendList

	def create_user (self, **kwargs):
		logger.info("Calling Create User Method")
		user = onto.User(kwargs['name'])
		user.has_name.append(kwargs['name'])
		return user

	def get_facebook_data (self,user):
		allfriends = []
		try:
			social_access_token = SocialToken.objects.get(account__user=user, account__provider='facebook')
		except ObjectDoesNotExist:
			logger.error("Authentication with social account required")
			return allfriends

		if social_access_token != None:
			graph = GraphAPI(social_access_token)
			# Get Frineds
			friends= graph.get('me/invitable_friends')
			
			# Wrap this block in a while loop so we can keep paginating requests until
			# finished.
			while(True):
			    try:
			        for friend in iter(friends['data']):
			            allfriends.append(friend['name'])
			            #print(friend['picture']['data']['url'])
			        # Attempt to make a request to the next page of data, if it exists.
			        friends=requests.get(friends['paging']['next']).json()
			    except KeyError:
			        # When there are no more pages (['paging']['next']), break from the
			        # loop and end the script.
			        break
			return allfriends

		
