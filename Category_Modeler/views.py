import csv, json, numpy, pydot, os, re
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
from matplotlib import gridspec
from matplotlib.colors import ListedColormap
from io import FileIO, BufferedWriter
from datetime import datetime
from shutil import copyfile
from ete3 import Tree, TreeStyle, TextFace # @UndefinedVariable
from operator import itemgetter
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from sklearn import tree, svm, cross_validation, metrics
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn.naive_bayes import GaussianNB
from sklearn.externals.six import StringIO
from Category_Modeler.models import Trainingset, ChangeTrainingsetActivity, AuthUser, Classificationmodel, Classifier, LearningActivity, ChangeTrainingsetActivityDetails
from Category_Modeler.models import Confusionmatrix, ExplorationChain, ClassificationActivity, Legend, CreateTrainingsetActivity
from Category_Modeler.models import  CreateTrainingsetActivityOperations, SatelliteImage, ClassifiedSatelliteImage, ClusteringActivity
from Category_Modeler.measuring_categories import TrainingSet, NormalDistributionIntensionalModel, DecisionTreeIntensionalModel, StatisticalMethods, ClassifiedFile
from Category_Modeler.data_processing import ManageRasterData, ManageCSVData
from Category_Modeler.database_transactions import UpdateDatabase, CustomQueries
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris
from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.grid_search import GridSearchCV
from matplotlib.colors import Normalize


class MidpointNormalize(Normalize):

    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return numpy.ma.masked_array(numpy.interp(value, x, y))

#Different Files Locations
TRAINING_SAMPLES_IMAGES_LOCATION = 'Category_Modeler/static/data/'
EXISTING_TRAINING_SAMPLES_LOCATION = 'Category_Modeler/static/trainingsamples/'
EXISTING_TRAINING_DATA_LOCATION = 'Category_Modeler/static/trainingfiles/'
CLUSTERING_DATA_LOCATION = 'Category_Modeler/static/clusteringfiles/'
CLASSIFICATION_MODEL_LOCATION = 'Category_Modeler/static/classificationmodel/'
VALIDATION_DATA_LOCATION = 'Category_Modeler/static/validationfiles/'
IMAGE_LOCATION = 'Category_Modeler/static/images/'
TEST_DATA_LOCATION = 'Category_Modeler/static/testfiles/'
CLASSIFIED_DATA_LOCATION = 'Category_Modeler/static/predictedvalues/'
CLASSIFIED_DATA_IN_RGB_LOCATION = 'Category_Modeler/static/predictedvaluesRGB/'
OUTPUT_RASTER_FILE_LOCATION = 'Category_Modeler/static/maps/'
TAXONOMY_IMAGE_LOCATION = 'Category_Modeler/static/taxonomyimage/'
DEFAULT_JM_DISTANCE_THRESHOLD_LIMIT = 1.1
DEFAULT_ACCURACY_THRESHOLD_LIMIT = 0.6
CINT_MIN_THRESHOLD_LIMIT = 0.1
CINT_MAX_THRESHOLD_LIMIT = 0.5
EXT_MIN_THRESHOLD_LIMIT = 0.1
EXT_MAX_THRESHOLD_LIMIT = 0.5
# Login and logout methods

def register_view(request):
    if request.method == 'POST':
        data = request.POST;
        user_name = data['user_name'];
        firstname = data['first-name'];
        lastname = data['last-name'];
        emailid = data['email'];
        password = data['register_password'];
        
        new_user = AuthUser(username=user_name, first_name=firstname, last_name=lastname, email= emailid, password= password, date_joined=datetime.now())
        new_user.save()

        return HttpResponseRedirect("/AdvoCate/")


def loginrequired(request):
    loginerror=True
    return render(request, 'base.html', {'loginerror':loginerror})

def auth_view(request):
    if request.method=='POST': 
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # Correct password, and the user is marked "active"
            login(request, user)
            # Redirect to a success page.
            user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username# @UndefinedVariable
            return JsonResponse({'user_name':user_name})
        else:
            error = "Invalid username or password!"
            return JsonResponse({'error':error})


def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/AdvoCate/")


# Methods for home page to select the activity and save details in the session variable

def index(request):
    if '_auth_user_id' in request.session:
        user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username  # @UndefinedVariable
        customQuery = CustomQueries()
        
        if Legend.objects.exists(): # @UndefinedVariable
            legend_list = customQuery.get_latest_versions_of_all_legends()  # @UndefinedVariable
            print legend_list
            return render(request, 'home.html', {'user_name': user_name, 'legend_list':legend_list})
        return render(request, 'home.html', {'user_name': user_name})
    form = UserCreationForm()
    return render(request, 'home.html', {'form': form})

def saveexistingtaxonomydetails(request):
    if request.method == 'POST':
        data = request.POST
        legendpkey = data['1']
        lid, ver = legendpkey.split('+')
        legend_name = data['2']
        etrigger = data['3']
        request.session['existing_taxonomy_name'] = legend_name
        request.session['external_trigger'] = etrigger
        request.session['existing_taxonomy_id'] = lid
        request.session['existing_taxonomy_ver'] = ver
        request.session['jm_distance_limit'] = DEFAULT_JM_DISTANCE_THRESHOLD_LIMIT
        request.session['accuracy_limit'] = DEFAULT_ACCURACY_THRESHOLD_LIMIT
        request.session['cint_min_limit'] = CINT_MIN_THRESHOLD_LIMIT
        request.session['cint_max_limit'] = CINT_MAX_THRESHOLD_LIMIT
        request.session['ext_min_limit'] = EXT_MIN_THRESHOLD_LIMIT
        request.session['ext_max_limit'] = EXT_MAX_THRESHOLD_LIMIT
        if ExplorationChain.objects.all().exists():
            request.session['exploration_chain_id'] = ExplorationChain.objects.latest("id").id + 1
        else:
            request.session['exploration_chain_id'] =0
        request.session['exploration_chain_step'] = 1
    if 'new_taxonomy_name' in request.session:
        del request.session['new_taxonomy_name']
        del request.session['new_taxonomy_description']
        request.session.modified = True
    if 'view_existing_taxonomies' in request.session:
        del request.session['view_existing_taxonomies']
        request.session.modified = True
    if 'current_exploration_chain_viz' in request.session:
        del request.session['current_exploration_chain_viz']
        request.session.modified = True
    
    return HttpResponse("Upload new training samples or choose an existing one, and start the exploration process!");

def savenewtaxonomydetails(request):
    if request.method == 'POST':
        data = request.POST
        request.session['new_taxonomy_name'] = data['newtaxonomyname']
        request.session['new_taxonomy_description'] = data['description']
        request.session['jm_distance_limit'] = DEFAULT_JM_DISTANCE_THRESHOLD_LIMIT
        request.session['accuracy_limit'] = DEFAULT_ACCURACY_THRESHOLD_LIMIT
        request.session['cint_min_limit'] = CINT_MIN_THRESHOLD_LIMIT
        request.session['cint_max_limit'] = CINT_MAX_THRESHOLD_LIMIT
        request.session['ext_min_limit'] = EXT_MIN_THRESHOLD_LIMIT
        request.session['ext_max_limit'] = EXT_MAX_THRESHOLD_LIMIT
        if ExplorationChain.objects.all().exists():
            request.session['exploration_chain_id'] = ExplorationChain.objects.latest("id").id + 1
        else:
            request.session['exploration_chain_id'] =0
        
        request.session['exploration_chain_step'] = 1
    if 'existing_taxonomy_name' in request.session:
        del request.session['existing_taxonomy_name']
        del request.session['external_trigger']
        request.session.modified = True
    if 'view_existing_taxonomies' in request.session:
        del request.session['view_existing_taxonomies']
        request.session.modified = True
    if 'current_exploration_chain_viz' in request.session:
        del request.session['current_exploration_chain_viz']
        request.session.modified = True
    return HttpResponse("Upload training samples by switching to 'Training Samples' tab, and start the modelling process!");

def compareexistingtaxonomies(request):
    if request.method == 'POST':
        data = request.POST
        request.session['view_existing_taxonomies'] = True
    if 'existing_taxonomy_name' in request.session:
        del request.session['existing_taxonomy_name']
        del request.session['external_trigger']
        request.session.modified = True
    if 'new_taxonomy_name' in request.session:
        del request.session['new_taxonomy_name']
        del request.session['new_taxonomy_description']
        request.session.modified = True
    return HttpResponse("Click on Visualization tab and compare and explore the existing taxonomies!");

# The method allow user to upload the training data file, which is then saved on the server and displayed in a tabular format on the page

@login_required
@transaction.atomic
def trainingsampleprocessing(request):
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username
    authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
    #Check the activity type. If none selected, request the user to select one
    if 'new_taxonomy_name' not in request.session and 'existing_taxonomy_name' not in request.session :
            messages.error(request, "Choose an activity before you proceed further")
            return HttpResponseRedirect("/AdvoCate/home/", {'user_name': user_name})
    

    elif request.method == 'POST' and request.is_ajax():
        data = request.POST
        managedata = ManageRasterData()
        manageCsvData = ManageCSVData()
        customQuery = CustomQueries()

        
        if 'IsFirstSample' in data:
            if 'create_trainingset_activity_id' in request.session:
                del request.session['create_trainingset_activity_id']
            if 'new_categories' in request.session:
                del request.session['new_categories']
            if 'existing_categories' in request.session:      
                del request.session['existing_categories']
            if 'categories_merged_from_existing' in request.session:
                del request.session['categories_merged_from_existing']
            if 'categories_merged_from_new_and_existing' in request.session:
                del request.session['categories_merged_from_new_and_existing']
            if 'categories_split_from_existing' in request.session:
                del request.session['categories_split_from_existing']
                
            request.session.modified = True
            create_tset_activity = CreateTrainingsetActivity(creator_id = authuser_instance)
            create_tset_activity.save(force_insert=True)
            request.session['create_trainingset_activity_id'] = create_tset_activity.id
            
        
        # New training samples for a new taxonomy
        if request.FILES and 'new_taxonomy_name' in request.session:
            trainingFilesList = request.FILES.getlist('file')
            concept_list = data['concept_list']
            list_of_concepts = concept_list.split(',')
            trainingsetfilename = data ['trainingsetfilename'];
            researcherName = data['FieldResearcherName'];
            trainingstart = data['TrainingTimePeriodStartDate'];
            trainingend = data['TrainingTimePeriodEndDate'];
            otherDetails = data['Description'];
            
            request.session['current_training_file_name'] = trainingsetfilename
            if len(trainingFilesList)==1 and trainingFilesList[0].name.split(".")[-1] == "csv":                
                with open('%s%s' % (EXISTING_TRAINING_DATA_LOCATION, trainingsetfilename), 'wb') as trainingset_file:
                    foo = trainingFilesList[0].read(1024)  
                    while foo:
                        trainingset_file.write(foo)
                        foo = trainingFilesList[0].read(1024)
                    trainingset_file.close()
            elif len(trainingFilesList)>1 and trainingFilesList[0].name.split(".")[-1] == "tif":
                rasterFileNameList = []
                for rasterfile in trainingFilesList:
                    rasterFileNameList.append(rasterfile.name)
                managedata.combine_multiple_raster_files_to_csv_file(rasterFileNameList, request.session['current_training_file_name'], EXISTING_TRAINING_DATA_LOCATION)
            manageCsvData.remove_no_data_value(trainingsetfilename, EXISTING_TRAINING_DATA_LOCATION, trainingsetfilename, '0')
            
            #save trainingset
            if Trainingset.objects.all().exists():
                latestid = int (Trainingset.objects.latest("trainingset_id").trainingset_id) + 1
            else:
                latestid = 0
            tr = Trainingset(trainingset_id=latestid, trainingset_ver =1, trainingset_name=request.session['current_training_file_name'], date_expired=datetime(9999, 9, 12), filelocation=EXISTING_TRAINING_DATA_LOCATION)
            tr.save(force_insert=True)
            request.session['current_training_file_id'] = tr.trainingset_id
            request.session['current_training_file_ver'] = tr.trainingset_ver
            
            #save create trainingset activity
            create_tset_activity = CreateTrainingsetActivity(creator_id = authuser_instance, trainingset_id= tr.trainingset_id, trainingset_ver = tr.trainingset_ver, collector = researcherName, data_collection_start_date=trainingstart, data_collection_end_date = trainingend, other_details = otherDetails)
            create_tset_activity.save(force_insert=True)
            
            #save create training set activity operations
            for concept in list_of_concepts:
                create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_tset_activity, operation = 'add new', concept1 = concept)
                create_tset_activity_ops.save(force_insert=True)
            
            exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'create trainingset', activity_instance = create_tset_activity.id)
            exp_chain.save(force_insert=True)
            request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1
      
            if 'currenteditoperations' in request.session:
                del request.session['currenteditoperations']
                                
            if 'current_model_id' in request.session:
                del request.session['model_type']    
                del request.session['current_model_name']
                del request.session['current_model_id']
                del request.session['model_score']
                del request.session['producer_accuracies']
                del request.session['user_accuracies']
    
            if 'current_predicted_file_name' in request.session:
                del request.session['current_test_file_name']
                del request.session['current_predicted_file_name']
                del request.session['current_test_file_columns']
                del request.session['current_test_file_rows']
            request.session.modified = True    
                
            trs = TrainingSet(request.session['current_training_file_name'])
            classes = list(numpy.unique(trs.target))
            no_of_spectral_bands = len(list(trs.features)) - 1
            title = "Create trainingset: " + request.session['current_training_file_name']
            with open('%s%s' % (EXISTING_TRAINING_DATA_LOCATION, request.session['current_training_file_name']), 'rU') as trainingset:
                datareader = csv.reader(trainingset, delimiter=',')
                trainingsetasArray = list(datareader)
                trainingset.close()
            data_content = "Spectral bands: " + str(no_of_spectral_bands) + "<br/><br/>" + "<b>New concepts added:</b> "
            for concept in classes:
                data_content = data_content + "<br/>" + concept
                
            #adding details for current exploration details for visualization
            current_step = ['Create trainingset', title, data_content]

            if 'current_exploration_chain_viz' in request.session:
                current_exploration_chain_viz = request.session['current_exploration_chain_viz']
                if current_exploration_chain_viz[-1][0] == 'End':
                    current_exploration_chain_viz.pop()
                current_exploration_chain_viz.append(current_step)
                request.session['current_exploration_chain_viz'] = current_exploration_chain_viz
            else:
                request.session['current_exploration_chain_viz'] = [current_step]
                    
                
            return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz']})  
            
        #----------------------------------------------------------------------------------------------------------------
        elif 'IsFinalSample' in data and 'existing_taxonomy_name' in request.session:

            create_ts_activity_instance = CreateTrainingsetActivity.objects.get(id = int(request.session['create_trainingset_activity_id']))
            
            if data['IsFinalSample'] == 'False':
                conceptType = data['ConceptType']
                if conceptType=='1':
                    conceptName = data['ConceptName']
                                    
                    create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'add new', concept1 = conceptName)
                    create_tset_activity_ops.save(force_insert=True)
                    
                    if 'new_categories' in request.session:
                        new_categories = request.session['new_categories']
                        new_categories.append(conceptName)
                        request.session['new_categories'] = new_categories
                    else:
                        new_categories = [conceptName]
                        request.session['new_categories'] = new_categories
                    
                elif conceptType=='2':
                    conceptName = data['ConceptName']
    
                    create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'add existing', concept1 = conceptName)
                    create_tset_activity_ops.save(force_insert=True)
                    
                    if 'existing_categories' in request.session:
                        existing_categories = request.session['existing_categories']
                        existing_categories.append(conceptName)
                        request.session['existing_categories'] = existing_categories
                    else:
                        existing_categories = [conceptName]
                        request.session['existing_categories'] = existing_categories
                    
                elif conceptType=='3':
                    firstConceptName = data['FirstConceptName']
                    secondConceptName = data['SecondConceptName']
                    mergedConceptName = data['MergedConceptName']
    
                    create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'merge', concept1 = firstConceptName, concept2 = secondConceptName, concept3 = mergedConceptName)
                    create_tset_activity_ops.save(force_insert=True)
                    
                    if 'categories_merged_from_existing' in request.session:
                        categories_merged_from_existing = request.session['categories_merged_from_existing']
                        categories_merged_from_existing.append([firstConceptName, secondConceptName, mergedConceptName])
                        request.session['existing_categories'] = categories_merged_from_existing
                    else:
                        categories_merged_from_existing = [[firstConceptName, secondConceptName, mergedConceptName]]
                        request.session['categories_merged_from_existing'] = categories_merged_from_existing
                    
                else:
                    conceptToSplit = data['ConceptToSplit']
                    conceptstosplitinto = data['conceptstosplitinto']
                    namesofsplitconcepts = conceptstosplitinto.split(',')
                    
                    if (len(namesofsplitconcepts)==3):
                        create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'split', concept1 = conceptToSplit, concept2 = namesofsplitconcepts[0], concept3 = namesofsplitconcepts[1], concept4 = namesofsplitconcepts[2])
                        create_tset_activity_ops.save(force_insert=True)
                        category_split_details = [conceptToSplit, namesofsplitconcepts[0], namesofsplitconcepts[1], namesofsplitconcepts[2]]
                    else:
                        create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'split', concept1 = conceptToSplit, concept2 = namesofsplitconcepts[0], concept3 = namesofsplitconcepts[1])
                        create_tset_activity_ops.save(force_insert=True)
                        category_split_details = [conceptToSplit, namesofsplitconcepts[0], namesofsplitconcepts[1]]
                        
                    
                    if 'categories_split_from_existing' in request.session:
                        categories_split_from_existing = request.session['categories_split_from_existing']
                        categories_split_from_existing.append(category_split_details)
                        request.session['categories_split_from_existing'] = categories_split_from_existing
                    else:
                        categories_split_from_existing = [category_split_details]
                        request.session['categories_split_from_existing'] = categories_split_from_existing
                
                return HttpResponse("")
                    
            else:
                trainingFilesList = request.FILES.getlist('file')
                trainingsetfilename = data ['trainingsetfilename'];
                researcherName = data['FieldResearcherName'];
                trainingstart = data['TrainingTimePeriodStartDate'];
                trainingend = data['TrainingTimePeriodEndDate'];
                otherDetails = data['Description'];
                
                request.session['current_training_file_name'] = trainingsetfilename
                if len(trainingFilesList)==1 and trainingFilesList[0].name.split(".")[-1] == "csv":                
                    with open('%s%s' % (EXISTING_TRAINING_DATA_LOCATION, trainingsetfilename), 'wb') as trainingset_file:
                        foo = trainingFilesList[0].read(1024)  
                        while foo:
                            trainingset_file.write(foo)
                            foo = trainingFilesList[0].read(1024)
                        trainingset_file.close()
                elif len(trainingFilesList)>1 and trainingFilesList[0].name.split(".")[-1] == "tif":
                    rasterFileNameList = []
                    for rasterfile in trainingFilesList:
                        rasterFileNameList.append(rasterfile.name)
                    managedata.combine_multiple_raster_files_to_csv_file(rasterFileNameList, request.session['current_training_file_name'], EXISTING_TRAINING_DATA_LOCATION)
                manageCsvData.remove_no_data_value(trainingsetfilename, EXISTING_TRAINING_DATA_LOCATION, trainingsetfilename, '0')
            
                #save trainingset
                latestid = int (Trainingset.objects.latest("trainingset_id").trainingset_id) + 1
                tr = Trainingset(trainingset_id=latestid, trainingset_ver =1, trainingset_name=request.session['current_training_file_name'], date_expired=datetime(9999, 9, 12), filelocation=EXISTING_TRAINING_DATA_LOCATION)
                tr.save(force_insert=True)
                request.session['current_training_file_id'] = tr.trainingset_id
                request.session['current_training_file_ver'] = tr.trainingset_ver
                
                old_trainingset = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])
                create_ts_activity_instance.reference_trainingset_id = old_trainingset[0]
                create_ts_activity_instance.reference_trainingset_ver = old_trainingset[1]
                create_ts_activity_instance.trainingset_id = request.session['current_training_file_id']
                create_ts_activity_instance.trainingset_ver = request.session['current_training_file_ver']
                create_ts_activity_instance.collector = researcherName
                create_ts_activity_instance.data_collection_start_date=trainingstart
                create_ts_activity_instance.data_collection_end_date = trainingend
                create_ts_activity_instance.other_details = otherDetails
                create_ts_activity_instance.save(force_update=True)
                
                exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'create trainingset', activity_instance = create_ts_activity_instance.id)
                exp_chain.save(force_insert=True)
                request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1
                
                if 'currenteditoperations' in request.session:
                    del request.session['currenteditoperations']
                
                if 'current_model_id' in request.session:
                    del request.session['model_type']    
                    del request.session['current_model_name']
                    del request.session['current_model_id']
                    del request.session['model_score']
                    del request.session['producer_accuracies']
                    del request.session['user_accuracies']
        
                if 'current_predicted_file_name' in request.session:
                    del request.session['current_test_file_name']
                    del request.session['current_predicted_file_name']
                    del request.session['current_test_file_columns']
                    del request.session['current_test_file_rows']
                request.session.modified = True
                
                trainingsetasArray = []
                trs = TrainingSet(request.session['current_training_file_name'])
                classes = list(numpy.unique(trs.target))
                with open('%s%s' % (EXISTING_TRAINING_DATA_LOCATION, request.session['current_training_file_name']), 'rU') as trainingset:
                    datareader = csv.reader(trainingset, delimiter=',')
                    trainingsetasArray = list(datareader)
                    trainingset.close()
                new_training_sample = TrainingSet(request.session['current_training_file_name'])
                old_training_sample = TrainingSet(old_trainingset[2])
                common_categories, new_categories, deprecated_categories = new_training_sample.compare_training_samples(old_training_sample)
                
                #adding details for current exploration details for visualization
                old_spectral_bands_no = len(old_training_sample.features)-1
                new_spectral_bands_no = len(new_training_sample.features)-1
                new_trainingset_name = request.session['current_training_file_name']
                reference_trainingset_name = old_trainingset[2]
                data_content = "Reference trainingset: " + reference_trainingset_name + " (" + str(old_spectral_bands_no) + "spectral bands)<br/> New trainingset: " + new_trainingset_name + " (" + str(new_spectral_bands_no) + "spectral bands)<br/><br/>" + "<b>Concepts in new trainingset:<b> <br/><br/>"
                
                
                if 'new_categories' in request.session:
                    new_categories = request.session['new_categories']
                    data_content = data_content + "<b>New concepts:</b><br/>"
                    for category in new_categories:
                        data_content = data_content + category + "<br/>"
                    data_content = data_content + "<br/>"
                
                if 'existing_categories' in request.session:
                    existing_categories = request.session['existing_categories']
                    data_content = data_content + "<b>Existing concepts:</b><br/>"
                    for category in existing_categories:
                        data_content = data_content + category + "<br/>"
                    data_content = data_content + "<br/>"
                
                if 'categories_merged_from_existing' in request.session:
                    categories_merged_from_existing = request.session['categories_merged_from_existing']
                    data_content = data_content + "<b>Merged concept:</b><br/>"
                    for category in categories_merged_from_existing:
                        data_content = data_content + category[0] + " and " + category[1] + " merged to create " + category[2] + "<br/>"
                    data_content = data_content + "<br/>"
                
                if 'categories_split_from_existing' in request.session:
                    categories_split_from_existing = request.session['categories_split_from_existing']
                    data_content = data_content + "<b>Split concepts:</b><br/>"
                    for category in categories_split_from_existing:
                        if len(category) == 3:
                            data_content = data_content + category[0] + " split into " + category[1] + " and " + category[2] + "<br/>"
                        else:
                            data_content = data_content + category[0] + " split into " + category[1] + ", " + category[2] +  " and " + category[3] +"<br/>"
                    data_content = data_content + "<br/>"
                      
                
                current_step = ['Create trainingset', 'Create trainingset', data_content]
                
                if 'current_exploration_chain_viz' in request.session:
                    current_exploration_chain_viz = request.session['current_exploration_chain_viz']
                    if current_exploration_chain_viz[-1][0] == 'End':
                        current_exploration_chain_viz.pop()
                    current_exploration_chain_viz.append(current_step)
                    request.session['current_exploration_chain_viz'] = current_exploration_chain_viz
                else:
                    request.session['current_exploration_chain_viz'] = [current_step]
               
                
                if len(common_categories) != 0 and isinstance(common_categories[0], list)==False:
                    common_categories_message = "The two training samples have different number of bands; so, we cannot compare common categories based on training samples"
                    return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories, 'common_categories_message':common_categories_message})
        
                return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories})

        else:
            trainingfilepkey = data['1']
            trid, ver = trainingfilepkey.split('+')
            trainingfilename = data['2']
            if 'new_taxonomy_name' in request.session:
                request.session['current_training_file_id'] = trid
                request.session['current_training_file_ver'] = ver
                request.session['current_training_file_name'] = trainingfilename
            elif 'current_training_file_id' not in request.session:
                request.session['current_training_file_id'] = trid
                request.session['current_training_file_ver'] = ver
                request.session['current_training_file_name'] = trainingfilename
                old_trainingset = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])
                old_training_sample = TrainingSet(old_trainingset[2])
                new_training_sample = TrainingSet(request.session['current_training_file_name'])
                common_categories, new_categories, deprecated_categories = new_training_sample.compare_training_samples(old_training_sample)
                list_of_common_categories = []
                for each_category in common_categories:
                    if type(each_category) is list:
                        list_of_common_categories.append(each_category[0])
                    else:
                        list_of_common_categories.append(each_category)
                request.session['existing_categories'] = list_of_common_categories
                request.session['new_categories'] = new_categories
                               
            else:
                if int(request.session['current_training_file_id']) != int(trid) or int(request.session['current_training_file_ver']) != int(ver):
                    old_trid = request.session['current_training_file_id']
                    old_ver = request.session['current_training_file_ver']
                    if 'trainingset_version_and_categories_relationship' in request.session:
                        not_existing = True
                        for each_set in request.session['trainingset_version_and_categories_relationship']:
                            if each_set[0] == old_trid and each_set[1] == old_ver:
                                not_existing = False
                                break;
                        if not_existing == True:
                            new_categories_while_exploring_changes = []
                            existing_categories = []
                            categories_merged_from_existing = []
                            categories_split_from_existing = []
                            categories_merged_from_new_and_existing = []
                            if 'new_categories' in request.session:
                                new_categories_while_exploring_changes = request.session['new_categories']
                            if 'existing_categories' in request.session:
                                existing_categories = request.session['existing_categories']
                            if 'categories_merged_from_existing' in request.session:
                                categories_merged_from_existing = request.session['categories_merged_from_existing']
                            if 'categories_split_from_existing' in request.session:
                                categories_split_from_existing = request.session['categories_split_from_existing']
                            if 'categories_merged_from_new_and_existing' in request.session:
                                categories_merged_from_new_and_existing = request.session['categories_merged_from_new_and_existing']
                            old_version_and_categories_relationships = [old_trid, old_ver, new_categories_while_exploring_changes, existing_categories, categories_merged_from_existing, categories_split_from_existing, categories_merged_from_new_and_existing]
                            trainingset_version_and_categories_relationship = request.session['trainingset_version_and_categories_relationship']
                            trainingset_version_and_categories_relationship.append(old_version_and_categories_relationships)
                            request.session['trainingset_version_and_categories_relationship'] = trainingset_version_and_categories_relationship
                    else:
                        new_categories_while_exploring_changes = []
                        existing_categories = []
                        categories_merged_from_existing = []
                        categories_split_from_existing = []
                        categories_merged_from_new_and_existing = []
                        if 'new_categories' in request.session:
                            new_categories_while_exploring_changes = request.session['new_categories']
                        if 'existing_categories' in request.session:
                            existing_categories = request.session['existing_categories']
                        if 'categories_merged_from_existing' in request.session:
                            categories_merged_from_existing = request.session['categories_merged_from_existing']
                        if 'categories_split_from_existing' in request.session:
                            categories_split_from_existing = request.session['categories_split_from_existing']
                        if 'categories_merged_from_new_and_existing' in request.session:
                            categories_merged_from_new_and_existing = request.session['categories_merged_from_new_and_existing']
                        old_version_and_categories_relationships = [old_trid, old_ver, new_categories_while_exploring_changes, existing_categories, categories_merged_from_existing, categories_split_from_existing, categories_merged_from_new_and_existing]
                        request.session['trainingset_version_and_categories_relationship'] = [old_version_and_categories_relationships]

                    
                    
                    request.session['current_training_file_id'] = trid
                    request.session['current_training_file_ver'] = ver
                    request.session['current_training_file_name'] = trainingfilename
                    if 'existing_categories' in request.session:
                        del request.session['existing_categories']
                    if 'new_categories' in request.session:
                        del request.session['new_categories']
                    if 'categories_split_from_existing' in request.session:
                        del request.session['categories_split_from_existing']
                    if 'categories_merged_from_existing' in request.session:
                        del request.session['categories_merged_from_existing']
                    if 'categories_merged_from_new_and_existing' in request.session:
                        del request.session['categories_merged_from_new_and_existing']                        
                    request.session.modified = True
                    
                    if_in_existing = False
                    for each_set in request.session['trainingset_version_and_categories_relationship']:
                        if each_set[0] == trid and each_set[1] == ver:
                            request.session['new_categories'] = each_set[2]
                            request.session['existing_categories'] = each_set[3]
                            request.session['categories_merged_from_existing'] = each_set[4]
                            request.session['categories_split_from_existing'] = each_set[5]
                            request.session['categories_merged_from_new_and_existing']= each_set[6]
                            if_in_existing = True
                            break
                    
                    if if_in_existing == False:
                        old_trainingset = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])
                        old_training_sample = TrainingSet(old_trainingset[2])
                        new_training_sample = TrainingSet(request.session['current_training_file_name'])
                        common_categories, new_categories, deprecated_categories = new_training_sample.compare_training_samples(old_training_sample)
                        list_of_common_categories = []
                        for each_category in common_categories:
                            if type(each_category) is list:
                                list_of_common_categories.append(each_category[0])
                            else:
                                list_of_common_categories.append(each_category)
                        request.session['existing_categories'] = list_of_common_categories
                        request.session['new_categories'] = new_categories

                
            
            trainingfilelocation = (Trainingset.objects.get(trainingset_id=trid, trainingset_ver=ver)).filelocation # @UndefinedVariable
            trainingsetasArray = []
            trs = TrainingSet(request.session['current_training_file_name'])
            classes = list(numpy.unique(trs.target))
                
            with open('%s%s' % (trainingfilelocation, trainingfilename), 'rU') as trainingset:
                datareader = csv.reader(trainingset, delimiter=',')
                trainingsetasArray = list(datareader)
                trainingset.close()
                
            if 'currenteditoperations' in request.session:
                del request.session['currenteditoperations']
                request.session.modified = True
            
            if 'current_model_id' in request.session:
                del request.session['model_type']    
                del request.session['current_model_name']
                del request.session['current_model_id']
                del request.session['model_score']
                del request.session['producer_accuracies']
                del request.session['user_accuracies']
                request.session.modified = True
    
            if 'current_predicted_file_name' in request.session:
                del request.session['current_test_file_name']
                del request.session['current_predicted_file_name']
                del request.session['current_test_file_columns']
                del request.session['current_test_file_rows']
                request.session.modified = True

            
            if 'existing_taxonomy_name' in request.session:    
                old_trainingset = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])
                new_training_sample = TrainingSet(request.session['current_training_file_name'])
                old_training_sample = TrainingSet(old_trainingset[2])
                common_categories, new_categories, deprecated_categories = new_training_sample.compare_training_samples(old_training_sample)
                if isinstance(common_categories[0], list)==False:
                    common_categories_message = "The two training samples have different number of bands; so, we cannot compare common categories based on training samples"
                    return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes, 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories, 'common_categories_message':common_categories_message})
                
                return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes, 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories})

            return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes})        
    else:
        if 'new_taxonomy_name' not in request.session:
            existing_taxonomy = request.session['existing_taxonomy_name']
            print existing_taxonomy
            if Trainingset.objects.exists(): # @UndefinedVariable
                training_set_list = Trainingset.objects.all()  # @UndefinedVariable
            print request.session['existing_taxonomy_id']
            print request.session['existing_taxonomy_ver']
            customQuery = CustomQueries()
            old_trainingset_name = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])[2]
            old_training_sample = TrainingSet(old_trainingset_name)
            category_list = list(numpy.unique(old_training_sample.target))
            if 'current_exploration_chain_viz' in request.session:
                return render(request, 'trainingsample.html', {'training_set_list':training_set_list, 'user_name': user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'existing_taxonomy': existing_taxonomy, 'concept_list': category_list})
            else:            
                return render(request, 'trainingsample.html', {'training_set_list':training_set_list, 'user_name': user_name, 'existing_taxonomy': existing_taxonomy, 'concept_list': category_list})
        else:
            new_taxonomy =    request.session['new_taxonomy_name'] 
            if Trainingset.objects.exists(): # @UndefinedVariable
                training_set_list = Trainingset.objects.all()  # @UndefinedVariable
                if 'current_exploration_chain_viz' in request.session:
                    return render(request, 'trainingsample.html', {'training_set_list':training_set_list, 'user_name': user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'new_taxonomy_name': new_taxonomy})
                else:
                    return render(request, 'trainingsample.html', {'training_set_list':training_set_list, 'user_name': user_name, 'new_taxonomy_name': new_taxonomy})
            else:
                return render(request, 'trainingsample.html', {'user_name': user_name, 'new_taxonomy_name': new_taxonomy})
        

