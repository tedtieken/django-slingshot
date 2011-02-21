from django.conf.urls.defaults import *

urlpatterns = patterns('website.views',
    (r'^$', 'index'),
    (r'^login/$', 'login_signup'),    
    (r'^signup/$', 'login_signup'),    
    (r'^post/$', 'view_post'),

    # form actions
    (r'^login_action/$', 'login_action'),
    (r'^signup_action/$', 'signup_action'),    
    
    # for development only
    (r'^core_only/$', 'core_only'),
    (r'^core_right/$', 'core_right'),
)
