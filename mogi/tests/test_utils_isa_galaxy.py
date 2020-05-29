# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals, print_function
#
# from django.test import TestCase
#
# from django.contrib.auth import get_user_model
#
# import subprocess
# import requests
#
#
# def setup_galaxy():
#     try:
#         request = requests.get('http://127.0.0.1:9090')
#         if request.status_code == 200:
#             return 0
#     except requests.exceptions.ConnectionError as e:
#         print(e)
#
#     docker_run = """
#         docker run -d -p 9090:80 -p 9022:22 -p 9021:21 \
#             -e GALAXY_CONFIG_ADMIN_USERS=jacob@jacob.com \
#             -e GALAXY_CONFIG_ALLOW_USER_CREATION=True \
#             -e GALAXY_CONFIG_LIBRARY_IMPORT_DIR=True \
#             -e GALAXY_CONFIG_USER_LIBRARY_IMPORT_DIR=True \
#             -e GALAXY_CONFIG_ALLOW_LIBRARY_PATH_PASTE=True \
#             -e GALAXY_CONFIG_CONDA_ENSURE_CHANNELS=tomnl,iuc,bioconda,conda-forge,defaults,r \
#             workflow4metabolomics/galaxy-workflow4metabolomics
#         """
#     print(docker_run)
#     subprocess.call(docker_run, shell=True)
#
#     import time
#     timeout = time.time() + 60 * 5  # 5 minutes from now
#     while True:
#
#         if time.time() > timeout:
#             break
#         else:
#             try:
#                 request = requests.get('http://127.0.0.1:9090')
#                 if request.status_code == 200:
#                     break
#                 else:
#                     print('Web site does not exist yet')
#             except requests.exceptions.ConnectionError as e:
#                 print(e)
#         time.sleep(5)
#
#
# class GalaxyInstanceCreateTestCase(TestCase):
#     urls = 'galaxy.test_urls'
#     def setUp(self):
#         setup_galaxy()
#         User = get_user_model()
#         self.user = User.objects.create_user(username='jacob', email='jacob@jacob.com', password='top_secret')
#
#     def test_galaxy_isa_upload_datalib(self):
#         """
#         Test to check if a guest user is redirect to the login page
#         """
#         print('CHECK')
