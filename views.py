from django.conf import settings
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext

from contactform.models import ContactForm


# try to get custom multiple choice fields to be treated properly
# if initial should be set via GET params
MULTIPLE_VALUES_FIELDS = getattr(settings, 'MULTIPLE_VALUES_FIELDS', ['django.forms.MultipleChoiceField'])


def index(request, form_model_id):
    contact_form = get_object_or_404(ContactForm, pk=form_model_id)
    FormClass = contact_form.get_form_class()
    if request.method == "POST":
        form = FormClass(request.POST, request.FILES)
        if form.is_valid() and form.handle_submission(request):
            # form was processed sucessfully
            context = {
                'form': form,
                'form_model': contact_form,
                'success': True,
            }
            return render_to_response("contactform/base.html", dictionary=context,
                                      context_instance=RequestContext(request))
        else:
            # error happened
            context = {
                'form': form,
                'form_model': contact_form,
                'success': False,
            }
            return render_to_response("contactform/base.html", dictionary=context,
                                      context_instance=RequestContext(request))
    else:
        initial_data = get_initial_data_from_request(request, contact_form)
        form = FormClass(initial=initial_data)
    context = {
        'form': form,
        'form_model': contact_form,
        'success': False,
    }
    return render_to_response("contactform/base.html", dictionary=context, context_instance=RequestContext(request))


def get_initial_data_from_request(request, contact_form):
    """
    Extract initial data from request.GET and return as dict to be passed to form initialization.
    will walk only on contact form field labels, everything else will be ignored.
    If no data were extracted - function will return {}.
    """
    initial_data = {}
    # try to extract initial data from request GET only if there is some items.
    if len(request.GET.items()) > 0:
        form_fields = sorted(contact_form.field_set.all(), key=lambda x: x.position)
        # we need to iterate over all fields to build correct names, since name is not
        # unique, and fields with same name but different positions may relate to different
        # fields
        for position, field in enumerate(form_fields):
            # construct actual form field_name, WARNING: position is not the field.position
            field_name = "{0}_{1}".format(slugify(field.label), position)
            # custom fields with multiple values should be added to MULTIPLE_VALUES_FIELDS
            # constant
            if field.field_type in MULTIPLE_VALUES_FIELDS:
                field_data = request.GET.getlist(field_name)
            else:
                field_data = request.GET.get(field_name, None)

            if field_data:
                initial_data[field_name] = field_data
    return initial_data