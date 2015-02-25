from django.conf.urls import patterns, url
from Category_Modeler.views import index, preprocess, supervised, savetrainingdatadetails

urlpatterns = patterns('',
        url(r'^$', index),
        url(r'^preprocess/$', preprocess),  
        url(r'^supervised/$', supervised),
        url(r'^savetrainingdatadetails/$', savetrainingdatadetails),
        
        
        
    )

