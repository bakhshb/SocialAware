"""socialawareness URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt
from commonfriends.views import UserBluetooth, SearchFriendByBluetooth, OwlReadyOntology
from facebookapi.views import FacePy, RestFacebookLogin, RestFacebookLogout




urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'^accounts/', include('allauth.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/bluetooth/user/$', csrf_exempt(UserBluetooth.as_view())),
    url(r'^api/bluetooth/search/$', csrf_exempt(SearchFriendByBluetooth.as_view())),
	url(r'^api/ontology/', OwlReadyOntology.as_view()),
	url(r'^api/facepy/', FacePy.as_view()),
    url(r'^api/login/facebook/$', csrf_exempt(RestFacebookLogin.as_view()), name='rest-facebook-login'),
    url(r'^api/logout/facebook/$', csrf_exempt(RestFacebookLogout.as_view()), name='rest-facebook-logout'),
    
]
