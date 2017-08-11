"""
Mixin to dynamically select only a subset of fields per DRF resource.
"""
import re
import warnings

_nested_field_pattern = re.compile("__")


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

        current_path = self._build_current_path(self.field_name or "", self.parent)
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
            filter_fields = self._get_params_for_include_path(current_path, params.get('fields', None).split(','))
        except AttributeError:
            filter_fields = None

        try:
            omit_fields = self._get_params_for_omit_path(current_path, params.get('omit', None).split(','))
        except AttributeError:
            omit_fields = []

        # Drop any fields that are not specified in the `fields` argument.
        existing = set(fields.keys())
        if (len(current_path) == 0 and filter_fields is None) or (len(current_path) > 0 and not filter_fields):
            # no fields param given, don't filter.
            allowed = existing
        else:
            allowed = set(filter(None, filter_fields))

        # omit fields in the `omit` argument.
        omitted = set(filter(None, omit_fields))

        for field in existing:

            if field not in allowed:
                fields.pop(field, None)

            if field in omitted:
                fields.pop(field, None)

        return fields

    def _get_params_for_include_path(self, current_path, field_names):
        path = current_path if len(current_path) == 0 else current_path + "__"
        current_fields_pattern = re.compile("^"+re.escape(path)+"(.+?)((?:__).+)?$")
        path_params = set()

        for name in field_names:
            match = current_fields_pattern.match(name)
            if match:
                path_params.add(match.group(1))

        return path_params

    def _get_params_for_omit_path(self, current_path, field_names):
        path = current_path if len(current_path) == 0 else current_path + "__"
        nested = len(path) > 0
        path_params = set()

        for name in field_names:
            if not nested or name.startswith(path):
                field = name if not nested else name.split(path, 1)[1]
                if not _nested_field_pattern.search(field):
                    path_params.add(field)

        return path_params

    def _build_current_path(self, path, parent):
        if not parent:
            return path

        if parent.field_name:
            new_path = parent.field_name
            if path:
                new_path = new_path + "__" + path
        else:
            new_path = path

        return self._build_current_path(new_path, parent.parent)
