import csv, json, numpy, pydot, os, re
import matplotlib.pyplot as plt
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
from sklearn.externals import joblib
from sklearn.naive_bayes import GaussianNB
from sklearn.externals.six import StringIO
from Category_Modeler.models import Trainingset, ChangeTrainingsetActivity, AuthUser, Classificationmodel, Classifier, LearningActivity, TrainingsampleForCategory, ChangeTrainingsetActivityDetails
from Category_Modeler.models import Confusionmatrix, ExplorationChain, ClassificationActivity, Legend, TrainingsetTrainingsamples, TrainingsampleCollection, CreateTrainingsetActivity
from Category_Modeler.models import  CreateTrainingsetActivityOperations, SatelliteImage, ClassifiedSatelliteImage
from Category_Modeler.measuring_categories import TrainingSet, NormalDistributionIntensionalModel, DecisionTreeIntensionalModel, StatisticalMethods, ClassifiedFile
from Category_Modeler.data_processing import ManageRasterData, ManageCSVData
from Category_Modeler.database_transactions import UpdateDatabase, CustomQueries


#Different Files Locations
TRAINING_SAMPLES_IMAGES_LOCATION = 'Category_Modeler/static/data/'
EXISTING_TRAINING_SAMPLES_LOCATION = 'Category_Modeler/static/trainingsamples/'
EXISTING_TRAINING_DATA_LOCATION = 'Category_Modeler/static/trainingfiles/'
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
            if 'current_samples_id_and_version' in request.session:
                del request.session['current_samples_id_and_version']
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
        if 'IsFinalSample' in data and 'new_taxonomy_name' in request.session:
            
            trainingFilesList = request.FILES.getlist('file')
            conceptName = data['conceptName']
            researcherName = data['FieldResearcherName'];
            trainingstart = data['TrainingTimePeriodStartDate'];
            trainingend = data['TrainingTimePeriodEndDate'];
            location = data['TrainingLocation'];
            otherDetails = data['OtherDetails'];
            isitfinalsample = data['IsFinalSample'];
            
            #Combine multiple samples and save it as a csv file
            samplefilename = conceptName + str(datetime.now()) + ".csv"
            trainingSamplesFileList = [trainingSamples.name for trainingSamples in trainingFilesList]            
            managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList, samplefilename, EXISTING_TRAINING_SAMPLES_LOCATION, conceptName)
            
            #Save trainingsample, training sample collection activity and adds an entry in create trainingset activity
            if TrainingsampleForCategory.objects.all().exists():
                latestid = int(TrainingsampleForCategory.objects.latest("trainingsample_id").trainingsample_id) + 1
            else:
                latestid = 0
            ts = TrainingsampleForCategory(trainingsample_id=latestid, trainingsample_ver =1, date_expired=datetime(9999, 9, 12), samplefile_name=samplefilename, filelocation=EXISTING_TRAINING_SAMPLES_LOCATION, concept_name = conceptName)
            ts.save(force_insert=True)
            ts_collection = TrainingsampleCollection( trainingsample_id= ts.trainingsample_id, trainingsample_ver =ts.trainingsample_ver, trainingsample_location = location, collector=researcherName, description= otherDetails, date_started = datetime.strptime(trainingstart, '%Y-%m-%d'), date_finished= datetime.strptime(trainingend, '%Y-%m-%d'))
            ts_collection.save()
            
            if 'current_samples_id_and_version' in request.session:
                current_samples_id_and_version = request.session['current_samples_id_and_version']
                current_samples_id_and_version.append([ts.trainingsample_id, ts.trainingsample_ver, ts.samplefile_name])
                request.session['current_samples_id_and_version'] = current_samples_id_and_version
            else:
                current_samples_id_and_version = [[ts.trainingsample_id, ts.trainingsample_ver, ts.samplefile_name]]
                request.session['current_samples_id_and_version'] = current_samples_id_and_version
            
            create_ts_activity_instance = CreateTrainingsetActivity.objects.get(id = int(request.session['create_trainingset_activity_id']))
            create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'add new', concept1 = conceptName)
            create_tset_activity_ops.save(force_insert=True)
    
          
            if isitfinalsample=='True':
                filename = data['TrainingsetName']
                current_samples_filenames = [sample_id_and_ver[2] for sample_id_and_ver in request.session['current_samples_id_and_version']]
                manageCsvData.combine_multiple_csv_files(current_samples_filenames, EXISTING_TRAINING_SAMPLES_LOCATION, EXISTING_TRAINING_DATA_LOCATION, filename)
                request.session['current_training_file_name'] = filename
    
                if Trainingset.objects.all().exists():
                    latestid = int (Trainingset.objects.latest("trainingset_id").trainingset_id) + 1
                else:
                    latestid = 0
                tr = Trainingset(trainingset_id=latestid, trainingset_ver =1, trainingset_name=request.session['current_training_file_name'], date_expired=datetime(9999, 9, 12), filelocation=EXISTING_TRAINING_DATA_LOCATION)
                tr.save(force_insert=True)
                request.session['current_training_file_id'] = tr.trainingset_id
                request.session['current_training_file_ver'] = tr.trainingset_ver
                
                create_ts_activity_instance.trainingset_id = request.session['current_training_file_id']
                create_ts_activity_instance.trainingset_ver = request.session['current_training_file_ver']
                create_ts_activity_instance.save()
                
                for sample_id_and_ver in current_samples_id_and_version:
                    trainingset_trainingsamples_instance = TrainingsetTrainingsamples(trainingset_id = request.session['current_training_file_id'], trainingset_ver = request.session['current_training_file_ver'], trainingsample_id = sample_id_and_ver[0], trainingsample_ver = sample_id_and_ver[1])
                    trainingset_trainingsamples_instance.save(force_insert=True)
                
                exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'create trainingset', activity_instance = create_ts_activity_instance.id)
                exp_chain.save(force_insert=True)
                request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1
                
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
                    current_exploration_chain_viz.append(current_step)
                    request.session['current_exploration_chain_viz'] = current_exploration_chain_viz
                else:
                    request.session['current_exploration_chain_viz'] = [current_step]
                    
                
                return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz']})  
            return HttpResponse("")
        #----------------------------------------------------------------------------------------------------------------
        elif 'IsFinalSample' in data and 'existing_taxonomy_name' in request.session:

            conceptType = data['ConceptType']
            create_ts_activity_instance = CreateTrainingsetActivity.objects.get(id = int(request.session['create_trainingset_activity_id']))
            old_trainingset = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_name'])
            create_ts_activity_instance.reference_trainingset_id = old_trainingset[0]
            create_ts_activity_instance.reference_trainingset_ver = old_trainingset[1]
            create_ts_activity_instance.save()
            latestid = int(TrainingsampleForCategory.objects.latest("trainingsample_id").trainingsample_id) + 1

            if conceptType=='1':
                trainingFilesList = request.FILES.getlist('file')
                conceptName = data['ConceptName']
                researcherName = data['FieldResearcherName'];
                trainingstart = data['TrainingTimePeriodStartDate'];
                trainingend = data['TrainingTimePeriodEndDate'];
                location = data['TrainingLocation'];
                otherDetails = data['OtherDetails'];
                
                #Combine multiple samples and save it as a csv file
                samplefilename = conceptName + str(datetime.now()) + ".csv"
                trainingSamplesFileList = [trainingSamples.name for trainingSamples in trainingFilesList]  
                managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList, samplefilename, EXISTING_TRAINING_SAMPLES_LOCATION, conceptName)
                
                #Save trainingsample, training sample collection activity and adds an entry in create trainingset activity
                ts = TrainingsampleForCategory(trainingsample_id=latestid, trainingsample_ver =1, date_expired=datetime(9999, 9, 12), samplefile_name=samplefilename, filelocation=EXISTING_TRAINING_SAMPLES_LOCATION, concept_name = conceptName)
                ts.save(force_insert=True)
                ts_collection = TrainingsampleCollection( trainingsample_id= ts.trainingsample_id, trainingsample_ver =ts.trainingsample_ver, trainingsample_location = location, collector=researcherName, description= otherDetails, date_started = datetime.strptime(trainingstart, '%Y-%m-%d'), date_finished= datetime.strptime(trainingend, '%Y-%m-%d'))
                ts_collection.save(force_insert=True)
                
                if 'current_samples_id_and_version' in request.session:
                    current_samples_id_and_version = request.session['current_samples_id_and_version']
                    current_samples_id_and_version.append([ts.trainingsample_id, ts.trainingsample_ver, ts.samplefile_name])
                    request.session['current_samples_id_and_version'] = current_samples_id_and_version
                else:
                    current_samples_id_and_version = [[ts.trainingsample_id, ts.trainingsample_ver, ts.samplefile_name]]
                    request.session['current_samples_id_and_version'] = current_samples_id_and_version
                
                create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'add new', concept1 = conceptName)
                create_tset_activity_ops.save()
                
                if 'new_categories' in request.session:
                    new_categories = request.session['new_categories']
                    new_categories.append(conceptName)
                    request.session['new_categories'] = new_categories
                else:
                    new_categories = [conceptName]
                    request.session['new_categories'] = new_categories
                
            elif conceptType=='2':
                conceptName = data['ConceptName']
                useExistingSamples = data['UseExistingSamples']
                
                if useExistingSamples == 'False':
                    trainingFilesList = request.FILES.getlist('file')
                    researcherName = data['FieldResearcherName'];
                    trainingstart = data['TrainingTimePeriodStartDate'];
                    trainingend = data['TrainingTimePeriodEndDate'];
                    location = data['TrainingLocation'];
                    otherDetails = data['OtherDetails'];
                    
                    #Combine multiple samples and save it as a csv file
                    samplefilename = conceptName + str(datetime.now()) + ".csv"
                    trainingSamplesFileList = [trainingSamples.name for trainingSamples in trainingFilesList]  
                    managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList, samplefilename, EXISTING_TRAINING_SAMPLES_LOCATION, conceptName)
                    
                    #Save trainingsample, training sample collection activity and adds an entry in create trainingset activity
                    ts = TrainingsampleForCategory(trainingsample_id=latestid, trainingsample_ver =1, date_expired=datetime(9999, 9, 12), samplefile_name=samplefilename, filelocation=EXISTING_TRAINING_SAMPLES_LOCATION, concept_name = conceptName)
                    ts.save(force_insert=True)
                    ts_collection = TrainingsampleCollection( trainingsample_id= ts.trainingsample_id, trainingsample_ver =ts.trainingsample_ver, trainingsample_location = location, collector=researcherName, description= otherDetails, date_started = datetime.strptime(trainingstart, '%Y-%m-%d'), date_finished= datetime.strptime(trainingend, '%Y-%m-%d'))
                    ts_collection.save(force_insert=True)
                    
                    currentSampleIdAndVer = [ts.trainingsample_id, ts.trainingsample_ver, ts.samplefile_name]
                    
                    
                else:
                    trainingsample = customQuery.get_trainingsample_id_and_ver_for_concept_in_reference_taxonomy(create_ts_activity_instance.reference_trainingset_id, create_ts_activity_instance.reference_trainingset_ver, conceptName)
                    currentSampleIdAndVer = [trainingsample[0], trainingsample[1], trainingsample[2]]
                    
                if 'current_samples_id_and_version' in request.session:
                    current_samples_id_and_version = request.session['current_samples_id_and_version']
                    current_samples_id_and_version.append(currentSampleIdAndVer)
                    request.session['current_samples_id_and_version'] = current_samples_id_and_version
                else:
                    current_samples_id_and_version = [currentSampleIdAndVer]
                    request.session['current_samples_id_and_version'] = current_samples_id_and_version
                  
                create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'add existing', concept1 = conceptName)
                create_tset_activity_ops.save()
                
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
                
                useExistingSamples = data['UseExistingSamples']
                
                if useExistingSamples == 'False':
                    trainingFilesList = request.FILES.getlist('file')
                    researcherName = data['FieldResearcherName'];
                    trainingstart = data['TrainingTimePeriodStartDate'];
                    trainingend = data['TrainingTimePeriodEndDate'];
                    location = data['TrainingLocation'];
                    otherDetails = data['OtherDetails'];
                    
                    #Combine multiple samples and save it as a csv file
                    samplefilename = mergedConceptName + str(datetime.now()) + ".csv"
                    trainingSamplesFileList = [trainingSamples.name for trainingSamples in trainingFilesList]  
                    managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList, samplefilename, EXISTING_TRAINING_SAMPLES_LOCATION, mergedConceptName)
                    
                    #Save trainingsample, training sample collection activity and adds an entry in create trainingset activity
                    ts = TrainingsampleForCategory(trainingsample_id=latestid, trainingsample_ver =1, date_expired=datetime(9999, 9, 12), samplefile_name=samplefilename, filelocation=EXISTING_TRAINING_SAMPLES_LOCATION, concept_name = mergedConceptName)
                    ts.save(force_insert=True)
                    ts_collection = TrainingsampleCollection( trainingsample_id= ts.trainingsample_id, trainingsample_ver =ts.trainingsample_ver, trainingsample_location = location, collector=researcherName, description= otherDetails, date_started = datetime.strptime(trainingstart, '%Y-%m-%d'), date_finished= datetime.strptime(trainingend, '%Y-%m-%d'))
                    ts_collection.save()
                    
                    currentSampleIdAndVer = [ts.trainingsample_id, ts.trainingsample_ver, ts.samplefile_name]
                else:
                    trainingsample1 = customQuery.get_trainingsample_id_and_ver_for_concept_in_reference_taxonomy(create_ts_activity_instance.reference_trainingset_id, create_ts_activity_instance.reference_trainingset_ver, firstConceptName)
                    trainingsample2 = customQuery.get_trainingsample_id_and_ver_for_concept_in_reference_taxonomy(create_ts_activity_instance.reference_trainingset_id, create_ts_activity_instance.reference_trainingset_ver, secondConceptName)
                    
                    #Combine multiple samples and save it as a csv file
                    samplefilename = mergedConceptName + str(datetime.now()) + ".csv"
                    manageCsvData = ManageCSVData()
                
                if 'current_samples_id_and_version' in request.session:
                    current_samples_id_and_version = request.session['current_samples_id_and_version']
                    current_samples_id_and_version.append(currentSampleIdAndVer)
                    request.session['current_samples_id_and_version'] = current_samples_id_and_version
                else:
                    current_samples_id_and_version = [currentSampleIdAndVer]
                    request.session['current_samples_id_and_version'] = current_samples_id_and_version    
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
                firstConceptNameFromSplit = namesofsplitconcepts[0]
                secondConceptNameFromSplit = namesofsplitconcepts[1]
                
                trainingFilesList1 = request.FILES.getlist('filesforfirstconcept')
                researcherName1 = data['FieldResearcherName1'];
                trainingstart1 = data['TrainingTimePeriodStartDate1'];
                trainingend1 = data['TrainingTimePeriodEndDate1'];
                location1 = data['TrainingLocation1'];
                otherDetails1 = data['OtherDetails1'];
                
                trainingFilesList2 = request.FILES.getlist('filesforsecondconcept')
                researcherName2 = data['FieldResearcherName2'];
                trainingstart2 = data['TrainingTimePeriodStartDate2'];
                trainingend2 = data['TrainingTimePeriodEndDate2'];
                location2 = data['TrainingLocation2'];
                otherDetails2 = data['OtherDetails2'];
                                                
                #Combine multiple samples and save it as a csv file
                samplefilename1 = firstConceptNameFromSplit + str(datetime.now()) + ".csv"
                samplefilename2 = secondConceptNameFromSplit + str(datetime.now()) + ".csv"
                trainingSamplesFileList1 = [trainingSamples.name for trainingSamples in trainingFilesList1]  
                trainingSamplesFileList2 = [trainingSamples.name for trainingSamples in trainingFilesList2]  
                managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList1, samplefilename1, EXISTING_TRAINING_SAMPLES_LOCATION, firstConceptNameFromSplit)
                managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList2, samplefilename2, EXISTING_TRAINING_SAMPLES_LOCATION, secondConceptNameFromSplit)
                
                #Save trainingsample, training sample collection activity and adds an entry in create trainingset activity
                ts1 = TrainingsampleForCategory(trainingsample_id=latestid, trainingsample_ver =1, date_expired=datetime(9999, 9, 12), samplefile_name=samplefilename1, filelocation=EXISTING_TRAINING_SAMPLES_LOCATION, concept_name = firstConceptNameFromSplit)
                ts2 = TrainingsampleForCategory(trainingsample_id=latestid + 1, trainingsample_ver =1, date_expired=datetime(9999, 9, 12), samplefile_name=samplefilename2, filelocation=EXISTING_TRAINING_SAMPLES_LOCATION, concept_name = secondConceptNameFromSplit)
                ts1.save(force_insert=True)
                ts2.save(force_insert=True)
                
                ts_collection1 = TrainingsampleCollection( trainingsample_id= ts1.trainingsample_id, trainingsample_ver =ts1.trainingsample_ver, trainingsample_location = location1, collector=researcherName1, description= otherDetails1, date_started = datetime.strptime(trainingstart1, '%Y-%m-%d'), date_finished= datetime.strptime(trainingend1, '%Y-%m-%d'))
                ts_collection2 = TrainingsampleCollection( trainingsample_id= ts2.trainingsample_id, trainingsample_ver =ts2.trainingsample_ver, trainingsample_location = location2, collector=researcherName2, description= otherDetails2, date_started = datetime.strptime(trainingstart2, '%Y-%m-%d'), date_finished= datetime.strptime(trainingend2, '%Y-%m-%d'))
                ts_collection1.save()
                ts_collection2.save()
                
                currentSampleIdAndVer1 = [ts1.trainingsample_id, ts1.trainingsample_ver, ts1.samplefile_name]
                currentSampleIdAndVer2 = [ts2.trainingsample_id, ts2.trainingsample_ver, ts2.samplefile_name]
    
                if 'current_samples_id_and_version' in request.session:
                    current_samples_id_and_version = request.session['current_samples_id_and_version']
                    current_samples_id_and_version.append(currentSampleIdAndVer1)
                    current_samples_id_and_version.append(currentSampleIdAndVer2)
                    request.session['current_samples_id_and_version'] = current_samples_id_and_version
                else:
                    current_samples_id_and_version = [currentSampleIdAndVer1, currentSampleIdAndVer2]
                    request.session['current_samples_id_and_version'] = current_samples_id_and_version
                
                if len(namesofsplitconcepts)==3:
                    thirdConceptNameFromSplit = namesofsplitconcepts[2]
                    trainingFilesList3 = request.FILES.getlist('filesforthirdconcept')
                    researcherName3 = data['FieldResearcherName3'];
                    trainingstart3 = data['TrainingTimePeriodStartDate3'];
                    trainingend3 = data['TrainingTimePeriodEndDate3'];
                    location3 = data['TrainingLocation3'];
                    otherDetails3 = data['OtherDetails3'];
                    
                    samplefilename3 = thirdConceptNameFromSplit + str(datetime.now()) + ".csv"
                    trainingSamplesFileList3 = [trainingSamples.name for trainingSamples in trainingFilesList3]  
                    managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList3, samplefilename3, EXISTING_TRAINING_SAMPLES_LOCATION, thirdConceptNameFromSplit)
                    
                    ts3 = TrainingsampleForCategory(trainingsample_id=latestid + 2, trainingsample_ver =1, date_expired=datetime(9999, 9, 12), samplefile_name=samplefilename3, filelocation=EXISTING_TRAINING_SAMPLES_LOCATION, concept_name = thirdConceptNameFromSplit)
                    ts3.save(force_insert=True)
                    
                    ts_collection3 = TrainingsampleCollection( trainingsample_id= ts3.trainingsample_id, trainingsample_ver =ts3.trainingsample_ver, trainingsample_location = location3, collector=researcherName3, description= otherDetails3, date_started = datetime.strptime(trainingstart3, '%Y-%m-%d'), date_finished= datetime.strptime(trainingend3, '%Y-%m-%d'))
                    ts_collection3.save()
                    
                    currentSampleIdAndVer3 = [ts3.trainingsample_id, ts3.trainingsample_ver, ts3.samplefile_name]
                    current_samples_id_and_version = request.session['current_samples_id_and_version']
                    current_samples_id_and_version.append(currentSampleIdAndVer3)
                    request.session['current_samples_id_and_version'] = current_samples_id_and_version
                                  
                    create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'split', concept1 = conceptToSplit, concept2 = firstConceptNameFromSplit, concept3 = secondConceptNameFromSplit, concept4 = thirdConceptNameFromSplit)
                    create_tset_activity_ops.save(force_insert=True)
                    category_split_details = [conceptToSplit, firstConceptNameFromSplit, secondConceptNameFromSplit, thirdConceptNameFromSplit]
                else:
                    create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'split', concept1 = conceptToSplit, concept2 = firstConceptNameFromSplit, concept3 = secondConceptNameFromSplit)
                    create_tset_activity_ops.save(force_insert=True)
                    category_split_details = [conceptToSplit, firstConceptNameFromSplit, secondConceptNameFromSplit]
                    
                
                if 'categories_split_from_existing' in request.session:
                    categories_split_from_existing = request.session['categories_split_from_existing']
                    categories_split_from_existing.append(category_split_details)
                    request.session['categories_split_from_existing'] = categories_split_from_existing
                else:
                    categories_split_from_existing = [category_split_details]
                    request.session['categories_split_from_existing'] = categories_split_from_existing
                
            if data['IsFinalSample']=='true':
                filename = data['TrainingsetName'];
                print request.session['current_samples_id_and_version']
                current_samples_filenames = [sample_id_and_ver[2] for sample_id_and_ver in request.session['current_samples_id_and_version']]
                
                manageCsvData.combine_multiple_csv_files(current_samples_filenames, EXISTING_TRAINING_SAMPLES_LOCATION, EXISTING_TRAINING_DATA_LOCATION, filename)
                request.session['current_training_file_name'] = filename
    
                latesttsid = int (Trainingset.objects.latest("trainingset_id").trainingset_id) + 1
                tr = Trainingset(trainingset_id=latesttsid, trainingset_ver =1, trainingset_name=request.session['current_training_file_name'], date_expired=datetime(9999, 9, 12), filelocation=EXISTING_TRAINING_DATA_LOCATION)
                tr.save(force_insert=True)
                request.session['current_training_file_id'] = tr.trainingset_id
                request.session['current_training_file_ver'] = tr.trainingset_ver               
                
                create_ts_activity_instance.trainingset_id = request.session['current_training_file_id']
                create_ts_activity_instance.trainingset_ver = request.session['current_training_file_ver']
                create_ts_activity_instance.save(force_update=True)
                
                for sample_id_and_ver in current_samples_id_and_version:
                    trainingset_trainingsamples_instance = TrainingsetTrainingsamples(trainingset_id = request.session['current_training_file_id'], trainingset_ver = request.session['current_training_file_ver'], trainingsample_id = sample_id_and_ver[0], trainingsample_ver = sample_id_and_ver[1])
                    trainingset_trainingsamples_instance.save(force_insert=True)
                
                exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'create trainingset', activity_instance = create_ts_activity_instance.id)
                exp_chain.save(force_insert=True)
                request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1
                
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
                    current_exploration_chain_viz.append(current_step)
                    request.session['current_exploration_chain_viz'] = current_exploration_chain_viz
                else:
                    request.session['current_exploration_chain_viz'] = [current_step]
                
                if isinstance(common_categories[0], list)==False:
                    common_categories_message = "The two training samples have different number of bands; so, we cannot compare common categories based on training samples"
                    return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories, 'common_categories_message':common_categories_message})
        
                return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories})

                
            return HttpResponse("")
        else:
            trainingfilepkey = data['1']
            trid, ver = trainingfilepkey.split('+')
            request.session['current_training_file_id'] = trid
            request.session['current_training_file_ver'] = ver
            trainingfilename = data['2']
            request.session['current_training_file_name'] = trainingfilename
            trainingfilelocation = (Trainingset.objects.get(trainingset_id=trid, trainingset_ver=ver)).filelocation # @UndefinedVariable
            trainingsetasArray = []
            trs = TrainingSet(request.session['current_training_file_name'])
            classes = list(numpy.unique(trs.target))
            
            if 'existing_categories' not in request.session and 'new_categories' not in request.session:
                request.session['existing_categories'] = classes
            
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
                old_trainingset = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_name'])
                print old_trainingset
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
            if Trainingset.objects.exists(): # @UndefinedVariable
                training_set_list = Trainingset.objects.all()  # @UndefinedVariable
                
            customQuery = CustomQueries()
            old_trainingset_name = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_name'])[2]
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
                return render(request, 'trainingsample.html', {'user_name': user_name, 'new_taxonomy': new_taxonomy})
        

