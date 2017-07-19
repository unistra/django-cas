import django
from django.conf.urls import url, include
from . import views



urlpatterns = [
    url(r'^anonymous/', views.test_anonymous_view, name='anonymous'),
    url(r'^authenticated/', views.test_authenticated_view,
        name='authenticated'),
]


if int(django.get_version().split('.')[1]) > 8:
    urlpatterns.append(
        url(r'^accounts/', include('django_cas.urls'))
    )
else:
    urlpatterns.append(
        url(r'^accounts/', include('django_cas.urls', namespace='django_cas'))
    )
