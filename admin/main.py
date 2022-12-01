from functools import update_wrapper

from django import get_version
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse

from ..models import (
    ContactForm,
    ContactFormSubmission,
    ContactFormSubmissionAttachment,
    FormField,
    Recipient,
)
from .exporter import Exporter


mimetype_map = {
    'xls': 'application/vnd.ms-excel',
    'csv': 'text/csv',
    'html': 'text/html',
    'yaml': 'text/yaml',
    'json': 'application/json',
}


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 4


class ContactFormAdmin(admin.ModelAdmin):
    inlines = [
        FormFieldInline,
    ]

    list_display = ('name', 'language',)
    list_filter = ('language',)
    search_fields = ('name',)
    ordering = ('id', 'language',)
    save_as = True
    raw_id_fields = ['success_page']

    if 'captcha' not in settings.INSTALLED_APPS:
        exclude = ('has_captcha',)

    class Media:
        css = {
            "all": ("contactform/css/contactform_admin.css",)
        }


class ContactFormSubmissionAttachmentAdmin(admin.TabularInline):
    model = ContactFormSubmissionAttachment
    extra = 0


class ContactFormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'submitted_at', 'language', 'sender_ip',)
    list_filter = ('form', 'language', 'submitted_at',)
    search_fields = ('form_data',)
    date_hierarchy = 'submitted_at'
    inlines = [
        ContactFormSubmissionAttachmentAdmin,
    ]
    export_filename = 'contactform-contactformsubmission'
    export_excluded_fields = ('form_data', 'form_data_pickle',)

    def get_urls(self):
        from django.conf.urls import url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^csv/$', wrap(self.export)),
        ]
        return urlpatterns + super(ContactFormSubmissionAdmin, self).get_urls()

    def export(self, request, file_type='csv'):
        queryset = self.get_export_queryset(request)
        # TODO: Check if queryset is empty.
        exporter = Exporter(
            queryset=queryset,
            excluded_fields=self.export_excluded_fields,
        )
        fields = exporter.get_fields_for_export()
        dataset = exporter.get_dataset(fields=fields)
        content_type = self.get_export_content_type(file_type)

        response_kwargs = {}

        if int(get_version().split('.')[1]) > 6:
            response_kwargs['content_type'] = content_type
        else:
            # Django <= 1.6 compatibility
            response_kwargs['mimetype'] = content_type

        data = getattr(dataset, file_type)
        filename = '%s.%s' % (self.export_filename, file_type)
        response = HttpResponse(data, **response_kwargs)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    def get_export_content_type(self, file_type):
        content_type = mimetype_map.get(
            file_type,
            'application/octet-stream'
        )
        return content_type

    def get_export_queryset(self, request):
        ChangeList = self.get_changelist(request)

        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        list_filter = self.get_list_filter(request)

        if hasattr(self, 'get_search_fields'):
            search_fields = self.get_search_fields(request)
        else:
            search_fields = self.search_fields

        cl = ChangeList(
            request,
            self.model,
            list_display,
            list_display_links,
            list_filter,
            self.date_hierarchy,
            search_fields,
            self.list_select_related,
            self.list_per_page,
            self.list_max_show_all,
            self.list_editable,
            self,
        )
        return cl.get_queryset(request)


admin.site.register(ContactForm, ContactFormAdmin)
admin.site.register(Recipient)
admin.site.register(ContactFormSubmission, ContactFormSubmissionAdmin)
