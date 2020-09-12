
# django imports
from django.core.paginator import EmptyPage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError


def responsedata(status,message,data={}):
    if status:
        return {
            "status":status,
            "message":message,
            "data": data
        }
    else:
        return {
            "status":status,
            "message":message,
        }


def paginate(data, paginator, pagenumber, total_pages=0):
    """
    This method to create the paginated results in list API views.
    """
    if int(pagenumber) > paginator.num_pages:
        raise ValidationError("Not enough pages", code=404)
    try:
        previous_page_number = paginator.page(pagenumber).previous_page_number()
    except EmptyPage:
        previous_page_number = None
    try:
        next_page_number = paginator.page(pagenumber).next_page_number()
    except EmptyPage:
        next_page_number = int(pagenumber) + 1 if int(pagenumber) < total_pages else None

    if paginator.page(pagenumber).has_next():
        is_next_page = paginator.page(pagenumber).has_next() 
    else:
       is_next_page =  True if next_page_number else False 

    return {'pagination': {
        'previous_page': previous_page_number,
        'is_previous_page': paginator.page(pagenumber).has_previous(),
        'next_page': next_page_number,
        'is_next_page': is_next_page,
        'start_index': paginator.page(pagenumber).start_index(),
        'end_index': paginator.page(pagenumber).end_index(),
        'total_entries': paginator.count,
        'total_pages': paginator.num_pages,
        'page': int(pagenumber)
    }, 'results': data}