def edittrainingset(request):
    if request.method=='POST':
        data = request.POST
        editoperation_no = data['1']
        editoperaiton_details = []
        editoperaiton_details.append(editoperation_no)
        if editoperation_no=='1':
            nodata_value = data['2'];
            editoperaiton_details.append(nodata_value)
        elif editoperation_no=='2':
            concept_to_remove = data['2'];
            editoperaiton_details.append(concept_to_remove)
        elif editoperation_no=='3':
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
            print editoperaiton_details
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
                
            managedata = ManageRasterData()
            managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList1, samplefilenameforfirstconcept, EXISTING_TRAINING_SAMPLES_LOCATION, concept1)
            managedata.combine_multiple_raster_files_to_csv_file(trainingSamplesFileList2, samplefilenameforsecondconcept, EXISTING_TRAINING_SAMPLES_LOCATION, concept2)

            
            editoperaiton_details.append(concepttosplit)
            editoperaiton_details.append(concept1)
            editoperaiton_details.append(samplefilenameforfirstconcept)
            editoperaiton_details.append(concept2)
            editoperaiton_details.append(samplefilenameforsecondconcept)
            
        
        if 'currenteditoperations' in request.session:
            currenteditoperations = request.session['currenteditoperations']
            print currenteditoperations
            currenteditoperations.append(editoperaiton_details)
            request.session['currenteditoperations'] = currenteditoperations
        else:
            currenteditoperations = []
            currenteditoperations.append(editoperaiton_details)
            request.session['currenteditoperations'] = currenteditoperations
        print request.session['currenteditoperations']
    
    return HttpResponse("done");

