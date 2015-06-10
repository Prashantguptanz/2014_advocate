from django.conf.urls import patterns, url
from Category_Modeler.views import index, trainingsampleprocessing, supervised, savetrainingdatadetails, saveNewTrainingVersion, signaturefile, visualization, loginrequired, logout_view, auth_view, register_view

urlpatterns = patterns('',
        url(r'^$', index),
        url(r'^home/$', index),
        url(r'^trainingsample/$', trainingsampleprocessing),
        url(r'^signaturefile/$', signaturefile),  
        url(r'^supervised/$', supervised),
        url(r'^savetrainingdatadetails/$', savetrainingdatadetails),
        url(r'^saveNewTrainingVersion/', saveNewTrainingVersion),
        url(r'^visualizer/', visualization),
        url(r'^accounts/loginrequired/', loginrequired),
        url(r'^accounts/logout/', logout_view),
        url(r'^accounts/auth/', auth_view),
        url(r'^accounts/register/', register_view)

        
        
    )

