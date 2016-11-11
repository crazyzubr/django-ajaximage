from django.conf.urls import url
import ajaximage.views as views

urlpatterns = [
     url(
        '^upload/(?P<upload_to>.*)/(?P<max_width>\d+)/(?P<max_height>\d+)/(?P<crop>\d+)',
        views.ajaximage,
        name='ajaximage'
    ),
]