@transaction.atomic
def applyeditoperations(request):
    
    currenteditoperations = request.session['currenteditoperations']
    print currenteditoperations
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
            nodata_value = editoperation[1]
            manageCsvData.remove_no_data_value(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", nodata_value)          
            tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'remove no data')
            tr_activity_details.save(force_insert=True)
            
        elif editoperation[0] == '2':
            concept_to_remove = editoperation[1]
            manageCsvData.removeConcept(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", concept_to_remove)
            tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'remove', concept1= concept_to_remove)
            tr_activity_details.save(force_insert=True)
            
        elif editoperation[0] == '3':
            mergedconceptname = editoperation[2]
            concepts_to_merge = editoperation[1]
            merged_sample_details = manageCsvData.mergeConcepts(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", concepts_to_merge, mergedconceptname)
            
            trainingset_trainingsamples_instance = TrainingsetTrainingsamples(trainingset_id = tr.trainingset_id, trainingset_ver = tr.trainingset_ver, trainingsample_id = merged_sample_details[0], trainingsample_ver = merged_sample_details[1])
            trainingset_trainingsamples_instance.save(force_insert=True)
            
            if (len(concepts_to_merge) ==2):
                tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'merge', concept1= concepts_to_merge[0], concept2 = concepts_to_merge[1], concept3 = mergedconceptname)
            else:
                tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'merge', concept1= concepts_to_merge[0], concept2 = concepts_to_merge[1], concept3 = concepts_to_merge[2], concept4 = mergedconceptname)
            tr_activity_details.save(force_insert=True)
            
        else:
            concepttosplit = editoperation[1];
            firstconcept = editoperation[2];
            samplefilenameforfirstconcept = editoperation[3];
            secondconcept = editoperation[4];
            samplefilenameforsecondconcept = editoperation[5];
            new_concept_details = manageCsvData.splitconcept(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", concepttosplit, firstconcept, samplefilenameforfirstconcept, secondconcept, samplefilenameforsecondconcept, EXISTING_TRAINING_SAMPLES_LOCATION)

            trainingset_trainingsamples_instance1 = TrainingsetTrainingsamples(trainingset_id = tr.trainingset_id, trainingset_ver = tr.trainingset_ver, trainingsample_id = new_concept_details[0], trainingsample_ver = new_concept_details[1])
            trainingset_trainingsamples_instance1.save(force_insert=True)
            trainingset_trainingsamples_instance2 = TrainingsetTrainingsamples(trainingset_id = tr.trainingset_id, trainingset_ver = tr.trainingset_ver, trainingsample_id = new_concept_details[2], trainingsample_ver = new_concept_details[3])
            trainingset_trainingsamples_instance2.save(force_insert=True)

            tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'split', concept1= concepttosplit, concept2 = firstconcept, concept3 = secondconcept)
            tr_activity_details.save(force_insert=True)
        
        if 'existing_taxonomy_name' in request.session:
            if 'new_categories' in request.session:
                new_categories_while_exploring_changes = request.session['new_categories']
            else:
                new_categories_while_exploring_changes = []
            if 'existing_categories' in request.session:
                existing_categories = request.session['existing_categories']
            if 'categories_merged_from_existing' in request.session:
                categories_merged_from_existing = request.session['categories_merged_from_existing']
            else:
                categories_merged_from_existing = []
            if 'categories_split_from_existing' in request.session:
                categories_split_from_existing = request.session['categories_split_from_existing']
            else:
                categories_split_from_existing = []
            if 'categories_merged_from_new_and_existing' in request.session:
                categories_merged_from_new_and_existing = request.session['categories_merged_from_new_and_existing']
            else:
                categories_merged_from_new_and_existing = []
            if editoperation[0] == '2':
                if concept_to_remove in new_categories_while_exploring_changes:
                    new_categories_while_exploring_changes.remove(concept_to_remove)
                    request.session['new_categories'] = new_categories_while_exploring_changes
                elif concept_to_remove in existing_categories:
                    existing_categories.remove(concept_to_remove)
                    request.session['existing_categories'] = existing_categories
                else:
                    if (len(categories_merged_from_existing) !=0):
                        for merged_category in categories_merged_from_existing:
                            if merged_category[2] == concept_to_remove:
                                categories_merged_from_existing.remove(merged_category)
                                request.session['categories_merged_from_existing'] = categories_merged_from_existing
                                break
            elif editoperation[0] == '3':
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
                    else:
                        allconceptsfromexisting = False
                        allconceptsfromnew = False
                
                if allconceptsfromnew == True:
                    for concept in editoperation[1]:
                        new_categories_while_exploring_changes.remove(concept)
                    new_categories_while_exploring_changes.append(mergedconceptname)
                    request.session['new_categories'] = new_categories_while_exploring_changes
                elif allconceptsfromexisting == True:
                    new_concept_from_merging_existing_concepts = []
                    for concept in editoperation[1]:
                        existing_categories.remove(concept)
                        new_concept_from_merging_existing_concepts.append(concept)
                    request.session['existing_categories'] = existing_categories
                    new_concept_from_merging_existing_concepts.append(mergedconceptname)
                    categories_merged_from_existing.append(new_concept_from_merging_existing_concepts)
                    request.session['categories_merged_from_existing'] = categories_merged_from_existing
                elif len(conceptsinbothnewandexisting) == len(editoperation[1]):
                    new_concept_from_merging_existing_and_new_concepts = []
                    for concept in conceptsinbothnewandexisting:
                        if concept[1] == 'new':
                            new_categories_while_exploring_changes.remove(concept[0])
                            new_concept_from_merging_existing_and_new_concepts.append(concept[0])
                        else:
                            existing_categories.remove(concept[0])
                            new_concept_from_merging_existing_and_new_concepts.append(concept[0])
                    request.session['new_categories'] = new_categories_while_exploring_changes
                    request.session['existing_categories'] = existing_categories
                    new_concept_from_merging_existing_and_new_concepts.append(mergedconceptname)
                    categories_merged_from_new_and_existing.append(new_concept_from_merging_existing_concepts)
                    request.session['categories_merged_from_existing'] = categories_merged_from_new_and_existing
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
                                categories_split_from_existing.remove(split_category)
                                request.session['categories_split_from_existing'] = categories_split_from_existing
                                existing_categories.append(mergedconceptname)
                                request.session['existing_categories'] = existing_categories
                                break
                    
            elif editoperation[0] == '4':
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
                else:
                    if (len(categories_merged_from_existing) !=0):
                        for merged_category in categories_merged_from_existing:
                            if merged_category[2] == concepttosplit:
                                if (merged_category[0] == firstconcept and merged_category[1] == secondconcept) or (merged_category[0] == secondconcept and merged_category[1] == firstconcept):
                                    categories_merged_from_existing.remove(merged_category)
                                    request.session['categories_merged_from_existing'] = categories_merged_from_existing
                                    existing_categories.append(firstconcept)
                                    existing_categories.append(secondconcept)
                                    request.session['existing_categories'] = existing_categories
                                    break
    
    if 'new_categories' in request.session:                            
        print request.session['new_categories']
    if 'existing_categories' in request.session:      
        print request.session['existing_categories']
    if 'categories_merged_from_existing' in request.session:
        print request.session['categories_merged_from_existing']
    if 'categories_merged_from_new_and_existing' in request.session:
        print request.session['categories_merged_from_new_and_existing']
    if 'categories_split_from_existing' in request.session:
        print request.session['categories_split_from_existing']

    
    #adding details for current exploration details for visualization
    old_trainingset_name = request.session['current_training_file_name']
    new_trainingset_name = newfilename
    data_content = "Old trainingset: " + old_trainingset_name + "<br/> New trainingset: " + new_trainingset_name + "<br/><br/>" + "<b>Edit operations: </b><br/>"

    for editoperation in currenteditoperations:
        if editoperation[0] == '1':
            data_content = data_content + "Remove 'no data' values<br/>"
        elif editoperation[0] == '2': 
            data_content = data_content + "Remove concept" + editoperation[1]  + "<br/>"
        elif editoperation[0] == '3':
            mergedconceptname = editoperation[2]
            concepts_to_merge = editoperation[1]
            if len(concepts_to_merge) ==2:
                data_content = data_content + "Merge" + concepts_to_merge[0] + " and " + concepts_to_merge[1] + " to create " + mergedconceptname + "<br/>"
            else:
                data_content = data_content + "Merge" + concepts_to_merge[0] + ", " + concepts_to_merge[1] + " and " + concepts_to_merge[2] + " to create " + mergedconceptname + "<br/>"
        else:
            concepttosplit = editoperation[1];
            firstconcept = editoperation[2];
            secondconcept = editoperation[4];
            data_content = data_content + "Split" + concepttosplit + " into " + firstconcept + " and " + secondconcept + "<br/>"
    
    current_step = ['Change trainingset', 'Change trainingset', data_content]
    
    if 'current_exploration_chain_viz' in request.session:
        current_exploration_chain_viz = request.session['current_exploration_chain_viz']
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
        old_trainingset_name = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_name'])[2]
        new_training_sample = TrainingSet(request.session['current_training_file_name'])
        old_training_sample = TrainingSet(old_trainingset_name)
        common_categories, new_categories, deprecated_categories = new_training_sample.compare_training_samples(old_training_sample)
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
        print request.session['accuracy_limit'] 
        return HttpResponse("")

