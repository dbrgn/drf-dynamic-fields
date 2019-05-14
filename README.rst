Dynamic Serializer Fields for Django REST Framework
===================================================

This package provides a mixin that allows the user to dynamically select only a
subset of fields per resource and also perform nested lookups for filtering in related_objects/relationships.

Official version support:

- Django 1.11, 2.0, 2.1
- Supported REST Framework versions: 3.8, 3.9
- Python 2.7 (deprecated), 3.4+



Installing
----------

::

    copy the source file :P

What It Does
------------

Example serializer:

.. sourcecode:: python

    class IdentitySerializer(DynamicFlexFieldsMixin, serializers.HyperlinkedModelSerializer):
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
        "data": "John Doe",
        "info": {
            "city": {
                "name": "Hyderabad",
                "radius": 1556,
                "field1": "value1",
                "field2": "value2",
                "field3": "value3",
                "field4": "value4"
            },
            "country": {
                "name": "India",
                "population": 133,
                "field1": "value1",
                "field2": "value2",
                "field3": "value3",
                "field4": "value4"
            }
        }
      },
      ...
    ]

A query with the `fields` parameter on the other hand returns only a subset of
the fields:

``GET /identities/?fields=id,data,info``

.. sourcecode:: json

    [
      {
        "id": 1,
        "data": "John Doe",
        "info": {
            "city": {
                "name": "Hyderabad",
                "radius": 1556,
                "field1": "value1",
                "field2": "value2",
                "field3": "value3",
                "field4": "value4"
            },
            "country": {
                "name": "India",
                "population": 133,
                "field1": "value1",
                "field2": "value2",
                "field3": "value3",
                "field4": "value4"
            }
         }
      },
      ...
    ]

Also you can filter by nested relationships using '__' to pass through child fields:

``GET /identities/?fields=id,data,info__city__name,info__country__name

.. sourcecode:: json

    [
      {
        "id": 1,
        "data": "John Doe",
        "info": {
            "city": {
                "name": "Hyderabad"
            },
            "country": {
                "name": "India"
            }
        }
      },
      ...
    ]

And a query with the `omit` parameter excludes specified fields also supports nested lookups just like that of fields.

``GET /identities/?omit=data,info`

.. sourcecode:: json

    [
      {
        "id": 1,
        "url": "http://localhost:8000/api/identities/1/",
        "type": 5
      },
      ...
    ]




It also works on single objects!

``GET /identities/1/?fields=id,data``

.. sourcecode:: json

    {
      "id": 1,
      "data": "John Doe"
    }

Usage
-----

When defining a serializer, use the ``DynamicFlexFieldsMixin``:

.. sourcecode:: python

    from drf_dynamic_fields import DynamicFlexFieldsMixin

    class IdentitySerializer(DynamicFlexFieldsMixin, serializers.ModelSerializer):
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


Scope
-----

This library is about filtering fields passed via url query params which also supports nested lookups filtering,it is based on https://github.com/dbrgn/drf-dynamic-fields. drf-dynamic-fields was deliberately kept simple and we do not plan to add new features, so i've added support for nested lookups taking drf-dynamic-fields as source/inspiration


Testing
-------

To run tests, install Django and DRF and then run ``runtests.py``, haven't added any additional tests for nested lookups :

    $ python runtests.py


Credits
-------

- The implementation is based on `this
  https://github.com/dbrgn/drf-dynamic-fields . Thanks
  ``Danilo Bargen``!
- Credits to Martin Garrix for his music which bought me enough motivation to implement this


License
-------

MIT license, see ``LICENSE`` file.
