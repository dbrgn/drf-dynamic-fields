"""
Mixin to dynamically select only a subset of fields per DRF resource.
"""
import warnings


class DynamicFieldsMixin(object):
    """
    A serializer mixin that takes an additional `fields` argument that controls
    which fields should be displayed.
    """

    @property
    def fields(self):
        """
        Filters the fields according to the `fields` query parameter.

        a blank `fields` parameter (?fields) will remove all fields.
        not passing `fields` will pass all fields
        individual fields are comma separated (?fields=id,name,url,email)
        """
        fields = super(DynamicFieldsMixin, self).fields

        if not hasattr(self, '_context'):
            # we are being called before a request cycle.
            return fields

        try:
            request = self.context['request']
        except KeyError:
            warnings.warn('Context does not have access to request')
            return fields

        # NOTE: drf test framework builds a request object where the query
        # parameters are found under the GET attribute.
        params = getattr(
            request, 'query_params', getattr(request, 'GET', None)
        )
        if params is None:
            warnings.warn('Request object does not contain query paramters')

        try:
            filter_fields = params.get('fields', None).split(',')
        except AttributeError:
            return fields

        # Drop any fields that are not specified in the `fields` argument.
        allowed = set(filter(None, filter_fields))
        existing = set(fields.keys())

        for field in existing - allowed:
            fields.pop(field)

        return fields
