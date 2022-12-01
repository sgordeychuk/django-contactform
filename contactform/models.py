from django import forms
from django.conf import settings
from django.db import models
from django.forms.widgets import HiddenInput
from django.template.defaultfilters import filesizeformat, slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.utils.html import strip_tags
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.forms import BooleanField, ChoiceField, FileField

from contactform.fields import PickledObjectField
from contactform.settings import MAX_FILE_SIZE
from contactform.field_loader import WIDGET_TYPES, FIELD_TYPES, load_class, TitlePseudoField
from contactform import south_introspections

from cms.models import CMSPlugin, Page


def _site_contact_email():
    if 'siteinfo' in settings.INSTALLED_APPS:
        try:
            from siteinfo.models import SiteSettings

            site_contact_email = SiteSettings.objects.get_current().email
        except:
            site_contact_email = 'n/a'
    else:
        site_contact_email = 'n/a'
    return site_contact_email


site_contact_email = lazy(_site_contact_email, unicode)
site_managers = u','.join([manager[1] for manager in settings.MANAGERS])


class ContactForm(models.Model):
    language = models.CharField(_('language'), max_length=15, choices=settings.LANGUAGES)
    name = models.CharField(_('name'), max_length=255)
    title = models.CharField(_('title'), max_length=255, null=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    submit_label = models.CharField(
        verbose_name=_('submit label'),
        max_length=30,
        blank=True,
        help_text=u'%s: "%s"' % (_('default'), _('submit')),
    )
    success_message = models.TextField(
        verbose_name=_('success message'),
        blank=True,
    )
    recipients = models.ManyToManyField('Recipient', verbose_name=_('recipients'))
    cc_managers = models.BooleanField(
        verbose_name=_('CC to managers'),
        help_text=_('Check to send a copy to the site managers (%s).') % site_managers
    )
    cc_site_contact = models.BooleanField(verbose_name=_('CC to site contact'))
    has_captcha = models.BooleanField(
        verbose_name=_("has a captcha"),
        default=False,
        help_text=_("Should the user be required to fill up a captcha to verify he is human?")
    )
    has_recaptcha = models.BooleanField(
        verbose_name=_("has a reRECAPTCHA"),
        default=False,
        help_text=_("Use Google reCAPTCHA to defeat bots. (Will disable plain CAPTCHA if applied.)")
    )
    css_class = models.CharField(_('CSS class'), null=True, blank=True, max_length=255)
    success_page = models.ForeignKey(Page, null=True, blank=True, on_delete=models.SET_NULL)
    notification_email_subject = models.CharField(
        verbose_name=_('notification email subject'),
        max_length=200,
        blank=True
    )
    notification_email_body = models.TextField(
        verbose_name=_('notification email body'),
        blank=True
    )
    created_by = models.ForeignKey(to='auth.User', null=True, blank=True, editable=False)


    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.language)


    def get_form_base_class(self):
        from .forms import ContactFormFormBase

        return ContactFormFormBase


    def get_form_class(self, unique_form_id=None):
        """
        Constructs a real django.forms Form() class out of this ContactForm instance and provides
        functionality for handling form submission.
        """

        ContactFormFormBase = self.get_form_base_class()

        attrs = {
            'model_instance_id': self.id,
            'contactform_id': forms.CharField(initial=self.pk, widget=HiddenInput),
            'model': self.__class__,
        }

        if unique_form_id:
            attrs['unique_form_id'] = forms.CharField(initial=unique_form_id, widget=HiddenInput)

        count = -1

        for field in self.field_set.all().order_by("position"):
            count += 1

            if field.widget == '':
                widget = None
            else:
                widget = load_class(field.widget)

            label = field.label
            initial = field.initial

            field_class = load_class(field.field_type)

            kwargs = {
                'required': field.required,
                'widget': widget,
            }

            if field_class is TitlePseudoField:
                continue
            elif issubclass(field_class, BooleanField):
                checked_values = ['1', 'checked', 'yes', 'true']
                initial = field.initial and field.initial.lower() in checked_values
            elif issubclass(field_class, ChoiceField):
                txt_choices = field.choices.replace('\n', '').replace('\r', '').split(';')
                choices = []
                for txt in txt_choices:
                    txt = txt.strip()
                    if txt != '':
                        choices.append((slugify(strip_tags(txt)), mark_safe(txt)))
                try:
                    initial = choices[int(field.initial.strip()) - 1][0]
                except:
                    initial = None

                if field.empty_label:
                    choices.insert(0, ('', field.empty_label))

                kwargs['choices'] = choices
            elif issubclass(field_class, FileField):
                label = u'%s (%s %s)' % (label, _('max.'), filesizeformat(MAX_FILE_SIZE))

            form_field = field_class(initial=initial, label=label, **kwargs)

            if field.css_class:
                form_field.widget.attrs['class'] = field.css_class
            attrs["%s_%s" % (slugify(field.label), count)] = form_field

        has_captcha = 'captcha' in settings.INSTALLED_APPS and self.has_captcha
        attrs['has_captcha'] = has_captcha

        if has_captcha:
            from captcha.fields import CaptchaField

            attrs['captcha'] = CaptchaField(label=_("Enter the characters showed in the image below."))

        has_recaptcha = 'snowpenguin.django.recaptcha2' in settings.INSTALLED_APPS and self.has_recaptcha
        attrs['has_recaptcha'] = has_recaptcha

        if has_recaptcha:
            from snowpenguin.django.recaptcha2.fields import ReCaptchaField
            from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

            attrs['captcha'] = ReCaptchaField(widget=ReCaptchaWidget(explicit=True))

        form_class = type(smart_str(slugify(self.name) + 'Form'), (ContactFormFormBase,), attrs)
        return form_class

    def get_submit_label(self):
        return self.submit_label or _('submit')

    class Meta:
        verbose_name = _('contact form')
        verbose_name_plural = _('contact forms')


