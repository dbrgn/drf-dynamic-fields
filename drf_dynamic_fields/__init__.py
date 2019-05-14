"""
Mixin to dynamically select only a subset of fields per DRF resource.
"""
import warnings

from django.conf import settings
from rest_framework.serializers import ListSerializer, ModelSerializer


class DynamicFieldsMixin(object):
    """
    A serializer mixin that takes an additional `fields` argument that controls
    which fields should be displayed.
    """

    @property
    def fields(self):
        """
        Filters the fields according to the `fields` query parameter.

        A blank `fields` parameter (?fields) will remove all fields. Not
        passing `fields` will pass all fields individual fields are comma
        separated (?fields=id,name,url,email).

        """
        fields = super(DynamicFieldsMixin, self).fields

        if not hasattr(self, '_context'):
            # We are being called before a request cycle
            return fields

        # Only filter if this is the root serializer, or if the parent is the
        # root serializer with many=True
        is_list_serializer = getattr(self, 'many', False)
        if is_list_serializer:
            return fields

        try:
            request = self.context['request']
        except KeyError:
            conf = getattr(settings, 'DRF_DYNAMIC_FIELDS', {})
            if not conf.get('SUPPRESS_CONTEXT_WARNING', False) is True:
                warnings.warn('Context does not have access to request. '
                              'See README for more information.')
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
            filter_fields = []

        try:
            omit_fields = params.get('omit', None).split(',')
        except AttributeError:
            omit_fields = []

        # Drop any fields that are not specified in the `fields` argument.
        existing = set(fields.keys())
        if filter_fields or omit_fields:
            # calculate the traversed path in bottom to top style
            current = self
            reverse_path = final_filter_fields = final_omit_fields = []
            while getattr(current, 'parent_field', None):
                reverse_path.append(current.field_name)
                current = current.parent_field
            current.field_name and reverse_path.append(current.field_name)
            # reversing the calculated path to get the result in top to bottom style
            actual_path = reversed(reverse_path)
            # creating the lookup string for the calculated path
            actual_path_str = '__'.join(actual_path)
            # current_depth
            current_depth = len(reverse_path)
            if filter_fields:
                # apply field filtering only if field query params are provided
                for filter_field in filter_fields:
                    # split the look_up string with the separator
                    filter_field_path = filter_field.split('__')
                    # check if there is a partial/full match of filter_field passed in url with current path
                    # or vice versa
                    if filter_field.startswith(actual_path_str) or actual_path_str.startswith(filter_field):
                        # get the field matched with current level if not then skip filtering and break
                        if current_depth < len(filter_field_path):
                            final_filter_fields.append(filter_field_path[current_depth])
                        else:
                            final_filter_fields = fields
                            break
                filter_fields = final_filter_fields

            if omit_fields:
                # apply omit filtering only if omit query params are provided
                for omit_field in omit_fields:
                    # split the look_up string with the separator
                    omit_field_path = omit_field.split('__')
                    # check if there is a full match of filter_field excluding it's deepest lookup passed in url
                    # with current path
                    if len(omit_field_path) == current_depth + 1 and omit_field.startswith(actual_path_str):
                        # get the omit field matched with current depth level
                        final_omit_fields.append(omit_field_path[current_depth])
                omit_fields = final_omit_fields

        allowed = set(filter(None, filter_fields)) or existing

        # omit fields in the `omit` argument.
        omitted = set(filter(None, omit_fields))

        for field in existing:

            if field not in allowed:
                fields.pop(field, None)

            if field in omitted:
                fields.pop(field, None)

        return fields

    def to_representation(self, instance):
        fields = super(DynamicFieldsMixin, self).fields
        for child_name, child in fields.iteritems():
            # checking for nested relationships
            if isinstance(child, ListSerializer) or isinstance(child, ModelSerializer):
                current_child = child if isinstance(child, ModelSerializer) else child.child
                # for the child set it's field_name and a reference to it's parent
                setattr(current_child, 'parent_field', self)
        return super(DynamicFieldsMixin, self).to_representation(instance)
