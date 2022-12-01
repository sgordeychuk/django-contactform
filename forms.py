from collections import OrderedDict

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.forms import Form, ValidationError, BooleanField, EmailField
from django.template.defaultfilters import yesno, slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives as EmailMessage
from django.core.mail import get_connection
from django.template.context import Context
from django.template.loader import render_to_string


try:
    from captcha.fields import CaptchaField
except ImportError:
    class CaptchaField:
        pass

from .models import ContactFormSubmission, ContactFormSubmissionAttachment
from .settings import MAX_FILE_SIZE
from .utils import get_ip_from_request


def id_compare(x):
    x = x.name.split('_')[-1]

    if x.isdigit():
        return int(x)
    else:
        return 0


class EmailWithConfirmation(EmailField):
    pass


class EmailWithConfirmationCheckbox(BooleanField):
    pass


class ContactFormFormBase(Form):
    model = None

    def render_values(self, show_hidden=False, for_display=False):
        """
        Renders values as dict.
        """
        if not self.is_valid():
            return

        field_mapping = OrderedDict()

        fields = list(self) if show_hidden else self.visible_fields()
        fields.sort(key=id_compare)

        for field in fields:
            name = field.name
            label = field.field.label
            value = self.cleaned_data[name]

            if isinstance(field, CaptchaField):
                continue

            if isinstance(value, bool):
                value = yesno(value, u"%s,%s" % (_('yes'), _('no')), )
            elif isinstance(value, UploadedFile):
                value = value.name

            if for_display:
                field_mapping[name] = {'label': unicode(label), 'value': unicode(value)}
            else:
                try:
                    position = int(name.split("_")[-1])
                except:
                    position = 0
                label = "%03d_%s" % (position, label)
                field_mapping[label] = unicode(value)
        return field_mapping

    def render_values_as_string(self):
        """
        Returns values as string with line breaks.
        Boolean values are filtered through yesno().
        """
        if not self.is_valid():
            return
        fields = self.render_values(show_hidden=False, for_display=True)
        values = (u'%s:%s' % (attrs['label'], attrs['value']) for attrs in fields.itervalues())
        return ''.join(values)

    def get_files_from_request(self, request):
        files = []
        for field_label in self.base_fields.keys():
            if request and field_label in request.FILES:
                this_file = request.FILES[field_label]
                if this_file.size <= MAX_FILE_SIZE:  # check if file is bigger than 10 MB (which is not good)
                    files.append(this_file)
        return files

    def handle_submission(self, request=None):
        """
        Processes the form submission.
        Constructs an EmailMessage and saves the submission as ContactFormSubmission instance.
        """
        if not self.is_valid():
            raise ValidationError(_("Form does not validate"))

        contact_form = self.model.objects.get(pk=self.model_instance_id)

        if request:
            sender_ip = get_ip_from_request(request) or ''
            form_url = request.build_absolute_uri()
            files = self.get_files_from_request(request)
        else:
            sender_ip = ""
            form_url = ""
            files = []

        # prepare a ContactFormSubmission but don't fill up all values yet
        submission = ContactFormSubmission(
            form=contact_form,
            sender_ip=sender_ip,
            form_url=form_url,
            language=contact_form.language,
            form_data="",
            form_data_pickle="",
        )
        submission.save()

        attachments = []

        for uploaded_file in files:
            submission_attachment = ContactFormSubmissionAttachment(submission=submission)
            submission_attachment.save()
            attachment_name = u"%u_%u-%s" % (submission.form.id, submission.id, uploaded_file.name)
            submission_attachment.file.save(
                name=attachment_name,
                content=uploaded_file
            )
            attachment = submission_attachment.file
            attachment.content_type = uploaded_file.content_type
            attachments.append(attachment)

        email_message, success = self.send_email(contact_form, submission, attachments)

        if not success:
            email_message = _(
                "*** There might be a problem with your SMTP configuration. I wasn't able to send this form submission as email. ***") \
                            + "\n\n" + email_message
        submission.form_data = email_message
        submission.form_data_pickle = self.render_values(show_hidden=True, for_display=False)
        submission.save()
        return True

    def send_email(self, contact_form, submission, attachments):
        """
        Processes the form submission.
        Constructs an EmailMessage and saves the submission as ContactFormSubmission instance.
        """
        if not self.is_valid():
            raise ValidationError(_("Form does not validate"))

        contact_form = self.model.objects.get(pk=self.model_instance_id)
        site = Site.objects.get_current()

        try:
            from siteinfo.models import SiteSettings

            contact = SiteSettings.objects.get_current()
        except:
            contact = None

        subject = u"[%s - %s] %s" % (site.domain, contact_form.name, _(u"Contact form sent"))

        # prepare email
        message_context = Context({
            'site': site,
            'contact_form': contact_form,
            'rows': self.render_values_as_string(),
            'sender_ip': submission.sender_ip,
            'form_url': submission.form_url,
            'cleaned_fields': self.render_values(show_hidden=False, for_display=True)
        }, autoescape=False)

        text_content = render_to_string(
            'contactform/form_submission_email.txt',
            context_instance=message_context,
        )

        html_content = render_to_string(
            'contactform/form_submission_email.html',
            context_instance=message_context,
        )

        recipients = contact_form.recipients.values_list('email', flat=True)

        bcc = []

        if contact_form.cc_managers:
            bcc += [manager[1] for manager in settings.MANAGERS]

        if contact_form.cc_site_contact and contact:
            bcc += [contact.email]

        try:
            connection = get_connection(fail_silently=False)
            connection.open()
            smtp_success = True
        except Exception:
            # SMTP misconfigured continue silently and at least save submission to DB.
            connection = False
            smtp_success = False
        else:
            # TODO: Log any failures
            message = EmailMessage(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipients,
                bcc=bcc
            )
            message.attach_alternative(html_content, "text/html")

            for attachment in attachments:
                message.attach(attachment.name, attachment.read(MAX_FILE_SIZE), attachment.content_type)
            connection.send_messages([message])

        all_fields = list(contact_form.field_set.all())

        try:
            send_conf_field = (
                contact_form
                .field_set
                .filter(field_type='contactform.forms.EmailWithConfirmationCheckbox')
            )[0]
            # I don't like this anymore than you do :(
            position = all_fields.index(send_conf_field)
            # TODO: Make a standard out of this and ship it to a helper function. (1)
            field = '%s_%s' % (slugify(send_conf_field.label), position)
            send_conf = self.cleaned_data.get(field)
        except IndexError:
            # If there's no checkbox but still 'EmailWithConfirmation' fields we send an email anyway
            send_conf = True

        if send_conf:
            email_confirmation_fields = list(
                contact_form.field_set.filter(field_type='contactform.forms.EmailWithConfirmation'))
            for email_field in email_confirmation_fields:
                # I don't like this anymore than you do :(
                position = all_fields.index(email_field)

                # TODO: Make a standard out of this and ship it to a helper function. (2)
                field = '%s_%s' % (slugify(email_field.label), position)

                email = self.cleaned_data.get(field)
                if email and connection:
                    user_message_body = contact_form.notification_email_body + "\n\n" + message.body
                    user_message = EmailMessage(
                        subject=contact_form.notification_email_subject,
                        body=user_message_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email],
                        attachments=message.attachments,
                    )
                    connection.send_messages([user_message])
        return text_content, smtp_success
