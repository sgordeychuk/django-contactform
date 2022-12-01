from importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

__loaded = False

DEFAULT_FIELD_TYPES = [
    ('django.forms.CharField', _('character field')),
    ('django.forms.EmailField', _('email field')),
    ('django.forms.BooleanField', _('checkbox')),
    ('django.forms.ChoiceField', _('choice field')),
    ('django.forms.FileField', _('file field')),
    ('contactform.forms.EmailWithConfirmation', _('send confirmation to user email field')),
    ('contactform.forms.EmailWithConfirmationCheckbox', _('send confirmation to user checkbox')),
]

FIELD_TYPES = list(DEFAULT_FIELD_TYPES)

if hasattr(settings, 'CONTACTFORM_CUSTOM_FIELD_TYPES'):
    FIELD_TYPES += settings.CONTACTFORM_CUSTOM_FIELD_TYPES

DEFAULT_WIDGET_TYPES = [
    ('django.forms.Textarea', _('textarea')),
    ('django.forms.PasswordInput', _('password input')),
    ('django.forms.RadioSelect', _('radio buttons')),
]

WIDGET_TYPES = list(DEFAULT_WIDGET_TYPES)

if hasattr(settings, 'CONTACTFORM_CUSTOM_WIDGET_TYPES'):
    WIDGET_TYPES += settings.CONTACTFORM_CUSTOM_WIDGET_TYPES


class TitlePseudoField: pass


def load_class(klass_string):
    if not klass_string:
        return None
    if klass_string == '__title__':
        return TitlePseudoField
    module, attr = klass_string.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing contactform field type module %s: "%s"' % (module, e))
    try:
        klass = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" contactform field type' % (module, attr))
    return klass
