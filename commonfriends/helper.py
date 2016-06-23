import logging
from allauth.socialaccount.models import SocialToken, SocialApp, SocialLogin
# Facepy 
from facepy import GraphAPI
import requests
# Owlready
from owlready import *
# get setting detail
from socialawareness.settings import BASE_DIR, ONTOLOGY_NAME



logger = logging.getLogger(__name__)


# load ontology
logger.info("Load Facebook.owl Ontology")
onto_path.append (BASE_DIR)
ONTO = Ontology(ONTOLOGY_NAME).load()


# Persing the ontology data
parsing_to_str = lambda args: str(args).replace("['",'').replace("']",'') 
remove_space = lambda args: str(args).replace(" ", "_") 


# Create instance of friend class for ontology
def create_friend (**kwargs):
	print("Calling Friendlist Method")
	friendList = ONTO.Friend(remove_space(kwargs['name']))
	friendList.has_name.append(kwargs['name'])
	friendList.has_id.append(kwargs['id'])
	friendList.has_picture.append(kwargs['url'])
	return friendList

# Create instance of user class for ontology
def create_user (**kwargs):
	print("Calling Create User Method")
	user = ONTO.User(remove_space(kwargs['user']))
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