=====
mogi
=====

Metabolome Organisation with Galaxy and ISA

Detailed documentation is in the "docs" directory (todo)

Quick start
-----------

1. Add "gfiles" to your INSTALLED_APPS setting like this (note that this app depends on gfiles, metab, misa and galaxy)::

    INSTALLED_APPS = [
        ...
        'gfiles',
        'metab',
        'misa',
        'galaxy',
        'mogi'
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('mogi/', include('mogi.urls')),

3. Run `python manage.py migrate` to create the polls models.
