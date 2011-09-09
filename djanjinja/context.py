"""
This contains an optional context processor that adds support for
Django's messaging framework.

It adds methods to the request object that act as shorthand for using
the messaging framework and adds the current messages to the context.
"""
from django.contrib import messages as django_messages

def messages(request):
    """
    Adds messaging support to the context.
    """
    return {'messages': django_messages.get_messages(request)}
