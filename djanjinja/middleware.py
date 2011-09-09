# -*- coding: utf-8 -*-

"""
djanjinja.middleware - Helpful middleware for using Jinja2 from Django.

This module contains middleware which helps you use Jinja2 from within
your views. ``RequestContextMiddleware`` adds a Context property to
all request objects that allows you to render templates with a request
context more elegantly. It also contains ``MessagesMiddleware``, which
adds methods to the request object that correspond to the methods made
available by Django's messaging framework.


"""
from functools import partial

from django.contrib import messages as django_messages

from djanjinja.views import RequestContext


class RequestContextMiddleware(object):
    
    """Attach a special ``RequestContext`` class to each request object."""
    
    @staticmethod
    def process_request(request):
        
        """
        Attach a special ``RequestContext`` subclass to each request object.
        
        This is the only method in the ``RequestContextMiddleware`` Django
        middleware class. It attaches a ``RequestContext`` subclass to each
        request as the ``Context`` attribute. This subclass has the request
        object pre-specified, so you only need to use ``request.Context()`` to
        make instances of ``django.template.RequestContext``.
        
        Consult the documentation for ``djanjinja.views.RequestContext`` for
        more information.
        """
        
        request.Context = RequestContext.with_request(request)

class MessagesMiddleware(object):
    """
    Adds shortcut methods to the request for Django's messages
    framework.
    """
    
    def process_request(self, request):
        """
        Mutates the request object to add messages methods
        """

        request.debug = partial(django_messages.debug, request)
        request.info = partial(django_messages.info, request)
        request.success = partial(django_messages.success, request)
        request.warning = partial(django_messages.warning, request)
        request.error = partial(django_messages.error, request)
        request.add_message = partial(django_messages.add_message, request)
        request.get_messages = partial(django_messages.get_messages, request)

