from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import JSONParser
from django.core.exceptions import ObjectDoesNotExist
import logging
from .helper import OntologyManager, parsing_to_str
import json


logger = logging.getLogger(__name__)

#send User Bluetooth to save it to ontology
# curl -X POST  -H "Content-Type: application/json" -H 'Authorization: Token f386ccc6c18ffe7863cd705340c3f138967033f3' -d "{'bluetooth':''}" http://localhost:8000/api/bluetooth/user/
# Path http://localhost:8000/api/bluetooth/user/
class UserBluetooth(APIView):
	permission_classes = (IsAuthenticated,)

	def dispatch(self, *args, **kwargs):
		return super(UserBluetooth, self).dispatch(*args, **kwargs)
	def post(self, request):
		logger.info("Register User Bluetooth")
		data = request.data
		user_bluetooth = data.get('user_bluetooth','')
		# Checking if user_bluetooth is submitted
		if not user_bluetooth:
			logger.info("User Bluetooth is empty")
			return Response(status = status.HTTP_204_NO_CONTENT, data={'status': status.HTTP_204_NO_CONTENT})

		user = request.user
		onto = OntologyManager(user)
		onto_user = onto.get_user()
		onto.create_bluetooth(user_bluetooth)
		logger.debug(onto_user.has_bluetooth)
		onto.save_ontology()

		return Response(status = status.HTTP_200_OK,data={'status':status.HTTP_200_OK })

#receive Bluetooth to check for mutual friends 
# curl -X POST  -H "Content-Type: application/json" -H 'Authorization: Token f386ccc6c18ffe7863cd705340c3f138967033f3' -d "{'bluetooth':''}" http://localhost:8000/api/bluetooth/search/
# Path http://localhost:8000/api/bluetooth/search/
class SearchFriendByBluetooth(APIView):
	permission_classes = (IsAuthenticated,)

	def dispatch(self, *args, **kwargs):
		return super(SearchFriendByBluetooth, self).dispatch(*args, **kwargs)
	def post(self, request):
		# Friend status
		NO_MATCH_FOUND = 0
		USER_ALREADY_FRIEND =1
		FOUND_MUTUAL_FRIENDS = 2

		logger.info("Receiving Surrounding Bluetooth")
		data = request.data
		bluetooth = data.get('bluetooth','')
		# Checking if bluetooth is submitted
		if not bluetooth:
			logger.info("Bluetooth is empty")
			return Response(status = status.HTTP_400_BAD_REQUEST, data={'status': status.HTTP_400_BAD_REQUEST})


		# Finding the user by bluetooth address in the ontology
		onto_received = OntologyManager()
		onto_received_user = onto_received.get_user_by_bluetooth(bluetooth)
		if onto_received_user is None:
			logger.debug("No Match Found")
			data = {
				'status':'204',
				'friend_status': NO_MATCH_FOUND,
				'friend': [],
			}
			return Response(status = status.HTTP_204_NO_CONTENT, data= data)
		# if user is found, then get user friend list
		onto_received_user_friends = onto_received.get_friends_name()

		# Getting the current user detail from ontology
		user = request.user
		onto_current = OntologyManager(user)
		onto_current_user_friends = onto_current.get_friends_name()
		# Checking if the received bluetooth is already friend with the current user
		if parsing_to_str(onto_received_user.has_name) in onto_current_user_friends:
			logger.info("User is already your friend")
			data = {
				'status':'200',
				'user': parsing_to_str(onto_received_user.has_name),
				'friend_status': USER_ALREADY_FRIEND,
				'friend': [],
			}
			return Response(status = status.HTTP_200_OK,data=data)


		# Comapring both friend list and finding mutual friends
		mutual = set(onto_current_user_friends) & set(onto_received_user_friends)
		# No mutual friend found
		if not mutual:
			data = {
				'status':'204',
				'friend_status': NO_MATCH_FOUND,
				'friend': [],
			}
			return Response(status = status.HTTP_204_NO_CONTENT, data= data)

		data = {
		'status':'200',
		'user': parsing_to_str(onto_received_user.has_name),
		'friend_status': FOUND_MUTUAL_FRIENDS,
		'friend': mutual,
		}
		return Response(status = status.HTTP_200_OK,data=data)



		
# curl -X GET -H 'Authorization: Token f386ccc6c18ffe7863cd705340c3f138967033f3' http://localhost:8000/api/ontology/
class OwlReadyOntology (APIView):
	permission_classes = (IsAuthenticated,)

	def get (self, request, format=None):
		user = request.user
		onto_friendlist=[]
		onto= OntologyManager(user)
		if repr(onto) == 'None':
			data={
				'status': status.HTTP_204_NO_CONTENT,
				'data': 'Authentication with social account required '
			}
			return Response(status = status.HTTP_204_NO_CONTENT, data=data)
		onto_friendlist = onto.get_friends_name()

		return Response (status=status.HTTP_200_OK, data= onto_friendlist)
