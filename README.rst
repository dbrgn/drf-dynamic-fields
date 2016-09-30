Dynamic Serializer Fields for Django REST Framework
===================================================

This package provides a mixin that allows the user to select only a sbuset of
fields per resource.

Example
-------

Serializer::

    class IdentitySerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = models.Identity
            fields = ('id', 'url', 'type', 'data')

A regular request returns all fields:

``GET /identities``

::

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

::

    [
      {
        "id": 1,
        "data": "John Doe"
      },
      ...
    ]

License
-------

MIT license, see ``LICENSE`` file.
