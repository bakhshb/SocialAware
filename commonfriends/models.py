from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.dispatch import receiver
# allauth
from allauth.account.signals import user_logged_in, user_signed_up
import logging
from .helper import ONTO, parsing_to_str, remove_space, create_friend, create_user, get_user_data, get_facebook_data 

logger = logging.getLogger(__name__)


# Add the new sign up user to ontology 
@receiver(user_signed_up)
def user_signed_up(request, user, sociallogin=False, **kwargs):
	if sociallogin:
		if not ONTO.instances:
			logger.info("Perparing to load data to ontology")

			logger.info("get user details")
			fb_user = get_user_data(user=user)
			onto_user = create_user(user= user.get_full_name(),
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
			ONTO.save('facebook.owl')


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
		for onto_user in ONTO.User.instances():
			if str(onto_user) == remove_space(user.get_full_name()):
				for onto_friend in onto_user.has_friend:
					onto_friendlist.append(parsing_to_str(onto_friend.has_name))

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
			ONTO.save('facebook.owl')
