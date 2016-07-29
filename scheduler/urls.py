from django.conf.urls import url, patterns
from django.conf import settings
from django.views.static import serve as static_view
from . import views

urlpatterns = [
    url(r'^$', views.scheduler, name='index'),
    url(r'^static/(?P<path>.*)$', static_view, {'document_root': settings.STATIC_ROOT}),
]
