# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
#  python manage.py test misa -v 3 --keepdb
#  coverage  run   manage.py test mogi  -v 3 --keepdb --testrunner=green.djangorunner.DjangoRunner  --settings
#  mogi.test_settings
#  coverage report
#  coverage html --omit="admin.py"

from django.contrib.auth.models import AnonymousUser, User, Permission, Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware


from django.contrib.messages import get_messages

from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from mogi.views import views_isa
from mogi.models import models_isa


def add_middleware_to_request(request, middleware_class):
    middleware = middleware_class()
    middleware.process_request(request)
    return request

def add_middleware_to_response(request, middleware_class):
    middleware = middleware_class()
    middleware.process_response(request)
    return request

def add_all_middleware_to_request(request):
    request = add_middleware_to_request(request, SessionMiddleware)
    request = add_middleware_to_request(request, MessageMiddleware)
    request = add_middleware_to_request(request, AuthenticationMiddleware)
    request.session.save()

    return request

########################################################################################################################
# Investigation tests
########################################################################################################################
class InvestigationListViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@jacob.com', password='top_secret')

    def test_view_request_correct_permissions(self):
        """
        Check that the view class works so that all users can use (request only - using RequestFactory)
        """
        # This uses RequestFactory which means the request is separate to the client. Is meant to be better for unit
        # testing (according to "two scoops of Django 1.11"). But by design you can't get the messages from the
        # response. So using for the most part I have just been using the "self.client.get" and "self.client.post".
        request = self.factory.get(reverse('ilist'))

        request.user = AnonymousUser()
        request = add_middleware_to_request(request, SessionMiddleware)
        response = views_isa.InvestigationListView.as_view()(request)
        #
        # client acts as a fake website for the request
        response.client = Client()
        self.assertEqual(response.status_code, 200)


