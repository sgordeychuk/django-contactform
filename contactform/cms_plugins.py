from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from .models import ContactFormIntermediate
from .views import get_initial_data_from_request


class ContactFormPlugin(CMSPluginBase):
    model = ContactFormIntermediate
    name = _("Contact Form")
    render_template = "contactform/form.html"
    cache = False

    def render(self, context, instance, placeholder):
        contact_form = instance.form
        FormClass = contact_form.get_form_class(unique_form_id=instance.pk)
        context = super(
            ContactFormPlugin, self).render(context, instance, placeholder)

        request = context['request']

        if request.method == "POST" and request.POST.get('unique_form_id', None) == str(instance.pk):
            form = FormClass(request.POST, request.FILES)
            success = form.is_valid() and form.handle_submission(request)
        else:
            initial_data = get_initial_data_from_request(request, contact_form)
            form = FormClass(initial=initial_data)
            success = False

        if success and contact_form.success_page:
            # form was processed successfully
            context['redirect'] = contact_form.success_page.get_absolute_url()

        context['success'] = success
        context['form'] = form
        context['form_model'] = contact_form
        return context


plugin_pool.register_plugin(ContactFormPlugin)
