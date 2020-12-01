from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search', views.search, name='search'),
    url(r'^title', views.title, name='title'),
    url(r'^import/data', views.excel_import, name="import"),
    url(r'^feedback', views.add_feedback, name="feedback")
]