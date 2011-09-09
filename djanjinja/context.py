"""
This contains an optional context processor that adds support for
Django's messaging framework.

It adds methods to the request object that act as shorthand for using
the messaging framework and adds the current messages to the context.
"""
from functools import partial

from django.contrib import messages as django_messages

from djanjinja.views import render_to_string


def messages(request):
    """
    Adds messaging support to the context.
    """
    # get the messages
    messages = django_messages.get_messages(request)
    # add an as_html property that returns the HTML for the message display
    # this is over-ridable by including a 'messages/messages.html' template
    setattr(messages, 'as_html', partial(render_to_string, "messages/messages.html", {'messages': messages}))
    
    return {'messages': messages}
