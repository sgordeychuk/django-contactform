# -*- coding: utf-8 -*-
from django.db import models

try:
    import cPickle as pickle
except ImportError:
    import pickle


class PickledObjectField(models.Field):
    """
    this version of pickled object does not work for pickling a single string. it must be some object, dict, list...
    """

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        if isinstance(value, basestring) and not value in ('', u''):
            # If the value is a sting and an error is raised in de-pickling
            # it should be allowed to propogate.
            return pickle.loads( str(value).decode('base64') )
        # its already whatever was pickled
        return value

    def get_prep_value(self, value):
        return pickle.dumps(value).encode('base64')

    def get_internal_type(self): 
        return 'TextField'
