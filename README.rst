====================
django-mogi
====================

Metabolomics organisation with Galaxy and ISA.

Used to create `DMAdb <https://mogi.readthedocs.io/en/latest/>`__, see `ReadTheDocs (DMAdb) <https://dmadb.readthedocs.io/en/latest/getting-started.html>`__ for documentation.

Previous documentation can be found at `ReadTheDocs (legacy) <https://mogi.readthedocs.io/en/latest/>`__.

PyPI Archive Notice
-------------------

This package is no longer updated on PyPI.

For current code and updates, use this `GitHub repository <https://github.com/computational-metabolomics/django-mogi>`__.

Quick start
-----------

1. Add "mogi" and django application dependencies to your INSTALLED_APPS setting like this (mogi should come before galaxy and gfiles)::


    INSTALLED_APPS = [
        ...
        'mogi',
        'galaxy',
        'gfiles',

        'django_tables2',
        'django_tables2_column_shifter',
        'django_filters',
        'bootstrap3',
        'django_sb_admin',
        'dal',
        'dal_select2',
    ]

2. Include the URLconf in your project urls.py like this::


    url(r'^', include('gfiles.urls')),
    url('mogi/', include('mogi.urls')),
    url('mbrowse/', include('mbrowse.urls')),
    url('misa/', include('misa.urls')),
    url('galaxy/', include('galaxy.urls')),


3. Run `python manage.py migrate` to create the mogi models.

4. Start the development server and visit http://127.0.0.1:8000/