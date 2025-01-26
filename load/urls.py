from django.urls import path
from . import views
from .views import test_download

urlpatterns = [
    path('', views.index, name='index'),
    #   path("api/download/", test_download, name="test_download"),
    path('api/download/', views.instagram_downloader, name="instagram_downloader"),

]
