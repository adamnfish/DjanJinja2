# DjanJinja

DjanJinja exists to help you leverage the power of
[Jinja2](http://jinja.pocoo.org/2/) templates in your Django projects. It's
simple to get started.

## Installing and Using DjanJinja

### Installing DjanJinja

1. Install DjanJinja using `easy_install djanjinja`, `pip install djanjinja`, or
   by grabbing a copy of the Mercurial repo and running `python setup.py
   install`.
2. Add `'djanjinja'` to your `INSTALLED_APPS` list.
3. (Optionally) add `'djanjinja.middleware.RequestContextMiddleware'` to your
   `MIDDLEWARE_CLASSES` list.

This fork of DjanJinja adds Django 1.3 compatibility so make sure you
are using at least that version. It is assumed that you have fairly
recent version of Jinja2 and installed, please raise an issue if you
have problems with a specific version of Jinja2. Both Django and
Jinja2 are installable via PyPI (i.e. a simple `easy_install` or `pip
install`). A lot of people have their own ways of installing things,
so the author hasn’t put any explicit requirements in the `setup.py`
file. DjanJinja just expects to find `jinja2` and `django` on the
import path.

### Using DjanJinja

* Instead of using django's template shortcuts
  (eg. `django.shortcuts.render_to_response`), use one of the
  Jinja2-based functions provided.

* Instead of using Django’s provided generic views, use those
  contained within `djanjinja.generic` (at the moment the only one is
  `direct_to_template()`).

## Shortcut Functions

DjanJinja provides you with two shortcut functions for rendering templates,
`render_to_response` and `render_to_string`. These are very similar to those
provided by Django in the `django.shortcuts` module, except they use Jinja2
instead of the Django templating system. To use them from your views, just do
`from djanjinja.views import render_to_response, render_to_string` at the top of
your views module.

## Bundles

A Jinja2 environment can contain additional filters, tests and global variables
which will be available in all templates rendered through that environment.
Since individual Django apps will have their own set of things to add to the
environment, DjanJinja adds the concept of ‘bundles’; small objects containing
some global variables, filters and tests. Each app may define any number of
these bundles which can then be loaded as required.

### Defining Bundles

It’s relatively easy to define a bundle; an example is shown below:
    
    from djanjinja.loader import Bundle
    
    foo = Bundle()
    foo.globals['myvar'] = 12345
    
    @foo.envfilter
    def myenvfilter(environment, value):
        pass # do something here...
    
    @foo.ctxfunction
    def mycontextfunction(context, value):
        pass # do something here...

Here we define a bundle called `foo`, with a global variable of `myvar`
containing the value `12345`, an environment filter and a context function (for
more information on each of these please consult the Jinja2 documentation). The
`Bundle` class also supplies these handy decorators (the full list can be found
as `djanjinja.loader.Bundle.TYPES`) to define various components.

DjanJinja expects to find bundles in a `bundles` submodule of your Django app.
You can lay things out in one of two ways:

* Add a file called `bundles.py` to your app, and within this define multiple
  `Bundle` instances.
* Add a package called `bundles` to your app (i.e. a `bundles` directory
  containing an empty file called `__init__.py`), and within this define
  submodules for each of your bundles. Each submodule should have a top-level
  `bundle` variable which is an instance of the `Bundle` class.

You can actually mix and match these; you could add some bundle instances to the
`bundles/__init__.py` file with different names, in addition to having the
submodules. These are loaded lazily, so DjanJinja sees no real difference. It
doesn’t scour the `bundles` module for definitions, it just loads what you ask
it to.

### Addressing Bundles

In order to use the functions, filters and tests defined in a bundle, you first
have to load it into the environment. Bundles are specified in two parts: the
‘app label’ and the ‘bundle name’. The app label is simply the name of the app
which contains it. For example, it may be `django.contrib.auth`, or simply
`auth`, since you may just give the last part of the full name and DjanJinja
will figure it out from looking at the `INSTALLED_APPS` setting.

If a bundle is defined within a `bundles.py` or a `bundles/__init__.py` file,
then the bundle name will be the name in the module with which it was defined.
For example:
    
    # in the file `myapp/bundles.py`
    foo = Bundle()
    foo.globals['myvar'] = 12345

In this case, the app label will be `myapp`, and the bundle name will be `foo`.
If the bundles are defined in submodules, then the bundle name will be the name
of the submodule.

### Loading Bundles

In order to load any bundles into the global Jinja2 environment, you need to specify a
`DJANJINJA_BUNDLES` setting in your `settings.py` file. This is a list or tuple
of bundle specifiers in an `'app_label.bundle_name'` format. For example:

    DJANJINJA_BUNDLES = (
        'djanjinja.cache',
        'djanjinja.humanize',
        'djanjinja.site',
    )

You can also add bundles to the environment programmatically. This is useful
when:

* Your app needs to do some initial setup before a bundle is loaded.
* Your app relies on a particular bundle being present in the global environment
  anyway, and you don’t want the user to have to add the bundle to
  `DJANJINJA_BUNDLES` manually.
* Your app needs to load bundles dynamically.
* Your app wants to use a bundle locally, not globally.

You can load a bundle into an environment like this:

    import djanjinja
    env = djanjinja.get_env()
    env.load('app_label', 'bundle_name', reload=False)

This will load the bundle into the environment, passing through if it’s already
loaded. If you specify `reload=True`, you can make it reload a bundle even if
it’s been loaded.

You should put this code somewhere where it will get executed when you want it
to. If you want it to be executed immediately, as Django starts up, put it in
`myapp/__init__.py`.

You can also use a bundle within only one app, by using a local environment
copied from the global environment. Here’s how you might do this:

    import djanjinja
    global_env = djanjinja.get_env()
    local_env = global_env.copy()
    local_env.load('app_label', 'bundle_name')

You'd then use that local environment later on in your code. For example, the
above code might be in `myapp/__init__.py`; so your views might look like this:

    from django.http import HttpResponse
    from myapp import local_env
    
    def view(request):
        template = local_env.get_template('template_name.html')
        data = template.render({'key1': 'value1', 'key2': 'value2'})
        return HttpResponse(content=data)

Of course, you’re probably going to want to use the usual shortcuts (i.e.
`render_to_response()` and `render_to_string()`). You can build these easily
using `djanjinja.views.shortcuts_for_environment()`:

    from djanjinja.views import shortcuts_for_environment
    
    render_to_response, render_to_string = shortcuts_for_environment(local_env)

Do this at the top of your `views.py` file, and then you can use the generated
functions throughout all of your views.

### Caveats and Limitations

Jinja2 does not yet support scoped filters and tests; as a result of
this, the contents of bundles specified in `DJANJINJA_BUNDLES` will be
loaded into the global environment. It is important to make sure that
definitions in your bundle do not override those in another
bundle. This is especially important with threaded web applications,
as multiple bundles overriding one another could cause unpredictable
behavior in the templates.

If you need to make functionality available to specific templates bear
in mind that [Jinja2 natively includes support for
macros](http://jinja.pocoo.org/docs/templates/#macros). DjanJinja
bundles are great for adding behaviours to your entire project and
Jinja2 macros are a better fit for small pieces of specific
functionality.

### Included Bundles

DjanJinja provides three default bundles which either mimic Django
counterparts or add some useful functionality to your Jinja2
templates. This makes it even easier to convert from Django's
templates to Jinja2:
    
* `djanjinja.cache`: Loading this bundle will add a global `cache` object to the
  environment; this is the Django cache, and allows you to carry out caching
  operations from within your templates (such as `cache.get(key)`, et cetera).

* `djanjinja.humanize`: This will add all of the filters contained
  within the `django.contrib.humanize` app; consult [the official Django
  docs](https://docs.djangoproject.com/en/dev/ref/contrib/humanize/)
  for more information on the filters provided.

* `djanjinja.site`: This will add two functions to the global
  environment: `url`, and `setting`. The former acts like Django’s
  template tag, by reversing URLconf names and views into
  URLs. Because Jinja2 supports a richer syntax, it can be used via
  `{{ url(name, *args, **kwargs) }}` instead. The `setting` function
  attempts to resolve a setting name into a value, optionally
  returning a default instead (i.e. `setting('MEDIA_URL', '/media')`).

## Extensions

Jinja2 supports the concept of *environment extensions*; these are non-trivial
plugins which enhance the Jinja2 templating engine itself. By default, the
environment is configured with the `do` statement and the loop controls (i.e.
`break` and `continue`), but if you want to add extensions to the environment
then you can do so with the `JINJA_EXTENSIONS` setting. Just add this to your
`settings.py` file:
    
    JINJA_EXTENSIONS = (
        'jinja2.ext.i18n', # i18n Extension
        ...
    )

For all the extensions you wish to load. This will be passed in directly to the
`jinja2.Environment` constructor.

If you have set `USE_I18N = True` in your settings file, then DjanJinja will
automatically initialize the i18n machinery for the Jinja2 environment, loading
your Django translations during the bootstrapping process. For more information
on how to use the Jinja2 i18n extension, please consult the Jinja2
documentation.

### Autoescaping

To enable autoescaping, just add `JINJA_AUTOESCAPE = True` to your settings
file. This will add the extension and set up the Jinja2 environment correctly.

### CSRF protection

With the v1.2 release, Django dramatically changed the way crsf
protection was handled. Prior to this version, Django provided
automatic csrf protection by automatically detecting and re-writing
form tags in the response markup and inserting the csrf token. To
prevent the csrf token from being leaked to third parties if the form
submits to another site you are now required to manually add the csrf
token to forms.

DjanJinja provides an extension to mimic Django's `{% csrf_token %}`
template tag. You should add it inside any form that POSTs to one of
your views.

    <form action="{{ url }}" method="post">{% csrf_token %}

See [Django's csrf
documentation](http://docs.djangoproject.com/en/dev/ref/contrib/csrf/)
for more information on how to use the csrf_token tag - it works in
exactly the same way in Djanjinja.

### Cache

DjanJinja also provides an extension for fragment caching using the Django cache
system. The code for this borrows heavily from the example in the Jinja2
documentation, but with a few extras thrown in. You can use the extension like
this:
    
    {% cache (parameter1, param2, param3), timeout %}
        ...
    {% endcache %}

The tuple of parameters is used to generate the cache key for this fragment. You
can place any object here, so long as it is suitable for serialization by the
standard library `marshal` module. The cache key for the fragment is generated
by marshaling the parameters, hashing them and then using the digest with a
prefix as the key. This allows you to specify cached fragments which vary
depending on multiple variables. The timeout is optional, and should be given in
seconds.

## 404 and 500 Handlers

Your project’s URLconf must specify two variables—`handler404` and
`handler500`—which give the name of a Django view to be processed in
the event of a 404 "Not Found" and a 500 "Server Error" response
respectively. These are set to a default which uses the Django
templating system to render a response from templates called
`404.html` and `500.html`. If you were to use the Jinja2 templating
system instead, you will be able to define richer error pages, and
your error pages will be able to inherit from and extend other Jinja2
master templates on the template path.

It’s relatively simple to set Django up to do this. Simply override
the handler variables like so from your `urls.py` file:

    handler404 = 'djanjinja.handlers.page_not_found'
    handler500 = 'djanjinja.handlers.server_error'

## `RequestContext`

One of Django's most useful features is the `RequestContext` class, which allows
you to specify several context processors which each add some information to the
context before templates are rendered. Luckily, this feature is
template-agnostic, and is therefore fully compatible with DjanJinja.

However, DjanJinja also provides you with some very helpful shortcuts for using
request contexts. Usually, without DjanJinja, you would use them like this:
    
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    
    def myview(request):
        context = {'foo': bar, 'spam': eggs}
        return render_to_response('template_name.html',
            context, context_instance=RequestContext())

To be honest,this doesn't look very much like a 'shortcut' at all. For this
reason, DjanJinja contains a subclass of `RequestContext` specialised for
Jinja2, which is used like this:

    from djanjinja.views import RequestContext
    
    def myview(request):
        context = RequestContext(request, {'foo': bar, 'spam': eggs})
        return context.render_response('template_name.html')

This code is much more concise, but loses none of the flexibility of the
previous example. The main changes made are the addition of `render_response`
and `render_string` methods to the context object itself. This is highly
specialised to rendering Jinja2 templates, so it may not be a very reusable
approach (indeed, other code which does not use Jinja2 will need to use the full
Django syntax), but it works for the problem domain it was designed for.

## Middleware

Djanjinja contains two middleware optional middleware classes for your
convenience.

### RequestContextMiddleware

Each time a `RequestContext` instance is constructed, it is necessary
to explicitly pass the request. In object-oriented programming, and
Python expecially, when we have functions to which we must always pass
an object of a certain type, it makes sense to make that function a
*method* of the type. When that function is not, in fact, a function,
but a constructor, this seems more difficult. However, thanks to a
feature of Python known as metaprogramming, we can do this very
easily. Because it's not exactly obvious how to do so, DjanJinja
includes a special piece of middleware which can help make your code a
lot shorter yet *still* retain all the functionality and flexibility
of the examples given above, in the RequestContext section.

To use this middleware, simply add
`'djanjinja.middleware.RequestContextMiddleware'` to your `MIDDLEWARE_CLASSES`
list in the settings module of your project. Then, you can write view code like
this:

    def myview(request):
        return request.Context({'foo': bar, 'spam': eggs}).render_response(
            'template_name.html')

As you can see, we've greatly reduced the verbosity of the previous code, but
it's still obvious what this code does. The middleware attaches a `Context`
attribute to each request object. This attribute is in fact a fully-fledged
Python class, which may itself be subclassed and modified later on. When
constructed, it behaves almost exactly the same as the usual `RequestContext`,
only it uses the request object to which it has been attached, so you don't have
to pass it in to the constructor every time.

### MessagesMiddleware

In the same way, Django's messaging framework requires you to add the
request as the first parameter to all its calls. Djanjinja's
MessagesMiddleware adds these methods to the request object to greatly
simplify their use.

To use this middleware, add
`'djanjinja.middleware.MessagesMiddleware'` to the
`MIDDLEWARE_CLASSES` setting for your project.

You can then use the new shortcuts in your views as follows:

    def myview(request):
        # add a debug-level message
        request.debug('My message here')
        # add an info-level message
        request.info('My message here')
        # add a success-level message
        request.success('My message here')
        # add a warning-level message
        # note that you can pass additional args
        request.warning('My message here', fail_silently=True)
        # add an error message
        request.error('My message here')
        
        # add a custom message
        request.add_message(MY_CUSTOM_LEVEL, 'My message')

Each of these methods correspond exactly to those described in the
Django documentation for the [messaging
framework](http://docs.djangoproject.com/en/dev/ref/contrib/messages/)
except that they are called from the request object and thus without
the request parameter.

Please note that for messaging to work you must also include any
dependancies required by Django's messaging framework in your
middleware settings. These dependancies are described in detail in the
[messaging
documentation](https://docs.djangoproject.com/en/dev/ref/contrib/messages/).

## Context Processors

Djanjinja also provides a context processor for handling Django#s
messages.

### Messages

This context processor is included to make using Django's messaging
framework in your Jnija2 templates simpler.

If you include `'djanjinja.context.messages'` in your application's
`TEMPLATE_CONTEXT_PROCESSORS` setting, a `messages` variable will be
exposed to all your templates that contains any messages associated
woth the request object. This works in the same way as Django's own
messaging context processor. Consult Django's [messaging
documentation](https://docs.djangoproject.com/en/dev/ref/contrib/messages/)
for more information on using this context processor.

However, Djanjinja's messages context processor also provides an
`as_html` method. This is a property on the messages template variable
itself. To use it in your templates, do the following:

    {{ messages.as_html() }}

By default, this fetches the messages and prints them out as an
unordered list, including CSS classes that correspond to the message
level. This output is identical to the sample output given in the
[messages
documentation](https://docs.djangoproject.com/en/dev/ref/contrib/messages/#displaying-messages). It
does this by rendering the `messages/messages.html` template with the
messages passed as the template's context. This template is found
within Djaninja - to override it you can include a template in your
application's template directory at the same location (`<template
dir>/messages/messgaes.html`). If you would rather customise the
rendering of the messages yourself then you can access the messages
variable directly without ever touching the as_html method, or use
Django's own messages context processor.

## Template Loading

DjanJinja hooks directly into the Django template loader machinery to load
templates. This means you can mix Jinja2 templates freely with Django templates,
in your `TEMPLATE_DIRS` and your applications, and render each type
independently and seamlessly. If you want more information on how it actually
works, please consult the `djanjinja/environment.py` file.

## (Un)license

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
software, either in source code form or as a compiled binary, for any purpose,
commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this
software dedicate any and all copyright interest in the software to the public
domain. We make this dedication for the benefit of the public at large and to
the detriment of our heirs and successors. We intend this dedication to be an
overt act of relinquishment in perpetuity of all present and future rights to
this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
