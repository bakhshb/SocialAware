from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging
from socialawareness.settings import BASE_DIR
from owlready import *

logger = logging.getLogger(__name__)

# load ontology
onto_path.append (BASE_DIR)
onto = Ontology("http://test.org/onto.owl").load()

class NonVegetarianPizza (onto.Pizza):
	def eat (self): return "I am Not Vegetarian"



class OwlReadyOntology (APIView):
	permission_classes = (AllowAny,)

	def get (self, request, format=None):
		test_pizza = onto.Pizza("test_pizza_owl_identifier")
		test_pizza.has_topping = [ onto.FishTopping(), onto.MeatTopping()]
		onto.sync_reasoner()
		return Response (test_pizza.eat())
		