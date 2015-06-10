from django.conf.urls import patterns, url
from Category_Modeler.views import index, trainingsampleprocessing, supervised, savetrainingdatadetails, saveNewTrainingVersion, signaturefile, visualization, login_view, logout_view, auth_view
from Category_Modeler.views import register_view
urlpatterns = patterns('',
        url(r'^$', index),
        url(r'^home/$', index),
        url(r'^trainingsample/$', trainingsampleprocessing),
        url(r'^signaturefile/$', signaturefile),  
        url(r'^supervised/$', supervised),
        url(r'^savetrainingdatadetails/$', savetrainingdatadetails),
        url(r'^saveNewTrainingVersion/', saveNewTrainingVersion),
        url(r'^visualizer/', visualization),
        url(r'^accounts/login/', login_view),
        url(r'^accounts/logout/', logout_view),
        url(r'^accounts/auth/', auth_view),
        url(r'^accounts/register/', register_view)
       # url(r'^accounts/loggedin/', loggedin_view),
      #  url(r'^accounts/invalid_login', invalidlogin_view),

        
        
    )