@login_required
def signaturefile(request):
    if 'currenteditoperations' in request.session:
        del request.session['currenteditoperations']
        request.session.modified = True
    request.session['exploration_chain_step'] = request.session['exploration_chain_step'] + 1
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
            skf = cross_validation.StratifiedKFold(trainingfile.target, n_folds=int(folds))
            cm=[]
            count =0
            for train_index, test_index in skf:
                X_train, X_test = trainingfile.samples[train_index], trainingfile.samples[test_index]
                y_train, y_test = trainingfile.target[train_index], trainingfile.target[test_index]
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
        print cm
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
            data_content = data_content + category + " (" + prodacc[i] + ", " + useracc[i] + ")<br/>" 
        
        current_step = ['Training activity', 'Training activity', data_content]
        
        if 'current_exploration_chain_viz' in request.session:
            current_exploration_chain_viz = request.session['current_exploration_chain_viz']
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
                    
            
            
            listofcategories = clf.classes_.tolist()
            overlapping_pairs = []
            for eachPair in jmdistances_list:
                if float(eachPair[2])<float(request.session['jm_distance_limit']):
                    overlapping_pairs.append(eachPair)
            sorted_overlapping_pairs = sorted(overlapping_pairs, key=itemgetter(2))     
            
            positive_pairs = []
            negative_pairs = []
            for index in range(len(sorted_overlapping_pairs)):
                if index==0:
                    positive_pairs.append(sorted_overlapping_pairs[index])
                else:
                    positive_pair= True
                    for pair in positive_pairs:
                        if sorted_overlapping_pairs[index][0] in pair or sorted_overlapping_pairs[index][1] in pair:
                            negative_pairs.append(sorted_overlapping_pairs[index])
                            positive_pair = False
                            break
                    if positive_pair == True:
                        positive_pairs.append(sorted_overlapping_pairs[index])
                        
            suggestion_list=[]
            for eachPair in positive_pairs:
                single_suggestion=[]
                index1 = listofcategories.index(eachPair[0])
                index2 = listofcategories.index(eachPair[1])
                acc_limit = float(request.session['accuracy_limit'])*2.0
                if float(prodacc[index1]) + float(useracc[index1]) < float(prodacc[index2]) + float(useracc[index2]) and float(prodacc[index1]) + float(useracc[index1])<acc_limit:
                    single_suggestion.append(listofcategories[index1])
                    single_suggestion.append(listofcategories[index2])
                    suggestion_list.append(single_suggestion)
                elif float(prodacc[index1]) + float(useracc[index1]) > float(prodacc[index2]) + float(useracc[index2]) and float(prodacc[index2]) + float(useracc[index2]) <acc_limit:
                    single_suggestion.append(listofcategories[index2])
                    single_suggestion.append(listofcategories[index1])
                    suggestion_list.append(single_suggestion)
            
            if 'existing_taxonomy_name' in request.session:
                customQuery = CustomQueries()

                old_trainingset_name = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_name'])[2]
                old_trainingfile = TrainingSet(old_trainingset_name)
                old_covariance_mat = old_trainingfile.create_covariance_matrix()
                old_mean_vectors = old_trainingfile.create_mean_vectors()
                new_categories = list(numpy.unique(trainingfile.target))
                old_categories = list(numpy.unique(old_trainingfile.target))
                common_categories = numpy.intersect1d(new_categories, old_categories)
                common_categories_comparison = []
                existing_categories_comparison_to_store = []
                if len(old_mean_vectors[0][1]) != len(mean_vectors[0][1]):
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
                        single_category_comparison.append(old_category_details[0][2])
                        single_category_comparison.append(old_category_details[0][3])
                        single_category_comparison.append(old_category_details[0][0])
                        single_category_comparison.append(old_category_details[0][1])
                        common_categories_comparison.append(single_category_comparison)
                    return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'meanvectors':clf.theta_.tolist(), 'variance':clf.sigma_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc, 'jmdistances': jmdistances_complete_list, 'suggestion_list': suggestion_list, 'common_categories_comparison': common_categories_comparison})
                else:
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
                        single_category_comparison.append(old_category_details[0][2])
                        single_category_comparison.append(old_category_details[0][3])
                        single_category_comparison.append(old_category_details[0][0])
                        single_category_comparison.append(old_category_details[0][1])
                        new_index = numpy.where(mean_vectors = common_category)[0][0]
                        old_index = numpy.where(old_mean_vectors = common_category)[0][0]
                        model1 = NormalDistributionIntensionalModel(mean_vectors[new_index][1], covariance_mat[new_index][1])
                        model2 = NormalDistributionIntensionalModel(old_mean_vectors[old_index][1], old_covariance_mat[old_index][1])
                        jm = model1.jm_distance(model2)
                        single_category_comparison.append(jm)
                        a = [common_category, jm]
                        existing_categories_comparison_to_store.append(a)
                        common_categories_comparison.append(single_category_comparison)
                    request.session['existing_categories_computational_intension_comparison'] = existing_categories_comparison_to_store
                    return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'],'jm_limit':request.session['jm_distance_limit'], 'acc_limit': request.session['accuracy_limit'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'meanvectors':clf.theta_.tolist(), 'variance':clf.sigma_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc, 'jmdistances': jmdistances_complete_list, 'suggestion_list': suggestion_list, 'common_categories_comparison': common_categories_comparison})
               
            return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'jm_limit':request.session['jm_distance_limit'], 'acc_limit': request.session['accuracy_limit'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'meanvectors':clf.theta_.tolist(), 'variance':clf.sigma_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc, 'jmdistances': jmdistances_complete_list, 'suggestion_list': suggestion_list})
        
        elif (classifiername=="Decision Tree"):
            #print clf.tree_.__getstate__()
            #print clf.tree_.children_left
            #print clf.tree_.children_right
            #print clf.tree_.feature
            #print clf.tree_.threshold
            #print clf.tree_.value
            newModel = DecisionTreeIntensionalModel(clf)
            dot_data = StringIO()
            tree.export_graphviz(clf, out_file=dot_data)
            graph = pydot.graph_from_dot_data(dot_data.getvalue())
            tree_name = modelname + "_tree.png"
            graph.write_png('%s%s' %(IMAGE_LOCATION, tree_name))
            
            listofcategories = clf.classes_.tolist()
            categories_with_low_accuracies = []
            acc_limit = float(request.session['accuracy_limit'])
            
            for index in range(len(listofcategories)):
                if (float(prodacc[index]) < acc_limit and float(useracc[index]) < acc_limit) or ((float(prodacc[index]) + float(useracc[index]))<(2.0*acc_limit)):
                    categories_with_low_accuracies.append(listofcategories[index])
            
            suggestion_list=[]
            for category in categories_with_low_accuracies:
                index = listofcategories.index(category)
                confusion_of_category_with_others = cm[index]
                highest_confusion_with_index = find_index_of_highest_number_except_a_given_index(confusion_of_category_with_others, index)
                if float(prodacc[index]) + float(useracc[index]) < float(prodacc[highest_confusion_with_index]) + float(useracc[highest_confusion_with_index]):
                    suggestion_list.append([category, listofcategories[highest_confusion_with_index]])
                else:
                    suggestion_list.append([listofcategories[highest_confusion_with_index], category])
            
            unique_suggestion_list = [list(t) for t in set(tuple(element) for element in suggestion_list)]    
            
            
            if 'existing_taxonomy_name' in request.session:
                customQuery = CustomQueries()
                old_trainingset_name = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_name'])[2]
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
                return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'suggestion_list': unique_suggestion_list, 'acc_limit': request.session['accuracy_limit'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'kappa':kp, 'cm': cmname, 'tree':tree_name, 'prodacc': prodacc, 'useracc': useracc, 'common_categories_comparison':common_categories_comparison})
                
            return JsonResponse({'attributes': features, 'user_name':user_name, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'suggestion_list': unique_suggestion_list, 'acc_limit': request.session['accuracy_limit'], 'score': score, 'listofclasses': clf.classes_.tolist(), 'kappa':kp, 'cm': cmname, 'tree':tree_name, 'prodacc': prodacc, 'useracc': useracc})
        else:
            return ""   
    else:
        if 'existing_taxonomy_name' in request.session:        
            return render (request, 'signaturefile.html', {'attributes': features, 'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'jm_limit':request.session['jm_distance_limit'], 'acc_limit': request.session['accuracy_limit']})
        else:
            return render (request, 'signaturefile.html', {'attributes': features, 'user_name':user_name, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'jm_limit':request.session['jm_distance_limit'], 'acc_limit': request.session['accuracy_limit']})

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
        clf = svm.SVC()
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
def supervised(request):
    request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1
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
                current_exploration_chain_viz.append(current_step)
                request.session['current_exploration_chain_viz'] = current_exploration_chain_viz
            else:
                request.session['current_exploration_chain_viz'] = [current_step]
            
            if 'existing_taxonomy_name' in request.session:
                customQuery = CustomQueries()
                old_trainingset = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_name'])[2]
                trs = TrainingSet(old_trainingset)
                oldCategories = list(numpy.unique(trs.target))
                change_matrix, J_Index_for_common_categories = create_change_matrix(oldCategories, predictedValue, rows, columns)
                request.session['J_Index_for_common_categories'] = J_Index_for_common_categories
                    
                return  JsonResponse({'map': outputmapinJPG, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'categories': listofcategories, 'change_matrix':change_matrix, 'old_categories': oldCategories});
            
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
        if 'current_exploration_chain_viz' in request.session:
            if 'existing_taxonomy_name' in request.session:
                return render(request, 'supervised.html', {'user_name':user_name, 'new_taxonomy': 'False', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'concepts': concepts_in_current_taxonomy})
            else:
                return render(request, 'supervised.html', {'user_name':user_name, 'new_taxonomy': 'True', 'current_exploration_chain': request.session['current_exploration_chain_viz'], 'concepts': concepts_in_current_taxonomy})
        else:
            return render (request, 'supervised.html', {'user_name':user_name, 'concepts': concepts_in_current_taxonomy})


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

def create_change_matrix(oldCategories, newPredictedValues, rows, columns):
    list_of_new_categories = list(numpy.unique(newPredictedValues))
    change_in_individual_matrix = [[0 for a in range(len(list_of_new_categories))] for x in range(len(oldCategories))]
    customQuery = CustomQueries()
    
    for index, category in enumerate(oldCategories):
        category_extension = customQuery.getExtension(category, '0', '1')
        for coordinates in category_extension:            
            ind = coordinates[0]*columns + coordinates[1] #coordinates[0]==row no
            new_category = newPredictedValues[ind]
            #new_category_index = numpy.where(list_of_new_categories == new_category)
            new_category_index = list_of_new_categories.index(new_category)
            change_in_individual_matrix[index][new_category_index] += 1
    
    J_Index_for_common_categories = []
    for index, category in enumerate(oldCategories):
        if category in list_of_new_categories:
            new_category_index = list_of_new_categories.index(category)
            common_elements = change_in_individual_matrix[index][new_category_index]
            old_elements = 0.0
            new_elements = 0.0
            for a in change_in_individual_matrix[index]:
                old_elements += a
                
            for b in change_in_individual_matrix:
                old_elements += b[new_category_index]
            
            union_of_elements = old_elements + new_elements - common_elements
            j_index = "{0:.2f}".format(float(common_elements/union_of_elements))
            J_Index_for_common_categories.append([category, j_index])
        
        
    print change_in_individual_matrix
    return change_in_individual_matrix, J_Index_for_common_categories
        
def calculate_J_index_for_catgeory_extension(category, ext1, ext2, predicted_file, rows, columns):
    common_elements = 0.0
    for coordinates in ext1:
        ind = coordinates[0]*columns + coordinates[1]
        new_category = predicted_file[ind]
        
        if new_category[0] == category:
            common_elements += 1.0


    extra_in_first_extension = len(ext1) - common_elements  
    extra_in_second_extension = len(ext2) - common_elements
    union_of_two_extensions = common_elements + extra_in_first_extension + extra_in_second_extension
    jaccard_index = float(common_elements/union_of_two_extensions)
    #common_elements_in_both_extensions = numpy.intersect1d(ext1, ext2)
    #union_of_both_extensions = numpy.union1d(ext1, ext2)
    #jaccard_index = float(len(common_elements_in_both_extensions)/len(union_of_both_extensions))
    return jaccard_index

    

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
            
            exploration_chain = ExplorationChain.objects.filter(id = request.session['exploration_chain_id'])
            exploration_chain_details = []
            for exp in exploration_chain:
                exploration_step = []
                if exp.activity == 'create trainingset':
                    details_of_create_trainingset_activity = customQuery.getDetailsOfCreateTrainingSetActivity(exp.activity_instance)
                    data_term = "Create trainingset (Trainingset id: " +  str(details_of_create_trainingset_activity[0][0]) + ", Trainingset version: " + str(details_of_create_trainingset_activity[0][1]) + ")"
                    exploration_step.append(data_term)
                    details_of_activity = []
                    for each_step in details_of_create_trainingset_activity:
                        details_of_activity.append(each_step[4] + " category: " + each_step[5])
                    exploration_step.append(details_of_activity)
                    exploration_chain_details.append(exploration_step)
                elif exp.activity == 'change trainingset':
                    details_of_change_trainingset_activity = customQuery.getDetailsOfChangeTrainingSetActivity(exp.activity_instance)
                    data_term = "Change trainingset (Trainingset id: " + str(details_of_change_trainingset_activity[0][0]) + ", old version: " + str(details_of_create_trainingset_activity[0][1]) + ", new version: " + str(details_of_create_trainingset_activity[0][2]) + ")"
                    exploration_step.append(data_term)
                    details_of_activity = []
                    for each_step in details_of_change_trainingset_activity:
                        if each_step[3] == 'remove no data':
                            details_of_activity.append("Remove 'no data' values")
                        elif each_step[3] == 'remove':
                            details_of_activity.append("Remove concept: " + each_step[4])
                        elif each_step[3] == 'merge':
                            if each_step[7] == None:
                                details_of_activity.append("Merge concepts: " + each_step[4] + " and " + each_step[5] + ", and create a new concept " +  each_step[6])
                            else:
                                details_of_activity.append("Merge concepts: " + each_step[4] + ", " + each_step[5] + " and " + each_step[6] + ", and create a new concept " +  each_step[7])
                        else:
                            details_of_activity.append([each_step[3], each_step[4], each_step[5], each_step[6], each_step[7]])
                    exploration_step.append(details_of_activity)
                    exploration_chain_details.append(exploration_step)
                elif exp.activity == 'learning':
                    details_of_learning_activity = customQuery.getDetailsOfTrainingActivity(exp.activity_instance)
                    data_term = "Learning activity (Model type: " + details_of_learning_activity[0] + ", Validation type: " + details_of_learning_activity[2] + ", Validation score: " + str(details_of_learning_activity[1]) + ")"
                    exploration_chain_details.append([data_term])
                else:
                    exploration_chain_details.append(["Classification activity"])

            return render(request, 'changerecognition.html', {'user_name':user_name, 'new_taxonomyName': new_taxonomy, 'exploration_chain':exploration_chain_details, 'conceptsList':concepts_in_current_taxonomy, 'modelType': model_type, 'modelScore': model_accuracy, 'userAccuracies': user_accuracies, 'producerAccuracies': producer_accuracies})
    else:
        existing_taxonomy = request.session['existing_taxonomy_name']
        existing_taxonomy_instance = Legend.objects.get(legend_name = existing_taxonomy) 
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
        old_trainingset = TrainingSet(customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_name'])[2])
        oldCategories = list(numpy.unique(old_trainingset.target))
        
        #categories common to newly modeled set of categories and the categories stored in the latest version of the legend
        existing_categories = request.session['existing_categories']
        
        common_categories_comparison_details = []
        J_Index_for_common_categories = request.session['J_Index_for_common_categories']

        for each_category in existing_categories:
            index = concepts_in_current_taxonomy.index(each_category)
            old_category_details = customQuery.get_accuracies_and_validation_method_of_a_category(request.session['existing_taxonomy_id'], request.session['existing_taxonomy_ver'], each_category)
            common_category_comparison_details = [each_category, user_accuracies[index], producer_accuracies[index], old_category_details[0][1], old_category_details[0][0]]
            for category_andJ_index in J_Index_for_common_categories:
                if each_category in category_andJ_index:
                    common_category_comparison_details.append(category_andJ_index[1])
                    break
            if 'existing_categories_computational_intension_comparison' in request.session:
                existing_categories_computational_intension_comparison = request.session['existing_categories_computational_intension_comparison']
                for each_category_compint_comparison in existing_categories_computational_intension_comparison:
                    if each_category_compint_comparison[0] == each_category:
                        common_category_comparison_details.append(each_category_compint_comparison[1])
            common_categories_comparison_details.append(common_category_comparison_details)
        print common_categories_comparison_details
        
        #new categories in the newly modeled set of categories
        
        new_categories_details = []
        if 'new_categories' in request.session:
            new_categories = request.session['new_categories']
            for each_category in new_categories:
                index = concepts_in_current_taxonomy.index(each_category)
                new_categories_details.append([each_category, user_accuracies[index], producer_accuracies[index]])
            print new_categories_details
            
        #categories resulted from merging of existing categories
        categories_merged_from_existing_details = []
        if 'categories_merged_from_existing' in request.session: 
            categories_merged_from_existing = request.session['categories_merged_from_existing']
            for each_merged_category in categories_merged_from_existing:
                index = concepts_in_current_taxonomy.index(each_merged_category[-1])
                details = [each_merged_category[-1]]
                details.append(user_accuracies[index])
                details.append(producer_accuracies[index])
                for i in range(len(each_merged_category)-1):
                    details.append(each_merged_category[i])
                categories_merged_from_existing_details.append(details)
          
        
        #categories resulted from splitting of existing
        categories_split_from_existing_details = []
        if 'categories_split_from_existing' in request.session: 
            categories_split_from_existing = request.session['categories_split_from_existing']
            print categories_split_from_existing
            for each_split_category in categories_split_from_existing:
                for i in range(len(each_split_category)-1):
                    index = concepts_in_current_taxonomy.index(each_split_category[i+1])
                    categories_split_from_existing_details.append([each_split_category[i+1], each_split_category[0], user_accuracies[index], producer_accuracies[index]])
                    print categories_split_from_existing_details

        categories_merged_from_new_and_existing_details = []
        if 'categories_merged_from_new_and_existing' in request.session: 
            categories_merged_from_new_and_existing = request.session['categories_merged_from_new_and_existing']
        
        
        
        return render(request, 'changerecognition.html', {'user_name':user_name, 'existing_taxonomyName': existing_taxonomy, 'model_type': model_type, 'model_score': model_accuracy, 'old_model_type':old_model_type, 'old_model_accuracy': old_model_accuracy, 'external_trigger': request.session['external_trigger'], 'common_categories_comparison_details':common_categories_comparison_details, 'new_categories_details': new_categories_details, 'categories_merged_from_existing_details': categories_merged_from_existing_details, 'categories_split_from_existing_details': categories_split_from_existing_details, 'categories_merged_from_new_and_existing_details': categories_merged_from_new_and_existing_details})
        
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
    compositeChangeOperations = []
    new_version = int(request.session['existing_taxonomy_ver'])+1
    firstOp, root_concept = get_addNewTaxonomyVersion_op_details(request.session['existing_taxonomy_name'], new_version)
    compositeChangeOperations.append(firstOp)
    
    if 'existing_categories' in request.session:
        existing_categories = request.session['existing_categories']
        for category in existing_categories:
            changeOperation = get_addExistingConceptForNewTaxonomyVersion_op_details(request.session['existing_taxonomy_name'], new_version, request.session['existing_taxonomy_ver'], root_concept, category)
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
    compositeOp = "Add_Concept ('" + taxonomy_name + "', '" + concept_name + "', '" + parent_concept_name + "')"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Create concept '" + concept_name + "' (if it does not exists)")
    if taxonomy_version == 1:
        compositeOp_details.append("Add '" + concept_name + "' to '" + taxonomy_name + "'")
    else:
        compositeOp_details.append("Add '" + concept_name + "' to '" + taxonomy_name + "'" + " Ver_" + taxonomy_version)
    compositeOp_details.append("Add hierarchical relationship - '" + parent_concept_name + "' parent of '" + concept_name + "'")
    compositeOp_details.append("Category Instantiation ('" + concept_name + "')")
    #catInst = []
    #catInst.append("Category Instantiation ('" + concept_name + "')")
    #catInst_details = []
    #catInst_details.append("Create category ('" + concept_name + "')")
    #catInst_details.append("Add computational intension")
    #catInst_details.append("Add extension")
    #catInst_details.append("Add the category to the concept")
    #catInst.append(catInst_details)
    #compositeOp_details.append(catInst)
    changeOperation.append(compositeOp_details)
    return changeOperation

def get_addExistingConceptForNewTaxonomyVersion_op_details(taxonomy_name, taxonomy_version, old_version, parent_concept_name, concept_name):
    changeOperation = []
    compositeOp = "Add_Existing_Concept_To_New_Legend_Version ('" + taxonomy_name + "', '" + str(taxonomy_version) + "', '" + concept_name + "', '" + parent_concept_name + "')"
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
    compositeOp = "Add_Merged_Concept_For_New_Legend_Version ('" + taxonomy_name + "', '" + str(taxonomy_version) + "', '" + concept_name + "', '" + parent_concept_name + "', '" + merged_concepts + "')"
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
    compositeOp = "Add_Concept_Split_From_Existing_Concept_For_New_Legend_Version ('" + taxonomy_name + "', '" +  str(taxonomy_version) + "', '" + new_concept + "', '" + parent_concept_name + "', '" + split_concept + "')"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Create concept '" + new_concept + "' (if it does not exists)")
    compositeOp_details.append("Add '" + new_concept + "' to '" + taxonomy_name + "' Ver_" +  str(taxonomy_version))
    compositeOp_details.append("Add hierarchical relationship - '" + parent_concept_name + "' parent of '" + new_concept + "'")
    compositeOp_details.append("Category Instantiation ('" + new_concept + "')")
    compositeOp_details.append("Add_horizontal_relationship ('" + new_concept + "', '" + split_concept + "', '" + taxonomy_name + "', " +  str(taxonomy_version) + ", " + str(old_version) + ")")
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
            change_event_queries.create_concept(concepts_in_current_taxonomy[i], mean_vectors[i][1], covariance_mat[i][1],  extension[i], producer_accuracies[i], user_accuracies[i])
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
        J_Index_for_common_categories = request.session['J_Index_for_common_categories']

        if 'existing_categories' in request.session:
            existing_categories = request.session['existing_categories']
            for each_existing_category in existing_categories:
                i = concepts_in_current_taxonomy.index(each_existing_category)
                extensional_similarity =0.00
                for category_andJ_index in J_Index_for_common_categories:
                    if each_existing_category in category_andJ_index:
                        extensional_similarity = category_andJ_index[1]
                        break
                intensional_similarity = 0.00
                if 'existing_categories_computational_intension_comparison' in request.session:
                    existing_categories_computational_intension_comparison = request.session['existing_categories_computational_intension_comparison']
                    for each_category_compint_comparison in existing_categories_computational_intension_comparison:
                        if each_category_compint_comparison[0] == each_existing_category:
                            intensional_similarity = each_category_compint_comparison[1]
                            break

                change_event_queries.add_existing_concept_to_new_version_of_legend_with_updated_categories(each_existing_category, mean_vectors[i][1], covariance_mat[i][1],  extension[i], producer_accuracies[i], user_accuracies[i], intensional_similarity, extensional_similarity)
    
    del request.session['new_taxonomy_name']
    del request.session['new_taxonomy_description']
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
    del request.session['root_concept']
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
    test_taxonomy = "((Sea water, inland water, Estuarine open water)Water_bodies, ((Urban, Suburban)Built space, Open space)artificial_surface, cloud, shadow, forest, grassland)Root;"
    t1 = Tree(test_taxonomy, format=8)   # @UndefinedVariable
    t1.add_face(TextFace("Root "), column=0, position = "branch-top")
    ts = TreeStyle()
    ts.show_leaf_name = True
    ts.show_scale = False
    ts.branch_vertical_margin = 20
    ts.scale = 25
    ts.title.add_face(TextFace("Auckland LCDB - Ver1", fsize=10), column=0)
    ts.rotation = 90
    for node in t1.traverse():
        if node.name == "Water_bodies":
            node.add_face(TextFace(" Water bodies "), column=0, position = "branch-top")
        elif node.name == " Built space ":
            node.add_face(TextFace("Built space"), column=0, position = "branch-top")
        elif node.name == "artificial_surface":
            node.add_face(TextFace(" Artificial Surface "), column=0, position = "branch-top")
    
    
    taxonomy_image_name = "tree.png"
    t1.render("%s%s" %(TAXONOMY_IMAGE_LOCATION, "tree.png"), tree_style=ts, dpi=150)

    return taxonomy_image_name