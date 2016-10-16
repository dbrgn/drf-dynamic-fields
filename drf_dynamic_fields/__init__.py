import warnings


class DynamicFieldsMixin(object):
    """
    A serializer mixin that takes an additional `fields` argument that controls
    which fields should be displayed.
    """
    def __init__(self, *args, **kwargs):
        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

        # If the context is not set, return
        if not self.context:
            return

        # If the request is not passed in, warn and return
        if 'request' not in self.context:
            warnings.warn('Context does not have access to request')
            return

        # NOTE: drf test framework builds a request object where the query
        # parameters are found under the GET attribute.
        if hasattr(self.context['request'], 'query_params'):
            fields = self.context['request'].query_params.get('fields', None)
        elif hasattr(self.context['request'], 'GET'):
            fields = self.context['request'].GET.get('fields', None)
        else:
            warnings.warn('Request object does not contain query paramters')
            return

        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