class FormField(models.Model):
    form = models.ForeignKey(
        ContactForm,
        related_name='field_set',
        on_delete=models.PROTECT,
    )
    label = models.CharField(_('label'), max_length=255)
    field_type = models.CharField(_('field type'), choices=FIELD_TYPES, max_length=100)
    widget = models.CharField(_('widget'), choices=WIDGET_TYPES, max_length=50, blank=True)
    required = models.BooleanField(_('required'))
    initial = models.CharField(_('initial'), max_length=64, blank=True)
    empty_label = models.CharField(_('empty label'), max_length=64, blank=True)
    choices = models.TextField(_('choices'), null=True, blank=True,
                               help_text=_('enter choices divided by a semicolon (;) for ChoiceFields'))
    css_class = models.CharField(_('CSS class'), null=True, blank=True, max_length=255)
    position = models.IntegerField(_('position'), default=1)

    def __unicode__(self):
        return u'%s, %s field %s' % (self.label, self.field_type, self.widget)

    class Meta:
        ordering = ('position',)

    def get_label(self):
        return self.label


class Recipient(models.Model):
    name = models.CharField(_('name'), max_length=100, blank=True)
    email = models.EmailField(_('email'))
    added_by = models.ForeignKey(to='auth.User', null=True, blank=True, editable=False)

    def __unicode__(self):
        return u'%s, %s' % (self.name, self.email)

    class Meta:
        verbose_name = _('recipient')
        verbose_name_plural = _('recipients')


class ContactFormSubmission(models.Model):
    form = models.ForeignKey(ContactForm, on_delete=models.PROTECT)
    submitted_at = models.DateTimeField(_('submit date/time'), auto_now_add=True)
    sender_ip = models.CharField(_('sender IP address'), max_length=40)
    form_url = models.URLField(_('form URL'))
    language = models.CharField(_('language'), default='unknown', max_length=255)
    form_data = models.TextField(_('form data'), null=True, blank=True)
    form_data_pickle = PickledObjectField(
        verbose_name=_('form data pickle'),
        null=True,
        blank=True,
        editable=False,
    )

    def __unicode__(self):
        return u'%s' % (self.form)

    class Meta:
        ordering = ("-submitted_at",)
        verbose_name = _('contact form submission')
        verbose_name_plural = _('contact form submissions')

    def get_form_data(self):
        return self.form_data_pickle or {}


class ContactFormSubmissionAttachment(models.Model):
    submission = models.ForeignKey(
        to=ContactFormSubmission,
        related_name="attachments",
        verbose_name=_('submission'),
        on_delete=models.PROTECT,
    )
    file = models.FileField(
        verbose_name=_('file'),
        upload_to="private/contactform/submissions/%Y-%m-%d",
        max_length=200,
    )

    class Meta:
        verbose_name = _('contact form submission attachment')
        verbose_name_plural = _('contact form submission attachments')


class ContactFormIntermediate(CMSPlugin):
    form = models.ForeignKey(ContactForm, verbose_name=_('form'))

    class Meta:
        db_table = 'cmsplugin_contactformintermediate'

    def __unicode__(self):
        return u'%s (%s)' % (self.form.name, self.form.language)
