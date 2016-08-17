from django.core.exceptions import ObjectDoesNotExist
from allauth.socialaccount.models import SocialToken, SocialApp, SocialLogin
# Facepy a plugin for Facebook
from facepy import GraphAPI
import requests
# Owlready
from owlready import *
# get setting detail
from socialawareness.settings import BASE_DIR, ONTOLOGY_IRI
import logging



logger = logging.getLogger(__name__)


# load ontology
logger.info("Loading Facebook.owl Ontology")
onto_path.append (BASE_DIR)
logger.error(BASE_DIR)
ONTO = Ontology(ONTOLOGY_IRI).load()


# Persing the ontology data
parsing_to_str = lambda args: str(args).replace("['",'').replace("']",'') 
remove_space = lambda args: str(args).replace(" ", "_") 

# Managing Facebook
class FacebookManager (object):
	def __init__(self, user=None):
		logger.info("Facebook Manager Started")
		self.user = None
		self.social_access_token = None
		if user is not None:
			self.user = user
			try:
				self.social_access_token = SocialToken.objects.get(account__user=self.user, account__provider='facebook')
			except ObjectDoesNotExist:
				logger.error("Authentication with social account required")

	def __repr__(self):
		return repr(self.social_access_token)


	def get_user_token (self):
		return self.social_access_token

	def get_user_detail(self):
		if self.social_access_token != None:
			graph = GraphAPI(self.social_access_token)
			# Get Frineds
			me= graph.get('me?fields=id,name,gender,picture')
			return me

	def get_user_friends(self):
		allfriends =[]
		if self.social_access_token != None:
			graph = GraphAPI(self.social_access_token)
			# Get Frineds taggable friends
			# friends= graph.get('me/invitable_friends')
			friends= graph.get('me/taggable_friends')
			# Wrap this block in a while loop so we can keep paginating requests until
			# finished.
			while(True):
			    try:
			        for friend in iter(friends['data']):
			            allfriends.append(dict(name=friend['name'], 
			            	id=friend['id'],
			            	url=friend['picture']['data']['url']))
			        # Attempt to make a request to the next page of data, if it exists.
			        friends=requests.get(friends['paging']['next']).json()
			    except KeyError:
			        # When there are no more pages (['paging']['next']), break from the
			        # loop and end the script.
			        break
			return allfriends


# Managing ontology
class OntologyManager (object):
	def __init__ (self, user=None):
		logger.info("Ontology Manager Started")
		global ONTO
		global ONTOLOGY_IRI
		self.user = None
		if user is not None:
			try:
				onto_user_object = ONTO.get_object(ONTOLOGY_IRI+"#%s"%remove_space(user.get_full_name()))
				if onto_user_object in ONTO.User.instances():
					self.user = onto_user_object
			except ValueError:
				logger.error("The user does not exist in the ontology because authentication with social account required")

	def __repr__(self):
		return repr(self.user)
		
	def get_user (self):
		if self.user is not None:
			return self.user
		else:
			raise ValueError ("user has not been created")
			logger.error("user has not been created")

	def get_friends (self):
		if self.user is not None:
			onto_friendlist=[]
			for onto_friend in self.user.has_friend:
				onto_friendlist.append(dict(friend=parsing_to_str(onto_friend.has_name),
					picture=parsing_to_str(onto_friend.has_picture)))
			return onto_friendlist
		else:
			raise ValueError ("Cannot get friends because user is not found")
			logger.error("Cannot get friends because user is not found")


	def get_friends_name (self):
		if self.user is not None:
			onto_friendlist=[]
			for onto_friend in self.user.has_friend:
				onto_friendlist.append(parsing_to_str(onto_friend.has_name))
			return onto_friendlist
		else:
			raise ValueError ("Cannot get friends because user is not found")
			logger.error("Cannot get friends because user is not found")

	def create_user (self, **kwargs):
		if self.user is None:
			if not remove_space(kwargs['user']) in ONTO.User.instances():
				self.user = ONTO.User(remove_space(kwargs['user']))
				self.user.has_name.append(kwargs['name'])
				self.user.has_id.append(kwargs['id'])
				self.user.has_gender= [kwargs['gender']]
				self.user.has_picture.append(kwargs['url'])
			else:
				raise ValueError ("User already exists")
				logger.error("User already exists")
		else:
			raise ValueError ("Cannot create user because user already exists")
			logger.error("Cannot create user because user already exists")

	def create_friend (self,**kwargs):
		if self.user is not None:
			friend = ONTO.Friend(remove_space(kwargs['name']))
			friend.has_name.append(kwargs['name'])
			friend.has_id.append(kwargs['id'])
			friend.has_picture.append(kwargs['url'])
			self.user.has_friend.append(friend)
		else:
			raise ValueError ("Cannot create friend because user is not found")
			logger.error("Cannot create friend because user is not found")

	def delete_instances (self,instance):
		ONTO.instances.remove(instance)

	def create_bluetooth(self, bluetooth):
		if self.user is not None:
			current_bluetooth = self.user.has_bluetooth
			if not current_bluetooth:
				# if there is no bluetooth create bluetooth
				self.user.has_bluetooth.append(bluetooth)
			else:
				# remove current bluetooth, then create new bluetooth
				self.user.has_bluetooth.remove(parsing_to_str(current_bluetooth))
				self.user.has_bluetooth.append(bluetooth)
		else:
			raise ValueError ("Cannot create bluetooth because user is not found")
			logger.error("Cannot create bluetooth because user is not found")

	def get_user_by_bluetooth (self, bluetooth):
		for onto_user in ONTO.User.instances():
			if parsing_to_str(onto_user.has_bluetooth) == bluetooth:
				self.user = onto_user
		return self.user

	def save_ontology(self):
		ONTO.save('facebook.owl')