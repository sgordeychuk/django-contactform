# -*- coding: utf-8 -*-
from tablib import Dataset

from .helpers import get_field_for_display


class Exporter(object):

    def __init__(self, queryset, excluded_fields=None):
        if excluded_fields is None:
            excluded_fields = []
        self.excluded_fields = excluded_fields
        self.queryset = queryset

    def get_dataset(self, fields):
        model_fields = self.get_model_export_fields()
        # First are model fields, then form fields
        headers = [field.verbose_name for field in model_fields] + fields
        dataset = Dataset(headers=headers)

        for submission in self.queryset.iterator():
            form_data = submission.get_form_data()
            # First are model fields
            row_data = [get_field_for_display(field.name, obj=submission)
                        for field in model_fields]

            # Then form fields
            for field in fields:
                if field in form_data:
                    value = form_data[field]
                else:
                    value = ''
                row_data.append(value)

            if row_data:
                dataset.append(row_data)
        return dataset

    def get_model(self):
        return self.queryset.model

    def get_model_export_fields(self):
        opts = self.get_model()._meta

        fields = [field for field in opts.fields
                  if field.name not in self.excluded_fields]
        return fields

    def get_fields_for_export(self):
        # A user can add fields to the form over time,
        # knowing this we use the latest form submission as a way
        # to get the latest form state.
        submissions = self.queryset.only('form_data_pickle').iterator()

        latest_data = next(submissions).get_form_data()
        fields = latest_data.keys()

        for submission in submissions:
            form_fields = submission.get_form_data()
            fields.extend(field for field in form_fields if field not in fields)
        return fields
