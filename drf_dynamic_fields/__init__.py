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
    def prevent_nested_processing(self) -> bool:
        """True when this serializer is not the root nor a root’s list-child."""
        return not (
            self is self.root
            or (self.parent is self.root and getattr(self.parent, "many", False))
        )

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

        if self.prevent_nested_processing:
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

        filter_fields = self.get_filter_fields(
            params.get("fields", None), level, source
        )
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

    def get_filter_fields(
        self, params, level, source, default=None, include_parent=True
    ):
        try:
            return params.split(",")
        except AttributeError:
            return default

    def get_omit_fields(self, params, level, source):
        return self.get_filter_fields(
            params, level, source, default=[], include_parent=False
        )


class NestedDynamicFieldsMixin(DynamicFieldsMixin):
    """A serializer mixin that extends DynamicFieldsMixin to allow nested serializers
    to filter their fields based on the original `fields` query parameter.

    Unlike the base mixin—which only applies filtering at the root serializer,
    this subclass:

    - Disables the `prevent_nested_processing` guard, allowing each level of nested
    serializer to apply field filtering independently.
    - Overrides `get_filter_fields` to slice the raw `fields` string
    down to exactly those names relevant at this serializer’s
    current nesting depth (using get_fields_for_level_and_prefix).
    - `get_filter_fields` first delegates to the super method for splitting
      the comma‐separated string, then calls a helper that:
        • Selects only the fields that are nested under this serializer's path in
          the hierarchy
        • Returns direct children at depth `level + 1`
    """

    @property
    def prevent_nested_processing(self):
        return False

    def get_filter_fields(
        self, params, level, source, default=None, include_parent=True
    ):
        """
        Parse the raw `fields` parameter and return the subset of fields
        that apply at this serializer’s nesting level under the given
        source prefix.
        """
        fields = super().get_filter_fields(
            params, level, source, default, include_parent
        )
        return get_fields_for_level_and_prefix(
            fields, level, source, default=default, include_parent=include_parent
        )


def get_source_path(serializer) -> str:
    """Recursively walks up the serializer tree to build the nested field path."""
    parent = getattr(serializer, "parent", None)
    if not parent:
        return ""
    parent_path = get_source_path(parent)
    name = getattr(serializer, "field_name", None)
    if not name:
        return parent_path
    return f"{parent_path}__{name}" if parent_path else name


def get_fields_for_level_and_prefix(
    fields_list, level, source, include_parent, default
):
    """Extract the field names relevant to a specific nesting depth
    from a list of double‑underscore lookup strings.
    """
    if not fields_list:
        return default

    prefix = source.split("__") if source else []
    allowed = set()
    for f in fields_list:
        parts = f.split("__")

        if parts[:level] != prefix:
            continue

        if len(parts) <= level + 1:
            allowed.add(parts[-1])
            continue

        if len(parts) > level + 1 and include_parent:
            # include parent field to ensure nesting proceeds
            allowed.add(parts[level])
            continue


    # If the only allowed fields are exactly the prefix itself,
    # fall back to default
    if allowed == set(prefix):
        return default

    return allowed


def compute_level(serializer) -> int:
    """Recursively count how many ancestors of `serializer` are not
    ListSerializer instances. Stops when parent is None.
    """
    parent = getattr(serializer, "parent", None)
    if parent is None:
        # base case, reached the top
        return 0

    # if this immediate parent is a ListSerializer, don’t count it, otherwise 1
    this_level = 0 if isinstance(parent, serializers.ListSerializer) else 1

    # recurse on the parent itself
    return this_level + compute_level(parent)
