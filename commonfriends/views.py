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
# curl -X POST  -H "Content-Type: application/json" -H 'Authorization: Token d930a6d3e0fa7698eeeb956c0ea0ac047bc76d2d' -d "{'bluetooth':''}" http://localhost:8000/api/bluetooth/user/
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
			return Response(status = status.HTTP_400_BAD_REQUEST, data={'status': status.HTTP_400_BAD_REQUEST})
		original_request = request._request
		user = original_request.user
		onto = OntologyManager(user.email)
		if onto.user is None:
			data={
				'status': '400',
				'data': 'Authentication with social account required '
			}
			return Response(status = status.HTTP_400_BAD_REQUEST, data=data)
		onto.add_bluetooth(user_bluetooth)

		return Response(status = status.HTTP_200_OK,data={'status':status.HTTP_200_OK })

#receive Bluetooth to check for mutual friends 
# curl -X POST  -H "Content-Type: application/json" -H 'Authorization: Token d930a6d3e0fa7698eeeb956c0ea0ac047bc76d2d' -d "{'bluetooth':''}" http://localhost:8000/api/bluetooth/search/
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
		SUGGEST_FRIEND =3

		logger.info("Receiving Surrounding Bluetooth")
		data = request.data
		bluetooth = data.get('bluetooth','')
		# Checking if bluetooth is submitted
		if not bluetooth:
			logger.info("Bluetooth is empty")
			return Response(status = status.HTTP_400_BAD_REQUEST, data={'status': status.HTTP_400_BAD_REQUEST})

		# Getting the current user detail from ontology
		original_request = request._request
		user = original_request.user
		onto_user = OntologyManager(user.email)

		# Getting user info by bluetooth mac address
		onto_user2 = OntologyManager()
		bluetooth_user2 = onto_user2.get_user_by_bluetooth (bluetooth)

		if bluetooth_user2:
			# Checking if they are already friends
			already_friends = onto_user.check_already_friends (None, bluetooth)

			if already_friends:
				data = {
				'status':'200',
				'user': already_friends,
				'friend_status': USER_ALREADY_FRIEND,
				'friend': [],
				}
				return Response(status = status.HTTP_200_OK,data=data)


			# Checking if No mutual friend found
			mutual = onto_user.get_common_friends_sec(None, bluetooth )

			if mutual:
				data = {
					'status':'200',
					'user': onto_user2.get_name(bluetooth_user2),
					'friend_status': FOUND_MUTUAL_FRIENDS,
					'friend': mutual,
				}
				return Response(status = status.HTTP_200_OK,data=data)

			# if they are not frined and they do not have mutual friends 
			# Then suggest a friend
			data = {
					'status':'200',
					'user': onto_user2.get_name(bluetooth_user2),
					'friend_status': SUGGEST_FRIEND,
					'friend': [],
			}
			return Response(status = status.HTTP_200_OK,data=data)
		else:
			# Otherwise return nothing
			data = {
					'status':'204',
					'friend_status': NO_MATCH_FOUND,
					'friend': [],
			}
			return Response(status = status.HTTP_204_NO_CONTENT, data= data)



		
# curl -X GET -H 'Authorization: Token f386ccc6c18ffe7863cd705340c3f138967033f3' http://localhost:8000/api/ontology/
class OwlReadyOntology (APIView):
	permission_classes = (IsAuthenticated,)

	def get (self, request, format=None):
		original_request = request._request
		user = original_request.user
		onto_friendlist=[]
		onto= OntologyManager(user.email)
		if onto.user is None:
			data={
				'status': '400',
				'data': 'Authentication with social account required '
			}
			return Response(status = status.HTTP_400_BAD_REQUEST, data=data)
		onto_friendlist = onto.get_friends_name()

		return Response (status=status.HTTP_200_OK, data= onto_friendlist)
