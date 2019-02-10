from django.conf.urls import url, include
from django.urls import path

import secure.views as views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^images/$', views.images, name='hosts'),
    url(r'^containers/$', views.containers, name='containers'),
    path('images/<img_id>/<img_name>', views.vulscan_images),
    path('containers/view/<cont_id>/<cont_name>', views.vulscan_containers_view, name='vul_container'),
    path('containers/<cont_id>/<cont_name>', views.vulscan_containers),
    url(r'^compcheck/$', views.compcheck, name='compliance_check'),
    url(r'^compscore/$', views.compliance_score, name='compliance_score'),
    path('perform/<action>/<name>', views.perform),
    url(r'^images/$', views.images, name='images'),
    path('perform/<action>/<name>', views.perform),
    path('total-images/', views.total_images)
    # url(r'^images/', views.images, name='images')
]
