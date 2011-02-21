from django.conf.urls.defaults import *
from settings import MEDIA_ROOT

urlpatterns = patterns('website.views',
	(r'^$', 'index'),
	(r'^login/$', 'login'),
	(r'^signup/$', 'signup'),
	(r'^features/$', 'features'),
	(r'^learn/$', 'learn'),	
	(r'^plans/$', 'signup'),
	(r'^pricing/$', 'signup'),
	(r'^faqs/$', 'faqs'),
	(r'^support/$', 'support'),
)

urlpatterns += patterns('',
    (r'^assets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
)