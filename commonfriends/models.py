from __future__ import unicode_literals

from django.db import models
# Create your models here.
from django.dispatch import receiver
# allauth
from allauth.account.signals import user_logged_in, user_signed_up
from .helper import ONTO, parsing_to_str, OntologyManager , FacebookManager
import logging



logger = logging.getLogger(__name__)


# Listen to new user and add them to ontology 
@receiver(user_signed_up)
def user_signed_up(request, user, sociallogin=False, **kwargs):
	if sociallogin:
		if not ONTO.instances:
			# get user detail from facebook
			fb = FacebookManager(user)
			fb_user = fb.get_user_detail()

			logger.info("Signing up new user in ontology")
			# Create a new user in ontology user
			# OntologyManager class should have no parameter 
			onto = OntologyManager()
			onto.create_user(user= user.get_full_name(),name=fb_user['name'],
				id=fb_user['id'],
				gender=fb_user['gender'],
				url=fb_user['picture']['data']['url'])


# Listen to loggin and check if facebook friend has been changed
@receiver(user_logged_in)
def user_logged_in(request, user, sociallogin=None, **kwargs):
	if sociallogin:

		logger.info("Getting he current user detail from facebook")
		fb = FacebookManager(user)
		fb_friendlist = fb.get_user_friends()

		logger.info("Getting the current user detail from ontology")
		onto = OntologyManager(user)
		onto_friendlist= onto.get_friends_name()

		logger.info("Comparing between ontology friends and facebook friends")
		save_to_ontology = False
		for friend in fb_friendlist:
			if not friend['name'] in onto_friendlist:
				logger.info("Adding a friend")
				save_to_ontology=True
				onto.create_friend(name=friend['name'],id=friend['id'], url=friend['url'])
			else:
				logger.info("No New Friend Found")
			
		if save_to_ontology:
			logger.info("updating ontology")
			onto.save_ontology()
