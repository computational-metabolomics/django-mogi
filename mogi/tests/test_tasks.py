# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals, print_function
# #  python manage.py test misa -v 3 --keepdb
# #  coverage  run   manage.py test mogi  -v 3 --keepdb --testrunner=green.djangorunner.DjangoRunner  --settings
# #  mogi.test_settings
# #  coverage report
# #  coverage html --omit="admin.py"
#
# from django.contrib.auth.models import AnonymousUser, User, Permission, Group
# from django.contrib.sessions.middleware import SessionMiddleware
# from django.contrib.messages.middleware import MessageMiddleware
# from django.contrib.auth.middleware import AuthenticationMiddleware
#
#
# from django.contrib.messages import get_messages
#
# from django.test import TestCase, RequestFactory, Client
# from django.urls import reverse
# from django.contrib.contenttypes.models import ContentType
#
# from mogi.views import views_isa
# from mogi.models import models_isa
#
#
# def add_middleware_to_request(request, middleware_class):
#     middleware = middleware_class()
#     middleware.process_request(request)
#     return request
#
# def add_middleware_to_response(request, middleware_class):
#     middleware = middleware_class()
#     middleware.process_response(request)
#     return request
#
# def add_all_middleware_to_request(request):
#     request = add_middleware_to_request(request, SessionMiddleware)
#     request = add_middleware_to_request(request, MessageMiddleware)
#     request = add_middleware_to_request(request, AuthenticationMiddleware)
#     request.session.save()
#
#     return request
#
# class TaskTestTestCase(TestCase):
#
#
#     def setUp(self):
#
#         self.factory = RequestFactory()
#         self.user = User.objects.create_user(username='jacob', email='jacob@jacob.com', password='top_secret')
#
#
#     def test_post(self):
#         """
#         Check that logged-in user with permissions can access and submit (post)
#         """
#         if self.view_type == 'create':
#
#             self.client.force_login(self.user)
#
#             response = self.client.post(reverse('search_frag'), {}, follow=True)
#
#
#
#
#
#