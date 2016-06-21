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
			logger.info("Filling the ontology with Facebook data for the first time loggin")
			onto_user = create_user ( name= str(user))
			
			try:
				social_access_token = SocialToken.objects.get(account__user=user, account__provider='facebook')
			except ObjectDoesNotExist:
				logger.error("Authentication with social account required")
				

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
				            #print(friend['picture']['data']['url'])
				            onto_user.has_friend.append(create_friendlist(name=friend['name']))
				        # Attempt to make a request to the next page of data, if it exists.
				        friends=requests.get(friends['paging']['next']).json()
				    except KeyError:
				        # When there are no more pages (['paging']['next']), break from the
				        # loop and end the script.
				        break
				logger.info("Save ontology to facebook ontology")
				onto.save('facebook.owl')

# Check if user has add a new friend in facebook
@receiver(user_logged_in)
def user_logged_in(request, user, sociallogin=None, **kwargs):
	if sociallogin:
		# This data from ontology
		logger.info("Getting the data from ontology")
		user = user
		allfriends = get_facebook_data(user= user)

		for onto_user in onto.User.instances():
			if str(onto_user) == str(user):
				friendlist=[]
				for onto_friend in onto_user.has_friend:
					friendlist.append(str(onto_friend.has_name).replace("['",'').replace("']",''))

				for friend in allfriends:
					if not friend in friendlist:
						logger.info("Add a new friend")
						onto_user.has_friend.append(create_friendlist(name=friend))
					else:
						logger.info("No new friend found")



# Create instance of friend class for ontology
def create_friendlist (**kwargs):
	logger.info("Calling Friendlist Method")
	friendList = onto.Friend(kwargs['name'].replace(" ","_"))
	friendList.has_name.append(kwargs['name'])
	return friendList

# Create instance of user class for ontology
def create_user (**kwargs):
	logger.info("Calling Create User Method")
	user = onto.User(kwargs['name'])
	user.has_name.append(kwargs['name'])
	return user

# Get facebook data
def get_facebook_data (**kwargs):
	user = kwargs['user']
	try:
		social_access_token = SocialToken.objects.get(account__user=user, account__provider='facebook')
	except ObjectDoesNotExist:
		logger.error("Authentication with social account required")
		return allfriends

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
		            allfriends.append(friend['name'])
		            #print(friend['picture']['data']['url'])
		        # Attempt to make a request to the next page of data, if it exists.
		        friends=requests.get(friends['paging']['next']).json()
		    except KeyError:
		        # When there are no more pages (['paging']['next']), break from the
		        # loop and end the script.
		        break
		return allfriends
