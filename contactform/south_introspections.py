from django.conf import settings
from django.db.models.fields import NOT_PROVIDED

from .fields import PickledObjectField


rules = [
            (
                (PickledObjectField, ),
                [],
                {"null": ["null", {"default": False}],
                "blank": ["blank", {"default": False, "ignore_if":"primary_key"}],
                "primary_key": ["primary_key", {"default": False}],
                "max_length": ["max_length", {"default": None}],
                "unique": ["_unique", {"default": False}],
                "db_index": ["db_index", {"default": False}],
                "default": ["default", {"default": NOT_PROVIDED}],
                "db_column": ["db_column", {"default": None}],
                "db_tablespace": ["db_tablespace", {"default": settings.DEFAULT_INDEX_TABLESPACE}],
                },
            ),
        ]


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules(rules, ["^contactform\.fields\.PickledObjectField$"])
