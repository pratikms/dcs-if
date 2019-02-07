from django.conf.urls import url, include

import secure.views

urlpatterns = [
    url(r'^$', secure.views.index, name='index')
]
