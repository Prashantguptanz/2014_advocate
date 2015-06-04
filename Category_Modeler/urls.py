from django.conf.urls import patterns, url
from Category_Modeler.views import index, trainingsampleprocessing, supervised, savetrainingdatadetails, saveNewTrainingVersion, signaturefile, visualization

urlpatterns = patterns('',
        url(r'^$', index),
        url(r'^home/$', index),
        url(r'^trainingsample/$', trainingsampleprocessing),
        url(r'^signaturefile/$', signaturefile),  
        url(r'^supervised/$', supervised),
        url(r'^savetrainingdatadetails/$', savetrainingdatadetails),
        url(r'^saveNewTrainingVersion/', saveNewTrainingVersion),
        url(r'^visualizer/', visualization),
        url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
        url(r'^logout/$', 'django.contrib.auth.views.logout'),
        
        
    )

