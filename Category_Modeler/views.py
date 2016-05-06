import csv, json, numpy, pydot, os
import matplotlib.pyplot as plt
from io import FileIO, BufferedWriter
from datetime import datetime
from shutil import copyfile
from ete3 import Tree, TreeStyle, TextFace # @UndefinedVariable
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
        if Legend.objects.exists(): # @UndefinedVariable
            legend_list = Legend.objects.all()  # @UndefinedVariable
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
    
    return HttpResponse("Upload new training samples or choose an existing one, and start the exploration process!");

def savenewtaxonomydetails(request):
    if request.method == 'POST':
        data = request.POST
        request.session['new_taxonomy_name'] = data['newtaxonomyname']
        request.session['new_taxonomy_description'] = data['description']
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
                exp_chain.save()
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
                with open('%s%s' % (EXISTING_TRAINING_DATA_LOCATION, request.session['current_training_file_name']), 'rU') as trainingset:
                    datareader = csv.reader(trainingset, delimiter=',')
                    trainingsetasArray = list(datareader)
                    trainingset.close()
                return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes})  
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
                print request.session['current_samples_id_and_version']
                create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'add new', concept1 = conceptName)
                create_tset_activity_ops.save()
                
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
                print request.session['current_samples_id_and_version']   
                create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'add existing', concept1 = conceptName)
                create_tset_activity_ops.save()
                
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

            else:
                conceptToSplit = data['ConceptToSplit']
                firstConceptNameFromSplit = data['FirstConceptName']
                secondConceptNameFromSplit = data['SecondConceptName']
                
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
                    
                create_tset_activity_ops = CreateTrainingsetActivityOperations(create_trainingset_activity_id = create_ts_activity_instance, operation = 'split', concept1 = conceptToSplit, concept2 = firstConceptNameFromSplit, concept3 = secondConceptNameFromSplit)
            
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
                create_ts_activity_instance.save()
                
                for sample_id_and_ver in current_samples_id_and_version:
                    trainingset_trainingsamples_instance = TrainingsetTrainingsamples(trainingset_id = request.session['current_training_file_id'], trainingset_ver = request.session['current_training_file_ver'], trainingsample_id = sample_id_and_ver[0], trainingsample_ver = sample_id_and_ver[1])
                    trainingset_trainingsamples_instance.save(force_insert=True)
                
                exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'create trainingset', activity_instance = create_ts_activity_instance.id)
                exp_chain.save()
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
                if isinstance(common_categories[0], list)==False:
                    common_categories_message = "The two training samples have different number of bands; so, we cannot compare common categories based on training samples"
                    return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes, 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories, 'common_categories_message':common_categories_message})
        
                return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes, 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories})

                
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

            return JsonResponse({'trainingset': trainingsetasArray, 'classes': classes})             
            #   fp = file (trainingfilelocation+trainingfilename, 'rb')
            #   response = HttpResponse( fp, content_type='text/csv')
            #   response['Content-Disposition'] = 'attachment; filename="temp.csv"'            
    else:
        if 'new_taxonomy_name' not in request.session:
            existing_taxonomy = request.session['existing_taxonomy_name']
            if Trainingset.objects.exists(): # @UndefinedVariable
                training_set_list = Trainingset.objects.all()  # @UndefinedVariable
                
            customQuery = CustomQueries()
            old_trainingset_name = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_name'])[2]
            old_training_sample = TrainingSet(old_trainingset_name)
            category_list = list(numpy.unique(old_training_sample.target))
            return render(request, 'trainingsample.html', {'training_set_list':training_set_list, 'user_name': user_name, 'existing_taxonomy': existing_taxonomy, 'concept_list': category_list})
        else:
            new_taxonomy =    request.session['new_taxonomy_name'] 
            if Trainingset.objects.exists(): # @UndefinedVariable
                training_set_list = Trainingset.objects.all()  # @UndefinedVariable
                
                return render(request, 'trainingsample.html', {'training_set_list':training_set_list, 'user_name': user_name, 'new_taxonomy': new_taxonomy})
            else:
                return render(request, 'trainingsample.html', {'user_name': user_name, 'new_taxonomy': new_taxonomy})
        
        
    '''  
            
        if request.FILES:
            trainingFilesList = request.FILES.getlist('file')
            
            if len(trainingFilesList)==1 and trainingFilesList[0].name.split(".")[-1] == "csv":
                request.session['current_training_file_name'] = trainingFilesList[0].name.split('.', 1)[0] + '.csv'
                save_csv_training_file(trainingFilesList[0])
                return HttpResponse("We got the file");
            elif len(trainingFilesList)>1 and trainingFilesList[0].name.split(".")[-1] == "tif":
                request.session['current_training_file_name'] = 'temp.csv'
                rasterFileNameList = []
                for rasterfile in trainingFilesList:
                    rasterFileNameList.append(rasterfile.name)
                managedata = ManageRasterData()
                managedata.combine_multiple_raster_files_to_csv_file(rasterFileNameList, request.session['current_training_file_name'], EXISTING_TRAINING_DATA_LOCATION)
                fp = file("%s%s" % (EXISTING_TRAINING_DATA_LOCATION, request.session['current_training_file_name']), 'rb')
                response = HttpResponse( fp, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="training File"'
                return response
            else:
                error = "Error: Training files not in right format: Either choose a single csv file or choose multiple raster files, each representing training samples for different categories"
                return JsonResponse({'error': error})
        else:
            data = request.POST
            trainingfilepkey = data['1']
            trid, ver = trainingfilepkey.split('+')
            request.session['current_training_file_id'] = trid
            request.session['current_training_file_ver'] = ver
            trainingfilename = data['2']
            request.session['current_training_file_name'] = trainingfilename
            trainingfilelocation = (Trainingset.objects.get(trainingset_id=trid, trainingset_ver=ver)).filelocation # @UndefinedVariable
            fp = file (trainingfilelocation+trainingfilename, 'rb')
            
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
            
            response = HttpResponse( fp, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="temp.csv"'
            
            return response'''

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
            firstconcepttomerge = data['2'];
            secondconcepttomerge = data['3'];
            mergedconceptname = data['4'];
            editoperaiton_details.append(firstconcepttomerge)
            editoperaiton_details.append(secondconcepttomerge)
            editoperaiton_details.append(mergedconceptname)
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
            currenteditoperations.append(editoperaiton_details)
            request.session['currenteditoperations'] = currenteditoperations
        else:
            currenteditoperations = []
            currenteditoperations.append(editoperaiton_details)
            request.session['currenteditoperations'] = currenteditoperations

    
    return HttpResponse("");

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
    print latestver
    newfilename = trainingfilename.rpartition('_')[0] + "_VER" + str(latestver) + ".csv"
    print newfilename
    oldversion = Trainingset.objects.get(trainingset_id=int(trid), trainingset_ver =int(ver))
    if  oldversion.date_expired == datetime(9999, 9, 12):
        oldversion.date_expired = datetime.now()
        oldversion.save()
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
            #trainingSamplesForCurrentTrainingset = customQuery.getTrainingSampleForTrainingset(trid, ver)            
            tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'remove no data')
            tr_activity_details.save(force_insert=True)
            
        elif editoperation[0] == '2':
            concept_to_remove = editoperation[1]
            manageCsvData.removeConcept(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", concept_to_remove)
            #id_and_ver_of_sample = customQuery.getTrainingSampleIdAndVersionForAGivenConceptInATrainingSet(trid, ver, concept_to_remove)
            #print id_and_ver_of_sample[0]
            tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'remove', concept1= concept_to_remove)
            tr_activity_details.save(force_insert=True)
            
        elif editoperation[0] == '3':
            firstconcepttomerge = editoperation[1];
            secondconcepttomerge = editoperation[2];
            mergedconceptname = editoperation[3];
            merged_sample_details = manageCsvData.mergeConcepts(trainingfilename, EXISTING_TRAINING_DATA_LOCATION, "temp.csv", firstconcepttomerge, secondconcepttomerge, mergedconceptname)
            
            trainingset_trainingsamples_instance = TrainingsetTrainingsamples(trainingset_id = tr.trainingset_id, trainingset_ver = tr.trainingset_ver, trainingsample_id = merged_sample_details[0], trainingsample_ver = merged_sample_details[1])
            trainingset_trainingsamples_instance.save(force_insert=True)
            
            tr_activity_details = ChangeTrainingsetActivityDetails(activity_id = tr_activity, operation = 'merge', concept1= firstconcepttomerge, concept2 = secondconcepttomerge, concept3 = mergedconceptname)
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

    os.rename(EXISTING_TRAINING_DATA_LOCATION + fname, EXISTING_TRAINING_DATA_LOCATION + newfilename)

    request.session['current_training_file_name'] = newfilename
    request.session['current_training_file_ver'] = latestver
    
    exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'change trainingset', activity_instance = tr_activity.id)
    exp_chain.save()
    
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
            return JsonResponse({'trainingset': trainingsetasArray, 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories, 'common_categories_message':common_categories_message})

        return JsonResponse({'trainingset': trainingsetasArray, 'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories})

    

def savetrainingdatadetails(request):
    if request.method=='POST':
        data = request.POST;
        trainingFileName = data['TrainingFileName']
        researcherName = data['FieldResearcherName'];
        trainingstart = data['TrainingTimePeriodStartDate'];
        trainingend = data['TrainingTimePeriodEndDate'];
        location = data['TrainingLocation'];
        otherDetails = data['OtherDetails'];
        
        os.rename("%s%s" %(EXISTING_TRAINING_DATA_LOCATION, request.session['current_training_file_name']), "%s%s" %(EXISTING_TRAINING_DATA_LOCATION, trainingFileName))
        request.session['current_training_file_name'] = trainingFileName
        
        #add training dataset details in trainingset table and a collection activity in trainingset_collection_activity table
        if Trainingset.objects.all().exists():
            latestid = Trainingset.objects.latest("trainingset_id").trainingset_id
        else:
            latestid = 0
        tr = Trainingset(trainingset_id=int(latestid)+1, trainingset_ver =1, trainingset_name=request.session['current_training_file_name'], description=otherDetails, date_expired=datetime(9999, 9, 12), filelocation=EXISTING_TRAINING_DATA_LOCATION)
        tr.save(force_insert=True)
        tr_activity = TrainingsetCollectionActivity( trainingset_id= int(latestid)+1, trainingset_ver =1, date_started = datetime.strptime(trainingstart, '%Y-%m-%d'), date_finished= datetime.strptime(trainingend, '%Y-%m-%d'), trainingset_location=location, collector=researcherName, description= otherDetails)
        tr_activity.save()
        request.session['current_training_file_id'] = int(latestid)+1
        request.session['current_training_file_ver'] = 1
        current_activity_instance = TrainingsetCollectionActivity.objects.get(trainingset_id=request.session['current_training_file_id'], trainingset_ver =request.session['current_training_file_ver']).id
        exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'trainingset collection', activity_instance = current_activity_instance)
        exp_chain.save()
        request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1
 
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
            customQuery = CustomQueries()
            old_trainingset_name = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_name'])[0]
            new_training_sample = TrainingSet(request.session['current_training_file_name'])
            old_training_sample = TrainingSet(old_trainingset_name)
            common_categories, new_categories, deprecated_categories = new_training_sample.compare_training_samples(old_training_sample)
            if isinstance(common_categories[0], list)==False:
                common_categories_message = "The two training samples have different number of bands; so, we cannot compare common categories based on training samples"
                return JsonResponse({'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories, 'common_categories_message':common_categories_message})
    
            return JsonResponse({'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories})
       
    return HttpResponse("");


def saveNewTrainingVersion(request):
    if request.method=='POST':
        
        data = json.loads(request.body)
        
        change_message = data.pop(0)
        filename= request.session['current_training_file_name']
        version = request.session['current_training_file_ver']
        fileid= request.session['current_training_file_id']
        
        new_tr_ver = Trainingset.objects.filter(trainingset_id = request.session['current_training_file_id']).latest("trainingset_ver").trainingset_ver
        newfilename = filename.rpartition('_')[0] + "_ver" + str(int(new_tr_ver)+1) + ".csv"
        f1 = open('%s%s' % (EXISTING_TRAINING_DATA_LOCATION, newfilename), 'w')
        writer = csv.writer(f1)
        for i in range(len(data)):
            writer.writerow(data[i])
        f1.close()
        
        oldversion = Trainingset.objects.get(trainingset_id=int(fileid), trainingset_ver =int(version))
        if  oldversion.date_expired == datetime(9999, 9, 12):
            oldversion.date_expired = datetime.now()
            oldversion.save()
        tr = Trainingset(trainingset_id=int(fileid), trainingset_ver =int(new_tr_ver)+1, trainingset_name=newfilename, date_expired=datetime(9999, 9, 12), filelocation=EXISTING_TRAINING_DATA_LOCATION)
        tr.save(force_insert=True)
        authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
        
        tr_activity = ChangeTrainingsetActivity( oldtrainingset_id= int(fileid), oldtrainingset_ver =int(version), newtrainingset_id=int(fileid), newtrainingset_ver=int(new_tr_ver)+1, completed_by=authuser_instance, reason_for_change = change_message)
        tr_activity.save()
        
        request.session['current_training_file_name'] = newfilename
        request.session['current_training_file_ver'] = int(new_tr_ver)+1
        
        exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'change trainingset', activity_instance = tr_activity.id)
        exp_chain.save()
        
        request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1
        
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
            customQuery = CustomQueries()
            old_trainingset_name = customQuery.get_trainingset_name_for_current_version_of_legend(request.session['existing_taxonomy_name'])[0]
            new_training_sample = TrainingSet(request.session['current_training_file_name'])
            old_training_sample = TrainingSet(old_trainingset_name)
            common_categories, new_categories, deprecated_categories = new_training_sample.compare_training_samples(old_training_sample)
            if isinstance(common_categories[0], list)==False:
                common_categories_message = "The two training samples have different number of bands; so, we cannot compare common categories based on training samples"
                return JsonResponse({'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories, 'common_categories_message':common_categories_message})
    
            return JsonResponse({'common_categories': common_categories, 'new_categories':new_categories, 'deprecated_categories': deprecated_categories})
       
    return HttpResponse("Changes are implemented and new training file is saved as "+ newfilename);
        
# create a file with similar name as provided in the static folder and copy all the contents    
def save_csv_training_file(f):
    with BufferedWriter( FileIO( '%s%s' % (EXISTING_TRAINING_DATA_LOCATION, f), "wb" ) ) as dest:
        foo = f.read(1024)  
        while foo:
            dest.write(foo)
            foo = f.read(1024)
        dest.close();


@login_required
def signaturefile(request):
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username # @UndefinedVariable
    if 'new_taxonomy_name' not in request.session and 'existing_taxonomy_name' not in request.session :
            messages.error(request, "Choose an activity before you proceed further")
            return HttpResponseRedirect("/AdvoCate/home/", {'user_name': user_name})
    
    if 'current_training_file_name' not in request.session:
        return render (request, 'signaturefile.html', {'user_name':user_name})
    
    print request.session['current_training_file_name']
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
        plot_confusion_matrix(cm, trainingfile.target)
        cmname = modelname+"_cm.png"
        plt.savefig("%s/%s" % (IMAGE_LOCATION, cmname),  bbox_inches='tight')
        
        sf = Classificationmodel(model_name = modelname, model_location=CLASSIFICATION_MODEL_LOCATION, accuracy=score)
        sf.save()
        request.session['current_model_id'] = sf.id
        
        conf_matrix = Confusionmatrix(confusionmatrix_name = cmname, confusionmatrix_location=IMAGE_LOCATION)
        conf_matrix.save()
        
        tc = LearningActivity(classifier=classifier_instance, model= sf, validation = validationtype, validation_score= score, confusionmatrix=conf_matrix, completed_by= authuser_instance)
        tc.save()
        
        exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'learning', activity_instance = tc.id)
        exp_chain.save()
        
        request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1
        
        if 'current_predicted_file_name' in request.session:
            del request.session['current_test_file_name']
            del request.session['current_predicted_file_name']
            del request.session['current_test_file_columns']
            del request.session['current_test_file_rows']
            request.session.modified = True
        
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
                    
            
            suggestion_list=[]
            listofcategories = clf.classes_.tolist()
            for eachPair in  jmdistances_list:
                single_suggestion=[]
                if float(eachPair[2])<1.1:
                    index1 = listofcategories.index(eachPair[0])
                    index2 = listofcategories.index(eachPair[1])
                    if float(prodacc[index1]) + float(useracc[index1]) < float(prodacc[index2]) + float(useracc[index2]) and float(prodacc[index1]) + float(useracc[index1])<1.2:
                        single_suggestion.append(listofcategories[index1])
                        single_suggestion.append(listofcategories[index2])
                        suggestion_list.append(single_suggestion)
                    elif float(prodacc[index1]) + float(useracc[index1]) > float(prodacc[index2]) + float(useracc[index2]) and float(prodacc[index2]) + float(useracc[index2]) <1.2:
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
                    return JsonResponse({'attributes': features, 'user_name':user_name, 'score': score, 'listofclasses': clf.classes_.tolist(), 'meanvectors':clf.theta_.tolist(), 'variance':clf.sigma_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc, 'jmdistances': jmdistances_complete_list, 'suggestion_list': suggestion_list, 'common_categories_comparison': common_categories_comparison})
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
                        common_categories_comparison.append(single_category_comparison)
                    return JsonResponse({'attributes': features, 'user_name':user_name, 'score': score, 'listofclasses': clf.classes_.tolist(), 'meanvectors':clf.theta_.tolist(), 'variance':clf.sigma_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc, 'jmdistances': jmdistances_complete_list, 'suggestion_list': suggestion_list, 'common_categories_comparison': common_categories_comparison})
               
            return JsonResponse({'attributes': features, 'user_name':user_name, 'score': score, 'listofclasses': clf.classes_.tolist(), 'meanvectors':clf.theta_.tolist(), 'variance':clf.sigma_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc, 'jmdistances': jmdistances_complete_list, 'suggestion_list': suggestion_list})
        
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
                return JsonResponse({'attributes': features, 'user_name':user_name, 'score': score, 'listofclasses': clf.classes_.tolist(), 'kappa':kp, 'cm': cmname, 'tree':tree_name, 'prodacc': prodacc, 'useracc': useracc, 'common_categories_comparison':common_categories_comparison})
                
            return JsonResponse({'attributes': features, 'user_name':user_name, 'score': score, 'listofclasses': clf.classes_.tolist(), 'kappa':kp, 'cm': cmname, 'tree':tree_name, 'prodacc': prodacc, 'useracc': useracc})
        else:
            return ""   
    else:
        return render (request, 'signaturefile.html', {'attributes': features, 'user_name':user_name})

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
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username
    if 'new_taxonomy_name' not in request.session and 'existing_taxonomy_name' not in request.session :
        messages.error(request, "Choose an activity before you proceed further")
        return HttpResponseRedirect("/AdvoCate/home/", {'user_name': user_name})
            
    if request.method == 'POST' and request.is_ajax():
        if request.FILES:
            testfile = request.FILES['testfile']
            copyfile(TRAINING_SAMPLES_IMAGES_LOCATION + testfile.name, TEST_DATA_LOCATION + testfile.name)
            request.session['current_test_file_name'] = testfile.name
            manageData = ManageRasterData()
            testFileAsArray = numpy.array(manageData.convert_raster_to_array(testfile.name))
            modelname = request.session['current_model_name']
            clf = joblib.load('%s%s' %(CLASSIFICATION_MODEL_LOCATION, modelname))
            predictedValue = clf.predict(testFileAsArray)
            request.session['current_predicted_file_name'] = testfile.name.split('.', 1)[0] + '.csv'
            savePredictedValues(request.session['current_predicted_file_name'], predictedValue)
            
            manageData.find_and_replace_data_in_csv_file("config.txt", request.session['current_predicted_file_name'], CLASSIFIED_DATA_LOCATION, request.session['current_predicted_file_name'], CLASSIFIED_DATA_IN_RGB_LOCATION)
            outputMap = testfile.name.split('.', 1)[0] + '.tif'
            columns, rows = manageData.create_raster_from_csv_file(request.session['current_predicted_file_name'], testfile.name, CLASSIFIED_DATA_IN_RGB_LOCATION, outputMap, OUTPUT_RASTER_FILE_LOCATION)
            request.session['current_test_file_columns'] = columns
            request.session['current_test_file_rows'] = rows
            outputmapinJPG = testfile.name.split('.', 1)[0] + '.jpeg'
            
            
            authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
            model_instance = Classificationmodel.objects.get(model_name=request.session['current_model_name'])
            si = SatelliteImage(name= request.session['current_test_file_name'], location = TEST_DATA_LOCATION, columns = request.session['current_test_file_columns'], rows = request.session['current_test_file_rows'])
            si.save()
            csi = ClassifiedSatelliteImage(name = outputmapinJPG, location = OUTPUT_RASTER_FILE_LOCATION)
            csi.save()
            tc = ClassificationActivity(model=model_instance, satellite_image_id = si, classified_satellite_image_id = csi, completed_by= authuser_instance)
            tc.save()
            exp_chain = ExplorationChain(id = request.session['exploration_chain_id'], step = request.session['exploration_chain_step'], activity = 'classification', activity_instance = tc.id)
            exp_chain.save()
            request.session['exploration_chain_step'] = request.session['exploration_chain_step']+1
            
            listofcategories = clf.classes_.tolist()
            
            
            if 'existing_taxonomy_name' in request.session:
                oldCategories = ['artificial_surface', 'cloud', 'forest', 'grassland', 'shadow', 'water']
                change_matrix = create_change_matrix(oldCategories, predictedValue, rows, columns)
            
            return  JsonResponse({'map': outputmapinJPG, 'categories': listofcategories});
    
    
    elif 'current_model_id' not in request.session:
        error = "Create a classification model before classifying an image"
        return render(request, 'supervised.html', {'user_name':user_name, 'error': error})
    else:
        return render (request, 'supervised.html', {'user_name':user_name})

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
    print len(list_of_new_categories)
    print list_of_new_categories
    print oldCategories
    change_in_individual_matrix = [[0 for a in range(len(list_of_new_categories))] for x in range(len(oldCategories))]
    print change_in_individual_matrix
    customQuery = CustomQueries()
    
    for index, category in enumerate(oldCategories):
        category_extension = customQuery.getExtension(category, '0', '1')
        for coordinates in category_extension:
            #print coordinates
            
            ind = coordinates[0]*columns + coordinates[1] #coordinates[0]==row no
            #print index
            new_category = newPredictedValues[ind]
            #print new_category
            #new_category_index = numpy.where(list_of_new_categories == new_category)
            new_category_index = list_of_new_categories.index(new_category)
            #print new_category_index
            change_in_individual_matrix[index][new_category_index] += 1
    print change_in_individual_matrix
    return change_in_individual_matrix
        
def calculate_J_index_for_catgeory_extension(ext1, ext2):
        common_elements_in_both_extensions = numpy.intersect1d(ext1, ext2)
        union_of_both_extensions = numpy.union1d(ext1, ext2)
        jaccard_index = float(len(common_elements_in_both_extensions)/len(union_of_both_extensions))
        return jaccard_index

@login_required
def changeRecognizer(request):
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
            return render(request, 'changerecognition.html', {'user_name':user_name, 'existing_taxonomyName': new_taxonomy, 'conceptsList':concepts_in_current_taxonomy, 'modelType': model_type, 'modelScore': model_accuracy, 'userAccuracies': user_accuracies, 'producerAccuracies': producer_accuracies})
   # else:
        
        
    return render (request, 'changerecognition.html', {'user_name':user_name})

def createChangeEventForNewTaxonomy(request):
    compositeChangeOperations = []
    firstOp, root_concept = get_addTaxonomy_op_details(request.session['new_taxonomy_name'])
    compositeChangeOperations.append(firstOp)
    

    trainingfile = TrainingSet(request.session['current_training_file_name'])
    concepts_in_current_taxonomy = list(numpy.unique(trainingfile.target))
    for concept in concepts_in_current_taxonomy:
        changeOperation = get_addConcept_op_details(request.session['new_taxonomy_name'], root_concept, concept)
        compositeChangeOperations.append(changeOperation)
        
    return JsonResponse({'listOfOperations': compositeChangeOperations});

def get_addTaxonomy_op_details(taxonomy_name):
    changeOperation = []
    compositeOp = "Add_Taxonomy ('" + taxonomy_name + "')"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Create taxonomy '" + taxonomy_name + "'")
    root_concept = "root_" + taxonomy_name.replace(" ", "_")
    compositeOp_details.append("Create root concept '" + root_concept + "'")
    compositeOp_details.append("Add '" + root_concept + "' to '" + taxonomy_name + "'")
    changeOperation.append(compositeOp_details)
    return changeOperation, root_concept
    
def get_addConcept_op_details(taxonomy_name,  parent_concept_name, concept_name):
    changeOperation = []
    compositeOp = "Add_Concept ('" + taxonomy_name + "', '" + concept_name + "', '" + parent_concept_name + "')"
    changeOperation.append(compositeOp)
    
    compositeOp_details = []
    compositeOp_details.append("Create concept '" + concept_name + "' (if it does not exists)")
    compositeOp_details.append("Add '" + concept_name + "' to '" + taxonomy_name + "'")
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

@transaction.atomic  
def applyChangeOperations(request):
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