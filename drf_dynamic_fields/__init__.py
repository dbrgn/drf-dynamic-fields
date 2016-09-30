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

        fields = self.context['request'].query_params.get('fields', None)
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
