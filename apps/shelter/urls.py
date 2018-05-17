from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.new),
    url(r'^users$', views.users),
    url(r'^users/(?P<id>\d+)$', views.profile),
    url(r'^users/destroy/(?P<id>\d+)$', views.deleteUser),
    url(r'^logout$', views.logout),
    url(r'^login$', views.login),
    url(r'^pets$', views.petList),
    url(r'^pets/new$', views.registerPet),
    url(r'^pets/adopted$', views.adopted),
    url(r'^pets/admin$', views.pending_approval),
    url(r'^pets/(?P<id>\d+)$', views.showPet),
    url(r'^pets/approve/(?P<id>\d+)$', views.approvePet),
    url(r'^pets/destroy/(?P<id>\d+)$', views.deletePet),
    url(r'^pets/adopt/(?P<id>\d+)$', views.adoptPet),
    url(r'^pets/unadopt/(?P<id>\d+)$', views.unadoptPet)

]
