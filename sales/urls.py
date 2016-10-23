from django.conf.urls import url
from . import views

app_name = 'sales'
urlpatterns = [
    url(r'^$', views.welcome, name='index'),
    url(r'^login$', views.login_site, name='login_site'),
    url(r'^logout_site$', views.logout_site, name='logout_site'),
    url(r'^email$', views.check_email, name='email'),
    url(r'^client_info$', views.client_info, name='client_info'),
    url(r'^ticket_info$', views.ticket_info, name='ticket_info'),
    url(r'^thankyou$', views.thankyou, name='thankyou'),
    url(r'^welcome$', views.welcome, name='welcome'),
    url(r'^overview$', views.overview, name='overview')
]