def edittrainingset(request):
    if request.method=='POST':
        managedata = ManageRasterData()
        data = request.POST
        editoperation_no = data['1']
        editoperaiton_details = []
        editoperaiton_details.append(editoperation_no)
        if editoperation_no=='1':
            new_concept_name = data['conceptname']
            trainingsamples = request.FILES.getlist('samplesfornewconcept')
            samplefilenamefortheconcept = new_concept_name + str(datetime.now()) + ".csv"
            trainingSamplesFileList = []
            for trainingSamples in trainingsamples:
                trainingSamplesFileList.append(trainingSamples.name)
            managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList, samplefilenamefortheconcept, EXISTING_TRAINING_SAMPLES_LOCATION, new_concept_name)
            editoperaiton_details.append(new_concept_name)
            editoperaiton_details.append(samplefilenamefortheconcept)
        elif editoperation_no=='2':
            concept_to_remove = data['2'];
            editoperaiton_details.append(concept_to_remove)
        elif editoperation_no=='3':
            concept_to_rename = data['2']
            new_name = data['3']
            editoperaiton_details.append(concept_to_rename)
            editoperaiton_details.append(new_name)
        elif editoperation_no=='4':
            concepttoedit = data['concepttoedit']
            trainingsamples = request.FILES.getlist('newsamples')
            samplefilenamefortheconcept = concepttoedit + str(datetime.now()) + ".csv"
            trainingSamplesFileList = []
            for trainingSamples in trainingsamples:
                trainingSamplesFileList.append(trainingSamples.name)
            managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList, samplefilenamefortheconcept, EXISTING_TRAINING_SAMPLES_LOCATION, concepttoedit)
            editoperaiton_details.append(concepttoedit)
            editoperaiton_details.append(samplefilenamefortheconcept)
        elif editoperation_no=='5':
            conceptstomerge = []
            concept1tomerge = data['concept1tomerge']
            concept2tomerge = data['concept2tomerge']
            conceptstomerge.append(concept1tomerge)
            conceptstomerge.append(concept2tomerge)
            if 'concept3tomerge' in data:
                concept3tomerge = data['concept3tomerge']
                conceptstomerge.append(concept3tomerge)
            mergedconceptname = data['mergedconceptname'];
            editoperaiton_details.append(conceptstomerge)
            editoperaiton_details.append(mergedconceptname)
        elif editoperation_no=='6':
            conceptstogroup = []
            concept1togroup = data['concept1togroup']
            concept2togroup = data['concept2togroup']
            conceptstogroup.append(concept1togroup)
            conceptstogroup.append(concept2togroup)
            if 'concept3togroup' in data:
                concept3togroup = data['concept3togroup']
                conceptstogroup.append(concept3togroup)
            groupedconceptname = data['groupedconceptname'];
            editoperaiton_details.append(conceptstogroup)
            editoperaiton_details.append(groupedconceptname)
        else:
            trainingsamplesforfirstconcept = request.FILES.getlist('filesforconcept1')
            trainingsamplesforsecondconcept = request.FILES.getlist('filesforconcept2')
            concepttosplit = data['concepttosplit']
            concept1 = data['concept1']
            concept2 = data['concept2']
            
            #Combine multiple samples and save it as a csv file
            samplefilenameforfirstconcept = concept1 + str(datetime.now()) + ".csv"
            samplefilenameforsecondconcept = concept2 + str(datetime.now()) + ".csv"
            trainingSamplesFileList1 = []
            trainingSamplesFileList2 = []
            for trainingSamples in trainingsamplesforfirstconcept:
                trainingSamplesFileList1.append(trainingSamples.name)
            for trainingSamples in trainingsamplesforsecondconcept:
                trainingSamplesFileList2.append(trainingSamples.name)
                
            
            managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList1, samplefilenameforfirstconcept, EXISTING_TRAINING_SAMPLES_LOCATION, concept1)
            managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList2, samplefilenameforsecondconcept, EXISTING_TRAINING_SAMPLES_LOCATION, concept2)

            
            editoperaiton_details.append(concepttosplit)
            editoperaiton_details.append(concept1)
            editoperaiton_details.append(samplefilenameforfirstconcept)
            editoperaiton_details.append(concept2)
            editoperaiton_details.append(samplefilenameforsecondconcept)
            
        
        if 'currenteditoperations' in request.session:
            currenteditoperations = request.session['currenteditoperations']
            currenteditoperations.append(editoperaiton_details)
            request.session['currenteditoperations'] = currenteditoperations
        else:
            currenteditoperations = []
            currenteditoperations.append(editoperaiton_details)
            request.session['currenteditoperations'] = currenteditoperations
    
    return HttpResponse("done");

