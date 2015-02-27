from django.conf.urls import patterns, url
from Category_Modeler.views import index, preprocess, supervised, savetrainingdatadetails, saveNewTrainingVersion

urlpatterns = patterns('',
        url(r'^$', index),
        url(r'^preprocess/$', preprocess),  
        url(r'^supervised/$', supervised),
        url(r'^savetrainingdatadetails/$', savetrainingdatadetails),
        url(r'^saveNewTrainingVersion/', saveNewTrainingVersion),
        
        
        
    )

