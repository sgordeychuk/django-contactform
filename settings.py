from django.conf import settings

# set the maximum size in bytes for files uploaded via file field.
MAX_FILE_SIZE = getattr(settings, "CONTACTFORM_MAX_FILE_SIZE", 10485760)