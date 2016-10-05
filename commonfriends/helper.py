from django.core.exceptions import ObjectDoesNotExist
from allauth.socialaccount.models import SocialToken, SocialApp, SocialLogin
# Facepy a plugin for Facebook
from facepy import GraphAPI
import requests
# REDFLIB 
import rdflib
from rdflib import Namespace, Literal, RDFS, URIRef, BNode
from rdflib.namespace import RDF, FOAF
# get setting detail
from socialawareness.settings import BASE_DIR
import logging



logger = logging.getLogger(__name__)


# load ontology
logger.info("Loading Ontology")
ONTO=rdflib.Graph()
ONTO.load(BASE_DIR+'/socialContext.owl')
#PREFIX SC = Social Context
SC = Namespace("http://www.semanticweb.org/xgc4811/ontologies/2016/9/socialContext#") 

# Persing the ontology data
parsing_to_str = lambda args: str(args).replace("['",'').replace("']",'') 
remove_space = lambda args: str(args).replace(" ", "_").lower()

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
			me= graph.get('me?fields=id,name,gender,picture,email,hometown,location,birthday')
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

    def __init__(self, user=None):
        #logger.info("Ontology Manager Started")
        global ONTO
        global SC
        self.user = None
        if user is not None:
            try:
                email = URIRef("http://www.semanticweb.org/xgc4811/ontologies/2016/9/socialContext#%s"%str(user).lower())
                qres = ONTO.query(
                    """SELECT ?person
                       WHERE {
                          ?person foaf:mbox ?email.
                       }""",initNs = { "foaf": FOAF}, initBindings = {"email": email})

                for row in qres:
                    self.user = URIRef("%s"%row)
##                for onto_user in ONTO.subjects(FOAF.name):
##                    if remove_space(user) in onto_user:
##                        self.user = onto_user
            except ValueError:
                print("The user does not exist in the ontology because authentication with social account required")


    def add_user (self,**kwargs):
        self.user = URIRef("http://www.semanticweb.org/xgc4811/ontologies/2016/9/socialContext#%s"%str(kwargs['email']).lower())
        ONTO.add ((self.user, RDF.type, FOAF.Person))
        ONTO.add ((self.user, FOAF.name, Literal(kwargs['name'])))
        ONTO.add ((self.user, FOAF.firstName, Literal(kwargs['first_name'])))
        ONTO.add ((self.user, FOAF.lastName, Literal(kwargs['last_name'])))
        ONTO.add ((self.user, FOAF.gender, Literal(kwargs['gender'])))
        ONTO.add ((self.user, FOAF.mbox, self.user))
        ONTO.add ((self.user, SC.facebookID, Literal(kwargs['id'])))
        ONTO.add ((self.user, SC.imageURL, Literal(kwargs['url'])))
        ONTO.serialize("socialContext.owl", format="pretty-xml")
        logger.info("User is added successfully ")

    def get_username (self):
        qres = ONTO.query(
            """SELECT ?name
               WHERE {
                  ?person foaf:name ?name.
               }""",initNs = { "foaf": FOAF}, initBindings = {"person": self.user})

        for row in qres:
            name = str ("%s"%row)
        return name

    def add_friend (self,**kwargs):
        if self.user is not None:
            friend = URIRef("http://www.semanticweb.org/xgc4811/ontologies/2016/9/socialContext#%s"%remove_space(kwargs['name']))
            ONTO.add ((friend, RDF.type, SC['FriendList']))
            ONTO.add ((friend, FOAF.name, Literal(kwargs['name'])))
            ONTO.add ((friend, SC.facebookID, Literal(kwargs['id'])))
            ONTO.add ((friend, SC.imageURL, Literal(kwargs['url'])))
            ONTO.add ((friend, SC.isFriendOf, self.user))
            ONTO.add ((self.user, SC.isFriendOf, friend))
            ONTO.serialize("socialContext.owl", format="pretty-xml")
            logger.info("Friend is added successfully ")
        else:
            raise ValueError ("Cannot add friends because user is not found")

    def get_friends (self):
        onto_friendlist = []
        if self.user is not None:
            # Get friends using SPARQL
            qres = ONTO.query(
                """SELECT ?name
                   WHERE {
                      ?person1 sc:isFriendOf ?friend.
                      ?friend foaf:name ?name.
                   }""",initNs = { "foaf": FOAF , "sc": "http://www.semanticweb.org/xgc4811/ontologies/2016/9/socialContext#"}, initBindings = {"person1": self.user})
            for row in qres:
                onto_friendlist.append("%s"%row)
            return onto_friendlist
##            Get friends using python code
##            for d in ONTO.objects(self.user, SC.isFriendOf):
##                for a in ONTO.objects(d,FOAF.name):
##                    onto_friendlist.append(a)
##            return onto_friendlist
        else:
            raise ValueError ("Cannot get friends because user is not found")

    def add_bluetooth(self, bluetooth):
        if self.user is not None:
            for b in ONTO.objects (self.user, FOAF.name):
                ONTO.set((self.user,SC.bluetoothID, Literal(bluetooth)))
                ONTO.serialize("socialContext.owl", format="pretty-xml")
                logger.info("Bluetooth is added successfully ")
        else:
            raise ValueError ("Cannot create bluetooth because user is not found")
            
   
    def get_user_by_bluetooth (self, bluetooth):
        # Get user by bluetooth ID using SPARQL
        bluetooth = Literal(bluetooth)
        qres = ONTO.query(
            """SELECT ?person
               WHERE {
                  ?person sc:bluetoothID ?bluetooth.
               }""",initNs = {"sc": "http://www.semanticweb.org/xgc4811/ontologies/2016/9/socialContext#"}, initBindings = {"bluetooth": bluetooth})

        for row in qres:
            user = URIRef("%s"%row)
        return user
    
##        Get user by bluetooth ID using python code
##        for user in ONTO.subjects(SC.bluetoothID):
##            for onto_bluetooth in ONTO.objects (user, SC.bluetoothID):
##                if bluetooth in onto_bluetooth:
##                    return user

    # Getting common firends using python code                
    def get_common_friends (self, user_uri = None, bluetooth = None):
        onto_friendlist1 = self.get_friends()
        onto_friendlist2 = []
        if bluetooth is not None:
            user_uri = self.get_user_by_bluetooth(bluetooth)
            
        if user_uri is not None:                
            for onto_friend in ONTO.objects (user_uri, SC.isFriendOf):
                for onto_friend_name in ONTO.objects (onto_friend, FOAF.name):
                    onto_friendlist2.append("%s"%onto_friend_name)
            common_friends = set(onto_friendlist1) & set(onto_friendlist2)
            return common_friends
        else:
            print ("Could not find such a user in the dataset")

    # Getting common friends using SPARQL
    def get_common_friends_sec (self, user_uri= None, bluetooth = None):
        common_friends = []
        if bluetooth is not None:
            user_uri = self.get_user_by_bluetooth(bluetooth)
        if (user_uri is not None and self.user is not None):
            qres = ONTO.query(
                """SELECT ?name
                   WHERE {
                      ?person1 sc:isFriendOf ?friend. 
                      ?person2 sc:isFriendOf ?friend.
                      ?friend foaf:name ?name
                   }""",initNs = { "foaf": FOAF , "sc": "http://www.semanticweb.org/xgc4811/ontologies/2016/9/socialContext#"}, initBindings = {"person1": self.user, "person2":user_uri})

            for row in qres:
            	common_friends.append("%s"%row)                    
            return qres
        else:
            print ("Could not find such a user in the dataset")