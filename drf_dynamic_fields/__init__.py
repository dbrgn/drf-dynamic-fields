"""
Mixin to dynamically select only a subset of fields per DRF resource.
"""

import warnings

from django.conf import settings
from django.utils.functional import cached_property

from rest_framework import serializers


class DynamicFieldsMixin(object):
    """
    A serializer mixin that takes an additional `fields` argument that controls
    which fields should be displayed.
    """

    @property
    def is_preventing_nested_serializers(self):
        is_root = self.root == self
        parent_is_list_root = self.parent == self.root and getattr(
            self.parent, "many", False
        )

        return not (is_root or parent_is_list_root)

    @cached_property
    def fields(self):
        """
        Filters the fields according to the `fields` query parameter.

        A blank `fields` parameter (?fields) will remove all fields. Not
        passing `fields` will pass all fields individual fields are comma
        separated (?fields=id,name,url,email).

        """
        fields = super(DynamicFieldsMixin, self).fields

        if not hasattr(self, "_context"):
            # We are being called before a request cycle
            return fields

        if self.is_preventing_nested_serializers:
            return fields

        try:
            request = self.context["request"]
        except KeyError:
            conf = getattr(settings, "DRF_DYNAMIC_FIELDS", {})
            if not conf.get("SUPPRESS_CONTEXT_WARNING", False) is True:
                warnings.warn(
                    "Context does not have access to request. "
                    "See README for more information."
                )
            return fields

        # NOTE: drf test framework builds a request object where the query
        # parameters are found under the GET attribute.
        params = getattr(request, "query_params", getattr(request, "GET", None))
        if params is None:
            warnings.warn("Request object does not contain query parameters")

        source = get_source_path(self)
        level = compute_level(self)

        filter_fields = self.get_filter_fields(params.get("fields", None), level, source)
        omit_fields = self.get_omit_fields(params.get("omit", None), level, source)

        # Drop any fields that are not specified in the `fields` argument.
        existing = set(fields.keys())
        if filter_fields is None:
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

    def get_filter_fields(self, params, level, source, default=None, include_parent=True):
        try:
            return params.split(",")
        except AttributeError:
            return default


    def get_omit_fields(self, params, level, source):
        return self.get_filter_fields(params, level, source, default=[], include_parent=False)


class NestedDynamicFieldsMixin(DynamicFieldsMixin):

    @property
    def is_preventing_nested_serializers(self):
        return False

    def get_filter_fields(self, params, level, source, default=None, include_parent=True):
        fields = super().get_filter_fields(params, level, source, default, include_parent)
        return get_fields_for_level_and_prefix(
                fields,
                level,
                source,
                default=default,
                include_parent=include_parent
            )

def get_source_path(serializer):
    parts = []
    current = serializer
    while current.parent is not None:
        if hasattr(current, 'field_name'):
            parts.insert(0, current.field_name)
        current = current.parent
    return "__".join(filter(None, parts))

def get_fields_for_level_and_prefix(fields_list, level, source, include_parent, default):
    if not fields_list:
        return default

    allowed = set()
    prefix = source.split("__") if source else []
    for f in fields_list:
        parts = f.split("__")
        if parts[:level] != prefix:
            continue
        if len(parts) <= level + 1:
            allowed.add(parts[-1])
        elif len(parts) > level + 1 and include_parent:
            # include parent field to ensure nesting proceeds
            allowed.add(parts[level])
    if set(prefix) == allowed:
        return default
    return allowed

def compute_level(serializer):
    level = 0
    current = serializer
    while hasattr(current, 'parent') and current.parent is not None:
        parent = current.parent

        # Handle ListSerializer by skipping over it
        if isinstance(parent, serializers.ListSerializer):
            current = parent.parent
        else:
            current = parent

        level += 1
    return level
