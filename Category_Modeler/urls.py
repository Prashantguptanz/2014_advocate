from django.conf.urls import patterns, url
from Category_Modeler.views import index, saveexistingtaxonomydetails, savenewtaxonomydetails, trainingsampleprocessing, supervised, createChangeEventForNewTaxonomy, applyChangeOperations
from Category_Modeler.views import savetrainingdatadetails, saveNewTrainingVersion, signaturefile, visualizer, loginrequired, logout_view, auth_view, register_view, changeRecognizer

urlpatterns = patterns('',
        url(r'^$', index),
        url(r'^home/$', index),
        url(r'^saveexistingtaxonomydetails/$', saveexistingtaxonomydetails),
        url(r'^savenewtaxonomydetails/$', savenewtaxonomydetails),
        url(r'^trainingsample/$', trainingsampleprocessing),
        url(r'^signaturefile/$', signaturefile),  
        url(r'^supervised/$', supervised),
        url(r'^savetrainingdatadetails/$', savetrainingdatadetails),
        url(r'^saveNewTrainingVersion/', saveNewTrainingVersion),
        url(r'^changerecognition/', changeRecognizer),
        url(r'^createChangeEventForNewTaxonomy/', createChangeEventForNewTaxonomy),
        url(r'^applyChangeOperations/', applyChangeOperations),
        url(r'^visualizer/', visualizer),
        url(r'^accounts/loginrequired/', loginrequired),
        url(r'^accounts/logout/', logout_view),
        url(r'^accounts/auth/', auth_view),
        url(r'^accounts/register/', register_view)
        
        

        
        
    )

