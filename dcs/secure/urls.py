from django.conf.urls import url, include
from django.urls import path

import secure.views as views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^images/$', views.images, name='images'),
    path('perform/<action>/<name>', views.perform),
    path('total-images/', views.total_images)
    # url(r'^images/', views.images, name='images')
]
