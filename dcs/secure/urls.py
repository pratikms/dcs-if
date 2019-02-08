from django.conf.urls import url, include
from django.urls import path

import secure.views as views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^hosts/$', views.hosts, name='hosts'),
    path('perform/<action>/<name>', views.perform)
]
