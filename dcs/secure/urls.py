from django.conf.urls import url, include

import secure.views

urlpatterns = [
    url(r'^$', secure.views.index, name='dashboard'),
    url(r'^dashboard/$', secure.views.dashboard, name='dashboard'),
    url(r'^hosts/$', secure.views.hosts, name='hosts'),
]
