Dynamic Serializer Fields for Django REST Framework
===================================================

.. image:: https://img.shields.io/pypi/dm/drf-dynamic-fields.svg
    :alt: PyPI Downloads
    :target: https://pypi.python.org/pypi/drf-dynamic-fields

.. image:: https://img.shields.io/codacy/grade/1a91ba7fd0db4724a722bce1c1a646d6/master.svg?maxAge=2592000
    :alt: Codacy grade
    :target: 1a91ba7fd0db4724a722bce1c1a646d6

.. image:: https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000
    :alt: License is MIT
    :target: https://github.com/dbrgn/drf-dynamic-fields/blob/master/LICENSE

This package provides a mixin that allows the user to dynamically select only a
subset of fields per resource.


What It Does
------------

Example serializer:

.. sourcecode:: python

    class IdentitySerializer(serializers.HyperlinkedModelSerializer):
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


Credits
-------

- The implementation is based on `this
  <http://stackoverflow.com/a/23674297/284318>`__ StackOverflow answer. Thanks
  ``YAtOff``!
- The GitHub users ``X17`` and ``rawbeans`` provided improvements on `my gist
  <https://gist.github.com/dbrgn/4e6fc1fe5922598592d6>`__ that were incorporated
  into this library. Thanks!


License
-------

MIT license, see ``LICENSE`` file.
