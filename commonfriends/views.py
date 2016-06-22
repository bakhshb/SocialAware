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
		onto_friendlist=[]
		na = "Moayad_Sameer_Bakhsh"
		for f in onto.Friend.instances():
			print (f)
			if str(na) == str(f):
				print ("Ifound itjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
				print (f.is_friend_of)
			else:
				print ("not found")
		for onto_user in onto.User.instances():
			if str(onto_user) == str(user.get_full_name()).replace(" ","_"):
				
				onto_friendlist.append(dict(user_id=onto_user.has_id,
					name=onto_user.has_name,
					gender=onto_user.has_gender,
					picture=onto_user.has_picture))

				for onto_friend in onto_user.has_friend:
					onto_friendlist.append(dict(friend=self.onto_parsing(onto_friend.has_name),
						picture=onto_friend.has_picture))
			
			return Response (status=status.HTTP_200_OK, data= onto_friendlist)

	# 	user = request.user
	# 	if not onto.instances:
	# 		logger.info("Filling the ontology with Facebook data for the first time loggin")

	# 		fb_user = self.get_user_data(user=user)
	# 		onto_user = self.create_user(user= str(user.get_full_name()),
	# 			name=fb_user['name'],
	# 			id=fb_user['id'],
	# 			gender=fb_user['gender'],
	# 			url=fb_user['picture']['data']['url'])
	# 		fb_friendlist = self.get_facebook_data(user)

	# 		if not fb_friendlist:
	# 			content = {'detail':'Authentication with social account required'}
	# 			return Response(content, status=status.HTTP_428_PRECONDITION_REQUIRED)

	# 		for friend in fb_friendlist:
	# 			onto_user.has_friend.append(self.create_friend(name=friend['name'], 
	# 				id=friend['id'], url=friend['url']))

	# 		logger.info("Save to ontology")
	# 		onto.save('facebook.owl')

	# 		return Response (status=status.HTTP_200_OK, data= fb_friendlist)
	# 	else:
	# 		# This data from ontology
	# 		logger.info("Getting data from facebook")
	# 		fb_friendlist = self.get_facebook_data(user)
	# 		onto_friendlist=[]
			
	# 		if not fb_friendlist:
	# 			content = {'detail':'Authentication with social account required'}
	# 			return Response(content, status=status.HTTP_428_PRECONDITION_REQUIRED)

	# 		logger.info("Getting the data from ontology")
	# 		for onto_user in onto.User.instances():
	# 			if str(onto_user) == str(user.get_full_name()).replace(" ","_"):
					
	# 				for onto_friend in onto_user.has_friend:
	# 					onto_friendlist.append(self.onto_parsing(onto_friend.has_name))

	# 			logger.info("Checking if user has a new friend")
	# 			save_to_ontology = False
	# 			for friend in fb_friendlist:
	# 				if not friend['name'] in onto_friendlist:
	# 					print("Add a new friend")
	# 					save_to_ontology=True
	# 					onto_user.has_friend.append(self.create_friend(name=friend['name'],id=friend['id'], url=friend['url']))
	# 				else:
	# 					print("No new friend found")


	# 			if save_to_ontology:
	# 				logger.info("Save to ontology")
	# 				onto.save('facebook.owl')					
	# 		return Response(status=status.HTTP_200_OK, data= onto_friendlist)
				

	# def create_friend (self, **kwargs):
	# 	friendList = onto.Friend(kwargs['name'].replace(" ","_"))
	# 	friendList.has_name.append(kwargs['name'])
	# 	friendList.has_id.append(kwargs['id'])
	# 	friendList.has_picture.append(kwargs['url'])
	# 	return friendList

	# def create_user (self, **kwargs):
	# 	user = onto.User(kwargs['user'].replace(" ","_"))
	# 	user.has_name.append(kwargs['name'])
	# 	user.has_id.append(kwargs['id'])
	# 	user.has_gender= [kwargs['gender']]
	# 	user.has_picture.append(kwargs['url'])
	# 	return user

	# def get_facebook_data (self,user):
	# 	allfriends = []
	# 	try:
	# 		social_access_token = SocialToken.objects.get(account__user=user, account__provider='facebook')
	# 	except ObjectDoesNotExist:
	# 		logger.error("Authentication with social account required")
	# 		return allfriends

	# 	if social_access_token != None:
	# 		graph = GraphAPI(social_access_token)
	# 		# Get Frineds
	# 		friends= graph.get('me/invitable_friends')
	# 		# Wrap this block in a while loop so we can keep paginating requests until
	# 		# finished.
	# 		while(True):
	# 		    try:
	# 		        for friend in iter(friends['data']):
	# 		            allfriends.append(dict(name=friend['name'], 
	# 		            	id=friend['id'],
	# 		            	url=friend['picture']['data']['url']))
	# 		            #print(friend['picture']['data']['url'])
	# 		        # Attempt to make a request to the next page of data, if it exists.
	# 		        friends=requests.get(friends['paging']['next']).json()
	# 		    except KeyError:
	# 		        # When there are no more pages (['paging']['next']), break from the
	# 		        # loop and end the script.
	# 		        break
	# 		return allfriends

	# def get_user_data(self,**kwargs):
	# 	user = kwargs['user']
	# 	try:
	# 		social_access_token = SocialToken.objects.get(account__user=user, account__provider='facebook')
	# 	except ObjectDoesNotExist:
	# 		logger.error("Authentication with social account required")
	# 	if social_access_token != None:
	# 		graph = GraphAPI(social_access_token)
	# 		# Get Frineds
	# 		me= graph.get('me?fields=id,name,gender,picture')
	# 		return me




	def onto_parsing (self, args):
		data = str(args).replace("['",'').replace("']",'')
		return data