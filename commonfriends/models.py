from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.dispatch import receiver
# allauth
from allauth.account.signals import user_logged_in, user_signed_up
from allauth.socialaccount.signals import pre_social_login
from allauth.socialaccount.models import SocialToken
# Facepy 
from facepy import GraphAPI
import requests
# Owlready
from owlready import *
# get setting detail
from socialawareness.settings import BASE_DIR, ONTOLOGY_NAME
import logging




logger = logging.getLogger(__name__)


# load ontology
logger.info("Load Facebook.owl Ontology")
onto_path.append (BASE_DIR)
print ("this is %s" % BASE_DIR)
onto = Ontology(ONTOLOGY_NAME).load()

# Add the new sign up user to ontology 
@receiver(user_signed_up)
def user_signed_up(request, user, sociallogin=False, **kwargs):
	if sociallogin:
		if not onto.instances:
			logger.info("Perparing to load data to ontology")

			logger.info("get user details")
			fb_user = get_user_data(user=user)
			onto_user = create_user(user= str(user.get_full_name()),
				name=fb_user['name'],
				id=fb_user['id'],
				gender=fb_user['gender'],
				url=fb_user['picture']['data']['url'])
			logger.info("get user friend list")
			fb_friendlist = get_facebook_data(user=user)

			if not fb_friendlist:
				logger.error("The friendlist is empty")

			for friend in fb_friendlist:
				onto_user.has_friend.append(create_friend(name=friend['name'], 
					id=friend['id'], url=friend['url']))
				
			logger.info("Save to facebook ontology")
			onto.save('facebook.owl')


# Check if user has add a new friend in facebook
@receiver(user_logged_in)
def user_logged_in(request, user, sociallogin=None, **kwargs):
	if sociallogin:
		# This data from ontology
		logger.info("Getting data from facebook")
		fb_friendlist = get_facebook_data(user=user)
		onto_friendlist=[]
		if not fb_friendlist:
			logger.error("The friendlist is empty")

		logger.info("Getting the data from ontology")
		for onto_user in onto.User.instances():
			if str(onto_user) == str(user.get_full_name()).replace(" ","_"):
				
				for onto_friend in onto_user.has_friend:
					onto_friendlist.append(onto_parsing(onto_friend.has_name))

			logger.info("Checking if user has a new friend")
			save_to_ontology = False
			for friend in fb_friendlist:
				if not friend['name'] in onto_friendlist:
					print("Add a new friend")
					save_to_ontology=True
					onto_user.has_friend.append(create_friend(name=friend['name'],id=friend['id'], url=friend['url']))
				else:
					print("No new friend found")

			if save_to_ontology:
				logger.info("update with new friend info facebook ontology")
				print("it has")
				onto.save('facebook.owl')

# Persing the ontology data
def onto_parsing (args):
	data = str(args).replace("['",'').replace("']",'')
	return data


# Create instance of friend class for ontology
def create_friend (**kwargs):
	logger.info("Calling Friendlist Method")
	friendList = onto.Friend(kwargs['name'].replace(" ","_"))
	friendList.has_name.append(kwargs['name'])
	friendList.has_id.append(kwargs['id'])
	friendList.has_picture.append(kwargs['url'])
	return friendList

# Create instance of user class for ontology
def create_user (**kwargs):
	print("Calling Create User Method")
	user = onto.User(kwargs['user'].replace(" ","_"))
	user.has_name.append(kwargs['name'])
	user.has_id.append(kwargs['id'])
	user.has_gender= [kwargs['gender']]
	user.has_picture.append(kwargs['url'])
	return user

# Get user details
def get_user_data(**kwargs):
	user = kwargs['user']
	try:
		social_access_token = SocialToken.objects.get(account__user=user, account__provider='facebook')
	except ObjectDoesNotExist:
		logger.error("Authentication with social account required")
	if social_access_token != None:
		graph = GraphAPI(social_access_token)
		# Get Frineds
		me= graph.get('me?fields=id,name,gender,picture')
		return me

# Get facebook data
def get_facebook_data (**kwargs):
	user = kwargs['user']
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
		            allfriends.append(dict(name=friend['name'], 
		            	id=friend['id'],
		            	url=friend['picture']['data']['url']))
		            #print(friend['picture']['data']['url'])
		        # Attempt to make a request to the next page of data, if it exists.
		        friends=requests.get(friends['paging']['next']).json()
		    except KeyError:
		        # When there are no more pages (['paging']['next']), break from the
		        # loop and end the script.
		        break
		return allfriends
