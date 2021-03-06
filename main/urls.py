from django.conf.urls import url
from main import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.user_login, name='user_login'),
    url(r'^logout$', views.user_logout, name='user_logout'),
    url(r'^signup$', views.user_signup, name='user_signup'),
    url(r'^user/(?P<id>\w+)', views.user_mypage, name='user_mypage'),
    url(r'^apikey/(?P<key>\w+)/secret', views.secret_key_new, name='secret_key_new'),
    url(r'^apikey/new', views.apikey_new, name='apikey_new'),
    url(r'^domain/new', views.domain_new, name='domain_new'),
    url(r'^jwt/new', views.jwt_new, name='jwt_new'),


    # dashboard test url

    url(r'dashboard_overview$', views.dashboard_overview, name='dashboard_overview'),
    url(r'dashboard_filter$', views.dashboard_filter, name='dashboard_filter'),
    url(r'dashboard_users$', views.dashboard_users, name='dashboard_users'),
]