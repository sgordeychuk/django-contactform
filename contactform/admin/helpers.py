# -*- coding: utf-8 -*-
import datetime

from django.utils import six
from django.template.defaultfilters import date
from django.utils.encoding import force_text
from django.utils.translation import ugettext


def get_field_for_display(field_name, obj):
    try:
        value = getattr(obj, 'get_{0}_display'.format(field_name))()
    except AttributeError:
        value = getattr(obj, field_name)

    if value is None or six.text_type(value) == "None":
        value = ""

    if isinstance(value, bool):
        value = ugettext("Yes") if value else ugettext("No")
    elif isinstance(value, (datetime.date, datetime.datetime)):
        value = date(value, 'SHORT_DATE_FORMAT')
    return force_text(value)
