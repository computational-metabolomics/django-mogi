import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-mogi',
    version='0.0.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.11.15',
        'django-galaxy',
        'django-misa',
    ],
    license='GNU License',  # example license
    description='Metabolomics Organisation with Galaxy and ISA',
    long_description=README,
    url='https://mogi.readthedocs.io',
    author='Thomas N lawson',
    author_email='thomas.nigel.lawson@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
