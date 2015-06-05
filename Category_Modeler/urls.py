from django.conf.urls import patterns, url
from Category_Modeler.views import index, trainingsampleprocessing, supervised, savetrainingdatadetails, saveNewTrainingVersion, signaturefile, visualization, login_view, logout

urlpatterns = patterns('',
        url(r'^$', index),
        url(r'^home/$', index),
        url(r'^trainingsample/$', trainingsampleprocessing),
        url(r'^signaturefile/$', signaturefile),  
        url(r'^supervised/$', supervised),
        url(r'^savetrainingdatadetails/$', savetrainingdatadetails),
        url(r'^saveNewTrainingVersion/', saveNewTrainingVersion),
        url(r'^visualizer/', visualization),
        url(r'^login/$', login_view),
        url(r'^logout/$', logout),
        
        
    )

