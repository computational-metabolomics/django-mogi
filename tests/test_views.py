# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse


from mogi.views import IncomingGalaxyDataListView

def add_middleware_to_request(request, middleware_class):
    middleware = middleware_class()
    middleware.process_request(request)
    return request

def add_middleware_to_response(request, middleware_class):
    middleware = middleware_class()
    middleware.process_response(request)
    return request




class IncomingGalaxyDataViewSetTestCase(TestCase):


    def setUp(self):

        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@jacob.com', password='top_secret')

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/mogi/incoming_galaxy_data_list/')

        request.user = AnonymousUser()
        request = add_middleware_to_request(request, SessionMiddleware)
        response = IncomingGalaxyDataListView.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        self.assertRedirects(response, '/login/?next=/mogi/incoming_galaxy_data_list/')

    def test_get(self):
        """
        """
        request = self.factory.get(reverse('incoming_galaxy_data_list'))
        request.user = self.user
        response = IncomingGalaxyDataListView.as_view()(request)
        self.assertEqual(response.status_code, 200) # done without error