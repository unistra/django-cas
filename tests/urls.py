from django.conf.urls import url
from django_cas.views import login, logout
from . import views


urlpatterns = [
    url(r'/accounts/login/$', login, name='login'),
    url(r'/accounts/logout/$', logout, name='logout'),
    url(r'^anonymous/', views.test_anonymous_view, name='anonymous'),
    url(r'^authenticated/', views.test_authenticated_view,
        name='authenticated'),
]
