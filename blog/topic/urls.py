from django.conf.urls import url
from django.urls import path,re_path
from . import views

urlpatterns = [
    # http://127.0.0.1/v1/topics/<author>
    re_path(r'^/(?P<author_id>[\w]{1,11})$',views.topics)
]
