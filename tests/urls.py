from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^anonymous/', views.test_anonymous_view, name='anonymous'),
    url(r'^authenticated/', views.test_authenticated_view,
        name='authenticated'),
]
