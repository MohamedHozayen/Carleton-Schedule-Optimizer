from django.conf.urls import url, patterns
from django.conf import settings

from . import views

urlpatterns = [
    url(r'^$', views.scheduler, name='index'),
]

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)