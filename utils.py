# -*- coding: utf-8 -*-


def get_ip_from_request(request):
    """
    This function assumes that your Nginx is configured with:
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    """
    ip_address_list = request.META.get('HTTP_X_FORWARDED_FOR')

    if ip_address_list:
        ip_address_list = ip_address_list.split(',')
        ip_address = ip_address_list[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR') or None
    return ip_address
