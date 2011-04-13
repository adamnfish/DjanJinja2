# -*- coding: utf-8 -*-

"""
A Jinja2 template tag to output the csrf token wrapped in a hidden
input wrapped in a hidden div. This duplicates Django's {% csrf_token
%} template tag.

Usage is as follows:
    
    {% csrf_token %}

The csrf_token context variable is used to populate the input's
value. This is always added by Django if you use RequestContext, no
matter what your TEMPLATE_CONTEXT_PROCESSORS setting says)

If you do not use request context and try to use the {% csrf_token %}
tag, an exception will be raised.
"""

from jinja2 import nodes, Markup
from jinja2.ext import Extension

class CsrfExtension(Extension):
    """
    Outputs the csrf token in a format suitable for inclusion in
    forms.

    Jinja syntax based on http://djangosnippets.org/snippets/1847/
    """
    tags = set(['csrf_token'])

    def parse(self, parser):
        """
        Parses the template tag and delegates rendering to the render
        method.
        """
        try:
            token = parser.stream.next()
            return nodes.Output(
                [self.call_method('_generate_csrf',
                                  [nodes.Name('csrf_token','load')])]
                ).set_lineno(token.lineno)
        except:
            traceback.print_exc()

    def _generate_csrf(self, csrf_token):
        """
        Generates the output for the csrf_token.
        """
        if csrf_token:
            if csrf_token == 'NOTPROVIDED':
                return Markup(u"")
            else:
                return Markup(
                    u'<div style="display: none;">'
                    u'<input type="hidden" name="csrfmiddlewaretoken" value="%s" />'
                    u'</div>' % (csrf_token,))
        else:
            raise ImproperlyConfigured(
                "csrf_token() was used in a template, but a CSRF token was not "
                "present in the context. This is usually caused by not using "
                "RequestContext.")
