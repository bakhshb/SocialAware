from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ObjectDoesNotExist
import logging
from .helper import ONTO, parsing_to_str, remove_space

logger = logging.getLogger(__name__)


class OwlReadyOntology (APIView):
	permission_classes = (IsAuthenticated,)

	def get (self, request, format=None):

		user = request.user
		onto_friendlist=[]
		for onto_user in ONTO.User.instances():
			if str(onto_user) == remove_space(user.get_full_name()):
				
				onto_friendlist.append(dict(user_id=parsing_to_str(onto_user.has_id),
					name=parsing_to_str(onto_user.has_name),
					gender=parsing_to_str(onto_user.has_gender),
					picture=parsing_to_str(onto_user.has_picture)))

				for onto_friend in onto_user.has_friend:
					onto_friendlist.append(dict(friend=parsing_to_str(onto_friend.has_name),
						picture=parsing_to_str(onto_friend.has_picture)))
			
			return Response (status=status.HTTP_200_OK, data= onto_friendlist)
