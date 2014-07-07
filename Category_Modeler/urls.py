from django.conf.urls import patterns, url
from Category_Modeler.views import index, preprocess, modeler

urlpatterns = patterns('',
        url(r'^$', index),
        url(r'^preprocess/$', preprocess),  
        url(r'^modeler/$', modeler),
        
        
    )

