Dynamic Serializer Fields for Django REST Framework
===================================================

.. image:: https://secure.travis-ci.org/dbrgn/drf-dynamic-fields.png?branch=master
    :alt: Build status
    :target: http://travis-ci.org/dbrgn/drf-dynamic-fields

.. image:: https://img.shields.io/pypi/v/drf-dynamic-fields.svg
    :alt: PyPI Version
    :target: https://pypi.python.org/pypi/drf-dynamic-fields

.. image:: https://img.shields.io/pypi/dm/drf-dynamic-fields.svg?maxAge=3600
    :alt: PyPI Downloads
    :target: https://pypi.python.org/pypi/drf-dynamic-fields

.. image:: https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000
    :alt: License is MIT
    :target: https://github.com/dbrgn/drf-dynamic-fields/blob/master/LICENSE

This package provides a mixin that allows the user to dynamically select only a
subset of fields per resource.

Official version support:

- Django 1.11, 2.0, 2.1
- Supported REST Framework versions: 3.8, 3.9
- Python 2.7 (deprecated), 3.4+

NOTE: Python 2 support is deprecated and will be removed in version 0.4.


Scope
-----

This library is about filtering fields based on individual requests. It is
deliberately kept simple and we do not plan to add new features (including
support for nested fields). Feel free to contribute improvements, code
simplifications and bugfixes though! (See also: `#18
<https://github.com/dbrgn/drf-dynamic-fields/issues/18>`__)

If you need more advanced filtering features, maybe `drf-flex-fields
<https://github.com/rsinger86/drf-flex-fields>`_ could be something for you.


Installing
----------

::

    pip install drf-dynamic-fields

What It Does
------------

Example serializer:

.. sourcecode:: python

    class IdentitySerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
        class Meta:
            model = models.Identity
            fields = ('id', 'url', 'type', 'data')

A regular request returns all fields:

``GET /identities``

.. sourcecode:: json

    [
      {
        "id": 1,
        "url": "http://localhost:8000/api/identities/1/",
        "type": 5,
        "data": "John Doe"
      },
      ...
    ]

A query with the `fields` parameter on the other hand returns only a subset of
the fields:

``GET /identities/?fields=id,data``

.. sourcecode:: json

    [
      {
        "id": 1,
        "data": "John Doe"
      },
      ...
    ]

And a query with the `omit` parameter excludes specified fields.

``GET /identities/?omit=data``

.. sourcecode:: json

    [
      {
        "id": 1,
        "url": "http://localhost:8000/api/identities/1/",
        "type": 5
      },
      ...
    ]

You can use both `fields` and `omit` in the same request!

``GET /identities/?omit=data,fields=data,id``

.. sourcecode:: json

    [
      {
        "id": 1
      },
      ...
    ]


Though why you would want to do something like that is beyond this author.

It also works on single objects!

``GET /identities/1/?fields=id,data``

.. sourcecode:: json

    {
      "id": 1,
      "data": "John Doe"
    }

Usage
-----

When defining a serializer, use the ``DynamicFieldsMixin``:

.. sourcecode:: python

    from drf_dynamic_fields import DynamicFieldsMixin

    class IdentitySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        class Meta:
            model = models.Identity
            fields = ('id', 'url', 'type', 'data')

The mixin needs access to the ``request`` object. Some DRF classes like the
``ModelViewSet`` set that by default, but if you handle serializers yourself,
pass in the request through the context:

.. sourcecode:: python

    events = Event.objects.all()
    serializer = EventSerializer(events, many=True, context={'request': request})


Warnings
--------

If the request context does not have access to the request, a warning is
emitted::

   UserWarning: Context does not have access to request.

First, make sure that you are passing the request to the serializer context (see
"Usage" section).

There are some cases (e.g. nested serializers) where you cannot get rid of the
warning that way (see `issue 27 <https://github.com/dbrgn/drf-dynamic-fields/issues/27>`_).
In that case, you can silence the warning through ``settings.py``:

.. sourcecode:: python

   DRF_DYNAMIC_FIELDS = {
      'SUPPRESS_CONTEXT_WARNING': True,
   }


Testing
-------

To run tests, install Django and DRF and then run ``runtests.py``:

    $ python runtests.py


Credits
-------

- The implementation is based on `this
  <http://stackoverflow.com/a/23674297/284318>`__ StackOverflow answer. Thanks
  ``YAtOff``!
- The GitHub users ``X17`` and ``rawbeans`` provided improvements on `my gist
  <https://gist.github.com/dbrgn/4e6fc1fe5922598592d6>`__ that were incorporated
  into this library. Thanks!
- For other contributors, please see `Github contributor stats
  <https://github.com/dbrgn/drf-dynamic-fields/graphs/contributors>`__.


License
-------

MIT license, see ``LICENSE`` file.
