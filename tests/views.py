from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def test_anonymous_view(request):
    return HttpResponse()


@login_required
def test_authenticated_view(request):
    return HttpResponse()