class InvestigationCreateViewTestCase(TestCase):
    urlkwargs = {}
    dictpost = {'name': 'test',
                     'description': 'test',
                     'slug': 'test',
                     'public': True}
    permission_code_name = 'add_investigation'
    urlname = 'icreate'
    error_privileges_msg = "User has insufficient privileges to create investigation"
    redirect_fail = 'ilist'
    redirect_pass = 'ilist'
    success_message = "Investigation created"
    view_class = views_isa.InvestigationCreateView
    model_class = models_isa.Investigation
    view_type = 'create'


    def setUp(self):

        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@jacob.com', password='top_secret')
        self.group, created = Group.objects.get_or_create(name='new_group')
        self.group.save()
        permission = Permission.objects.get(codename=self.permission_code_name)
        self.group.permissions.add(permission)
        self.group.save()


    def _check_privileges_response_failure(self, response):
        all_messages = [msg for msg in get_messages(response.wsgi_request)]

        # here's how you test the first message
        self.assertEqual(all_messages[0].tags, "error")
        self.assertEqual(all_messages[0].message, self.error_privileges_msg)
        self.assertRedirects(response, reverse(self.redirect_fail))

    def test_view_request_correct_permissions(self):
        """
        Check that view class works with correct permissions (request only - using RequestFactory) (get)
        """
        # This uses RequestFactory which means the request is separate to the client. Is meant to be better for unit
        # testing (according to "two scoops of Django 1.11"). But by design you can't get the messages from the
        # response. So using for the most part I have just been using the "self.client.get" and "self.client.post".
        request = self.factory.get(reverse(self.urlname, kwargs=self.urlkwargs))
        request = add_all_middleware_to_request(request)
        request = add_all_middleware_to_request(request)

        request.user = self.user
        request.user.groups.add(self.group)
        request.user.save()

        # RequestFactory loses the kwargs so need to give them again...
        # https://stackoverflow.com/questions/48580465/django-requestfactory-loses-url-kwargs
        response = self.view_class.as_view()(request, **self.urlkwargs)
        # client acts as a fake website for the request
        response.client = Client()

        self.assertEqual(response.status_code, 200)  # done without error

    def test_anonymous_user(self):
        """
        Check that anonymous user can't access (get)
        """
        # follow=True allows for the messages to be tested
        response = self.client.get(reverse(self.urlname, kwargs=self.urlkwargs), follow=True)

        # Check the tests
        self._check_privileges_response_failure(response)

    def test_loggedin_user(self):
        """
        Check that default logged-in user can't access (get)
        """
        self.client.force_login(self.user)
        # follow=True allows for the messages to be tested
        response = self.client.get(reverse(self.urlname, kwargs=self.urlkwargs), follow=True)
        self._check_privileges_response_failure(response)


    def test_get_loggedin_user_with_permissions(self):
        """
        Check that logged-in user with permissions can have access (get)
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse(self.urlname, kwargs=self.urlkwargs), follow=True)
        self.assertEqual(response.status_code, 200)  # done without error

    def test_post(self):
        """
        Check that logged-in user with permissions can access and submit (post)
        """
        if self.view_type == 'create':
            before_c = len(self.model_class.objects.all())

            # Login
            self.user.groups.add(self.group)
            self.user.save()

            self.client.force_login(self.user)

            response = self.client.post(reverse(self.urlname, kwargs=self.urlkwargs),
                                        self.dictpost, follow=True)

            self.assertRedirects(response, reverse(self.redirect_pass))

            all_messages = [msg for msg in get_messages(response.wsgi_request)]


            # Check message for user correct
            self.assertEqual(all_messages[0].tags, "success")
            self.assertEqual(all_messages[0].message, self.success_message)

            # Check item actually added
            self.assertEqual(len(self.model_class.objects.all()), before_c+1)

            # Check user assigned as owner
            self.assertEqual(self.model_class.objects.last().owner, self.user)

        elif self.view_type == 'update':

            self.user.groups.add(self.group)
            self.user.save()

            self.client.force_login(self.user)

            response = self.client.post(reverse(self.urlname, kwargs=self.urlkwargs),
                                        self.dictpost, follow=True)

            self.assertRedirects(response, reverse(self.redirect_pass))

            all_messages = [msg for msg in get_messages(response.wsgi_request)]

            # Check message for user correct
            self.assertEqual(all_messages[0].tags, "success")
            self.assertEqual(all_messages[0].message, self.success_message)

            post_object = self.model_class.objects.get(pk=self.urlkwargs['pk'])

            # Check item update correctly
            self.assertEqual(post_object.name, 'test_updated')

        elif self.view_type == 'delete':
            before_c = len(self.model_class.objects.all())

            self.user.groups.add(self.group)
            self.user.save()

            self.client.force_login(self.user)

            response = self.client.post(reverse(self.urlname, kwargs=self.urlkwargs),
                                        self.dictpost, follow=True)

            self.assertRedirects(response, reverse(self.redirect_pass))

            # Fors some reason the messages are handled differently for deleting
            # all_messages = [msg for msg in get_messages(response.wsgi_request)]
            # Check message for user correct
            # self.assertEqual(all_messages[0].tags, "success")
            # self.assertEqual(all_messages[0].message, self.success_message)

            # Check item deleted correctly
            self.assertEqual(len(self.model_class.objects.all()), before_c - 1)


class InvestigationUpdateViewTestCase(InvestigationCreateViewTestCase):
    permission_code_name = 'change_investigation'
    urlname = 'iupdate'
    error_privileges_msg = "User has insufficient privileges to update investigation"
    redirect_fail = 'ilist'
    redirect_pass = 'ilist'
    success_message = "Investigation updated"
    view_class = views_isa.InvestigationUpdateView
    model_class = models_isa.Investigation
    view_type = 'update'

    def setUp(self):
        super().setUp()
        obj_to_update = models_isa.Investigation(name='test1', description='test', slug='test1', public=True,
                                                 owner=self.user)
        obj_to_update.save()

        obj_to_not_update = models_isa.Investigation(name='test2', description='test', slug='test2', public=False,
                                                 owner=None)
        obj_to_not_update.save()

        self.urlkwargs = {'pk': obj_to_update.pk}
        self.dictpost = {'name': 'test_updated',
                         'description': 'test_updated',
                         'slug': 'test',
                         'public': True}

    def test_object_not_owned(self):
        """
        Check that a user cannot update/delete another users object (get)
        """
        pk = self.model_class.objects.get(name='test2').pk

        self.client.force_login(self.user)
        # follow=True allows for the messages to be tested
        response = self.client.get(reverse(self.urlname, kwargs={'pk': pk}), follow=True)
        self._check_privileges_response_failure(response)



class InvestigationDeleteViewTestCase(InvestigationUpdateViewTestCase):
    permission_code_name = 'delete_investigation'
    urlname = 'idelete'
    error_privileges_msg = "User has insufficient privileges to delete investigation"
    redirect_fail = 'ilist'
    redirect_pass = 'ilist'
    success_message = "Investigation deleted"
    view_class = views_isa.InvestigationDeleteView
    model_class = models_isa.Investigation
    view_type = 'delete'


########################################################################################################################
# Study tests
########################################################################################################################
class StudyCreateViewTestCase(InvestigationCreateViewTestCase):
    urlkwargs = {}
    permission_code_name = 'add_study'
    urlname = 'screate'
    error_privileges_msg = "User has insufficient privileges to create study"
    redirect_fail = 'ilist'
    redirect_pass = 'ilist'
    success_message = "Study created"
    view_class = views_isa.StudyCreateView
    model_class = models_isa.Study
    view_type = 'create'

    def setUp(self):
        super().setUp()
        i = models_isa.Investigation.objects.create(name='test', description='test', owner=self.user)
        i.save()

        self.dictpost = {'name': 'test',
                         'description': 'test',
                         'public': True,
                         'investigation': i.pk}


class StudyUpdateViewTestCase(InvestigationUpdateViewTestCase):
    permission_code_name = 'change_study'
    urlname = 'supdate'
    error_privileges_msg = "User has insufficient privileges to update study"
    redirect_fail = 'ilist'
    redirect_pass = 'ilist'
    success_message = "Study updated"
    view_class = views_isa.StudyUpdateView
    model_class = models_isa.Study
    view_type = 'update'

    def setUp(self):
        super().setUp()
        i = models_isa.Investigation.objects.create(name='test', description='test', owner=self.user)
        i.save()

        self.dictpost = {'name': 'test',
                         'description': 'test',
                         'public': True,
                         'investigation': i.pk}


        obj_to_update = models_isa.Study(name='test1', description='test',public=True, owner=self.user, investigation=i)
        obj_to_update.save()

        obj_to_not_update = models_isa.Study(name='test2', description='test', public=False, owner=None,investigation=i)
        obj_to_not_update.save()

        self.urlkwargs = {'pk': obj_to_update.pk}
        self.dictpost = {'name': 'test_updated',
                         'description': 'test_updated',
                         'public': True,
                         'investigation': i.pk}


class StudyDeleteViewTestCase(StudyUpdateViewTestCase):
    permission_code_name = 'delete_study'
    urlname = 'sdelete'
    error_privileges_msg = "User has insufficient privileges to delete study"
    redirect_fail = 'ilist'
    redirect_pass = 'ilist'
    success_message = "Study delete"
    view_class = views_isa.StudyDeleteView
    model_class = models_isa.Study
    view_type = 'delete'


########################################################################################################################
# Assay tests
########################################################################################################################
class AssayCreateViewTestCase(InvestigationCreateViewTestCase):
    urlkwargs = {}
    permission_code_name = 'add_assay'
    urlname = 'acreate'
    error_privileges_msg = "User has insufficient privileges to create assay"
    redirect_fail = 'ilist'
    redirect_pass = 'ilist'
    success_message = "Assay created"
    view_class = views_isa.AssayCreateView
    model_class = models_isa.Assay
    view_type = 'create'


    def setUp(self):
        super().setUp()
        i = models_isa.Investigation.objects.create(name='test', description='test', owner=self.user)
        i.save()

        s = models_isa.Study.objects.create(name='test', description='test', owner=self.user, investigation=i)
        s.save()

        self.dictpost = {'name': 'test',
                         'description': 'test',
                         'public': True,
                         'study': s.pk}

class AssayUpdateViewTestCase(InvestigationUpdateViewTestCase):
    permission_code_name = 'change_assay'
    urlname = 'aupdate'
    error_privileges_msg = "User has insufficient privileges to update assay"
    redirect_fail = 'ilist'
    redirect_pass = 'ilist'
    success_message = "Assay updated"
    view_class = views_isa.AssayUpdateView
    model_class = models_isa.Assay
    view_type = 'update'

    def setUp(self):
        super().setUp()
        i = models_isa.Investigation.objects.create(name='test', description='test', owner=self.user)
        i.save()

        s = models_isa.Study.objects.create(name='test', description='test', owner=self.user, investigation=i)
        s.save()

        self.dictpost = {'name': 'test',
                         'description': 'test',
                         'public': True,
                         'study': s.pk}

        obj_to_update = models_isa.Assay(name='test1', description='test',public=True, owner=self.user, study=s)
        obj_to_update.save()

        obj_to_not_update = models_isa.Assay(name='test2', description='test', public=False, owner=None,study=s)
        obj_to_not_update.save()

        self.urlkwargs = {'pk': obj_to_update.pk}
        self.dictpost = {'name': 'test_updated',
                         'description': 'test_updated',
                         'public': True,
                         'study': s.pk}


class AssayDeleteViewTestCase(AssayUpdateViewTestCase):
    permission_code_name = 'delete_assay'
    urlname = 'adelete'
    error_privileges_msg = "User has insufficient privileges to delete assay"
    redirect_fail = 'ilist'
    redirect_pass = 'ilist'
    success_message = "Assay delete"
    view_class = views_isa.AssayDeleteView
    model_class = models_isa.Assay
    view_type = 'delete'


########################################################################################################################
# Ontology term tests
########################################################################################################################
class OntologyTermCreateView(InvestigationCreateViewTestCase):
    urlkwargs = {}
    dictpost = {'name': 'test',
                'ontology_id': 'test1',
                'short_form': 'test1',
                'public': True}
    permission_code_name = 'add_ontologyterm'
    urlname = 'create_ontologyterm'
    error_privileges_msg = "User has insufficient privileges to create ontology term"
    redirect_fail = 'list_ontologyterm'
    redirect_pass = 'list_ontologyterm'
    success_message = "Ontology term created"
    view_class = views_isa.OntologyTermCreateView
    model_class = models_isa.OntologyTerm
    view_type = 'create'


class OntologyTermUpdateViewTestCase(InvestigationUpdateViewTestCase):
    permission_code_name = 'change_ontologyterm'
    urlname = 'update_ontologyterm'
    error_privileges_msg = "User has insufficient privileges to update ontology term"
    redirect_fail = 'list_ontologyterm'
    redirect_pass = 'list_ontologyterm'
    success_message = "Ontology term updated"
    view_class = views_isa.OntologyTermUpdateView
    model_class = models_isa.OntologyTerm
    view_type = 'update'

    def setUp(self):
        super().setUp()
        obj_to_update = models_isa.OntologyTerm(name='test1', description='test', public=True,
                                                short_form='test1',
                                                ontology_id='test1', owner=self.user)
        obj_to_update.save()

        obj_to_not_update = models_isa.OntologyTerm(name='test2', description='test', public=True,
                                                    short_form='test2',
                                                    ontology_id='test2')
        obj_to_not_update.save()

        self.urlkwargs = {'pk': obj_to_update.pk}
        self.dictpost = {'name': 'test_updated',
                         'short_form': 'test_updated',
                         'ontology_id': 'test_updated'}


class OntologyTermDeleteViewTestCase(OntologyTermUpdateViewTestCase):
    permission_code_name = 'delete_ontologyterm'
    urlname = 'delete_ontologyterm'
    error_privileges_msg = "User has insufficient privileges to delete ontology term"
    redirect_fail = 'list_ontologyterm'
    redirect_pass = 'list_ontologyterm'
    success_message = "Ontology term deleted"
    view_class = views_isa.OntologyTermDeleteView
    model_class = models_isa.OntologyTerm
    view_type = 'delete'