@transaction.atomic
def applyeditoperations(request):
    
    currenteditoperations = request.session['currenteditoperations']
    trid = request.session['current_training_file_id']
    ver = request.session['current_training_file_ver']
    trainingfilename = request.session['current_training_file_name']
    manageCsvData = ManageCSVData()
    fname = "temp.csv"
    customQuery = CustomQueries()
    
    latestver = int(customQuery.get_latest_version_of_a_trainingset(trid)) + 1
    newfilename = trainingfilename.rpartition('_')[0] + "_VER" + str(latestver) + ".csv"
    Trainingset.objects.filter(trainingset_id=int(trid), trainingset_ver =int(ver)).update(date_expired = datetime.now())

    tr = Trainingset(trainingset_id=int(trid), trainingset_ver =latestver, trainingset_name=newfilename, date_expired=datetime(9999, 9, 12), filelocation=EXISTING_TRAINING_DATA_LOCATION)
    tr.save(force_insert=True)
    authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
    
    tr_activity = ChangeTrainingsetActivity( oldtrainingset_id= int(trid), oldtrainingset_ver =int(ver), newtrainingset_id=int(trid), newtrainingset_ver=int(ver)+1, completed_by=authuser_instance)
    tr_activity.save(force_insert=True)
    
    for editoperation in currenteditoperations:
        if os.path.isfile(EXISTING_TRAINING_DATA_LOCATION + "temp.csv"):
            trainingfilename = fname
        if editoperation[0] == '1':
            new_concept_name = editoperation[1]
            samplefile_for_new_concept = editoperation[2]
            manageCsvData.add_new_concept(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", new_concept_name, samplefile_for_new_concept, EXISTING_TRAINING_SAMPLES_LOCATION)         
            tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'add', concept1= new_concept_name)
            tr_activity_details.save(force_insert=True)
            
        elif editoperation[0] == '2':
            concept_to_remove = editoperation[1]
            manageCsvData.removeConcept(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", concept_to_remove)
            tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'remove', concept1= concept_to_remove)
            tr_activity_details.save(force_insert=True)
            
        elif editoperation[0] == '3':
            concept_to_rename = editoperation[1]
            new_name = editoperation[2]
            manageCsvData.renameConcept(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", concept_to_rename, new_name)
            tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'rename', concept1= concept_to_rename, concept2 = new_name)
            tr_activity_details.save(force_insert=True)
        
        elif editoperation[0] == '4':
            concepttoedit = editoperation[1]
            samplefilenamefortheconcept = editoperation[2]
            manageCsvData.removeConcept(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", concepttoedit)
            manageCsvData.add_new_concept("temp.csv", EXISTING_TRAINING_DATA_LOCATION, "temp.csv", concepttoedit, samplefilenamefortheconcept, EXISTING_TRAINING_SAMPLES_LOCATION)
            tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'edit', concept1= concepttoedit)
            tr_activity_details.save(force_insert=True)
            
        elif editoperation[0] == '5':
            
            mergedconceptname = editoperation[2]
            concepts_to_merge = editoperation[1]
            manageCsvData.mergeConcepts(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", concepts_to_merge, mergedconceptname)
                        
            if (len(concepts_to_merge) ==2):
                tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'merge', concept1= concepts_to_merge[0], concept2 = concepts_to_merge[1], concept3 = mergedconceptname)
            else:
                tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'merge', concept1= concepts_to_merge[0], concept2 = concepts_to_merge[1], concept3 = concepts_to_merge[2], concept4 = mergedconceptname)
            tr_activity_details.save(force_insert=True)
        
        elif editoperation[0] == '6':
            conceptstogroup = editoperation[1]
            groupedconceptname = editoperation[2]
        else:
            concepttosplit = editoperation[1];
            firstconcept = editoperation[2];
            samplefilenameforfirstconcept = editoperation[3];
            secondconcept = editoperation[4];
            samplefilenameforsecondconcept = editoperation[5];
            manageCsvData.splitconcept(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", concepttosplit, firstconcept, samplefilenameforfirstconcept, secondconcept, samplefilenameforsecondconcept, EXISTING_TRAINING_SAMPLES_LOCATION)

            tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'split', concept1= concepttosplit, concept2 = firstconcept, concept3 = secondconcept)
            tr_activity_details.save(force_insert=True)
        
        if 'existing_taxonomy_name' in request.session:
            new_categories_while_exploring_changes = []
            existing_categories = []
            categories_merged_from_existing = []
            categories_split_from_existing = []
            categories_merged_from_new_and_existing = []
            grouped_categories = []
            renamed_existing_categories = []
            if 'new_categories' in request.session:
                new_categories_while_exploring_changes = request.session['new_categories']
            if 'existing_categories' in request.session:
                existing_categories = request.session['existing_categories']
            if 'categories_merged_from_existing' in request.session:
                categories_merged_from_existing = request.session['categories_merged_from_existing']
            if 'categories_split_from_existing' in request.session:
                categories_split_from_existing = request.session['categories_split_from_existing']
            if 'categories_merged_from_new_and_existing' in request.session:
                categories_merged_from_new_and_existing = request.session['categories_merged_from_new_and_existing']
            if 'grouped_categories' in request.session:
                grouped_categories = request.session['grouped_categories']
            if 'renamed_existing_categories' in request.session:
                renamed_existing_categories = request.session['renamed_existing_categories']
            
            #save the relationships of categories from trainingset, which is just versioned, with the categories from trainingset of existing taxonomy that we are trying to change
            old_version_and_categories_relationships = [trid, ver, [elem for elem in new_categories_while_exploring_changes], [elem for elem in existing_categories], [elem for elem in categories_merged_from_existing], [elem for elem in categories_split_from_existing], [elem for elem in categories_merged_from_new_and_existing]]
            
            if 'trainingset_version_and_categories_relationship' in request.session:
                trainingset_version_and_categories_relationship = request.session['trainingset_version_and_categories_relationship']
                trainingset_version_and_categories_relationship.append(old_version_and_categories_relationships)
                request.session['trainingset_version_and_categories_relationship'] = trainingset_version_and_categories_relationship
            else:
                request.session['trainingset_version_and_categories_relationship'] = [old_version_and_categories_relationships]
                
            #Update the relationship of concepts when add a new concept
            if editoperation[0] == '1':
                new_categories_while_exploring_changes.append(new_concept_name)
                request.session['new_categories'] = new_categories_while_exploring_changes
            #Update the relationship of concepts when remove a concept          
            elif editoperation[0] == '2':
                if concept_to_remove in new_categories_while_exploring_changes:
                    new_categories_while_exploring_changes.remove(concept_to_remove)
                    request.session['new_categories'] = new_categories_while_exploring_changes
                elif concept_to_remove in existing_categories:
                    existing_categories.remove(concept_to_remove)
                    request.session['existing_categories'] = existing_categories
                elif len([True for x in renamed_existing_categories if concept_to_remove in x]) >0:
                    request.session['renamed_existing_categories'] = [y for y in renamed_existing_categories if concept_to_remove not in y]
                else:
                    found_the_category = False
                    if (len(categories_merged_from_existing) !=0):
                        for merged_category in categories_merged_from_existing:
                            if merged_category[-1] == concept_to_remove:
                                categories_merged_from_existing.remove(merged_category)
                                request.session['categories_merged_from_existing'] = categories_merged_from_existing
                                found_the_category = True
                                break
                            
                    if found_the_category==False and (len(categories_merged_from_new_and_existing) !=0):
                        for merged_category in categories_merged_from_new_and_existing:
                            if merged_category[-1] == concept_to_remove:
                                categories_merged_from_new_and_existing.remove(merged_category)
                                request.session['categories_merged_from_new_and_existing'] = categories_merged_from_new_and_existing
                                found_the_category = True
                                break
                    
                    if found_the_category==False and (len(categories_split_from_existing) !=0):
                        for each_set in categories_split_from_existing:
                            if concept_to_remove in each_set:
                                x = each_set
                                x.remove(concept_to_remove)
                                #x.append("sub-classes")
                                categories_split_from_existing.remove(each_set)
                                categories_split_from_existing.append(x)
                                request.session['categories_split_from_existing'] = categories_split_from_existing
                                found_the_category = True
                                break
                if (len(grouped_categories) !=0):
                    for each_set in grouped_categories:
                        if concept_to_remove in each_set:
                            x = each_set
                            x.remove(concept_to_remove)
                            grouped_categories.remove(each_set)
                            grouped_categories.append(x)
                            request.session['grouped_categories'] = grouped_categories
                            break
                                
            #Update the relationship of concepts when renamed a concept
            elif editoperation[0] == '3':
                if concept_to_rename in new_categories_while_exploring_changes:
                    new_categories_while_exploring_changes.remove(concept_to_rename)
                    new_categories_while_exploring_changes.append(new_name)
                    request.session['new_categories'] = new_categories_while_exploring_changes
                elif concept_to_rename in existing_categories:
                    existing_categories.remove(concept_to_rename)
                    request.session['existing_categories'] = existing_categories
                    renamed_existing_categories.append(new_name)
                    request.session['renamed_existing_categories'] = renamed_existing_categories
                elif len([True for x in renamed_existing_categories if concept_to_rename in x]) >0:
                    for each_set in renamed_existing_categories:
                        if concept_to_rename in each_set:
                            x = each_set
                            x.remove(concept_to_rename)
                            x.append(new_name)
                            renamed_existing_categories.remove(each_set)
                            renamed_existing_categories.append(x)
                            request.session['renamed_existing_categories'] = renamed_existing_categories
                            break
                else:
                    found_the_category = False
                    if (len(categories_merged_from_existing) !=0):
                        for merged_category in categories_merged_from_existing:
                            if merged_category[-1] == concept_to_rename:
                                x = merged_category
                                categories_merged_from_existing.remove(merged_category)
                                x.pop()
                                x.append(new_name)
                                categories_merged_from_existing.append(x)
                                request.session['categories_merged_from_existing'] = categories_merged_from_existing
                                found_the_category = True
                                break
                    if found_the_category==False and (len(categories_merged_from_new_and_existing) !=0):
                        for merged_category in categories_merged_from_new_and_existing:
                            if merged_category[-1] == concept_to_rename:
                                x = merged_category
                                categories_merged_from_new_and_existing.remove(merged_category)
                                x.pop()
                                x.append(new_name)
                                categories_merged_from_new_and_existing.append(x)
                                request.session['categories_merged_from_new_and_existing'] = categories_merged_from_new_and_existing
                                found_the_category = True
                                break
                    
                    if found_the_category==False and (len(categories_split_from_existing) !=0):
                        for each_set in categories_split_from_existing:
                            if concept_to_rename in each_set:
                                x = each_set
                                categories_split_from_existing.remove(each_set)
                                x.remove(concept_to_rename)
                                x.append(new_name)
                                categories_split_from_existing.append(x)
                                request.session['categories_split_from_existing'] = categories_split_from_existing
                                found_the_category = True
                                break
                if (len(grouped_categories) !=0):
                    for each_set in grouped_categories:
                        if concept_to_rename in each_set:
                            x = each_set
                            x.remove(concept_to_rename)
                            x.insert(0, new_name)
                            grouped_categories.remove(each_set)
                            grouped_categories.append(x)
                            request.session['grouped_categories'] = grouped_categories
                            break
              
                            
            #Update the relationship of concepts when merging concepts          
            elif editoperation[0] == '5':
                allconceptsfromnew = True
                allconceptsfromexisting = True
                conceptsinbothnewandexisting = []
                for concept in editoperation[1]:
                    if concept in new_categories_while_exploring_changes:
                        conceptsinbothnewandexisting.append([concept, 'new'])
                        allconceptsfromexisting = False
                    elif concept in existing_categories:
                        conceptsinbothnewandexisting.append([concept, 'existing'])
                        allconceptsfromnew = False
                    elif len([True for x in renamed_existing_categories if concept in x]) >0:
                        conceptsinbothnewandexisting.append([concept, 'existing_renamed'])
                        allconceptsfromnew = False
                    else:
                        allconceptsfromexisting = False
                        allconceptsfromnew = False
                if allconceptsfromnew == True:
                    for concept in editoperation[1]:
                        new_categories_while_exploring_changes.remove(concept)
                    old_trainingset = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])
                    trs = TrainingSet(old_trainingset[2])
                    classes = list(numpy.unique(trs.target))
                    if mergedconceptname in classes:
                        existing_categories.append(mergedconceptname)
                        request.session['existing_categories'] = existing_categories
                    else:
                        new_categories_while_exploring_changes.append(mergedconceptname)
                    request.session['new_categories'] = new_categories_while_exploring_changes
                elif allconceptsfromexisting == True:
                    new_concept_from_merging_existing_concepts = []
                    for concept in editoperation[1]:
                        if concept in existing_categories:
                            existing_categories.remove(concept)
                            request.session['existing_categories'] = existing_categories
                            new_concept_from_merging_existing_concepts.append(concept)
                        else:
                            for a in renamed_existing_categories:
                                if concept in a:
                                    new_concept_from_merging_existing_concepts.append(a[0])
                                    renamed_existing_categories.remove(a)
                                    request.session['renamed_existing_categories'] = renamed_existing_categories
                                    break
                    new_concept_from_merging_existing_concepts.append(mergedconceptname)
                    categories_merged_from_existing.append(new_concept_from_merging_existing_concepts)
                    request.session['categories_merged_from_existing'] = categories_merged_from_existing
                elif len(conceptsinbothnewandexisting) == len(editoperation[1]):
                    new_concept_from_merging_existing_and_new_concepts = []
                    for concept in conceptsinbothnewandexisting:
                        if concept[1] == 'new':
                            new_categories_while_exploring_changes.remove(concept[0])
                            request.session['new_categories'] = new_categories_while_exploring_changes
                            new_concept_from_merging_existing_and_new_concepts.append(concept[0])
                        elif concept[1] == 'existing':
                            existing_categories.remove(concept[0])
                            request.session['existing_categories'] = existing_categories
                            new_concept_from_merging_existing_and_new_concepts.append(concept[0])
                        else:
                            a = [x for x in renamed_existing_categories if concept[0] in x][0]
                            new_concept_from_merging_existing_and_new_concepts.append(a[0])
                            renamed_existing_categories.remove(a)
                            request.session['renamed_existing_categories'] = renamed_existing_categories
                            
                    new_concept_from_merging_existing_and_new_concepts.append(mergedconceptname)
                    categories_merged_from_new_and_existing.append(new_concept_from_merging_existing_and_new_concepts)
                    request.session['categories_merged_from_new_and_existing'] = categories_merged_from_new_and_existing
                    
                elif len(conceptsinbothnewandexisting) < len(editoperation[1]) and len(conceptsinbothnewandexisting)>0:
                    concepts_not_in_both_new_and_existing = []
                    for concept in editoperation[1]:
                        if any(concept in sublist for sublist in conceptsinbothnewandexisting)== False:
                            concepts_not_in_both_new_and_existing.append(concept)
                    concepts_found_in_merged_from_existing = False
                    for merged_concept in categories_merged_from_existing:
                        found_concepts = True
                        for concept in concepts_not_in_both_new_and_existing:
                            if concept not in merged_concept:
                                found_concepts = False
                        if found_concepts == True:
                            x = merged_concept
                            categories_merged_from_existing.remove(merged_concept)
                            request.session['categories_merged_from_existing'] = categories_merged_from_existing
                            x.pop()
                            add_this_operation_to_new_and_existing = False
                            for concept in conceptsinbothnewandexisting:
                                x.append(concept[0])
                                if concept[1] == 'new':
                                    add_this_operation_to_new_and_existing = True
                            x.append(mergedconceptname)
                            if add_this_operation_to_new_and_existing == False:
                                categories_merged_from_existing.append(x)
                                request.session['categories_merged_from_existing'] = categories_merged_from_existing
                            else:
                                categories_merged_from_new_and_existing.append(x)
                                request.session['categories_merged_from_new_and_existing'] = categories_merged_from_new_and_existing
                            concepts_found_in_merged_from_existing = True
                            break
                    if concepts_found_in_merged_from_existing == False:
                        for merged_concept in categories_merged_from_new_and_existing:
                            found_concepts = True
                            for concept in concepts_not_in_both_new_and_existing:
                                if concept not in merged_concept:
                                    found_concepts = False
                            if found_concepts == True:
                                x = merged_concept
                                categories_merged_from_new_and_existing.remove(merged_concept)
                                request.session['categories_merged_from_new_and_existing'] = categories_merged_from_new_and_existing
                                x.pop()
                                for concept in conceptsinbothnewandexisting:
                                    x.append(concept[0])
                                x.append(mergedconceptname)
                                categories_merged_from_new_and_existing.append(x)
                                request.session['categories_merged_from_new_and_existing'] = categories_merged_from_new_and_existing
                                break
                else:
                    if (len(categories_split_from_existing) !=0):
                        for split_category in categories_split_from_existing:
                            merging_split_concepts = True
                            for concept in editoperation[1]:
                                if concept in split_category:
                                    continue
                                else:
                                    merging_split_concepts = False
                                    
                            if merging_split_concepts == True:
                                if len(editoperation[1]) == (len(split_category)-1):
                                    categories_split_from_existing.remove(split_category)
                                    request.session['categories_split_from_existing'] = categories_split_from_existing
                                    existing_categories.append(mergedconceptname)
                                    request.session['existing_categories'] = existing_categories
                                    break
                                else:
                                    new_split_categories = split_category
                                    categories_split_from_existing.remove(split_category)
                                    for concept in editoperation[1]:
                                        new_split_categories.remove(concept)
                                    new_split_categories.append(mergedconceptname)
                                    categories_split_from_existing.append(new_split_categories)
                                    request.session['categories_split_from_existing'] = categories_split_from_existing
            
            elif editoperation[0] == '6':
                grouping = [x for x in conceptstogroup]
                grouping.append(groupedconceptname)
                grouped_categories.append(grouping)        
                request.session['grouped_categories'] =  grouped_categories        
            #Update the relationship of concepts when splitting concepts - assuming a concept is split in two concepts only         
            elif editoperation[0] == '7':
                if concepttosplit in new_categories_while_exploring_changes:
                    new_categories_while_exploring_changes.remove(concepttosplit)
                    new_categories_while_exploring_changes.append(firstconcept)
                    new_categories_while_exploring_changes.append(secondconcept)
                    request.session['new_categories_while_exploring_changes'] = new_categories_while_exploring_changes
                elif concepttosplit in existing_categories:
                    existing_categories.remove(concepttosplit)
                    request.session['existing_categories'] = existing_categories
                    categories_split_from_existing.append([concepttosplit, firstconcept, secondconcept])
                    request.session['categories_split_from_existing'] = categories_split_from_existing
                elif len([True for x in renamed_existing_categories if concepttosplit in x]) >0:
                    for each_set in renamed_existing_categories:
                        if concepttosplit in each_set:
                            categories_split_from_existing.append([each_set[0], firstconcept, secondconcept])
                            renamed_existing_categories.remove(each_set)
                            request.session['renamed_existing_categories'] = renamed_existing_categories
                            request.session['categories_split_from_existing'] = categories_split_from_existing
                            break
                else:
                    FoundTheConcept = False
                    if (len(categories_merged_from_existing) !=0):
                        for merged_category in categories_merged_from_existing:
                            if merged_category[-1] == concepttosplit and firstconcept in merged_category and secondconcept in merged_category:
                                categories_merged_from_existing.remove(merged_category)
                                request.session['categories_merged_from_existing'] = categories_merged_from_existing
                                existing_categories.append(firstconcept)
                                existing_categories.append(secondconcept)
                                request.session['existing_categories'] = existing_categories
                                FoundTheConcept = True
                                break
                    if FoundTheConcept == False and (len(categories_merged_from_new_and_existing) !=0):
                        for merged_category in categories_merged_from_new_and_existing:
                            if merged_category[-1] == concepttosplit and firstconcept in merged_category and secondconcept in merged_category:
                                categories_merged_from_new_and_existing.remove(merged_category)
                                request.session['categories_merged_from_new_and_existing'] = categories_merged_from_new_and_existing
                                old_trainingset = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])
                                trs = TrainingSet(old_trainingset[2])
                                classes = list(numpy.unique(trs.target))
                                if firstconcept in classes:
                                    existing_categories.append(firstconcept)
                                    request.session['existing_categories'] = existing_categories
                                else:
                                    new_categories_while_exploring_changes.append(firstconcept)
                                    request.session['new_categories'] = new_categories_while_exploring_changes
                                if secondconcept in classes:
                                    existing_categories.append(secondconcept)
                                    request.session['existing_categories'] = existing_categories
                                else:
                                    new_categories_while_exploring_changes.append(secondconcept)
                                    request.session['new_categories'] = new_categories_while_exploring_changes
                                FoundTheConcept = True
                                break
                    if FoundTheConcept == False:
                        for each_set in categories_split_from_existing:
                            if concepttosplit in each_set:
                                x = each_set
                                categories_split_from_existing.remove(each_set)
                                x.remove(concepttosplit)
                                x.append(firstconcept)
                                x.append(secondconcept)
                                categories_split_from_existing.append(x)
                                request.session['categories_split_from_existing'] = categories_split_from_existing
                                break
                                
    request.session.modified = True
    if 'new_categories' in request.session:
        print "1"                           
        print request.session['new_categories']
    if 'existing_categories' in request.session:  
        print "2"     
        print request.session['existing_categories']
    if 'renamed_existing_categories' in request.session:
        print "3" 
        print request.session['renamed_existing_categories']  
    if 'categories_merged_from_existing' in request.session:
        print "4" 
        print request.session['categories_merged_from_existing']
    if 'categories_merged_from_new_and_existing' in request.session:
        print "5" 
        print request.session['categories_merged_from_new_and_existing']
    if 'categories_split_from_existing' in request.session:
        print "6" 
        print request.session['categories_split_from_existing']
    if 'categories_grouped' in request.session:
        print "7" 
        print request.session['categories_grouped']
    
    #adding details for current exploration details for visualization
    old_trainingset_name = request.session['current_training_file_name']
    new_trainingset_name = newfilename
    data_content = "Old trainingset: " + old_trainingset_name + "<br/> New trainingset: " + new_trainingset_name + "<br/><br/>" + "<b>Edit operations: </b><br/>"

    for editoperation in currenteditoperations:
        if editoperation[0] == '1':
            data_content = data_content + "Add new concept " + editoperation[1] + "<br/>"
        elif editoperation[0] == '2': 
            data_content = data_content + "Remove concept " + editoperation[1]  + "<br/>"
        elif editoperation[0] == '3':
            data_content = data_content + "Rename " + editoperation[1]  + " to " + editoperation[2] + "<br/>"
        elif editoperation[0] == '4':
            data_content = data_content + "Edit concept " + editoperation[1]  + "<br/>"
        elif editoperation[0] == '5':
            mergedconceptname = editoperation[2]
            concepts_to_merge = editoperation[1]
            if len(concepts_to_merge) ==2:
                data_content = data_content + "Merge " + concepts_to_merge[0] + " and " + concepts_to_merge[1] + " to create " + mergedconceptname + "<br/>"
            else:
                data_content = data_content + "Merge " + concepts_to_merge[0] + ", " + concepts_to_merge[1] + " and " + concepts_to_merge[2] + " to create " + mergedconceptname + "<br/>"
        elif editoperation[0] == '6':
            groupedconceptname = editoperation[2]
            concepts_to_group = editoperation[1]
            if len(concepts_to_group) ==2:
                data_content = data_content + "Group " + concepts_to_group[0] + " and " + concepts_to_group[1] + " to create " + groupedconceptname + "<br/>"
            else:
                data_content = data_content + "Group " + concepts_to_group[0] + ", " + concepts_to_group[1] + " and " + concepts_to_group[2] + " to create " + groupedconceptname + "<br/>"
        else:
            concepttosplit = editoperation[1];
            firstconcept = editoperation[2];
            secondconcept = editoperation[4];
            data_content = data_content + "Split" + concepttosplit + " into " + firstconcept + " and " + secondconcept + "<br/>"
    
    current_step = ['Change trainingset', 'Change trainingset', data_content]
    
    if 'current_exploration_chain_viz' in request.session:
        current_exploration_chain_viz = request.session['current_exploration_chain_viz']
        if current_exploration_chain_viz[-1][0] == 'End':
            current_exploration_chain_viz.pop()
        current_exploration_chain_viz.append(current_step)
        request.session['current_exploration_chain_viz'] = current_exploration_chain_viz
    else:
        request.session['current_exploration_chain_viz'] = [current_step]
    
    
    
    os.rename(EXISTING_TRAINING_DATA_LOCATION + fname, EXISTING_TRAINING_DATA_LOCATION + newfilename)

    request.session['current_training_file_name'] = newfilename
    request.session['current_training_file_ver'] = latestver
    
    exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'change trainingset', activity_instance = tr_activity.id)
    exp_chain.save(force_insert=True)
    request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1

    if 'currenteditoperations' in request.session:
        del request.session['currenteditoperations']
        request.session.modified = True
    
    with open('%s%s' % (EXISTING_TRAINING_DATA_LOCATION, request.session['current_training_file_name']), 'rU') as trainingset:
        datareader = csv.reader(trainingset, delimiter=',')
        trainingsetasArray = list(datareader)
        trainingset.close()
    
    if 'existing_taxonomy_name' in request.session:
        old_trainingset_name = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])[2]
        new_training_sample = TrainingSet(request.session['current_training_file_name'])
        old_training_sample = TrainingSet(old_trainingset_name)
        common_categories, new_categories, deprecated_categories = new_training_sample.compare_training_samples(old_training_sample)
        if len(common_categories)!=0:
            if isinstance(common_categories[0], list)==False:
                common_categories_message = "The two training samples have different number of bands; so, we cannot compare common categories based on training samples"
                return JsonResponse({'trainingset': trainingsetasArray, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories, 'common_categories_message':common_categories_message})

        return JsonResponse({'trainingset': trainingsetasArray, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories})

    return JsonResponse({'trainingset': trainingsetasArray, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'],})



# create a file with similar name as provided in the static folder and copy all the contents    
def save_csv_training_file(f):
    with BufferedWriter( FileIO( '%s%s' % (EXISTING_TRAINING_DATA_LOCATION, f), "wb" ) ) as dest:
        foo = f.read(1024)  
        while foo:
            dest.write(foo)
            foo = f.read(1024)
        dest.close();

def changethresholdlimits(request):
    if request.method=='POST':
        data = request.POST;
        jm_limit = data['1']
        acc_limit = data['2']
        request.session['jm_distance_limit'] = jm_limit
        request.session['accuracy_limit'] = acc_limit
        return HttpResponse("")



@login_required
@transaction.atomic
def signaturefile(request):
    #print request.session['trainingset_version_and_categories_relationship']
    if 'currenteditoperations' in request.session:
        del request.session['currenteditoperations']
        request.session.modified = True
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username # @UndefinedVariable
    if 'new_taxonomy_name' not in request.session and 'existing_taxonomy_name' not in request.session :
            messages.error(request, "Choose an activity before you proceed further")
            return HttpResponseRedirect("/AdvoCate/home/", {'user_name': user_name})
    
    if 'current_training_file_name' not in request.session:
        return render (request, 'signaturefile.html', {'user_name':user_name})

    trainingfile = TrainingSet(request.session['current_training_file_name'])
    features = list(trainingfile.features)

    if request.method=='POST':
        data = request.POST;        
        classifiername = data['classifiertype']
        request.session['model_type'] = classifiername
        validationoption = data['validationoption']
        classifier = chooseClassifier(classifiername)
        modelname = "model_" + str(datetime.now())
        authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
        statistical_methods = StatisticalMethods()
        
        if (validationoption=='1'):
            validationtype="training data" 
            clf = classifier.fit(trainingfile.samples, trainingfile.target)
            y_pred= clf.predict(trainingfile.samples)
            score= "{0:.2f}".format(metrics.accuracy_score(trainingfile.target, y_pred))
            cm = metrics.confusion_matrix(trainingfile.target, y_pred)
            kp = "{0:.2f}".format(statistical_methods.calculateKappa(cm))
                                  
        elif (validationoption=='2'):
            validationfile = request.FILES['validationfile']
            validationtype = "validation data"
            
        else:
            folds = data['fold']
            validationtype = "cross validation"
            '''
            X = trainingfile.samples
            Y = trainingfile.target
            C_range = numpy.linspace(18, 24, 14)
            gamma_range = numpy.logspace(-3, -1, 14)
            param_grid = dict(gamma=gamma_range, C=C_range)
            cv = StratifiedShuffleSplit(Y, n_iter=5, test_size=0.2, random_state=42)
            grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv)
            grid.fit(X, Y)
            print grid.best_params_
            print grid.best_score_
            scores = [x[1] for x in grid.grid_scores_]
            scores = numpy.array(scores).reshape(len(C_range), len(gamma_range))
            
            plt.figure(figsize=(8, 6))
            plt.subplots_adjust(left=.2, right=0.95, bottom=0.15, top=0.95)
            plt.imshow(scores, interpolation='nearest', cmap=plt.cm.hot, norm=MidpointNormalize(vmin=0.2, midpoint=0.92))
            plt.xlabel('gamma')
            plt.ylabel('C')
            plt.colorbar()
            plt.xticks(numpy.arange(len(gamma_range)), numpy.around(gamma_range, 6), rotation=45)
            plt.yticks(numpy.arange(len(C_range)), numpy.around(C_range, 4))
            plt.title('Validation accuracy')
            plt.savefig("%s/%s" % (IMAGE_LOCATION, "test.png"),  bbox_inches='tight')
            '''
            skf = cross_validation.StratifiedKFold(trainingfile.target, n_folds=int(folds))
            cm=[]
            count =0
                        
            for train_index, test_index in skf:
                X_train, X_test = trainingfile.samples[train_index], trainingfile.samples[test_index]
                y_train, y_test = trainingfile.target[train_index], trainingfile.target[test_index]
                #scaler = StandardScaler()
                #X_train = scaler.fit_transform(X_train)
                #X_test = scaler.fit_transform(X_test)
                clf=classifier.fit(X_train, y_train)
                y_pred = clf.predict(X_test)
                individual_cm = metrics.confusion_matrix(y_test, y_pred)
                if (count==0):
                    count +=1
                    cm = individual_cm
                else:
                    cm += individual_cm
            
            scores=cross_validation.cross_val_score(clf, trainingfile.samples, trainingfile.target, cv=int(folds))
            score = "{0:.2f}".format(scores.mean())
            kp = "{0:.2f}".format(statistical_methods.calculateKappa(cm))
            
        
        prodacc, useracc = statistical_methods.calculateAccuracies(cm)
        request.session['model_score'] = score
        request.session['producer_accuracies'] = prodacc
        request.session['user_accuracies'] = useracc
        joblib.dump(clf, '%s/%s' % (CLASSIFICATION_MODEL_LOCATION, modelname))
        request.session['current_model_name']= modelname
        authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
        classifier_instance = Classifier.objects.get(classifier_name=classifiername)
        numpy.set_printoptions(precision=2)
        plt.figure()
        plot_confusion_matrix(cm, trainingfile.target)
        cmname = modelname+"_cm.png"
        plt.savefig("%s/%s" % (IMAGE_LOCATION, cmname),  bbox_inches='tight')
        
        
        
        sf = Classificationmodel(model_name = modelname, model_location=CLASSIFICATION_MODEL_LOCATION, accuracy=score, model_type=classifiername)
        sf.save()
        request.session['current_model_id'] = sf.id
        
        conf_matrix = Confusionmatrix(confusionmatrix_name = cmname, confusionmatrix_location=IMAGE_LOCATION)
        conf_matrix.save()
        
        tc = LearningActivity(classifier=classifier_instance, model= sf, validation = validationtype, validation_score= score, confusionmatrix=conf_matrix, completed_by= authuser_instance)
        tc.save()
        
        exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'learning', activity_instance = tc.id)
        exp_chain.save(force_insert=True)
        
        request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1
        
        if 'current_predicted_file_name' in request.session:
            del request.session['current_test_file_name']
            del request.session['current_predicted_file_name']
            del request.session['current_test_file_columns']
            del request.session['current_test_file_rows']
            request.session.modified = True
        
            #adding details for current exploration details for visualization
    
        data_content = "Model type: " + classifiername + "<br/> Validation type: " + validationtype + "<br/> Validation score: " + score + "<br/>Kappa: " + kp + "<br/><br/>" + "<b>Producer/user accuracies:</b><br/>"
        categories = list(numpy.unique(trainingfile.target))
        for i, category in enumerate(categories):
            data_content = data_content + category + " (" + str(prodacc[i]) + ", " + str(useracc[i]) + ")<br/>" 
        
        current_step = ['Training activity', 'Training activity', data_content]
        
        if 'current_exploration_chain_viz' in request.session:
            current_exploration_chain_viz = request.session['current_exploration_chain_viz']
            if current_exploration_chain_viz[-1][0] == 'End':
                current_exploration_chain_viz.pop()
            current_exploration_chain_viz.append(current_step)
            request.session['current_exploration_chain_viz'] = current_exploration_chain_viz
        else:
            request.session['current_exploration_chain_viz'] = [current_step]
    
        
        if (classifiername=="Naive Bayes"):
            covariance_mat = trainingfile.create_covariance_matrix()
            mean_vectors = trainingfile.create_mean_vectors()
            jmdistances_list=[]
            jmdistances_complete_list=[]
            for i in range(len(mean_vectors)):
                for j in range(i+1, len(mean_vectors)):
                    jmdistance_for_each_pair =[]
                    model1 = NormalDistributionIntensionalModel(mean_vectors[i][1], covariance_mat[i][1])
                    model2 = NormalDistributionIntensionalModel(mean_vectors[j][1], covariance_mat[j][1])
                    jm = model1.jm_distance(model2)
                    jmdistance_for_each_pair.append(mean_vectors[i][0])
                    jmdistance_for_each_pair.append(mean_vectors[j][0])
                    jmdistance_for_each_pair.append(jm)
                    jmdistances_list.append(jmdistance_for_each_pair)
                complete_jmdistance_for_each_pair =[]
                for k in range(len(mean_vectors)):
                    model1 = NormalDistributionIntensionalModel(mean_vectors[i][1], covariance_mat[i][1])
                    model2 = NormalDistributionIntensionalModel(mean_vectors[k][1], covariance_mat[k][1])
                    jm = model1.jm_distance(model2)
                    complete_jmdistance_for_each_pair.append(jm)
                jmdistances_complete_list.append(complete_jmdistance_for_each_pair)
                    
            
            # getting a list of unique overlapping pairs using JM distance among categories - overlapping pairs are considered if the JM distance between them is less than the threshold limit
            listofcategories = clf.classes_.tolist()
            overlapping_pairs_jm_list = []
            for eachPair in jmdistances_list:
                if float(eachPair[2])<float(request.session['jm_distance_limit']):
                    overlapping_pairs_jm_list.append(eachPair)
            overlapping_pairs_sorted_by_jm_distance = sorted(overlapping_pairs_jm_list, key=itemgetter(2))     
            
            list_of_unique_overlapping_categories = []
            for index in range(len(overlapping_pairs_sorted_by_jm_distance)):
                if index==0:
                    list_of_unique_overlapping_categories.append(overlapping_pairs_sorted_by_jm_distance[index])
                else:
                    is_pair_unique = True
                    for pair in list_of_unique_overlapping_categories:
                        if overlapping_pairs_sorted_by_jm_distance[index][0] in pair or overlapping_pairs_sorted_by_jm_distance[index][1] in pair:
                            is_pair_unique = False
                            break
                    if is_pair_unique == True:
                        list_of_unique_overlapping_categories.append(overlapping_pairs_sorted_by_jm_distance[index])
            
            #getting a list of categories with low accuracies based on the threshold limit
            categories_with_low_accuracies = []
            acc_limit = float(request.session['accuracy_limit'])
            for index in range(len(listofcategories)):
                if (float(prodacc[index]) < acc_limit and float(useracc[index]) < acc_limit) or ((float(prodacc[index]) + float(useracc[index]))<(2.0*acc_limit)):
                    categories_with_low_accuracies.append(listofcategories[index])
            
            
            #generating suggestions based on unique overlapping pairs with low accuracies
            suggestions_based_on_overlapping_pairs_with_low_accuracies = []
            for eachPair in list_of_unique_overlapping_categories:
                single_suggestion=[]
                index1 = listofcategories.index(eachPair[0])
                index2 = listofcategories.index(eachPair[1])
                
                if float(prodacc[index1]) + float(useracc[index1]) < float(prodacc[index2]) + float(useracc[index2]):
                    single_suggestion.append(listofcategories[index1])
                    single_suggestion.append(listofcategories[index2])
                    suggestions_based_on_overlapping_pairs_with_low_accuracies.append(single_suggestion)
                else:
                    single_suggestion.append(listofcategories[index2])
                    single_suggestion.append(listofcategories[index1])
                    suggestions_based_on_overlapping_pairs_with_low_accuracies.append(single_suggestion)
                                
            #generating suggestions based on categories with low accuracies being confused with other categories (using confusion matrix)
            confusing_categories_with_low_accuracies=[]
            for category in categories_with_low_accuracies:
                index = listofcategories.index(category)
                confusion1_of_category_with_others = cm[index]
                confusion2_of_category_with_others = [row[index] for row in cm]
                total_confusion_of_category_with_others = [x+y for x, y in zip(confusion1_of_category_with_others, confusion2_of_category_with_others)]
                highest_confusion_with_index = find_index_of_highest_number_except_a_given_index(total_confusion_of_category_with_others, index)
                confusion = float(float(total_confusion_of_category_with_others[highest_confusion_with_index])/float(sum(total_confusion_of_category_with_others)))
                confusing_categories_with_low_accuracies.append([category, listofcategories[highest_confusion_with_index], confusion])
                
            confusing_categories_with_low_accuracies_sorted_by_confusion_percent = sorted(confusing_categories_with_low_accuracies, key=itemgetter(2), reverse=True)
            
            suggestions_based_on_categories_with_low_accuracies_and_high_confusion = []
            for i in range(len(confusing_categories_with_low_accuracies_sorted_by_confusion_percent)):
                if i==0:
                    suggestions_based_on_categories_with_low_accuracies_and_high_confusion = [confusing_categories_with_low_accuracies_sorted_by_confusion_percent[0]]
                else:
                    current_suggestion = confusing_categories_with_low_accuracies_sorted_by_confusion_percent[i]
                    is_unique= True
                    for suggestion in suggestions_based_on_categories_with_low_accuracies_and_high_confusion:
                        if current_suggestion[0] in suggestion or current_suggestion[1] in suggestion:
                            is_unique = False
                            break;
                    if is_unique == True:
                        suggestions_based_on_categories_with_low_accuracies_and_high_confusion.append(current_suggestion)
            
            #Generating unique suggestions using JM distance among categories, producer and user accuracies, and confusion matrix
            final_suggestion_list = suggestions_based_on_overlapping_pairs_with_low_accuracies
            for suggestion1 in suggestions_based_on_categories_with_low_accuracies_and_high_confusion:
                suggestion1_not_in_suggestion2 = True
                for suggestion2 in suggestions_based_on_overlapping_pairs_with_low_accuracies:
                    if suggestion1[0] in suggestion2 or suggestion1[1] in suggestion2:
                        suggestion1_not_in_suggestion2 = False
                        break;
                if suggestion1_not_in_suggestion2 == True:
                    final_suggestion_list.append([suggestion1[0], suggestion1[1]])
            
            
                                
            if 'existing_taxonomy_name' in request.session:
                customQuery = CustomQueries()
                
                old_categories, old_mean_vectors, old_covariance_mat = find_all_active_categories_and_their_comp_int_for_a_legend_version(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])
                new_categories = list(numpy.unique(trainingfile.target))
                common_categories = []
                common_categories_with_different_names = []
                if 'existing_categories' in request.session:
                    common_categories = request.session['existing_categories']
                if 'renamed_existing_categories' in request.session:
                    common_categories_with_different_names = request.session['renamed_existing_categories']
                    
                common_categories_comparison = []
                common_categories_with_different_names_comparison = []
                if len(old_mean_vectors[0]) != len(mean_vectors[0][1]):
                    for common_category in common_categories:
                        single_category_comparison = []
                        index_of_common_category_in_accuracy_list = new_categories.index(common_category)
                        producerAccuracy = prodacc[index_of_common_category_in_accuracy_list]
                        userAccuracy = useracc[index_of_common_category_in_accuracy_list]
                        single_category_comparison.append(common_category)
                        single_category_comparison.append("Naive bayes")
                        single_category_comparison.append(validationtype)
                        single_category_comparison.append(producerAccuracy)
                        single_category_comparison.append(userAccuracy)
                        old_category_details = customQuery.get_accuracies_and_validation_method_of_a_category(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'], common_category)
                        if len(old_category_details) == 1:
                            single_category_comparison.append(old_category_details[0][3])
                            single_category_comparison.append(old_category_details[0][2])
                            single_category_comparison.append(old_category_details[0][0])
                            single_category_comparison.append(old_category_details[0][1])
                        else:
                            w1, x1, y1, z1 = str(old_category_details[0][2]), str(old_category_details[0][3]), str(old_category_details[0][0]), str(old_category_details[0][1])
                            for i in range(1, len(old_category_details)):
                                w1 = w1 + ", " + str(old_category_details[i][3])
                                x1 = x1 + ", " + str(old_category_details[i][2])
                                y1 = y1 + ", " + str(old_category_details[i][0])
                                z1 = z1 + ", " + str(old_category_details[i][1])
                            single_category_comparison.append(w1)
                            single_category_comparison.append(x1)
                            single_category_comparison.append(y1)
                            single_category_comparison.append(z1)
                        common_categories_comparison.append(single_category_comparison)
                        
                    for common_category in common_categories_with_different_names:
                        single_category_comparison = []
                        index_of_common_category_in_accuracy_list = new_categories.index(common_category[1])
                        producerAccuracy = prodacc[index_of_common_category_in_accuracy_list]
                        userAccuracy = useracc[index_of_common_category_in_accuracy_list]
                        single_category_comparison.append(common_category[1])
                        single_category_comparison.append("Naive bayes")
                        single_category_comparison.append(validationtype)
                        single_category_comparison.append(producerAccuracy)
                        single_category_comparison.append(userAccuracy)
                        old_category_details = customQuery.get_accuracies_and_validation_method_of_a_category(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'], common_category[0])
                        single_category_comparison.append(common_category[0])
                        if len(old_category_details) == 1:
                            single_category_comparison.append(old_category_details[0][3])
                            single_category_comparison.append(old_category_details[0][2])
                            single_category_comparison.append(old_category_details[0][0])
                            single_category_comparison.append(old_category_details[0][1])
                        else:
                            w1, x1, y1, z1 = str(old_category_details[0][2]), str(old_category_details[0][3]), str(old_category_details[0][0]), str(old_category_details[0][1])
                            for i in range(1, len(old_category_details)):
                                w1 = w1 + ", " + str(old_category_details[i][3])
                                x1 = x1 + ", " + str(old_category_details[i][2])
                                y1 = y1 + ", " + str(old_category_details[i][0])
                                z1 = z1 + ", " + str(old_category_details[i][1])
                            single_category_comparison.append(w1)
                            single_category_comparison.append(x1)
                            single_category_comparison.append(y1)
                            single_category_comparison.append(z1)
                        common_categories_with_different_names_comparison.append(single_category_comparison)
                        
                    return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'jm_limit':request.session['jm_distance_limit'], 'acc_limit': request.session['accuracy_limit'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'meanvectors':clf.theta_.tolist(), 'variance':clf.sigma_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc, 'jmdistances': jmdistances_complete_list, 'suggestion_list': final_suggestion_list, 'common_categories_comparison': common_categories_comparison, 'common_categories_with_different_names_comparison': common_categories_with_different_names_comparison})
                else:
                    existing_categories_computational_intension_comparison = []
                                        
                    for common_category in common_categories:
                        single_category_comparison = []
                        index_of_common_category_in_accuracy_list = new_categories.index(common_category)
                        producerAccuracy = prodacc[index_of_common_category_in_accuracy_list]
                        userAccuracy = useracc[index_of_common_category_in_accuracy_list]
                        single_category_comparison.append(common_category)
                        single_category_comparison.append("Naive bayes")
                        single_category_comparison.append(validationtype)
                        single_category_comparison.append(producerAccuracy)
                        single_category_comparison.append(userAccuracy)
                        old_category_details = customQuery.get_accuracies_and_validation_method_of_a_category(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'], common_category)
                        if len(old_category_details) == 1:
                            single_category_comparison.append(old_category_details[0][3])
                            single_category_comparison.append(old_category_details[0][2])
                            single_category_comparison.append(old_category_details[0][0])
                            single_category_comparison.append(old_category_details[0][1])
                        else:
                            w1, x1, y1, z1 = str(old_category_details[0][3]), str(old_category_details[0][2]), str(old_category_details[0][0]), str(old_category_details[0][1])
                            for i in range(1, len(old_category_details)):
                                #w1 = w1 + ", " + str(old_category_details[i][3])
                                #x1 = x1 + ", " + str(old_category_details[i][2])
                                y1 = y1 + ", " + str(old_category_details[i][0])
                                z1 = z1 + ", " + str(old_category_details[i][1])
                            single_category_comparison.append(w1)
                            single_category_comparison.append(x1)
                            single_category_comparison.append(y1)
                            single_category_comparison.append(z1)
                        
                        new_index = [i for i, each_vector in enumerate(mean_vectors) if  each_vector[0] == common_category][0]
                        model1 = NormalDistributionIntensionalModel(mean_vectors[new_index][1], covariance_mat[new_index][1])
                        num_of_comp_ver = 1
                        for each_old_category in old_categories:
                            if common_category in each_old_category:
                                num_of_comp_ver = len(each_old_category) -3
                                old_index = old_categories.index(each_old_category)
                                break
                            
                        if num_of_comp_ver==1:
                            model2 = NormalDistributionIntensionalModel(old_mean_vectors[old_index], old_covariance_mat[old_index])
                            jm = model1.jm_distance(model2)
                            single_category_comparison.append(jm)
                            a = [common_category, [jm]]
                        else:
                            jm_for_multiple_comp_vers = ""
                            jm_list = []
                            for i in range(num_of_comp_ver):
                                model = NormalDistributionIntensionalModel(old_mean_vectors[old_index][i], old_covariance_mat[old_index][i])
                                jm = model1.jm_distance(model)
                                jm_for_multiple_comp_vers = jm_for_multiple_comp_vers + jm + ", "
                                jm_list.append([old_categories[old_index][3+i], jm])
                            jm_for_multiple_comp_vers = jm_for_multiple_comp_vers[:-2]
                            single_category_comparison.append(jm_for_multiple_comp_vers)
                            a = [common_category, jm_list]
                        
                        existing_categories_computational_intension_comparison.append(a)
                        common_categories_comparison.append(single_category_comparison)
                    
                    if len(existing_categories_computational_intension_comparison) != 0:
                        request.session['existing_categories_computational_intension_comparison'] = existing_categories_computational_intension_comparison
                    
                    
                    renamed_existing_categories_computational_intension_comparison = [] 
                    for common_category in common_categories_with_different_names:
                        single_category_comparison = []
                        index_of_common_category_in_accuracy_list = new_categories.index(common_category[1])
                        producerAccuracy = prodacc[index_of_common_category_in_accuracy_list]
                        userAccuracy = useracc[index_of_common_category_in_accuracy_list]
                        single_category_comparison.append(common_category[1])
                        single_category_comparison.append("Naive bayes")
                        single_category_comparison.append(validationtype)
                        single_category_comparison.append(producerAccuracy)
                        single_category_comparison.append(userAccuracy)
                        old_category_details = customQuery.get_accuracies_and_validation_method_of_a_category(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'], common_category[0])
                        single_category_comparison.append(common_category[0])
                        if len(old_category_details) == 1:
                            single_category_comparison.append(old_category_details[0][3])
                            single_category_comparison.append(old_category_details[0][2])
                            single_category_comparison.append(old_category_details[0][0])
                            single_category_comparison.append(old_category_details[0][1])
                        else:
                            w1, x1, y1, z1 = str(old_category_details[0][2]), str(old_category_details[0][3]), str(old_category_details[0][0]), str(old_category_details[0][1])
                            for i in range(1, len(old_category_details)):
                                #w1 = w1 + ", " + str(old_category_details[i][3])
                                #x1 = x1 + ", " + str(old_category_details[i][2])
                                y1 = y1 + ", " + str(old_category_details[i][0])
                                z1 = z1 + ", " + str(old_category_details[i][1])
                            single_category_comparison.append(w1)
                            single_category_comparison.append(x1)
                            single_category_comparison.append(y1)
                            single_category_comparison.append(z1)
                        
                        new_index = [i for i, each_vector in enumerate(mean_vectors) if  each_vector[0] == common_category[1]][0]
                        model1 = NormalDistributionIntensionalModel(mean_vectors[new_index][1], covariance_mat[new_index][1])
                        num_of_comp_ver = 1
                        for each_old_category in old_categories:
                            if common_category[0] in each_old_category:
                                num_of_comp_ver = len(each_old_category) -3
                                old_index = old_categories.index(each_old_category)
                                break
                            
                        if num_of_comp_ver==1:
                            model2 = NormalDistributionIntensionalModel(old_mean_vectors[old_index], old_covariance_mat[old_index])
                            jm = model1.jm_distance(model2)
                            single_category_comparison.append(jm)
                            a = [common_category[1], common_category[0], [jm]]
                        else:
                            jm_for_multiple_comp_vers = ""
                            jm_list = []
                            for i in range(num_of_comp_ver):
                                model = NormalDistributionIntensionalModel(old_mean_vectors[old_index][i], old_covariance_mat[old_index][i])
                                jm = model1.jm_distance(model)
                                jm_for_multiple_comp_vers = jm_for_multiple_comp_vers + jm + ", "
                                jm_list.append([old_categories[old_index][3+i], jm])
                            jm_for_multiple_comp_vers = jm_for_multiple_comp_vers[:-2]
                            single_category_comparison.append(jm_for_multiple_comp_vers)
                            a = [common_category[1], common_category[0], jm_list]
                            
                        renamed_existing_categories_computational_intension_comparison.append(a)
                        common_categories_with_different_names_comparison.append(single_category_comparison)
                    
                    if len(renamed_existing_categories_computational_intension_comparison) != 0:
                        request.session['renamed_existing_categories_computational_intension_comparison'] = renamed_existing_categories_computational_intension_comparison
                    
                    
                    
                                
                    categories_split_from_existing = []
                    categories_split_from_existing_comparison = []
                    split_categories_computational_intension_comparison = []
                    if 'categories_split_from_existing' in request.session:
                        categories_split_from_existing = request.session['categories_split_from_existing']
                    for split_categories in categories_split_from_existing:
                        existing_category_that_is_split = split_categories[0]
                        num_of_comp_ver = 1
                        for each_old_category in old_categories:
                            if existing_category_that_is_split in each_old_category:
                                num_of_comp_ver = len(each_old_category) -3
                                old_index = old_categories.index(each_old_category)
                                break
                        
                        for i in range(1, len(split_categories)):
                            single_category_comparison = []
                            index_of_new_category = [j for j, each_vector in enumerate(mean_vectors) if  each_vector[0] == split_categories[i]][0]
                            model1 = NormalDistributionIntensionalModel(mean_vectors[index_of_new_category][1], covariance_mat[index_of_new_category][1])
                            
                            if num_of_comp_ver==1:
                                model2 = NormalDistributionIntensionalModel(old_mean_vectors[old_index], old_covariance_mat[old_index])
                                jm = model1.jm_distance(model2)
                                single_category_comparison = [split_categories[i], split_categories[0], jm]
                                a = [split_categories[i], split_categories[0], [jm]]
                            else:
                                jm_for_multiple_comp_vers = ""
                                jm_list = []
                                for i in range(num_of_comp_ver):
                                    model = NormalDistributionIntensionalModel(old_mean_vectors[old_index][i], old_covariance_mat[old_index][i])
                                    jm = model1.jm_distance(model)
                                    jm_for_multiple_comp_vers = jm_for_multiple_comp_vers + jm + ", "
                                    jm_list.append([old_categories[old_index][3+i], jm])
                                single_category_comparison = [split_categories[i], split_categories[0], jm_for_multiple_comp_vers]
                                a = [split_categories[i], split_categories[0], jm_list]
                                
                            categories_split_from_existing_comparison.append(single_category_comparison)
                            split_categories_computational_intension_comparison.append(a)
                            
                    if len(split_categories_computational_intension_comparison) !=0:
                        request.session['split_categories_computational_intension_comparison'] = split_categories_computational_intension_comparison
                    
                                    
                    categories_merged_from_existing = []
                    categories_merged_from_existing_comparison = []
                    merged_categories_computational_intensional_comparison = []
                    if 'categories_merged_from_existing' in request.session:
                        categories_merged_from_existing = request.session['categories_merged_from_existing']      
                                
                    for merged_categories in categories_merged_from_existing:
                        resulting_merged_category = merged_categories[-1]
                        for i in range(0, len(merged_categories)-1):
                            single_category_comparison = []
                            a = []
                            for each_old_category in old_categories:
                                if merged_categories[i] in each_old_category:
                                    num_of_comp_ver = len(each_old_category) -3
                                    old_index = old_categories.index(each_old_category)
                                    break
                            index_of_resulting_merged_category = [j for j, each_vector in enumerate(mean_vectors) if  each_vector[0] == resulting_merged_category][0]
                            model1 = NormalDistributionIntensionalModel(mean_vectors[index_of_resulting_merged_category][1], covariance_mat[index_of_resulting_merged_category][1])
                            
                            if num_of_comp_ver==1:
                                model2 = NormalDistributionIntensionalModel(old_mean_vectors[old_index], old_covariance_mat[old_index])
                                jm = model1.jm_distance(model2)
                                single_category_comparison = [merged_categories[-1], merged_categories[i], [jm]]
                                a = [merged_categories[-1], merged_categories[i], jm]
                            else:
                                jm_for_multiple_comp_vers = ""
                                jm_list = []
                                for i in range(num_of_comp_ver):
                                    model = NormalDistributionIntensionalModel(old_mean_vectors[old_index][i], old_covariance_mat[old_index][i])
                                    jm = model1.jm_distance(model)
                                    jm_for_multiple_comp_vers = jm_for_multiple_comp_vers + jm + ", "
                                    jm_list.append([old_categories[old_index][3+i], jm])
                                    
                                single_category_comparison = [merged_categories[-1], merged_categories[i], jm_for_multiple_comp_vers]
                                a = [merged_categories[-1], merged_categories[i], jm_list]
                            
                            categories_merged_from_existing_comparison.append(single_category_comparison)
                            merged_categories_computational_intensional_comparison.append(a)
                    if len(merged_categories_computational_intensional_comparison) !=0:
                        request.session['merged_categories_computational_intensional_comparison'] = merged_categories_computational_intensional_comparison
                        
                    
                    categories_merged_from_new_and_existing = []
                    categories_merged_from_new_and_existing_comparison = []
                    merged_categories_from_new_and_existing_computational_intension_comparison = []
                    if 'categories_merged_from_new_and_existing' in request.session:
                        categories_merged_from_new_and_existing = request.session['categories_merged_from_new_and_existing']
                        
                    for merged_categories in categories_merged_from_new_and_existing:
                        resulting_merged_category = merged_categories[-1]
                        
                        for i in range(0, len(merged_categories)-1):
                            single_category_comparison = []
                            a = []
                            is_existing_category = False
                            for each_old_category in old_categories:
                                if merged_categories[i] in each_old_category:
                                    is_existing_category = True
                                    num_of_comp_ver = len(each_old_category) -3
                                    old_index = old_categories.index(each_old_category)
                                    break
                            if is_existing_category == True:
                                index_of_resulting_merged_category = [j for j, each_vector in enumerate(mean_vectors) if  each_vector[0] == resulting_merged_category][0]
                                model1 = NormalDistributionIntensionalModel(mean_vectors[index_of_resulting_merged_category][1], covariance_mat[index_of_resulting_merged_category][1])
                                
                                if num_of_comp_ver==1:
                                    model2 = NormalDistributionIntensionalModel(old_mean_vectors[old_index], old_covariance_mat[old_index])
                                    jm = model1.jm_distance(model2)
                                    single_category_comparison = [merged_categories[-1], merged_categories[i], jm]
                                    a = [merged_categories[-1], merged_categories[i], [jm]]
                                else:
                                    jm_for_multiple_comp_vers = ""
                                    jm_list = []
                                    for i in range(num_of_comp_ver):
                                        model = NormalDistributionIntensionalModel(old_mean_vectors[old_index][i], old_covariance_mat[old_index][i])
                                        jm = model1.jm_distance(model)
                                        jm_for_multiple_comp_vers = jm_for_multiple_comp_vers + jm + ", "
                                        jm_list.append([old_categories[old_index][3+i], jm])
                                        
                                    single_category_comparison = [merged_categories[-1], merged_categories[i], jm_for_multiple_comp_vers]
                                    a = [merged_categories[-1], merged_categories[i], jm_list]
                                
                                categories_merged_from_new_and_existing_comparison.append(single_category_comparison)
                                merged_categories_from_new_and_existing_computational_intension_comparison.append(a)
                    if len(merged_categories_from_new_and_existing_computational_intension_comparison) !=0:
                        request.session['merged_categories_from_new_and_existing_computational_intension_comparison'] = merged_categories_from_new_and_existing_computational_intension_comparison
                        
                    
                    return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'],'jm_limit':request.session['jm_distance_limit'], 'acc_limit': request.session['accuracy_limit'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'meanvectors':clf.theta_.tolist(), 'variance':clf.sigma_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc, 'jmdistances': jmdistances_complete_list, 'suggestion_list': final_suggestion_list, 'common_categories_comparison': common_categories_comparison, 'common_categories_with_different_names_comparison': common_categories_with_different_names_comparison, 'split_categories_comparison': categories_split_from_existing_comparison, 'merged_categories_comparison': categories_merged_from_existing_comparison, 'categories_merged_from_new_and_existing_comparison': categories_merged_from_new_and_existing_comparison})
               
            return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'jm_limit':request.session['jm_distance_limit'], 'acc_limit': request.session['accuracy_limit'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'meanvectors':clf.theta_.tolist(), 'variance':clf.sigma_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc, 'jmdistances': jmdistances_complete_list, 'suggestion_list': final_suggestion_list})
        
        elif (classifiername=="Decision Tree"):
            dot_data = StringIO()
            tree.export_graphviz(clf, out_file=dot_data)
            graph = pydot.graph_from_dot_data(dot_data.getvalue())
            tree_name = modelname + "_tree.png"
            graph.write_png('%s%s' %(IMAGE_LOCATION, tree_name))
            
            listofcategories = clf.classes_.tolist()
            categories_with_low_accuracies1 = []
            acc_limit = float(request.session['accuracy_limit'])
            
            for index in range(len(listofcategories)):
                if (float(prodacc[index]) < acc_limit and float(useracc[index]) < acc_limit) or ((float(prodacc[index]) + float(useracc[index]))<(2.0*acc_limit)):
                    categories_with_low_accuracies1.append(listofcategories[index])
            
            confusing_categories_with_low_accuracies1=[]
            for category in categories_with_low_accuracies1:
                index = listofcategories.index(category)
                confusion1_of_category_with_others = cm[index]
                confusion2_of_category_with_others = [row[index] for row in cm]
                total_confusion_of_category_with_others = [x+y for x, y in zip(confusion1_of_category_with_others, confusion2_of_category_with_others)]
                highest_confusion_with_index = find_index_of_highest_number_except_a_given_index(total_confusion_of_category_with_others, index)
                confusion = float(float(total_confusion_of_category_with_others[highest_confusion_with_index])/float(sum(total_confusion_of_category_with_others)))
                confusing_categories_with_low_accuracies1.append([category, listofcategories[highest_confusion_with_index], confusion])
                
            confusing_categories_with_low_accuracies_sorted_by_confusion_percent1 = sorted(confusing_categories_with_low_accuracies1, key=itemgetter(2), reverse=True)
            
            final_suggestion_list1 = []
            if (len(confusing_categories_with_low_accuracies_sorted_by_confusion_percent1)>0):
                final_suggestion_list1 = [confusing_categories_with_low_accuracies_sorted_by_confusion_percent1[0]]
                for i in range(1, len(confusing_categories_with_low_accuracies_sorted_by_confusion_percent1)):
                    current_suggestion = confusing_categories_with_low_accuracies_sorted_by_confusion_percent1[i]
                    is_unique= True
                    for suggestion in final_suggestion_list1:
                        if current_suggestion[0] in suggestion or current_suggestion[1] in suggestion:
                            is_unique = False
                            break;
                    if is_unique == True:
                        final_suggestion_list1.append(current_suggestion)
 
            if 'existing_taxonomy_name' in request.session:
                customQuery = CustomQueries()
                old_trainingset_name = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])[2]
                old_trainingfile = TrainingSet(old_trainingset_name)
                new_categories = list(numpy.unique(trainingfile.target))
                old_categories = list(numpy.unique(old_trainingfile.target))
                common_categories = numpy.intersect1d(new_categories, old_categories)
                common_categories_comparison = []
                for common_category in common_categories:
                    single_category_comparison = []
                    index_of_common_category_in_accuracy_list = new_categories.index(common_category)
                    producerAccuracy = prodacc[index_of_common_category_in_accuracy_list]
                    userAccuracy = useracc[index_of_common_category_in_accuracy_list]
                    single_category_comparison.append(common_category)
                    single_category_comparison.append("Decision tree")
                    single_category_comparison.append(validationtype)
                    single_category_comparison.append(producerAccuracy)
                    single_category_comparison.append(userAccuracy)
                    old_category_details = customQuery.get_accuracies_and_validation_method_of_a_category(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'], common_category)
                    single_category_comparison.append(old_category_details[0][2])
                    single_category_comparison.append(old_category_details[0][3])
                    single_category_comparison.append(old_category_details[0][0])
                    single_category_comparison.append(old_category_details[0][1])
                    common_categories_comparison.append(single_category_comparison)
                return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'suggestion_list': final_suggestion_list1, 'acc_limit': request.session['accuracy_limit'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'kappa':kp, 'cm': cmname, 'tree':tree_name, 'prodacc': prodacc, 'useracc': useracc, 'common_categories_comparison':common_categories_comparison})
                
            return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'suggestion_list': final_suggestion_list1, 'acc_limit': request.session['accuracy_limit'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'kappa':kp, 'cm': cmname, 'tree':tree_name, 'prodacc': prodacc, 'useracc': useracc})
        
        else:
            listofcategories = clf.classes_.tolist()
            categories_with_low_accuracies1 = []
            acc_limit = float(request.session['accuracy_limit'])
            
            for index in range(len(listofcategories)):
                if (float(prodacc[index]) < acc_limit and float(useracc[index]) < acc_limit) or ((float(prodacc[index]) + float(useracc[index]))<(2.0*acc_limit)):
                    categories_with_low_accuracies1.append(listofcategories[index])
            
            confusing_categories_with_low_accuracies1=[]
            for category in categories_with_low_accuracies1:
                index = listofcategories.index(category)
                confusion1_of_category_with_others = cm[index]
                confusion2_of_category_with_others = [row[index] for row in cm]
                total_confusion_of_category_with_others = [x+y for x, y in zip(confusion1_of_category_with_others, confusion2_of_category_with_others)]
                highest_confusion_with_index = find_index_of_highest_number_except_a_given_index(total_confusion_of_category_with_others, index)
                confusion = float(float(total_confusion_of_category_with_others[highest_confusion_with_index])/float(sum(total_confusion_of_category_with_others)))
                confusing_categories_with_low_accuracies1.append([category, listofcategories[highest_confusion_with_index], confusion])
                
            confusing_categories_with_low_accuracies_sorted_by_confusion_percent1 = sorted(confusing_categories_with_low_accuracies1, key=itemgetter(2), reverse=True)
            
            final_suggestion_list1 = []
            if (len(confusing_categories_with_low_accuracies_sorted_by_confusion_percent1)>0):
                final_suggestion_list1 = [confusing_categories_with_low_accuracies_sorted_by_confusion_percent1[0]]
                for i in range(1, len(confusing_categories_with_low_accuracies_sorted_by_confusion_percent1)):
                    current_suggestion = confusing_categories_with_low_accuracies_sorted_by_confusion_percent1[i]
                    is_unique= True
                    for suggestion in final_suggestion_list1:
                        if current_suggestion[0] in suggestion or current_suggestion[1] in suggestion:
                            is_unique = False
                            break;
                    if is_unique == True:
                        final_suggestion_list1.append(current_suggestion)
            if 'existing_taxonomy_name' in request.session:
                customQuery = CustomQueries()
                old_trainingset_name = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])[2]
                old_trainingfile = TrainingSet(old_trainingset_name)
                new_categories = list(numpy.unique(trainingfile.target))
                old_categories = list(numpy.unique(old_trainingfile.target))
                common_categories = numpy.intersect1d(new_categories, old_categories)
                common_categories_comparison = []
                for common_category in common_categories:
                    single_category_comparison = []
                    index_of_common_category_in_accuracy_list = new_categories.index(common_category)
                    producerAccuracy = prodacc[index_of_common_category_in_accuracy_list]
                    userAccuracy = useracc[index_of_common_category_in_accuracy_list]
                    single_category_comparison.append(common_category)
                    single_category_comparison.append("Support Vector Machine")
                    single_category_comparison.append(validationtype)
                    single_category_comparison.append(producerAccuracy)
                    single_category_comparison.append(userAccuracy)
                    old_category_details = customQuery.get_accuracies_and_validation_method_of_a_category(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'], common_category)
                    single_category_comparison.append(old_category_details[0][2])
                    single_category_comparison.append(old_category_details[0][3])
                    single_category_comparison.append(old_category_details[0][0])
                    single_category_comparison.append(old_category_details[0][1])
                    common_categories_comparison.append(single_category_comparison)
                return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'suggestion_list': final_suggestion_list1, 'acc_limit': request.session['accuracy_limit'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc, 'common_categories_comparison':common_categories_comparison})
                
            
            return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'suggestion_list': final_suggestion_list1, 'acc_limit': request.session['accuracy_limit'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc})
                  
    else:
        if 'existing_taxonomy_name' in request.session:
            if 'current_exploration_chain_viz' in request.session:
                return render (request, 'signaturefile.html', {'attributes': features, 'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'jm_limit':request.session['jm_distance_limit'], 'acc_limit': request.session['accuracy_limit']})
            else:
                return render (request, 'signaturefile.html', {'attributes': features, 'user_name':user_name, 'jm_limit':request.session['jm_distance_limit'], 'acc_limit': request.session['accuracy_limit']})
        else:
            return render (request, 'signaturefile.html', {'attributes': features, 'user_name':user_name, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'jm_limit':request.session['jm_distance_limit'], 'acc_limit': request.session['accuracy_limit']})


def find_all_active_categories_and_their_comp_int_for_a_legend_version(legend_id, legend_ver):
    customQuery = CustomQueries()
    categories_details = customQuery.getAllActiveCategoriesWithConceptNameForALegend(legend_id, legend_ver)
    
    active_categories_including_comp_versions=[]
    for i, category in enumerate(categories_details):
        if i==0:
            active_categories_including_comp_versions.append([category[0], category[1], category[2], category[3]])
        else:
            comp_ver = False
            for each_category in active_categories_including_comp_versions:
                if category[0] in each_category:
                    comp_ver = True
                    index = active_categories_including_comp_versions.index(each_category)
                    active_categories_including_comp_versions[index].append(category[3])
                    break
            if comp_ver == False:  
                active_categories_including_comp_versions.append([category[0], category[1], category[2], category[3]])
    
    mean_vectors = []
    cov_matrices = []
    
    for each_category in active_categories_including_comp_versions:
        if len(each_category) == 4:
            mean_vector = customQuery.getMeanVectorForACategory(each_category[1], each_category[2], each_category[3])
            cov_matrix = customQuery.getCovMatForACategory(each_category[1], each_category[2], each_category[3])
            mean_vector_list=[]
            for i, value in enumerate(mean_vector[0]):
                mean_vector_list.append(value)
            mean_vector_list.pop(0)
            no_of_bands = 0
            if mean_vector_list[-1] is None:
                mean_vectors.append(mean_vector_list[:3])
                no_of_bands =3
            else:
                mean_vectors.append(mean_vector_list)
                no_of_bands = len(mean_vector_list)
                
            cov_mat_2d_list = []
            a= 0
            each_row= []
            for cell_value in cov_matrix:
                each_row.append(cell_value[0])
                a = a + 1
                if a == no_of_bands:
                    cov_mat_2d_list.append(each_row)
                    each_row= []
                    a = 0
            cov_matrices.append(numpy.matrix(cov_mat_2d_list))

        else:
            no_of_comp_versions = len(each_category) - 3
            comp_versions_mean_vec_list = []
            comp_versions_cov_mat_list = []
            for i in range(no_of_comp_versions):
                mean_vector_list = []
                mean_vector = customQuery.getMeanVectorForACategory(each_category[1], each_category[2], each_category[3+i])
                cov_matrix = customQuery.getCovMatForACategory(each_category[1], each_category[2], each_category[3+i])
                for i, value in enumerate(mean_vector[0]):
                    mean_vector_list.append(value)
                mean_vector_list.pop(0)
                no_of_bands = 0
                if mean_vector_list[-1] == 'None':
                    comp_versions_mean_vec_list.append(mean_vector_list[:3])
                    no_of_bands =3
                else:
                    comp_versions_mean_vec_list.append(mean_vector_list)
                    no_of_bands = len(mean_vector_list)
                
                cov_mat_2d_list = []
                a= 0
                each_row= []
                for cell_value in cov_matrix:
                    each_row.append(cell_value[0])
                    a = a + 1
                    if a == no_of_bands:
                        cov_mat_2d_list.append(each_row)
                        each_row= []
                        a = 0
                comp_versions_cov_mat_list.append(numpy.matrix(cov_mat_2d_list))
                
            mean_vectors.append(comp_versions_mean_vec_list)
            cov_matrices.append(comp_versions_cov_mat_list)
    return active_categories_including_comp_versions, mean_vectors, cov_matrices


def find_index_of_highest_number_except_a_given_index(lst, index):
    if index !=0:
        highest_number_with_index = [0, lst[0]]
    else:
        highest_number_with_index = [1, lst[1]]
    
    for i, num in enumerate(lst):
        if i==index or i==highest_number_with_index[0]:
            continue
        else:
            if num > highest_number_with_index[1]:
                highest_number_with_index = [i, num]
            
    return highest_number_with_index[0]
    

def chooseClassifier(classifiername):
    if classifiername=='Naive Bayes':
        clf= GaussianNB()  
    elif classifiername=='Decision Tree':
        clf=tree.DecisionTreeClassifier()
    else:
        clf = svm.SVC(kernel='rbf', C = 20, gamma = 0.0043287612810830574) #69.123823, 0.001953  21.544346900318832, 'gamma': 0.00046415888336127822} 5.4555947811685188, 'gamma': 0.0012742749857031334}
    #{'C': 21.544346900318832, 'gamma': 0.0059948425031894088}
    #{'C': 4.6415888336127793, 'gamma': 0.0016681005372000592}
    #{'C': 4.3287612810830574, 'gamma': 0.0015199110829529332}
    #{'C': 4.3287612810830574, 'gamma': 0.0015199110829529332}
    #{'C': 15.199110829529332, 'gamma': 0.0043287612810830574}
    #{'C': 12.32846739442066, 'gamma': 0.0043287612810830574}
    # best so far C = 20, gamma = 0.0043287612810830574
    #{'C': 22.615384615384617, 'gamma': 0.0041246263829013523}
    print clf
    return clf

def plot_confusion_matrix(cm, targetValueArray, title='Confusion matrix', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    target_values = numpy.unique(targetValueArray)
    tick_marks = numpy.arange(len(target_values))
    plt.xticks(tick_marks, target_values, rotation=90)
    plt.yticks(tick_marks, target_values)   
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

@login_required
@transaction.atomic 
def unsupervised(request):
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username
    if 'new_taxonomy_name' not in request.session and 'existing_taxonomy_name' not in request.session :
        messages.error(request, "Choose an activity before you proceed further")
        return HttpResponseRedirect("/AdvoCate/home/", {'user_name': user_name})
    
    if request.method == 'POST' and request.is_ajax():
        data = request.POST
        clusteringFilesList = request.FILES.getlist('file')
        number_of_clusters = data['numberofclusters']
        #Combine multiple samples and save it as a csv file
        managedata = ManageRasterData()
        manageCsvData = ManageCSVData()
        clusteringfilename = "cluster_" + str(datetime.now()) + ".csv"
        clusteringFilenameList = [clusteringfile.name for clusteringfile in clusteringFilesList]            
        managedata.combine_multiple_raster_files_to_csv_file(clusteringFilenameList, clusteringfilename, CLUSTERING_DATA_LOCATION, "", False)
        manageCsvData.remove_no_data_value(clusteringfilename, CLUSTERING_DATA_LOCATION, clusteringfilename, '0')
        
        with open('%s%s' % (CLUSTERING_DATA_LOCATION, clusteringfilename), 'rU') as clustering_file:
            datareader = csv.reader(clustering_file, delimiter=',')
            samples = list(datareader)
            num_of_bands = len(samples[0])
            clustering_file.close();
            samples_as_nparray = numpy.asarray(samples, dtype=numpy.float32)
            
        
        
        clustering_method = KMeans(n_clusters = int(number_of_clusters))
        cluster_labels = clustering_method.fit_predict(samples_as_nparray)
        
        '''      
        if num_of_bands == 8:
            fig, axes = plt.subplots(10, 3, squeeze=False)
            fig.set_size_inches(35, 70)
            matplotlib.rcParams.update({'font.size':20})
        else: 
            fig, axes = plt.subplots(1, 3, squeeze=False)
            fig.set_size_inches(15, 5)
            matplotlib.rcParams.update({'font.size':10})
            '''
        
        fig = plt.figure()
        gs = gridspec.GridSpec(2, 2)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 0])
        fig.set_size_inches(18, 14)
        matplotlib.rcParams.update({'font.size':18})
        colors = cm.spectral(cluster_labels.astype(float) / int(number_of_clusters))
        
       
        ax1.scatter(samples_as_nparray[:, 0], samples_as_nparray[:, 3], marker = '.', s=30, lw=0, alpha = 0.7, c = colors)
        ax1.set_xlabel("Band 1")
        ax1.set_ylabel("Band 4")
        centers = clustering_method.cluster_centers_
        ax1.scatter(centers[:, 0], centers[:, 3], marker='o', c="yellow", alpha = 1, s= 200)
        for i, c in enumerate(centers):
            ax1.scatter(c[0], c[3], marker='$%d$' % i, alpha=1, s=50)
        
        ax2.scatter(samples_as_nparray[:, 0], samples_as_nparray[:, 4], marker = '.', s=30, lw=0, alpha = 0.7, c = colors)
        ax2.set_xlabel("Band 1")
        ax2.set_ylabel("Band 5")
        centers = clustering_method.cluster_centers_
        ax2.scatter(centers[:, 0], centers[:, 4], marker='o', c="yellow", alpha = 1, s= 200)
        for i, c in enumerate(centers):
            ax2.scatter(c[0], c[4], marker='$%d$' % i, alpha=1, s=50)
            
        ax3.scatter(samples_as_nparray[:, 3], samples_as_nparray[:, 4], marker = '.', s=30, lw=0, alpha = 0.7, c = colors)
        ax3.set_xlabel("Band 4")
        ax3.set_ylabel("Band 5")
        centers = clustering_method.cluster_centers_
        ax3.scatter(centers[:, 3], centers[:, 4], marker='o', c="yellow", alpha = 1, s= 200)
        for i, c in enumerate(centers):
            ax3.scatter(c[3], c[4], marker='$%d$' % i, alpha=1, s=50)
        
        '''     
        xband = 0
        yband = 1
        for row in axes:
            for cell in row:
                cell.scatter(samples_as_nparray[:, xband], samples_as_nparray[:, yband], marker = '.', s=30, lw=0, alpha = 0.7, c = colors)
                xtitle = "Band" + str(xband+1)
                ytitle = "Band" + str(yband+1)
                cell.set_xlabel(xtitle)
                cell.set_ylabel(ytitle)
                centers = clustering_method.cluster_centers_
                cell.scatter(centers[:, xband], centers[:, yband], marker='o', c="white", alpha = 1, s= 200)
                for i, c in enumerate(centers):
                    cell.scatter(c[xband], c[yband], marker='$%d$' % i, alpha=1, s=50)
                if yband == num_of_bands-1 and xband<num_of_bands-2:
                    xband = xband + 1
                    yband = xband + 1
                elif yband < num_of_bands-1 and xband<num_of_bands-1:
                    yband = yband + 1
                else:
                    break
            if xband>=num_of_bands-1:
                break
        '''
        
        image_name = "cluster_scatter_plot_" + str(datetime.now()) + ".png"
        plt.savefig("%s/%s" % (IMAGE_LOCATION, image_name),  bbox_inches='tight')
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
        ca = ClusteringActivity(clustered_file_name=clusteringfilename, clustered_file_location = CLUSTERING_DATA_LOCATION, scatterplot_image_name = image_name, scatterplot_image_location= IMAGE_LOCATION, completed_by=authuser_instance)
        ca.save()
        exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'clustering', activity_instance = ca.id)
        exp_chain.save(force_insert=True)
        request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1

        data_content = "Clustered file: " + clusteringfilename + "<br/> Scatterplot image: " + image_name + "<br/> Number of clusters: " + number_of_clusters
        current_step = ['Clustering', 'Clustering', data_content]
        
        if 'current_exploration_chain_viz' in request.session:
            current_exploration_chain_viz = request.session['current_exploration_chain_viz']
            if current_exploration_chain_viz[-1][0] == 'End':
                current_exploration_chain_viz.pop()
            current_exploration_chain_viz.append(current_step)
            request.session['current_exploration_chain_viz'] = current_exploration_chain_viz
        else:
            request.session['current_exploration_chain_viz'] = [current_step]
            
        if 'existing_taxonomy_name' in request.session:
            return JsonResponse({'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'scatterplot': image_name})
        else:
            return JsonResponse({'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'scatterplot': image_name})
    else:
        if 'current_exploration_chain_viz' in request.session:
            current_exploration_chain_viz = request.session['current_exploration_chain_viz']
            if current_exploration_chain_viz[-1][0] == 'End':
                current_exploration_chain_viz.pop()
            if 'existing_taxonomy_name' in request.session:
                return render(request, 'unsupervised.html', {'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz']})
            else:
                return render(request, 'unsupervised.html', {'user_name':user_name, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz']})
        
        return render (request, 'unsupervised.html', {'user_name':user_name})
    

@login_required
@transaction.atomic 
def supervised(request):
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username
    if 'new_taxonomy_name' not in request.session and 'existing_taxonomy_name' not in request.session :
        messages.error(request, "Choose an activity before you proceed further")
        return HttpResponseRedirect("/AdvoCate/home/", {'user_name': user_name})
            
    if request.method == 'POST' and request.is_ajax():
        if request.FILES:
            data = request.POST
            testfile = request.FILES['testfile']
            trainingfile = TrainingSet(request.session['current_training_file_name'])
            concepts_in_modelled_taxonomy = list(numpy.unique(trainingfile.target))
            colors = []
            for i, concept in enumerate(concepts_in_modelled_taxonomy):
                color = (re.sub('[(rgb) ]', '', data[str(i)])).split(',')
                colors.append([concept, color])
            updateConfigFiles(colors)
            copyfile(TRAINING_SAMPLES_IMAGES_LOCATION + testfile.name, TEST_DATA_LOCATION + testfile.name)
            request.session['current_test_file_name'] = testfile.name
            manageData = ManageRasterData()
            testFileAsArray = numpy.array(manageData.convert_raster_to_array(testfile.name))
            modelname = request.session['current_model_name']
            clf = joblib.load('%s%s' %(CLASSIFICATION_MODEL_LOCATION, modelname))
            predictedValue = clf.predict(testFileAsArray)
            request.session['current_predicted_file_name'] = testfile.name.split('.', 1)[0] + str(datetime.now()) + '.csv'
            savePredictedValues(request.session['current_predicted_file_name'], predictedValue)
            
            manageData.find_and_replace_data_in_csv_file("config.txt", request.session['current_predicted_file_name'], CLASSIFIED_DATA_LOCATION, request.session['current_predicted_file_name'], CLASSIFIED_DATA_IN_RGB_LOCATION)
            outputMap = testfile.name.split('.', 1)[0] + '_' + str(request.session['exploration_chain_id']) + str(request.session['exploration_chain_step']) + '.tif'
            columns, rows = manageData.create_raster_from_csv_file(request.session['current_predicted_file_name'], testfile.name, CLASSIFIED_DATA_IN_RGB_LOCATION, outputMap, OUTPUT_RASTER_FILE_LOCATION)
            request.session['current_test_file_columns'] = columns
            request.session['current_test_file_rows'] = rows
            outputmapinJPG = testfile.name.split('.', 1)[0] + '_' + str(request.session['exploration_chain_id']) + str(request.session['exploration_chain_step'])  + '.jpeg'
            
            
            authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
            model_instance = Classificationmodel.objects.get(model_name=request.session['current_model_name'])
            si = SatelliteImage(name= request.session['current_test_file_name'], location = TEST_DATA_LOCATION, columns = request.session['current_test_file_columns'], rows = request.session['current_test_file_rows'])
            si.save()
            csi = ClassifiedSatelliteImage(name = outputmapinJPG, location = OUTPUT_RASTER_FILE_LOCATION)
            csi.save()
            tc = ClassificationActivity(model=model_instance, satellite_image_id = si, classified_satellite_image_id = csi, completed_by= authuser_instance)
            tc.save()
            exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'classification', activity_instance = tc.id)
            exp_chain.save(force_insert=True)
            request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1
            
            listofcategories = clf.classes_.tolist()
            
            data_content = "Test file: " + testfile.name + "<br/> Classified map: " + outputmapinJPG
            current_step = ['Classification', 'Classification', data_content]
            
            if 'current_exploration_chain_viz' in request.session:
                current_exploration_chain_viz = request.session['current_exploration_chain_viz']
                if current_exploration_chain_viz[-1][0] == 'End':
                    current_exploration_chain_viz.pop()
                current_exploration_chain_viz.append(current_step)
                request.session['current_exploration_chain_viz'] = current_exploration_chain_viz
            else:
                request.session['current_exploration_chain_viz'] = [current_step]
            
            if 'existing_taxonomy_name' in request.session:
                old_categories, old_mean_vectors, old_covariance_mat = find_all_active_categories_and_their_comp_int_for_a_legend_version(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])
                oldCategories_name = [x[0] for x in old_categories]
                change_matrix, J_Index_for_common_categories, J_Index_for_renamed_existing_categories, extensional_containment_for_categories_split_from_existing, extensional_containment_for_category_merged_from_existing, extensional_containment_for_category_merged_from_new_and_existing = create_change_matrix(request, old_categories, predictedValue, rows, columns)
                
                request.session['J_Index_for_common_categories'] = J_Index_for_common_categories
                request.session['J_Index_for_renamed_existing_categories'] = J_Index_for_renamed_existing_categories
                request.session['extensional_containment_for_categories_split_from_existing'] = extensional_containment_for_categories_split_from_existing
                request.session['extensional_containment_for_category_merged_from_existing'] = extensional_containment_for_category_merged_from_existing
                request.session['extensional_containment_for_category_merged_from_new_and_existing'] = extensional_containment_for_category_merged_from_new_and_existing
                    
                return  JsonResponse({'map': outputmapinJPG, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'categories': listofcategories, 'change_matrix':change_matrix, 'old_categories': oldCategories_name});
            
            return  JsonResponse({'map': outputmapinJPG, 'categories': listofcategories, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz']});
    
    
    elif 'current_model_id' not in request.session:
        trainingfile = TrainingSet(request.session['current_training_file_name'])
        concepts_in_current_taxonomy = list(numpy.unique(trainingfile.target))
        error = "Error: Create a classification model before classifying an image"
        if 'current_exploration_chain_viz' in request.session:
            if 'existing_taxonomy_name' in request.session:
                return render(request, 'supervised.html', {'user_name':user_name, 'error': error, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'concepts': concepts_in_current_taxonomy})
            else:
                return render(request, 'supervised.html', {'user_name':user_name, 'error': error, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'concepts': concepts_in_current_taxonomy})
        else:
            return render(request, 'supervised.html', {'user_name':user_name, 'error': error})
    else:
        trainingfile = TrainingSet(request.session['current_training_file_name'])
        concepts_in_current_taxonomy = list(numpy.unique(trainingfile.target))
        diverging_colors = []
        if (len(concepts_in_current_taxonomy)==4):
            diverging_colors = ['#d7191c', '#fdae61', '#abd9e9', '#2c7bb6']
        elif (len(concepts_in_current_taxonomy)==5):
            diverging_colors = ['#d7191c', '#fdae61', '#ffffbf', '#abd9e9', '#2c7bb6']
        elif (len(concepts_in_current_taxonomy)==6):
            diverging_colors = ['#d73027', '#fc8d59', '#fee090', '#e0f3f8', '#91bfdb', '#4575b4']
        elif (len(concepts_in_current_taxonomy)==7):
            diverging_colors = ['#d73027', '#fc8d59', '#fee090', '#ffffbf', '#e0f3f8', '#91bfdb', '#4575b4']
        elif (len(concepts_in_current_taxonomy)==8):
            diverging_colors = ['#d73027', '#f46d43', '#fdae61', '#fee090', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4']
        elif (len(concepts_in_current_taxonomy)==9):
            diverging_colors = ['#d73027', '#f46d43', '#fdae61', '#fee090', '#ffffbf', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4']
        elif (len(concepts_in_current_taxonomy)==10):
            diverging_colors = ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee090', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
        elif (len(concepts_in_current_taxonomy)==11):
            diverging_colors = ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee090', '#ffffbf', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
        else:
            diverging_colors = ['#ffffff', '#a50026', '#d73027', '#f46d43', '#fdae61', '#fee090', '#ffffbf', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
            
        if 'current_exploration_chain_viz' in request.session:
            if 'existing_taxonomy_name' in request.session:
                return render(request, 'supervised.html', {'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'concepts': concepts_in_current_taxonomy, 'diverging_colors': diverging_colors})
            else:
                return render(request, 'supervised.html', {'user_name':user_name, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'concepts': concepts_in_current_taxonomy, 'diverging_colors': diverging_colors})
        else:
            return render (request, 'supervised.html', {'user_name':user_name, 'concepts': concepts_in_current_taxonomy, 'diverging_colors': diverging_colors})


def updateConfigFiles(conceptsandcolors):
    sorted_concepts = sorted(conceptsandcolors, key= lambda concept: len(concept[0]))
    line1 = ""
    line2 = ""
    for concept in reversed(sorted_concepts):
        line1 = line1 + concept[0] + ";"
        line2 = line2 + concept[1][0] + "," + concept[1][1] + "," + concept[1][2] + ";"
    
    with open("Category_Modeler/config.txt", 'w') as text_file:
        text_file.write(line1 + "\n")
        text_file.write(line2 + "\n")
    
    

def savePredictedValues(filename, predictedValue):
    with BufferedWriter( FileIO( '%s%s' % (CLASSIFIED_DATA_LOCATION, filename), "wb" ) ) as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        for i in range(len(predictedValue)):
            spamwriter.writerow([predictedValue[i]])
    csvfile.close();


def read_test_file_as_array(f):
    with open('Category_Modeler/static/testfiles/%s' % f, 'rU') as datafile:
        dataReader = csv.reader(datafile, delimiter=',', quoting=csv.QUOTE_NONE)
        samples = list(dataReader)
        datafile.close();
    return samples

def create_change_matrix(request, oldCategories, newPredictedValues, rows, columns):
    list_of_new_categories = list(numpy.unique(newPredictedValues))
    change_in_individual_matrix = [[0 for a in range(len(list_of_new_categories)+1)] for x in range(len(oldCategories)+1)]
    customQuery = CustomQueries()
    
    total_competing_versions = 1
    for category_details in oldCategories:
        if len(category_details) <= (3+ total_competing_versions):
            continue
        else:
            total_competing_versions = len(category_details) - 3
    
    total_change_matrices = []
    for i in range(total_competing_versions):
        change_in_individual_matrix = [[0 for a in range(len(list_of_new_categories)+1)] for x in range(len(oldCategories)+1)]
        for index, category_details in enumerate(oldCategories):
            if len(category_details) >= (4+i):
                category_extension = customQuery.getExtension(category_details[1], category_details[2], category_details[3+i])
            else:
                category_extension = customQuery.getExtension(category_details[1], category_details[2], category_details[3])
            for coordinates in category_extension: 
                ind = coordinates[0]*columns + coordinates[1]
                new_category = newPredictedValues[ind]
                new_category_index = list_of_new_categories.index(new_category)
                change_in_individual_matrix[index][new_category_index] += 1
            change_in_individual_matrix[index][len(list_of_new_categories)] += len(category_extension)
        
        for ind, change in enumerate(change_in_individual_matrix):
            if ind != len(oldCategories):
                for inde, value in enumerate(change):
                    change_in_individual_matrix[-1][inde] += value
        
        total_change_matrices.append(change_in_individual_matrix)
              

    J_Index_for_common_categories = []
    common_categories = []
    if 'existing_categories' in request.session:
        common_categories = request.session['existing_categories']
    
    for category in common_categories:
        new_category_index = list_of_new_categories.index(category)
        old_category_index = [item[0] for item in oldCategories].index(category)
        number_of_comp_versions = len(oldCategories[old_category_index])-3
        j_index_list= []
        for i in range(number_of_comp_versions):
            common_elements = float(total_change_matrices[i][old_category_index][new_category_index])
            old_elements = float(total_change_matrices[i][old_category_index][-1])
            new_elements = float(total_change_matrices[i][-1][new_category_index])
            union_of_elements = old_elements + new_elements - common_elements
            j_index = "{0:.2f}".format(float(common_elements/union_of_elements))
            j_index_list.append([oldCategories[old_category_index][1], oldCategories[old_category_index][2], oldCategories[old_category_index][3+i], j_index])
        J_Index_for_common_categories.append([category, j_index_list])

    
    J_Index_for_renamed_existing_categories = []
    renamed_existing_categories = []
    if 'renamed_existing_categories' in request.session:
        renamed_existing_categories = request.session['renamed_existing_categories']
        
    for category_details in renamed_existing_categories:
        new_category_index = [item for item in list_of_new_categories].index(category_details[1])
        old_category_index = [item[0] for item in oldCategories].index(category_details[0])
        number_of_comp_versions = len(oldCategories[old_category_index])-3
        j_index_list= []
        for i in range(number_of_comp_versions):
            common_elements = float(total_change_matrices[i][old_category_index][new_category_index])
            old_elements = float(total_change_matrices[i][old_category_index][-1])
            new_elements = float(total_change_matrices[i][-1][new_category_index])
            
            union_of_elements = old_elements + new_elements - common_elements
            j_index = "{0:.2f}".format(float(common_elements/union_of_elements))
            j_index_list.append([oldCategories[old_category_index][1], oldCategories[old_category_index][2], oldCategories[old_category_index][3+i], j_index])
        J_Index_for_renamed_existing_categories.append([category_details[1], category_details[0], j_index_list])   
    
    
    extensional_containment_for_categories_split_from_existing = []
    if 'categories_split_from_existing' in request.session:
        for index, category in enumerate(list_of_new_categories):
            for split_categories in request.session['categories_split_from_existing']:
                if category in split_categories:
                    index_of_category_split_from = [item[0] for item in oldCategories].index(split_categories[0])
                    number_of_comp_versions = len(oldCategories[index_of_category_split_from])-3
                    j_index_list= []
                    for i in range(number_of_comp_versions):
                        total_extension_of_category = float(total_change_matrices[i][-1][index])
                        common_extension_of_catgeory_as_category_it_split_from = float(total_change_matrices[i][index_of_category_split_from][index])
                        containment = "{0:.2f}".format(float(common_extension_of_catgeory_as_category_it_split_from/total_extension_of_category))
                        j_index_list.append([oldCategories[index_of_category_split_from][1], oldCategories[index_of_category_split_from][2], oldCategories[index_of_category_split_from][3+i], containment])
                    extensional_containment_for_categories_split_from_existing.append([category, split_categories[0], j_index_list])
                    break
                        
    
    extensional_containment_for_category_merged_from_existing = []
    if 'categories_merged_from_existing' in request.session:
        for index, category in enumerate(list_of_new_categories):
            containment_details = []
            for merge_categories in request.session['categories_merged_from_existing']:
                if category in merge_categories:
                    containment_details.append(category)
                    for i in range(len(merge_categories)-1):
                        index_of_category_merged = [item[0] for item in oldCategories].index(merge_categories[i])
                        number_of_comp_versions = len(oldCategories[index_of_category_merged])-3
                        j_index_list= []
                        for j in range(number_of_comp_versions):
                            total_extension_of_category_merged = float(total_change_matrices[j][index_of_category_merged][-1])
                            common_extension = float(total_change_matrices[j][index_of_category_merged][index])
                            containment = "{0:.2f}".format(float(common_extension/total_extension_of_category_merged))
                            j_index_list.append([oldCategories[index_of_category_merged][1], oldCategories[index_of_category_merged][2], oldCategories[index_of_category_merged][3+j], containment])
                        containment_details.append([merge_categories[i], j_index_list])
                    extensional_containment_for_category_merged_from_existing.append(containment_details)
                    break
                    

    extensional_containment_for_category_merged_from_new_and_existing = []
    if 'categories_merged_from_new_and_existing' in request.session:
        for index, category in enumerate(list_of_new_categories):
            containment_details = []
            for merge_categories in request.session['categories_merged_from_new_and_existing']:
                if category in merge_categories:
                    containment_details.append(category)
                    for i in range(len(merge_categories)-1):
                        if merge_categories[i] in [item[0] for item in oldCategories]:
                            index1 = [item[0] for item in oldCategories].index(merge_categories[i])
                            number_of_comp_versions = len(oldCategories[index1])-3
                            j_index_list= []
                            for j in range(number_of_comp_versions):
                                total_extension_of_existing_category_that_is_merged = float(total_change_matrices[j][index1][-1])
                                common_extension = float(total_change_matrices[j][index1][index])
                                containment = "{0:.2f}".format(float(common_extension/total_extension_of_existing_category_that_is_merged))
                                j_index_list.append([oldCategories[index1][1], oldCategories[index1][2], oldCategories[index1][3+j], containment])
                            containment_details.append([merge_categories[i], j_index_list])
                    extensional_containment_for_category_merged_from_new_and_existing.append(containment_details)
                    break                        
            
    return total_change_matrices[0], J_Index_for_common_categories, J_Index_for_renamed_existing_categories, extensional_containment_for_categories_split_from_existing, extensional_containment_for_category_merged_from_existing, extensional_containment_for_category_merged_from_new_and_existing

    

@login_required
def changeRecognizer(request):
    customQuery = CustomQueries()
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username
    if 'new_taxonomy_name' not in request.session and 'existing_taxonomy_name' not in request.session:
        if 'view_existing_taxonomies' not in request.session:
            messages.error(request, "Choose an activity before you proceed further")
            return HttpResponseRedirect("/AdvoCate/home/", {'user_name': user_name})
        else:
            messsage = "Choose visualization tab to view and compare existing taxonomies"
            return render (request, 'changerecognition.html', {'user_name':user_name, 'error_message': messsage})
    elif 'existing_taxonomy_name' not in request.session:
        if 'current_predicted_file_name' not in request.session:
            exp_incomplete = "The exploration process is not yet completed. No changes can be detected."
            return render (request, 'changerecognition.html', {'user_name':user_name, 'error_message': exp_incomplete})
        else:
            new_taxonomy = request.session['new_taxonomy_name']
            trainingfile = TrainingSet(request.session['current_training_file_name'])
            concepts_in_current_taxonomy = list(numpy.unique(trainingfile.target))
            model_accuracy = request.session['model_score']
            user_accuracies = request.session['user_accuracies']
            producer_accuracies = request.session['producer_accuracies']
            model_type = request.session['model_type']
            
            exploration_chain_details = []
            
            current_exploration_chain_viz = request.session['current_exploration_chain_viz']
            last_data_content = current_exploration_chain_viz[-1]
            if last_data_content[0] != 'End':
                current_step = ['End', 'End', ""]
                current_exploration_chain_viz.append(current_step)
                request.session['current_exploration_chain_viz'] = current_exploration_chain_viz

            return render(request, 'changerecognition.html', {'user_name':user_name, 'new_taxonomyName': new_taxonomy, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'exploration_chain':exploration_chain_details, 'conceptsList':concepts_in_current_taxonomy, 'modelType': model_type, 'modelScore': model_accuracy, 'userAccuracies': user_accuracies, 'producerAccuracies': producer_accuracies})
    else:
        existing_taxonomy = request.session['existing_taxonomy_name']
        existing_taxonomy_instance = Legend.objects.get(legend_id = request.session['existing_taxonomy_id'], legend_ver = request.session['existing_taxonomy_ver']) 
        trid = existing_taxonomy_instance.legend_id
        ver = existing_taxonomy_instance.legend_ver
        old_model = customQuery.get_model_name_and_accuracy_from_a_legend(trid, ver)
        old_model_type = old_model[0]
        old_model_accuracy = float(old_model[1])*100.00
        model_type = request.session['model_type']
        model_accuracy = float(request.session['model_score'])*100.00
        trainingfile = TrainingSet(request.session['current_training_file_name'])
        concepts_in_current_taxonomy = list(numpy.unique(trainingfile.target))
        user_accuracies = request.session['user_accuracies']
        producer_accuracies = request.session['producer_accuracies']
                
        #new categories in the newly modeled set of categories
        new_categories_details = []
        if 'new_categories' in request.session:
            new_categories = request.session['new_categories']
            for each_category in new_categories:
                index = concepts_in_current_taxonomy.index(each_category)
                new_categories_details.append([each_category, user_accuracies[index], producer_accuracies[index]])
        
        #categories common to newly modeled set of categories and the categories stored in the latest version of the legend
        common_categories_comparison_details = []
        if 'existing_categories' in request.session:
            J_Index_for_common_categories = request.session['J_Index_for_common_categories']
            existing_categories = request.session['existing_categories']
            for each_category in existing_categories:
                single_category_comparison = [each_category]
                index = concepts_in_current_taxonomy.index(each_category)
                single_category_comparison.extend([user_accuracies[index], producer_accuracies[index]])
                old_category_details = customQuery.get_accuracies_and_validation_method_of_a_category(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'], each_category)
                if len(old_category_details) == 1:
                    single_category_comparison.extend([old_category_details[0][1], old_category_details[0][0]])
                else:
                    x1, y1 = str(old_category_details[0][1]), str(old_category_details[0][0])
                    for i in range(1, len(old_category_details)):
                        x1 = x1 + ", " + str(old_category_details[i][1])
                        y1 = y1 + ", " + str(old_category_details[i][0])
                    single_category_comparison.extend([x1, y1])
                    
                for category_andJ_index in J_Index_for_common_categories:
                    if each_category in category_andJ_index:
                        jindex_list = str(category_andJ_index[1][0][3])
                        for i in range(1, len(category_andJ_index[1])):
                            jindex_list = jindex_list + ", " + str(category_andJ_index[1][i][3])
                        single_category_comparison.append(jindex_list)
                        break
                if 'existing_categories_computational_intension_comparison' in request.session:
                    existing_categories_computational_intension_comparison = request.session['existing_categories_computational_intension_comparison']
                    for each_category_compint_comparison in existing_categories_computational_intension_comparison:
                        if each_category_compint_comparison[0] == each_category:
                            if len(each_category_compint_comparison[1]) ==1:
                                JM_list = str(each_category_compint_comparison[1][0])
                            else:
                                JM_list = str(each_category_compint_comparison[1][0][1])
                                for j in range(1, len(each_category_compint_comparison[1])):
                                    JM_list = JM_list + ", " +  each_category_compint_comparison[1][j][1]
                            single_category_comparison.append(JM_list)
                            break
                common_categories_comparison_details.append(single_category_comparison)
        
        #categories common to newly modeled set of categories and the categories stored in the latest version of the legend, but the concept is renamed
        if 'renamed_existing_categories' in request.session:
            J_Index_for_renamed_existing_categories = request.session['J_Index_for_renamed_existing_categories']
            renamed_existing_categories = request.session['renamed_existing_categories']
            for each_category in renamed_existing_categories:
                single_category_comparison = []
                single_category_comparison.append(each_category[1] + "/" + each_category[0])
                index = concepts_in_current_taxonomy.index(each_category[1])
                single_category_comparison.extend([user_accuracies[index], producer_accuracies[index]])
                old_category_details = customQuery.get_accuracies_and_validation_method_of_a_category(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'], each_category[0])
                if len(old_category_details) == 1:
                    single_category_comparison.extend([old_category_details[0][1], old_category_details[0][0]])
                else:
                    x1, y1 = str(old_category_details[0][1]), str(old_category_details[0][0])
                    for i in range(1, len(old_category_details)):
                        x1 = x1 + ", " + str(old_category_details[i][1])
                        y1 = y1 + ", " + str(old_category_details[i][0])
                    single_category_comparison.extend([x1, y1])
                    
                for category_andJ_index in J_Index_for_renamed_existing_categories:
                    if each_category[1] in category_andJ_index:
                        jindex_list = str(category_andJ_index[2][0][3])
                        for i in range(1, len(category_andJ_index[2])):
                            jindex_list = jindex_list + ", " + str(category_andJ_index[2][i][3])
                        single_category_comparison.append(jindex_list)
                        break
                if 'renamed_existing_categories_computational_intension_comparison' in request.session:
                    renamed_existing_categories_computational_intension_comparison = request.session['renamed_existing_categories_computational_intension_comparison']
                    for each_category_compint_comparison in renamed_existing_categories_computational_intension_comparison:
                        if each_category_compint_comparison[0] == each_category[1]:
                            if len(each_category_compint_comparison[2]) ==1:
                                JM_list = str(each_category_compint_comparison[2][0])
                            else:
                                JM_list = str(each_category_compint_comparison[2][0][1])
                                for j in range(1, len(each_category_compint_comparison[2])):
                                    JM_list = JM_list + ", " +  each_category_compint_comparison[2][j][1]
                            single_category_comparison.append(JM_list)
                            break
                common_categories_comparison_details.append(single_category_comparison)

            
        #categories resulted from merging of existing categories
        categories_merged_from_existing_details = []
        if 'categories_merged_from_existing' in request.session:
            extensional_containment_for_category_merged_from_existing = request.session['extensional_containment_for_category_merged_from_existing']
            categories_merged_from_existing = request.session['categories_merged_from_existing']
            for each_merged_category in categories_merged_from_existing:
                index = concepts_in_current_taxonomy.index(each_merged_category[-1])
                index1 = extensional_containment_for_category_merged_from_existing.index([x for x in extensional_containment_for_category_merged_from_existing if each_merged_category[-1] in x][0])
                
                for i in range(len(each_merged_category)-1):
                    details = []
                    details = [each_merged_category[-1]]
                    details.append(user_accuracies[index])
                    details.append(producer_accuracies[index])
                    details.append(extensional_containment_for_category_merged_from_existing[index1][i+1][0])
                    j_index_list = extensional_containment_for_category_merged_from_existing[index1][i+1][1][0][3]
                    for j in range (1, len(extensional_containment_for_category_merged_from_existing[index1][i+1][1])):
                        j_index_list = j_index_list + ", " + extensional_containment_for_category_merged_from_existing[index1][i+1][1][j][3]
                    details.append(j_index_list)
                    
                    if 'merged_categories_computational_intension_comparison' in request.session:
                        merged_categories_computational_intension_comparison = request.session['merged_categories_computational_intension_comparison']
                        for each_set in merged_categories_computational_intension_comparison:
                            if each_merged_category[-1] == each_set[0] and each_merged_category[i] == each_set[1]:
                                if len(each_set[2])==1:
                                    jm_list = str(each_set[2][0])
                                else:
                                    jm_list = str(each_set[2][0][1])
                                    for k in range(1, len(each_set[2])):
                                        jm_list = jm_list + ", " + str(each_set[2][k][1])
                                details.append(jm_list)
                                break
                        
                    categories_merged_from_existing_details.append(details)
          
        #categories resulted from merging of existing and new categories
        categories_merged_from_new_and_existing_details = []
        if 'categories_merged_from_new_and_existing' in request.session: 
            extensional_containment_for_category_merged_from_new_and_existing = request.session['extensional_containment_for_category_merged_from_new_and_existing']
            categories_merged_from_new_and_existing = request.session['categories_merged_from_new_and_existing']
            for each_merged_category in categories_merged_from_new_and_existing:
                index = concepts_in_current_taxonomy.index(each_merged_category[-1])
                
                for each_set in extensional_containment_for_category_merged_from_new_and_existing:
                    if each_merged_category[-1] in each_set[0]:
                        for i in range(1, len(each_set)):
                            details = []
                            details = [each_merged_category[-1]]
                            details.append(user_accuracies[index])
                            details.append(producer_accuracies[index])
                            details.append(each_set[i][0])
                            j_index_list = str(each_set[i][1][0][3])
                            for j in range(1, len(each_set[i][1])):
                                j_index_list = j_index_list + ", " + str(each_set[i][1][j][3])
                            details.append(j_index_list)
                            
                            if 'merged_categories_from_new_and_existing_comparison' in request.session:
                                merged_categories_from_new_and_existing_comparison = request.session['merged_categories_from_new_and_existing_comparison']
                                for each_set1 in merged_categories_from_new_and_existing_comparison:
                                    if each_merged_category[-1] == each_set1[0] and each_set[i][0] == each_set1[1]:
                                        if len(each_set1[2])==1:
                                            jm_list = str(each_set1[2][0])
                                        else:
                                            jm_list = str(each_set1[2][0][1])
                                            for k in range(1, len(each_set1[2])):
                                                jm_list = jm_list + ", " + str(each_set1[2][k][1])
                                        details.append(jm_list)
                                        break
                            categories_merged_from_new_and_existing_details.append(details)
                        break
                
        
        #categories resulted from splitting of existing
        categories_split_from_existing_details = []
        if 'categories_split_from_existing' in request.session: 
            extensional_containment_for_categories_split_from_existing = request.session['extensional_containment_for_categories_split_from_existing']
            categories_split_from_existing = request.session['categories_split_from_existing']
            for each_split_category in categories_split_from_existing:
                for i in range(1, len(each_split_category)):
                    index = concepts_in_current_taxonomy.index(each_split_category[i])
                    details = []
                    details.extend([each_split_category[i], user_accuracies[index], producer_accuracies[index], each_split_category[0]])
                    for each_set in extensional_containment_for_categories_split_from_existing:
                        if each_split_category[i] in each_set and each_split_category[0] in each_set:
                            j_index_list = str(each_set[2][0][3])
                            for j in range(1, len(each_set[2])):
                                j_index_list = j_index_list + ", " + each_set[2][j][3]
                            details.append(j_index_list)
                            break
                    if 'split_categories_computational_intension_comparison' in request.session:
                        split_categories_computational_intension_comparison = request.session['split_categories_computational_intension_comparison']
                        for each_set1 in split_categories_computational_intension_comparison:
                            if each_set1[0] == each_split_category[i] and each_set1[1] == each_split_category[0]:
                                if len(each_set1[2])==1:
                                    jm_list = str(each_set1[2][0])
                                else:
                                    jm_list = str(each_set1[2][0][1])
                                    for k in range(1, len(each_set1[2])):
                                        jm_list = jm_list + ", " + str(each_set1[2][k][1])
                                details.append(jm_list)
                                break
                    categories_split_from_existing_details.append(details)

        grouped_categories_details = []
        if 'grouped_categories' in request.session:
            categories_grouped = request.session['grouped_categories']
            for each_set in categories_grouped:
                details = [each_set[-1]]
                grouped_categories_list = str(each_set[0])
                for i in range(1, len(each_set)-1):
                    grouped_categories_list = grouped_categories_list + ", " + str(each_set[i])
                details.append(grouped_categories_list)
                grouped_categories_details.append(details)
                    

        current_exploration_chain_viz = request.session['current_exploration_chain_viz']
        last_data_content = current_exploration_chain_viz[-1]
        if last_data_content[0] != 'End':
            current_step = ['End', 'End', ""]
            current_exploration_chain_viz.append(current_step)
            request.session['current_exploration_chain_viz'] = current_exploration_chain_viz
            
        cint_min_limit = request.session['cint_min_limit']
        cint_max_limit = request.session['cint_max_limit']
        ext_min_limit = request.session['ext_min_limit']
        ext_max_limit = request.session['ext_max_limit']
        
        return render(request, 'changerecognition.html', {'user_name':user_name, 'existing_taxonomyName': existing_taxonomy, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'model_type': model_type, 'model_score': model_accuracy, 'old_model_type':old_model_type, 'old_model_accuracy': old_model_accuracy, 'external_trigger': request.session['external_trigger'], 'common_categories_comparison_details':common_categories_comparison_details, 'new_categories_details': new_categories_details, 'categories_merged_from_existing_details': categories_merged_from_existing_details, 'categories_split_from_existing_details': categories_split_from_existing_details, 'categories_merged_from_new_and_existing_details': categories_merged_from_new_and_existing_details, 'grouped_categories_details': grouped_categories_details, 'cint_min_limit': cint_min_limit, 'cint_max_limit': cint_max_limit, 'ext_min_limit': ext_min_limit, 'ext_max_limit': ext_max_limit})
        
    return render (request, 'changerecognition.html', {'user_name':user_name})

def createChangeEventForNewTaxonomy(request):
    compositeChangeOperations = []
    firstOp, root_concept = get_addTaxonomy_op_details(request.session['new_taxonomy_name'])
    compositeChangeOperations.append(firstOp)

    trainingfile = TrainingSet(request.session['current_training_file_name'])
    concepts_in_current_taxonomy = list(numpy.unique(trainingfile.target))
    for concept in concepts_in_current_taxonomy:
        changeOperation = get_addConcept_op_details(request.session['new_taxonomy_name'], 1, root_concept, concept)
        compositeChangeOperations.append(changeOperation)
        
    return JsonResponse({'listOfOperations': compositeChangeOperations});

def createChangeEventForNewTaxonomyVersion(request):
    request.session['create_new_taxonomy_version'] = True
    customQuery = CustomQueries()
    old_trainingset = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])
    old_training_sample = TrainingSet(old_trainingset[2])
    concepts_in_existing_taxonomy = list(numpy.unique(old_training_sample.target))
    compositeChangeOperations = []
    new_version = int(request.session['existing_taxonomy_ver'])+1
    firstOp, root_concept = get_addNewTaxonomyVersion_op_details(request.session['existing_taxonomy_name'], new_version)
    compositeChangeOperations.append(firstOp)
    
    if 'existing_categories' in request.session:
        existing_categories = request.session['existing_categories']
        for category in existing_categories:
            changeOperation = get_addExistingConceptForNewTaxonomyVersion_op_details(request.session['existing_taxonomy_name'], new_version, request.session['existing_taxonomy_ver'], root_concept, category)
            compositeChangeOperations.append(changeOperation)

    if 'renamed_existing_categories' in request.session:
        renamed_existing_categories = request.session['renamed_existing_categories']
        for category in renamed_existing_categories:
            changeOperation = get_addExistingConceptForNewTaxonomyVersion_op_details(request.session['existing_taxonomy_name'], new_version, request.session['existing_taxonomy_ver'], root_concept, category[1])
            compositeChangeOperations.append(changeOperation)

    if 'new_categories' in request.session:
        new_categories = request.session['new_categories']
        for category in new_categories:
            changeOperation = get_addConcept_op_details(request.session['existing_taxonomy_name'], new_version, root_concept, category)
            compositeChangeOperations.append(changeOperation)
            
    if 'categories_merged_from_existing' in request.session:
        categories_merged_from_existing = request.session['categories_merged_from_existing']
        for category in categories_merged_from_existing:
            new_concept = category[-1]
            changeOperation = get_addMergedConceptFromExistingConceptsForNewTaxonomyVersion_op_details(request.session['existing_taxonomy_name'], new_version, request.session['existing_taxonomy_ver'], root_concept, new_concept, category[:-1])
            compositeChangeOperations.append(changeOperation)
    
    if 'categories_split_from_existing' in request.session:
        categories_split_from_existing = request.session['categories_split_from_existing']
        for category in categories_split_from_existing:
            split_concept = category[0]
            for i in range(1, len(category)):
                changeOperation = get_addNewConceptSplitFromExistingConceptForNewTaxonomyVersion_op_details(request.session['existing_taxonomy_name'], new_version, request.session['existing_taxonomy_ver'], root_concept, category[i], split_concept)
                compositeChangeOperations.append(changeOperation)
    
    if 'categories_merged_from_new_and_existing' in request.session:
        categories_merged_from_new_and_existing = request.session['categories_merged_from_new_and_existing']
        for category in categories_merged_from_new_and_existing:
            new_concept = category[-1]
            existing_categories = [x for x in category[:-1] if x in concepts_in_existing_taxonomy]
            changeOperation = get_addMergedConceptFromNewAndExistingConceptsForNewTaxonomyVersion_op_details(request.session['existing_taxonomy_name'], new_version, request.session['existing_taxonomy_ver'], root_concept, new_concept, existing_categories)
            compositeChangeOperations.append(changeOperation)
            
    if 'grouped_categories' in request.session:
        categories_grouped = request.session['grouped_categories']
        parent_name = "root_AKL_LCDB2"
        for each_set in categories_grouped:
            new_concept = each_set[-1]
            changeOperation = get_groupConcepts_op_details(request.session['existing_taxonomy_name'], new_version, new_concept, parent_name, each_set[:-1])
            compositeChangeOperations.append(changeOperation)
                
    
    return JsonResponse({'listOfOperations': compositeChangeOperations});

def changeintandextThresholdLimits(request):
    if request.method=='POST':
        data = request.POST;
        cint_min_limit = data['1']
        cint_max_limit = data['2']
        ext_min_limit = data['3']
        ext_max_limit = data['4']
        
        request.session['cint_min_limit'] = cint_min_limit
        request.session['cint_max_limit'] = cint_max_limit
        request.session['ext_min_limit'] = ext_min_limit
        request.session['ext_max_limit'] = ext_max_limit
        return HttpResponse("")
    

def getChangeSuggestionsBasedOnThresholdLimits(request):
    if 'add_evolutionary_version' in request.session:
        del request.session['add_evolutionary_version']
    if 'add_competing_version' in request.session:
        del request.session['add_competing_version']
    request.session.modified = True
    request.session['add_evolutionary_version'] = []
    request.session['add_competing_version'] = []
    cint_min = float(request.session['cint_min_limit'])
    cint_max = float(request.session['cint_max_limit'])
    ext_min = float(request.session['ext_min_limit'])
    ext_max = float(request.session['ext_max_limit'])
    existing_categories = []
    renamed_existing_categories = []
    if 'existing_categories' in request.session:
        existing_categories = request.session['existing_categories']
    if 'renamed_existing_categories' in request.session:
        renamed_existing_categories = request.session['renamed_existing_categories']
        
    existing_categories_int_comparison = []
    existing_categories_ext_comparison = []
    renamed_existing_categories_int_comparison = []
    renamed_existing_categories_ext_comparison = []
    if 'existing_categories_computational_intension_comparison' in request.session:
        existing_categories_int_comparison = request.session['existing_categories_computational_intension_comparison']
    if 'renamed_existing_categories_computational_intension_comparison'in request.session:
        renamed_existing_categories_int_comparison = request.session['renamed_existing_categories_computational_intension_comparison']
    if 'J_Index_for_common_categories' in request.session:
        existing_categories_ext_comparison = request.session['J_Index_for_common_categories']
    if 'J_Index_for_renamed_existing_categories' in request.session:
        renamed_existing_categories_ext_comparison = request.session['J_Index_for_renamed_existing_categories']
    
    for category in existing_categories:
        ext_similarity = 0.0
        for each_set in existing_categories_ext_comparison:
            if category in each_set:
                ext_similarity = float(each_set[1][-1][3])
                break
        JM_distance = 0.0
        for each_set1 in existing_categories_int_comparison:
            if category in each_set1:
                if len(each_set1[1]) == 1:
                    JM_distance = float(each_set1[1][0])
                else:
                    JM_distance = float(each_set1[1][-1][1])
                break
        if (1.0-ext_similarity) <= ext_min and JM_distance <= cint_min:
            continue
        elif (1.0-ext_similarity) > ext_max or JM_distance > cint_max:
            add_evolutionary_version = request.session['add_evolutionary_version']
            add_evolutionary_version.append(category)
            request.session['add_evolutionary_version'] = add_evolutionary_version
        elif ((1.0-ext_similarity) > ext_min and (1.0-ext_similarity) <= ext_max)  or (JM_distance > cint_min and JM_distance <= cint_max):
            add_competing_version = request.session['add_competing_version']
            add_competing_version.append(category)
            request.session['add_competing_version'] = add_competing_version
        
    for category in renamed_existing_categories:
        ext_similarity = 0.0
        for each_set in renamed_existing_categories_ext_comparison:
            if category[1] in each_set:
                ext_similarity = float(each_set[2][-1][3])
                break
        JM_distance = 0.0
        for each_set1 in renamed_existing_categories_int_comparison:
            if category[1] in each_set1:
                if len(each_set1[2]) == 1:
                    JM_distance = float(each_set1[2][0])
                else:
                    JM_distance = float(each_set1[2][-1][1])
                break
        
        if (1.0-ext_similarity) <= ext_min and JM_distance <= cint_min:
            continue
        elif (1.0-ext_similarity) > ext_max or JM_distance > cint_max:
            add_evolutionary_version = request.session['add_evolutionary_version']
            add_evolutionary_version.append(category[1])
            request.session['add_evolutionary_version'] = add_evolutionary_version
        elif ((1.0-ext_similarity) > ext_min and (1.0-ext_similarity) <= ext_max)  or (JM_distance > cint_min and JM_distance <= cint_max):
            add_competing_version = request.session['add_competing_version']
            add_competing_version.append(category[1])
            request.session['add_competing_version'] = add_competing_version
            
    return JsonResponse({'evolutionary_versions': request.session['add_evolutionary_version'], 'competing_versions':  request.session['add_competing_version']})
        
        

def getUserInputToCreateChangeEvent(request):
    existing_categories = []
    if 'existing_categories' in request.session:
        existing_categories = request.session['existing_categories']
    if 'renamed_existing_categories' in request.session:
        renamed_existing_categories = request.session['renamed_existing_categories']
    for each_set in renamed_existing_categories:
        existing_categories.append(each_set[1] + "(old name: " + each_set[0] + ")")
    return JsonResponse({'existing_categories': existing_categories});
                                    
        

def createChangeEventForExistingTaxonomy(request):

    if request.method == 'POST' and request.is_ajax():
        if 'add_evolutionary_version' in request.session:
            del request.session['add_evolutionary_version']
        if 'add_competing_version' in request.session:
            del request.session['add_competing_version']
        request.session.modified = True
        data = request.POST
        for i in range(1, len(data)+1):
            category = data[str(i)]
            catgeory_details = category.rsplit(' ', 1)
            if catgeory_details[1] == "evol":
                if 'add_evolutionary_version' in request.session:
                    add_evolutionary_version = request.session['add_evolutionary_version']
                    add_evolutionary_version.append(catgeory_details[0])
                    request.session['add_evolutionary_version'] = add_evolutionary_version
                else:
                    add_evolutionary_version = [catgeory_details[0]]
                    request.session['add_evolutionary_version'] = add_evolutionary_version
            elif catgeory_details[1] == "comp":
                if 'add_competing_version' in request.session:
                    add_competing_version = request.session['add_competing_version']
                    add_competing_version.append(catgeory_details[0])
                    request.session['add_competing_version'] = add_competing_version
                else:
                    add_competing_version = [catgeory_details[0]]
                    request.session['add_competing_version'] = add_competing_version

        
    compositeChangeOperations = []
    version = request.session['existing_taxonomy_ver']
    root_concept = "root_" + request.session['existing_taxonomy_name'] + str(version)
    customqueries = CustomQueries()
    
    if 'new_categories' in request.session:
        new_categories = request.session['new_categories']         
        for category in new_categories:
            changeOperation = get_addConcept_op_details(request.session['existing_taxonomy_name'], version, root_concept, category)
            compositeChangeOperations.append(changeOperation)
    
    if 'add_evolutionary_version' in request.session:
        add_evolutionary_version = request.session['add_evolutionary_version']
        for category in add_evolutionary_version:
            changeOperation = get_addEvolutionaryVersion_op_details(request.session['existing_taxonomy_name'], version, category)
            compositeChangeOperations.append(changeOperation)
    
    if 'add_competing_version' in request.session:
        add_competing_version = request.session['add_competing_version']
        for category in add_competing_version:
            changeOperation = get_addCompetingVersion_op_details(request.session['existing_taxonomy_name'], version, category)
            compositeChangeOperations.append(changeOperation)
    
            
    if 'categories_merged_from_existing' in request.session:
        
        merge_categories = request.session['categories_merged_from_existing']
        for category in merge_categories:
            new_concept = category[-1]
            parent_name = customqueries.getParentNameOfAConcept(request.session['existing_taxonomy_id'], version, category[0])
            changeOperation = get_MergeConcepts_op_details(request.session['existing_taxonomy_name'], version, new_concept, parent_name, category[:-1])
            compositeChangeOperations.append(changeOperation)
    
    if 'grouped_categories' in request.session:
        categories_grouped = request.session['grouped_categories']
        for each_set in categories_grouped:
            new_concept = each_set[-1]
            parent_name = customqueries.getParentNameOfAConcept(request.session['existing_taxonomy_id'], version, each_set[0])
            changeOperation = get_groupConcepts_op_details(request.session['existing_taxonomy_name'], version, new_concept, parent_name, each_set[:-1])
            compositeChangeOperations.append(changeOperation)

    
    if 'categories_split_from_existing' in request.session:
        categories_split_from_existing = request.session['categories_split_from_existing']
        for category in categories_split_from_existing:
            split_concept = category[0]
            for i in range(1, len(category)):
                changeOperation = get_addNewConceptSplitFromExistingConceptForNewTaxonomyVersion_op_details(request.session['existing_taxonomy_name'], version, request.session['existing_taxonomy_ver'], root_concept, category[i], split_concept)
                compositeChangeOperations.append(changeOperation)
    
    return JsonResponse({'listOfOperations': compositeChangeOperations});                
    

def get_addTaxonomy_op_details(taxonomy_name):
    changeOperation = []
    compositeOp = "Add_Taxonomy ('" + taxonomy_name + "')"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Create taxonomy '" + taxonomy_name + "'")
    root_concept = "root_" + taxonomy_name.replace(" ", "_") + "1"
    compositeOp_details.append("Create root concept '" + root_concept + "'")
    compositeOp_details.append("Add '" + root_concept + "' to '" + taxonomy_name + "'")
    changeOperation.append(compositeOp_details)
    return changeOperation, root_concept

def get_addNewTaxonomyVersion_op_details(taxonomy_name, taxonomy_version):
    changeOperation = []
    compositeOp = "Add_New_Taxonomy_Version ('" + taxonomy_name + "')"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Create new taxonomy version '" + taxonomy_name + "'" + " Ver_" +  str(taxonomy_version))
    old_version = taxonomy_version -1
    compositeOp_details.append("Retire taxonomy version '" + taxonomy_name + "'" + " Ver_" +  str(old_version))
    root_concept = "root_" + taxonomy_name.replace(" ", "_") + str(taxonomy_version)
    compositeOp_details.append("Create root concept '" + root_concept + "'")
    compositeOp_details.append("Add '" + root_concept + "' to '" + taxonomy_name + "'" + " Ver_" +  str(taxonomy_version))
    changeOperation.append(compositeOp_details)
    return changeOperation, root_concept
    

def get_addConcept_op_details(taxonomy_name, taxonomy_version,  parent_concept_name, concept_name):
    changeOperation = []
    compositeOp = "Add_Concept ('" + taxonomy_name + " - ver" + str(taxonomy_version) + "', '" + concept_name + "', '" + parent_concept_name + "')"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Create concept '" + concept_name + "' (if it does not exists)")
    compositeOp_details.append("Add '" + concept_name + "' to '" + taxonomy_name + " - ver" + str(taxonomy_version) + "'")
    compositeOp_details.append("Add hierarchical relationship - '" + parent_concept_name + "' parent of '" + concept_name + "'")
    compositeOp_details.append("Category Instantiation ('" + concept_name + "')")
    changeOperation.append(compositeOp_details)
    return changeOperation

def get_addExistingConceptForNewTaxonomyVersion_op_details(taxonomy_name, taxonomy_version, old_version, parent_concept_name, concept_name):
    changeOperation = []
    compositeOp = "Add_Existing_Concept_To_New_Legend_Version ('" + taxonomy_name + " - ver" + str(taxonomy_version) + "', '" + concept_name + "', '" + parent_concept_name + "')"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Add '" + concept_name + "' to '" + taxonomy_name + "' Ver_" + str(taxonomy_version))
    compositeOp_details.append("Add hierarchical relationship - '" + parent_concept_name + "' parent of '" + concept_name + "'")
    compositeOp_details.append("Category Instantiation ('" + concept_name + "')")
    compositeOp_details.append("Add_horizontal_relationship ('" + concept_name + "', '" +  taxonomy_name + "', " + str(taxonomy_version) + ", " + str(old_version) + ")")
    changeOperation.append(compositeOp_details)
    return changeOperation

def get_addMergedConceptFromExistingConceptsForNewTaxonomyVersion_op_details(taxonomy_name, taxonomy_version, old_version, parent_concept_name, concept_name, merged_concepts):
    changeOperation = []
    compositeOp = "Add_Merged_Concept_For_New_Legend_Version ('" + taxonomy_name + " - ver" + str(taxonomy_version) + "', '" + concept_name + "', '" + parent_concept_name + "', [" 
    for concept in merged_concepts:
        compositeOp = compositeOp + concept + ", "
        
    compositeOp = compositeOp + "])"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Create concept '" + concept_name + "' (if it does not exists)")
    compositeOp_details.append("Add '" + concept_name + "' to '" + taxonomy_name + "' Ver_" + str(taxonomy_version))
    compositeOp_details.append("Add hierarchical relationship - '" + parent_concept_name + "' parent of '" + concept_name + "'")
    compositeOp_details.append("Category Instantiation ('" + concept_name + "')")
    for mergedConcept in merged_concepts:
        compositeOp_details.append("Add_horizontal_relationship ('" + concept_name + "', '" + mergedConcept + "', '" + taxonomy_name + "', " + str(taxonomy_version) + ", " + str(old_version) + ")")
    changeOperation.append(compositeOp_details)
    return changeOperation

def get_addMergedConceptFromNewAndExistingConceptsForNewTaxonomyVersion_op_details(taxonomy_name, taxonomy_version, old_version, parent_concept_name, concept_name, merged_concepts):
    changeOperation = []
    compositeOp = "Add_Generalized_Concept_For_New_Legend_Version ('" + taxonomy_name + " - ver" + str(taxonomy_version) + "', '" + concept_name + "', '" + parent_concept_name + "', [" 
    for concept in merged_concepts:
        compositeOp = compositeOp + concept + ", "
        
    compositeOp = compositeOp + "])"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Create concept '" + concept_name + "' (if it does not exists)")
    compositeOp_details.append("Add '" + concept_name + "' to '" + taxonomy_name + "' Ver_" + str(taxonomy_version))
    compositeOp_details.append("Add hierarchical relationship - '" + parent_concept_name + "' parent of '" + concept_name + "'")
    compositeOp_details.append("Category Instantiation ('" + concept_name + "')")
    for mergedConcept in merged_concepts:
        compositeOp_details.append("Add_horizontal_relationship ('" + concept_name + "', '" + mergedConcept + "', '" + taxonomy_name + "', " + str(taxonomy_version) + ", " + str(old_version) + ")")
    changeOperation.append(compositeOp_details)
    return changeOperation   
    
def get_addNewConceptSplitFromExistingConceptForNewTaxonomyVersion_op_details(taxonomy_name, taxonomy_version, old_version, parent_concept_name, new_concept, split_concept):
    changeOperation = []
    compositeOp = "Add_Concept_Split_From_Existing_Concept_For_New_Legend_Version ('" + taxonomy_name + " - ver" + str(taxonomy_version) + "', '" + new_concept + "', '" + parent_concept_name + "', '" + split_concept + "')"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Create concept '" + new_concept + "' (if it does not exists)")
    compositeOp_details.append("Add '" + new_concept + "' to '" + taxonomy_name + "' Ver_" +  str(taxonomy_version))
    compositeOp_details.append("Add hierarchical relationship - '" + parent_concept_name + "' parent of '" + new_concept + "'")
    compositeOp_details.append("Category Instantiation ('" + new_concept + "')")
    compositeOp_details.append("Add_horizontal_relationship ('" + new_concept + "', '" + split_concept + "', '" + taxonomy_name + "', " +  str(taxonomy_version) + ", " + str(old_version) + ")")
    changeOperation.append(compositeOp_details)
    return changeOperation

def get_groupConcepts_op_details(taxonomy_name, taxonomy_version, new_concept, parentName, existing_concepts):
    changeOperation = []
    compositeOp = "Group_Concepts ('" + taxonomy_name + " - ver" + str(taxonomy_version) + "', '" + new_concept + "', ["
    for concept in existing_concepts:
        compositeOp = compositeOp + concept + ", "
    compositeOp = compositeOp + "])"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Create concept '" + new_concept + "' (if it does not exists)")
    compositeOp_details.append("Add '" + new_concept + "' to '" + taxonomy_name + "' Ver_" + str(taxonomy_version))
    
    for groupedConcept in existing_concepts:
        compositeOp_details.append("Retire hierarchical relationship - '" + parentName + " parent of " + groupedConcept + "'")
        compositeOp_details.append("Add hierarchical relationship - '" + new_concept + " parent of " + groupedConcept + "'")
    compositeOp_details.append("Add hierarchical relationship - '" + parentName + " parent of '" + new_concept + "'")
    changeOperation.append(compositeOp_details)
    return changeOperation  
    

def get_addEvolutionaryVersion_op_details(taxonomy_name, version, concept):
    changeOperation = []
    compositeOp = "Add_Evolutionary_Version ('" + taxonomy_name + " - ver" + str(version) + "', '" +  concept + "')"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    changeOperation.append(compositeOp_details)
    return changeOperation  
    
    
def get_addCompetingVersion_op_details(taxonomy_name, version, concept):
    changeOperation = []
    compositeOp = "Add_Competing_Version ('" + taxonomy_name + " - ver" + str(version) + "', '" +  concept + "')"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    changeOperation.append(compositeOp_details)
    return changeOperation  

def get_MergeConcepts_op_details(taxonomy_name, version, merged_concept, parent_concept, list_of_concepts_merged):
    changeOperation = []
    compositeOp = "Merge_Concepts ('" + taxonomy_name + " - ver" + str(version) + "', '" +  merged_concept + "', '" + parent_concept + "', [" + list_of_concepts_merged[0] 
    for i in range(1, len(list_of_concepts_merged)):
        compositeOp = compositeOp + ", " + list_of_concepts_merged[i]
    compositeOp = compositeOp + "])"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    changeOperation.append(compositeOp_details)
    return changeOperation  
    

@transaction.atomic  
def applyChangeOperations(request):
    if 'new_taxonomy_name' in request.session:
        change_event_queries = UpdateDatabase(request)
        change_event_queries.create_legend()
        trainingfile = TrainingSet(request.session['current_training_file_name'])
        concepts_in_current_taxonomy = list(numpy.unique(trainingfile.target))
        covariance_mat = trainingfile.create_covariance_matrix()
        mean_vectors = trainingfile.create_mean_vectors()
        
        predicted_file = ClassifiedFile(request.session['current_predicted_file_name'])
        producer_accuracies = request.session['producer_accuracies']
        user_accuracies = request.session['user_accuracies']
        extension = predicted_file.create_extension(request.session['current_test_file_columns'], request.session['current_test_file_rows'], request.session['current_training_file_name'])
        for i in range(len(concepts_in_current_taxonomy)):
            change_event_queries.add_concept(concepts_in_current_taxonomy[i], mean_vectors[i][1], covariance_mat[i][1],  extension[i], producer_accuracies[i], user_accuracies[i])
        del request.session['new_taxonomy_name']
        del request.session['new_taxonomy_description']
        request.session.modified = True
        
    elif 'existing_taxonomy_name' in request.session and 'create_new_taxonomy_version' in request.session:
        change_event_queries = UpdateDatabase(request)
        change_event_queries.create_new_legend_version()
        trainingfile = TrainingSet(request.session['current_training_file_name'])
        concepts_in_current_taxonomy = list(numpy.unique(trainingfile.target))
        covariance_mat = trainingfile.create_covariance_matrix()
        mean_vectors = trainingfile.create_mean_vectors()
        predicted_file = ClassifiedFile(request.session['current_predicted_file_name'])
        user_accuracies = request.session['user_accuracies']
        producer_accuracies = request.session['producer_accuracies']
        extension = predicted_file.create_extension(request.session['current_test_file_columns'], request.session['current_test_file_rows'], request.session['current_training_file_name'])
      
        if 'new_categories' in request.session:
            new_categories = request.session['new_categories']
            for new_category in new_categories:
                i = concepts_in_current_taxonomy.index(new_category)
                change_event_queries.add_concept(concepts_in_current_taxonomy[i], mean_vectors[i][1], covariance_mat[i][1],  extension[i], producer_accuracies[i], user_accuracies[i])
                
                        
        if 'existing_categories' in request.session:
            J_Index_for_common_categories = request.session['J_Index_for_common_categories']
            existing_categories = request.session['existing_categories']
            for each_existing_category in existing_categories:
                i = concepts_in_current_taxonomy.index(each_existing_category)
                comp_versions_and_extensional_similarity = []
                for category_andJ_index in J_Index_for_common_categories:
                    if each_existing_category in category_andJ_index:
                        comp_versions_and_extensional_similarity = category_andJ_index[1]
                        break
                comp_versions_and_intensional_similarity = []
                if 'existing_categories_computational_intension_comparison' in request.session:
                    existing_categories_computational_intension_comparison = request.session['existing_categories_computational_intension_comparison']
                    for each_category_compint_comparison in existing_categories_computational_intension_comparison:
                        if each_category_compint_comparison[0] == each_existing_category:
                            comp_versions_and_intensional_similarity = each_category_compint_comparison[1]
                            break
                change_event_queries.add_evolutionary_version_to_new_legend_version(each_existing_category, mean_vectors[i][1], covariance_mat[i][1],  extension[i], producer_accuracies[i], user_accuracies[i], comp_versions_and_intensional_similarity, comp_versions_and_extensional_similarity)
        
        if 'renamed_existing_categories' in request.session:
            J_Index_for_renamed_existing_categories = request.session['J_Index_for_renamed_existing_categories']
            renamed_existing_categories = request.session['renamed_existing_categories']
            for each_existing_category in renamed_existing_categories:
                i = concepts_in_current_taxonomy.index(each_existing_category[1])
                comp_versions_and_extensional_similarity = []
                for category_andJ_index in J_Index_for_renamed_existing_categories:
                    if each_existing_category in category_andJ_index:
                        comp_versions_and_extensional_similarity = category_andJ_index[2]
                        break
                comp_versions_and_intensional_similarity = []
                if 'existing_categories_computational_intension_comparison' in request.session:
                    existing_categories_computational_intension_comparison = request.session['existing_categories_computational_intension_comparison']
                    for each_category_compint_comparison in existing_categories_computational_intension_comparison:
                        if each_category_compint_comparison[0] == each_existing_category:
                            comp_versions_and_intensional_similarity = each_category_compint_comparison[2]
                            break
                        
                change_event_queries.add_evolutionary_version_to_new_legend_version(each_existing_category[1], mean_vectors[i][1], covariance_mat[i][1],  extension[i], producer_accuracies[i], user_accuracies[i], comp_versions_and_intensional_similarity, comp_versions_and_extensional_similarity)
        
        
        if 'categories_split_from_existing' in request.session:
            categories_split_from_existing = request.session['categories_split_from_existing']
            extensional_containment_for_categories_split_from_existing = request.session['extensional_containment_for_categories_split_from_existing']
            for each_set_of_categories_split_from_an_existing_category in categories_split_from_existing:
                existing_category_that_is_split = each_set_of_categories_split_from_an_existing_category[0]
                for i in range(1, len(each_set_of_categories_split_from_an_existing_category)):
                    index = concepts_in_current_taxonomy.index(each_set_of_categories_split_from_an_existing_category[i])
                    for extensional_containment_for_category in extensional_containment_for_categories_split_from_existing:
                        if each_set_of_categories_split_from_an_existing_category[i] in extensional_containment_for_category:
                            comp_versions_and_extensional_containment = extensional_containment_for_category[2]
                            break
                    comp_versions_and_intensional_similarity = []
                    if 'split_categories_computational_intension_comparison' in request.session:
                        split_categories_computational_intension_comparison = request.session['split_categories_computational_intension_comparison']
                        for each_set in split_categories_computational_intension_comparison:
                            if each_set_of_categories_split_from_an_existing_category[i] in each_set:
                                comp_versions_and_intensional_similarity = each_set[2]
                                break
                    change_event_queries.add_concept_split_from_existing_concept_to_new_version_of_legend(each_set_of_categories_split_from_an_existing_category[i], existing_category_that_is_split, mean_vectors[index][1], covariance_mat[index][1], extension[index], producer_accuracies[index], user_accuracies[index], comp_versions_and_intensional_similarity, comp_versions_and_extensional_containment)
        
        if 'categories_merged_from_existing' in request.session:
            categories_merged_from_existing = request.session['categories_merged_from_existing']
            extensional_containment_for_category_merged_from_existing = request.session['extensional_containment_for_category_merged_from_existing']
            
            for new_category_resulted_from_merging_existing_categories in categories_merged_from_existing:
                new_category = new_category_resulted_from_merging_existing_categories[-1]
                index = concepts_in_current_taxonomy.index(new_category)
                comp_versions_and_extensional_containment = []
                merged_categories = new_category_resulted_from_merging_existing_categories
                merged_categories.pop()
                for each_set in extensional_containment_for_category_merged_from_existing:
                    if new_category in each_set:
                        comp_versions_and_extensional_containment = each_set
                        comp_versions_and_extensional_containment.pop(0)
                        break
                comp_versions_and_intensional_similarity = []
                if 'merged_categories_computational_intension_comparison' in request.session:
                    merged_categories_computational_intension_comparison = request.session['merged_categories_computational_intension_comparison']
                    for i, each_category_merged in enumerate(merged_categories):
                        for each_set1 in merged_categories_computational_intension_comparison:
                            if new_category == each_set1[0] and each_category_merged == each_set1[1]:
                                comp_versions_and_intensional_similarity.append(each_set1[2])
                                break

                change_event_queries.add_concept_resulted_from_merging_existing_concept_to_new_version_of_legend(new_category, merged_categories, mean_vectors[index][1], covariance_mat[index][1], extension[index], producer_accuracies[index], user_accuracies[index],  comp_versions_and_extensional_containment, comp_versions_and_intensional_similarity)
        
        if 'categories_merged_from_new_and_existing' in request.session:
            categories_merged_from_new_and_existing = request.session['categories_merged_from_new_and_existing']
            extensional_containment_for_category_merged_from_new_and_existing = request.session['extensional_containment_for_category_merged_from_new_and_existing']
            for new_category_resulted_from_merging_existing_categories in categories_merged_from_new_and_existing:
                new_category = new_category_resulted_from_merging_existing_categories[-1]
                index = concepts_in_current_taxonomy.index(new_category)
                extensional_containment = []
                merged_categories = new_category_resulted_from_merging_existing_categories
                merged_categories.pop()
                old_categories, old_mean_vectors, old_covariance_mat = find_all_active_categories_and_their_comp_int_for_a_legend_version(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])
                oldCategories_name = [x[0] for x in old_categories]
                existing_merged_categories = [category for category in merged_categories if category in oldCategories_name]
                for each_set in extensional_containment_for_category_merged_from_new_and_existing:
                    if new_category in each_set:
                        comp_versions_and_extensional_containment = each_set
                        comp_versions_and_extensional_containment.pop(0)
                        break
                        
                comp_versions_and_intensional_similarity = []
                if 'merged_categories_from_new_and_existing_computational_intension_comparison' in request.session:
                    merged_categories_from_new_and_existing_computational_intension_comparison = request.session['merged_categories_from_new_and_existing_computational_intension_comparison']
                    for i, each_category_merged in enumerate(existing_merged_categories):
                        for each_set1 in merged_categories_from_new_and_existing_computational_intension_comparison:
                            if new_category == each_set1[0] and each_category_merged == each_set1[1]:
                                comp_versions_and_intensional_similarity.append(each_set1[2])
                                break
                change_event_queries.add_generalized_concept_to_new_version_of_legend(new_category, existing_merged_categories, mean_vectors[index][1], covariance_mat[index][1], extension[index], producer_accuracies[index], user_accuracies[index],  comp_versions_and_extensional_containment, comp_versions_and_intensional_similarity)
        
        if 'grouped_categories' in request.session:
            grouped_categories = request.session['grouped_categories']
            for each_set in grouped_categories:
                new_category = each_set[-1]
                categories_that_are_grouped = each_set
                categories_that_are_grouped.pop()
                change_event_queries.group_concepts(new_category, categories_that_are_grouped)
        del request.session['create_new_taxonomy_version'] 
        request.session.modified = True
    else:
        change_event_queries = UpdateDatabase(request)
        trainingfile = TrainingSet(request.session['current_training_file_name'])
        concepts_in_current_taxonomy = list(numpy.unique(trainingfile.target))
        covariance_mat = trainingfile.create_covariance_matrix()
        mean_vectors = trainingfile.create_mean_vectors()
        predicted_file = ClassifiedFile(request.session['current_predicted_file_name'])
        user_accuracies = request.session['user_accuracies']
        producer_accuracies = request.session['producer_accuracies']
        extension = predicted_file.create_extension(request.session['current_test_file_columns'], request.session['current_test_file_rows'], request.session['current_training_file_name'])       
        customqueries = CustomQueries()
        
        
        if 'new_categories' in request.session:
            new_categories = request.session['new_categories']
            parent_name = customqueries.getRootConceptOfATaxonomyVersion(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'])
            for new_category in new_categories:
                i = concepts_in_current_taxonomy.index(new_category)
                change_event_queries.add_concept(concepts_in_current_taxonomy[i], mean_vectors[i][1], covariance_mat[i][1],  extension[i], producer_accuracies[i], user_accuracies[i], parent_name)

        if 'add_evolutionary_version' in request.session:
            add_evolutionary_version = request.session['add_evolutionary_version']
            J_Index_for_common_categories = request.session['J_Index_for_common_categories']
            
            for category in add_evolutionary_version:
                i = concepts_in_current_taxonomy.index(category)
                comp_versions_and_extensional_similarity = []
                for category_andJ_index in J_Index_for_common_categories:
                    if category in category_andJ_index:
                        comp_versions_and_extensional_similarity = category_andJ_index[1]
                        break
                comp_versions_and_intensional_similarity = []
                if 'existing_categories_computational_intension_comparison' in request.session:
                    existing_categories_computational_intension_comparison = request.session['existing_categories_computational_intension_comparison']
                    for each_category_compint_comparison in existing_categories_computational_intension_comparison:
                        if each_category_compint_comparison[0] == category:
                            comp_versions_and_intensional_similarity = each_category_compint_comparison[1]
                            break
                                
                change_event_queries.add_evolutionary_version_to_existing_legend(category, mean_vectors[i][1], covariance_mat[i][1],  extension[i], producer_accuracies[i], user_accuracies[i], comp_versions_and_intensional_similarity, comp_versions_and_extensional_similarity)   
            
  
            
        if 'add_competing_version' in request.session:
            add_competing_version = request.session['add_competing_version']
            J_Index_for_common_categories = request.session['J_Index_for_common_categories']
            
            for category in add_competing_version:
                i = concepts_in_current_taxonomy.index(category)
                comp_versions_and_extensional_similarity = []
                for category_andJ_index in J_Index_for_common_categories:
                    if category in category_andJ_index:
                        comp_versions_and_extensional_similarity = category_andJ_index[1]
                        break
                comp_versions_and_intensional_similarity = []
                if 'existing_categories_computational_intension_comparison' in request.session:
                    existing_categories_computational_intension_comparison = request.session['existing_categories_computational_intension_comparison']
                    for each_category_compint_comparison in existing_categories_computational_intension_comparison:
                        if each_category_compint_comparison[0] == category:
                            comp_versions_and_intensional_similarity = each_category_compint_comparison[1]
                            break
                                
                change_event_queries.add_competing_version_to_existing_legend(category, mean_vectors[i][1], covariance_mat[i][1],  extension[i], producer_accuracies[i], user_accuracies[i], comp_versions_and_intensional_similarity, comp_versions_and_extensional_similarity)   
            
  
            
        if 'categories_merged_from_existing' in request.session:
            categories_merged_from_existing = request.session['categories_merged_from_existing']
        
        if 'categories_merged_from_new_and_existing' in request.session:
            categories_merged_from_new_and_existing = request.session['categories_merged_from_new_and_existing']
            
        if 'grouped_categories' in request.session:
            grouped_categories = request.session['grouped_categories']
            for each_set in grouped_categories:
                new_category = each_set[-1]
                categories_that_are_grouped = each_set
                categories_that_are_grouped.pop()
                change_event_queries.group_concepts(new_category, categories_that_are_grouped)             

        if 'categories_split_from_existing' in request.session:
            categories_split_from_existing = request.session['categories_split_from_existing']
        
        del request.session['existing_taxonomy_name']
        del request.session['existing_taxonomy_id']
        del request.session['existing_taxonomy_ver']
        request.session.modified = True
    del request.session['exploration_chain_id']
    del request.session['exploration_chain_step']
    del request.session['current_training_file_name']
    del request.session['current_training_file_id']
    del request.session['current_training_file_ver']
    del request.session['current_model_name']
    del request.session['current_model_id']
    del request.session['current_test_file_name']
    del request.session['current_predicted_file_name']
    del request.session['current_test_file_columns']
    del request.session['current_test_file_rows']
    del request.session['legend_id'] 
    del request.session['legend_ver']
    request.session.modified = True
    return HttpResponse("The changes are committed and stored in the database. Choose an activity from the Home page to continue further!")
    
@login_required
def visualizer(request):
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username
    legend_list = Legend.objects.all()
    if request.method == 'POST' and request.is_ajax():
        data = request.POST
        legendpkey = data['1']
        lid, ver = legendpkey.split('+')
        legend_name = data['2']
        taxonomy_image = create_taxonomy_visualization()
        customqueries = CustomQueries()
        model_type = customqueries.get_model_name_and_accuracy_from_a_legend(lid, ver)
        concepts_list = customqueries.get_concepts_list_for_a_legend(lid, ver)
        message = "The taxonomy is modeled using a " + str(model_type[0]) + " classification model with an accuracy of " + str(model_type[1]*100.00) + "%"
        
        return JsonResponse({'image_name': taxonomy_image, 'message':message, 'concept_list': concepts_list});
    else:
        
        return render (request, 'visualization.html', {'user_name':user_name, 'legend_list':legend_list})

def getconceptdetails(request):
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username
    if request.method == 'POST' and request.is_ajax():
        data = request.POST
        conceptlegendpkey = data['1']
        concept_name = data['2']
        customqueries = CustomQueries()
        concept_details = customqueries.get_concept_details(conceptlegendpkey)

def create_taxonomy_visualization():
    #test_taxonomy = "((Sea water, inland water, Estuarine open water)Water_bodies, ((Urban, Suburban)Built space, Open space)artificial_surface, cloud, shadow, forest, grassland)Root;"
    #test_taxonomy = "(Shadow, Cloud, Pasture, Woody Vegetation, (Suburban, Urban)Built_up_Area, (Inland Water, Water)Water Bodies)Root;"
    test_taxonomy = "(Shadow, Cloud, ((Indigenous Forest, Mangrove)Forest, Grassland, Scrub)Vegetation, ((Urban, Suburban)Built-up Area, Open Space)Artificial Surface, (Inland Water, Estuarine Open Water, Sea Water)Water Bodies)Root;"
    t1 = Tree(test_taxonomy, format=8)   # @UndefinedVariable
    t1.add_face(TextFace("Root"), column=0, position = "branch-top")
    ts = TreeStyle()
    ts.show_leaf_name = True
    ts.show_scale = False
    ts.branch_vertical_margin = 20
    ts.scale = 25
    ts.title.add_face(TextFace("AKL LCDB - Version 3", fsize=10), column=0)
    #ts.rotation = 90
    
    for node in t1.traverse():
        if node.name == "Water Bodies":
            node.add_face(TextFace("  Water Bodies  "), column=0, position = "branch-top")
        elif node.name == "Built-up Area":
            node.add_face(TextFace("  Built-up Area  "), column=0, position = "branch-top")
        elif node.name == "Artificial Surface":
            node.add_face(TextFace("  Artificial Surface  "), column=0, position = "branch-top")
        elif node.name == "Forest":
            node.add_face(TextFace("  Forest     "), column=0, position = "branch-top")
        elif node.name == "Vegetation":
            node.add_face(TextFace("  Vegetation  "), column=0, position = "branch-top")
    
    
    taxonomy_image_name = "tree.png"
    t1.render("%s%s" %(TAXONOMY_IMAGE_LOCATION, "tree3.png"), tree_style=ts, dpi=300, h=2.5, units="in")

    return taxonomy_image_name