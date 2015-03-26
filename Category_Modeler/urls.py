from django.conf.urls import patterns, url
from Category_Modeler.views import index, trainingsampleprocessing, supervised, savetrainingdatadetails, saveNewTrainingVersion, signaturefile, visualization

urlpatterns = patterns('',
        url(r'^$', index),
        url(r'^trainingsample/$', trainingsampleprocessing),
        url(r'^signaturefile/$', signaturefile),  
        url(r'^supervised/$', supervised),
        url(r'^savetrainingdatadetails/$', savetrainingdatadetails),
        url(r'^saveNewTrainingVersion/', saveNewTrainingVersion),
        url(r'^visualizer/', visualization),
        
        
        
    )

