# django-cas-sso

[![Code Health](https://landscape.io/github/unistra/django-cas/master/landscape.svg?style=flat)](https://landscape.io/github/unistra/django-cas/master)

CAS client for Django.  This is K-State&#39;s fork of the original, which lives at
https://bitbucket.org/cpcc/django-cas/overview.  This fork is actively maintaned and
includes several new features.

Current version: 1.2.6

https://github.com/kstateome/django-cas


## Install


See the document at Bitbucket

https://bitbucket.org/cpcc/django-cas/overview

## Settings.py for CAS

Add the following to middleware if you want to use CAS::

    MIDDLEWARE = (
    'django_cas.middleware.CASMiddleware',
    )


Add these to ``settings.py`` to use the CAS Backend::


    CAS_SERVER_URL = "Your Cas Server"
    CAS_LOGOUT_COMPLETELY = True

To disable CAS authentication for the entire django admin app, you should use the ``CAS_ADMIN_AUTH`` parameter::

    CAS_ADMIN_AUTH = False

## Url namespace

Include `django_cas` urls :

* if your django version is 1.8 or older (defining the namespace "django_cas" is required) :

		url(r'your-base_uri/', include('django_cas.urls', namespace='django_cas'))

* for version >= 1.9 (a default namespace "django_cas" will be set but you can set yours if you want) :

		url(r'your-base_uri/', include('django_cas.urls'))


# Additional Features

This fork contains additional features not found in the original:
*  Proxied Hosts
*  CAS Response Callbacks
*  CAS Gateway
*  Proxy Tickets (From Edmund Crewe)

## Proxied Hosts

You will need to setup middleware to handle the use of proxies.

Add a setting ``PROXY_DOMAIN`` of the domain you want the client to use.  Then add

    MIDDLEWARE = (
    'django_cas.middleware.ProxyMiddleware',
    )

This middleware needs to be added before the django ``common`` middleware.


## CAS Response Callbacks

To store data from CAS, create a callback function that accepts the dict from the
proxyValidate response. There can be multiple callbacks, and they can live anywhere. Define the
callback(s) in ``settings.py``:

    CAS_RESPONSE_CALLBACKS = (
        'path.to.module.callbackfunction',
        'anotherpath.to.module.callbackfunction2',
    )

and create the functions in ``path/to/module.py``:

    def callbackfunction(attribute_dict):
		# direct access
        username = attribute_dict.get('username')

        user, user_created = User.objects.get_or_create(username=username)
        profile, created = user.get_profile()

		# ldap monovalued field
        profile.email = attribute_dict.get('mail',[''])[0]
		# ldap multivalued field
        profile.affiliations = attribute_dict.get('eduPersonAffiliation',[])
        profile.save()

### Custom User creation 

If automated user creation is enabled (``CAS_USER_CREATION = True``), you can define a custom user creation function.

Give its path to the settings file like this:

	CAS_USER_CREATION_CALLBACK = (
		'path.to.module.user_creation_function',
	)

Provide the function in ``path/to/module.py``,  
which receive user data as a list of two items: ``[app_user_model, user_attributes_dict]``   
and return created user instance:  

	def user_creation_function(user_data):
		user_model, user_attributes = user_data
		username = user_attributes['username']
		email = user_attributes.get('email', '')
		return user_model.objects.create_user(username, email)		

With default settings ticket verification provide a dict of all attributes defined in your CAS server configuration file.
If ``CAS_VERSION`` setting is lower than 3 then dict contains only the username. 

## CAS Gateway

To use the CAS Gateway feature, first enable it in settings. Trying to use it without explicitly
enabling this setting will raise an ImproperlyConfigured:

    CAS_GATEWAY = True

Then, add the ``gateway`` decorator to a view:

    from django_cas.decorators import gateway

    @gateway()
    def foo(request):
        #stuff
        return render(request, 'foo/bar.html')


## Custom Forbidden Page

To show a custom forbidden page, set ``CAS_CUSTOM_FORBIDDEN`` to a ``path.to.some_view``.  Otherwise,
a generic ``HttpResponseForbidden`` will be returned.

## Require SSL Login

To force the service url to always target HTTPS, set ``CAS_FORCE_SSL_SERVICE_URL`` to ``True``.

## Proxy Tickets

This fork also includes Edmund Crewe's proxy ticket patch:
http://code.google.com/r/edmundcrewe-proxypatch/source/browse/django-cas-proxy.patch
