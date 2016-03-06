from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib import messages
from django.http import JsonResponse
import csv, json, numpy
import gdal
from gdalconst import *
from io import FileIO, BufferedWriter
from Category_Modeler.models import Trainingset, TrainingsetCollectionActivity, ChangeTrainingsetActivity, AuthUser, Classificationmodel, Classifier, LearningActivity, Confusionmatrix
import os, pickle
from datetime import datetime
from sklearn.naive_bayes import GaussianNB
from sklearn import tree, svm, cross_validation, metrics
from sklearn.externals import joblib
from sklearn.covariance import EmpiricalCovariance, MinCovDet
from sklearn.externals.six import StringIO
import matplotlib.pyplot as plt
import pydot
from Category_Modeler.measuring_categories import DecisionTreeIntensionalModel


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


# Methods for home page to define the task and save details in session variable

def index(request):
    if '_auth_user_id' in request.session:
        user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username  # @UndefinedVariable
        return render(request, 'home.html', {'user_name': user_name})
    form = UserCreationForm()
    print request.session['_auth_user_id']
    return render(request, 'home.html', {'form': form})

def saveexistingtaxonomydetails(request):
    if request.method == 'POST':
        data = request.POST
        request.session['existing_taxonomy_name'] = data['existingtaxonomies'];
        request.session['external_trigger'] = data['externaltriggers']
    return HttpResponse("Upload new training samples or choose an existing one, and start the exploration process!");

def savenewtaxonomydetails(request):
    if request.method == 'POST':
        data = request.POST
        request.session['new_taxonomy_name'] = data['newtaxonomyname']
        request.session['new_taxonomy_description'] = data['description']
    return HttpResponse("Upload training samples by switching to 'Training Samples' tab, and start the modelling process!");



# The method allow user to upload the training data file, which is then saved on the server and displayed in a tabular format on the page

@login_required
def trainingsampleprocessing(request):
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username 
    print request.session['new_taxonomy_name']
    print request.session['new_taxonomy_description']
    
    if request.method == 'POST' and request.is_ajax():
        if request.FILES:
            trainingfile = request.FILES['trainingfile']
            request.session['current_training_file_name'] = trainingfile.name.split('.', 1)[0] + '.csv'
            if trainingfile.name.split(".")[-1] == "csv":
                handle_uploaded_file(request, trainingfile)
                return HttpResponse("We got the file");
            else:
                handle_raster_file(request, trainingfile)
                filename = trainingfile.name.split('.', 1)[0] + '.csv'
                fp = file("Category_Modeler/static/trainingfiles/%s" % filename, 'rb')
                response = HttpResponse( fp, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="training File"'
                return response
        else:
            data = request.POST
            trainingfilepkey = data['1']
            trid, ver = trainingfilepkey.split('+')
            request.session['current_training_file_id'] = trid
            request.session['current_training_file_ver'] = ver
            trainingfilename = data['2']
            request.session['current_training_file_name'] = trainingfilename
            print trid, ver
            trainingfilelocation = (Trainingset.objects.get(trainingset_id=trid, trainingset_ver=ver)).filelocation # @UndefinedVariable
            fp = file (trainingfilelocation+trainingfilename, 'rb')
            response = HttpResponse( fp, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="training File"'
            return response

    else:
        if 'new_taxonomy_name' not in request.session and 'existing_taxonomy_name' not in request.session :
            messages.error(request, "Choose an activity before you proceed further")
            return HttpResponseRedirect("/AdvoCate/home/", {'user_name': user_name})
        elif Trainingset.objects.exists(): # @UndefinedVariable
            training_set_list = Trainingset.objects.all()  # @UndefinedVariable
            return render(request, 'trainingsample.html', {'training_set_list':training_set_list, 'user_name': user_name})
        else:
            return render(request, 'trainingsample.html', {'user_name': user_name})


def savetrainingdatadetails(request):
    if request.method=='POST':
        data = request.POST;
        researcherName = data['FieldResearcherName'];
        trainingstart = data['TrainingTimePeriodStartDate'];
        trainingend = data['TrainingTimePeriodEndDate'];
        location = data['TrainingLocation'];
        otherDetails = data['OtherDetails'];
        
        #add training dataset details in trainingset table and a collection activity in trainingset_collection_activity table
        latestidarray = Trainingset.objects.all().order_by("-trainingset_id")
        if not latestidarray:
            latestid = 0
        else:
            latestid = latestidarray[0].trainingset_id
            
        tr = Trainingset(trainingset_id=int(latestid)+1, trainingset_ver =1, trainingset_name=request.session['current_training_file_name'], description=otherDetails, date_expired=datetime(9999, 9, 12), filelocation="Category_Modeler/static/trainingfiles/")
        tr.save(force_insert=True)
        tr_activity = TrainingsetCollectionActivity( trainingset_id= int(latestid)+1, trainingset_ver =1, date_started = datetime.strptime(trainingstart, '%Y-%m-%d'), date_finished= datetime.strptime(trainingend, '%Y-%m-%d'), trainingset_location=location, collector=researcherName, description= otherDetails)
        tr_activity.save()
        request.session['current_training_file_id'] = int(latestid)+1
        request.session['current_training_file_ver'] = 1
    return HttpResponse("We got the data");


def saveNewTrainingVersion(request):
    if request.method=='POST':
        data = json.loads(request.body)
        filename= request.session['current_training_file_name']
        version = request.session['current_training_file_ver']
        fileid= request.session['current_training_file_id']
        newfilename = (filename.split('.')[0]).split('_')[0] + "_ver" + str(int(version)+1) + ".csv"
        f1 = open('Category_Modeler/static/trainingfiles/%s' % newfilename, 'w')
        writer = csv.writer(f1)
        for i in range(len(data)):
            writer.writerow(data[i])
        f1.close()
        
        oldversion = Trainingset.objects.get(trainingset_id=int(fileid), trainingset_ver =int(version)) 
        oldversion.date_expired = datetime.now()
        oldversion.save()
        tr = Trainingset(trainingset_id=int(fileid), trainingset_ver =int(version)+1, trainingset_name=newfilename, date_expired=datetime(9999, 9, 12), filelocation="Category_Modeler/static/trainingfiles/")
        tr.save(force_insert=True)
        authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
        tr_activity = ChangeTrainingsetActivity( oldtrainingset_id= int(fileid), oldtrainingset_ver =int(version), newtrainingset_id=int(fileid), newtrainingset_ver=int(version)+1, completed_by=authuser_instance)
        tr_activity.save()
        request.session['current_training_file_name'] = newfilename
        request.session['current_training_file_ver'] = int(version)+1
        
    return HttpResponse("Changed dataset is saved as a new version");
        
# create a file with similar name as provided in the static folder and copy all the contents    
def handle_uploaded_file(request, f):
    with BufferedWriter( FileIO( 'Category_Modeler/static/trainingfiles/%s' % f, "wb" ) ) as dest:
        foo = f.read(1024)  
        while foo:
            dest.write(foo)
            foo = f.read(1024)
        dest.close();

def handle_raster_file(request, f):
    print f.name
    dataset = gdal.Open('Category_Modeler/static/data/%s' % f.name, GA_ReadOnly)
    print dataset
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    noOfBands = dataset.RasterCount
    print noOfBands
    geotransform = dataset.GetGeoTransform()
    print geotransform[0]
    print geotransform[1]
    print geotransform[2]
    print geotransform[3]
    print geotransform[4]
    print geotransform[5]
    bands = []
    
    final_array = []
    pixelValue=[]

    for i in range(1, noOfBands+1):
        bands.append(dataset.GetRasterBand(i).ReadAsArray(0,0,cols,rows))
    
    for j in range(rows):
        for k in range (cols):
            pixelValue.append(j)
            pixelValue.append(k)
            for l in range(noOfBands):
                
                pixelValue.append(bands[l][j][k])
            final_array.append(pixelValue)
            pixelValue=[]

    head = f.name.split('.', 1)[0] 
    filename = head + '.csv'    
    with BufferedWriter( FileIO( 'Category_Modeler/static/trainingfiles/%s' % filename, "wb" ) ) as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow(['X', 'Y', 'band1', 'band2', 'band3', 'band4', 'band5', 'band6', 'band7', 'band8'])
        for i in range(len(final_array)):
            spamwriter.writerow(final_array[i])
        csvfile.close();




@login_required
def signaturefile(request):
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username # @UndefinedVariable
    print request.session['current_training_file_name']
    
    if 'new_taxonomy_name' not in request.session and 'existing_taxonomy_name' not in request.session :
        messages.error(request, "Choose an activity before you proceed further")
        return HttpResponseRedirect("/AdvoCate/home/", {'user_name': user_name})
    
    if 'current_training_file_name' not in request.session:
        return render (request, 'signaturefile.html', {'user_name':user_name})
    
    trainingfile = request.session['current_training_file_name']
    print trainingfile
    trainingFileAsArray = read_training_File_as_array(trainingfile)
    features = trainingFileAsArray[0]
    if request.method=='POST':
        data = request.POST;
        
        classifiername = data['classifiertype']
        targetattribute = data['targetattribute']
        validationoption = data['validationoption']
        
        if (validationoption=='1'):
            validationtype="training data"  
        elif (validationoption=='2'):   
            validationfile = request.FILES['validationfile']
            validationtype = "validation data"
        elif(validationoption=='3'):
            folds = data['fold']
            validationtype = "cross validation"
        elif(validationoption=='4'):
            percentsplit = float(data['Percentage'])
            validationtype = "train test split"
            
        
        classifier = chooseClassifier(classifiername)
        targetAttributeIndex = features.index(targetattribute)
        
        trainingSampleArray, targetValueArray = createSampleArray(trainingFileAsArray, targetAttributeIndex)
        print trainingSampleArray
        data_array=numpy.array(trainingSampleArray, dtype=numpy.float32)
        target_array=numpy.array(targetValueArray)
        modelname = "model_" + str(datetime.now())
        authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
       
     #   clf = joblib.load('Category_Modeler/static/signaturefile/%s' % (request.session['current_signature_file']))
        
        if (validationoption=='1'):
            clf = classifier.fit(data_array, target_array)
            y_pred= clf.predict(data_array)
            score= "{0:.2f}".format(metrics.accuracy_score(target_array, y_pred))
            cm = metrics.confusion_matrix(target_array, y_pred)
            kp = "{0:.2f}".format(calculateKappa(cm))
                      
        elif (validationoption=='2'):
            print "test"
            
        elif (validationoption=='3'):
            skf = cross_validation.KFold(len(target_array), n_folds=int(folds))
            print skf
            cm=[]
            count =0
            for train_index, test_index in skf:
                X_train, X_test = data_array[train_index], data_array[test_index]
                y_train, y_test = target_array[train_index], target_array[test_index]
                clf=classifier.fit(X_train, y_train)
                y_pred = clf.predict(X_test)
                individual_cm = metrics.confusion_matrix(y_test, y_pred)
                if (count==0):
                    count +=1
                    cm = individual_cm
                else:
                    if (individual_cm.shape == cm.shape):
                        cm += individual_cm
    
            scores=cross_validation.cross_val_score(clf, data_array, target_array, cv=int(folds))
            score = "{0:.2f}".format(scores.mean())
            kp = "{0:.2f}".format(calculateKappa(cm))
            
        else:
            x_train, x_test, y_train, y_test = cross_validation.train_test_split(data_array, target_array, test_size=percentsplit/100.0)
            clf=classifier.fit(x_train, y_train)
            score = "{0:.2f}".format(clf.score(x_test, y_test))
            y_pred = clf.predict(x_test)
            cm = metrics.confusion_matrix(y_test, y_pred)
            kp = "{0:.2f}".format(calculateKappa(cm))
            robust_cov = MinCovDet().fit(x_train, y_train)
            emp_cov = EmpiricalCovariance().fit(x_train, y_train)
            print x_train
            covariance = numpy.cov(x_train.T, bias=1)
            print covariance
            print robust_cov.covariance_
            print emp_cov.covariance_
            

        prodacc, useracc = calculateAccuracies(cm) 
        joblib.dump(clf, 'Category_Modeler/static/classificationmodel/%s' %modelname)
        request.session['current_signature_file']= modelname
        authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
        sf = Classificationmodel(model_name = modelname, model_location="Category_Modeler/static/classificationmodel/", accuracy=score)
        sf.save()
        numpy.set_printoptions(precision=2)
        plt.figure()
        plot_confusion_matrix(cm, targetValueArray)
        cmname = modelname+"_cm.png"
        plt.savefig("Category_Modeler/static/images/%s" % cmname,  bbox_inches='tight')
        conf_matrix = Confusionmatrix(confusionmatrix_name = cmname, confusionmatrix_location="Category_Modeler/static/images/")
        conf_matrix.save()
        classifier_instance = Classifier.objects.get(classifier_name=classifiername)
        signaturefile_instance = Classificationmodel.objects.get(model_name=request.session['current_signature_file'])
        confusionmatrix_instance = Confusionmatrix.objects.get(confusionmatrix_name=cmname)
        tc = LearningActivity(classifier=classifier_instance, model= signaturefile_instance, validation = validationtype, validation_score= score, confusionmatrix=confusionmatrix_instance, completed_by= authuser_instance)
        tc.save()    
        
        
        if (classifiername=="Naive Bayes"):
            return JsonResponse({'attributes': features, 'user_name':user_name, 'score': score, 'listofclasses': clf.classes_.tolist(), 'meanvectors':clf.theta_.tolist(), 'variance':clf.sigma_.tolist(), 'kappa':kp, 'cm': cmname, 'prodacc': prodacc, 'useracc': useracc})
        elif (classifiername=="C4.5"):
          #  print clf.tree_.__getstate__()
           # print clf.tree_.children_left
           # print clf.tree_.children_right
           # print clf.tree_.feature
           # print clf.tree_.threshold
           # print clf.tree_.value
            newModel = DecisionTreeIntensionalModel(clf)
            dot_data = StringIO()
            tree.export_graphviz(clf, out_file=dot_data)
            graph = pydot.graph_from_dot_data(dot_data.getvalue())
            tree_name = modelname + "_tree.png"
            graph.write_png('Category_Modeler/static/images/%s'%tree_name)
            return JsonResponse({'attributes': features, 'user_name':user_name, 'score': score, 'listofclasses': clf.classes_.tolist(), 'kappa':kp, 'cm': cmname, 'tree':tree_name, 'prodacc': prodacc, 'useracc': useracc})
        else:
            return ""   
    else:
        return render (request, 'signaturefile.html', {'attributes': features, 'user_name':user_name})

def plot_confusion_matrix(cm, targetValueArray, title='Confusion matrix', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    target_values = numpy.unique(targetValueArray)
    tick_marks = numpy.arange(len(target_values))
    plt.xticks(tick_marks, target_values, rotation=45)
    plt.yticks(tick_marks, target_values)   
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

def read_training_File_as_array(f):
    with open('Category_Modeler/static/trainingfiles/%s' % f, 'rU') as datafile:
        dataReader = csv.reader(datafile, delimiter=',', quoting=csv.QUOTE_NONE)
        samples = list(dataReader)
        datafile.close();
    return samples

def read_test_file_as_array(f):
    with open('Category_Modeler/static/testfiles/%s' % f, 'rU') as datafile:
        dataReader = csv.reader(datafile, delimiter=',', quoting=csv.QUOTE_NONE)
        samples = list(dataReader)
        print samples[0]
        #print samples.shape
        datafile.close();
    return samples

def chooseClassifier(classifiername):
    if classifiername=='Naive Bayes':
        clf= GaussianNB()
        
    elif classifiername=='C4.5':
        clf=tree.DecisionTreeClassifier()
    else:
        clf = svm.SVC()
    return clf

def createSampleArray(trainingsample, targetAttributeIndex):
    trainingsample.pop(0)
    trainingSampleArray = []
    targetValueArray = []
    for sample in trainingsample:
        targetValueArray.append(sample[targetAttributeIndex])
        sample.pop(targetAttributeIndex)
        del sample[0:2]
        trainingSampleArray.append(sample)
    #print targetValueArray
 #   distinct_values = list(set(targetValueArray))
 #   print distinct_values
 #   for i in range(len(targetValueArray)):
 #       targetValueArray[i] = distinct_values.index(targetValueArray[i])
    #print targetValueArray
    return trainingSampleArray, targetValueArray


    

def calculateSumOfRows(confusionMatrix):
    sumRows = []
    for i, row in enumerate(confusionMatrix):
        for j,column in enumerate(row):
            if i<=len(sumRows)-1:
                b=sumRows.pop(i)
                sumRows.insert(i, (column+b))
            else:
                sumRows.insert(i, column)
    return sumRows

def calculateSumOfColumns(confusionMatrix):
    sumColumns = []
    for i, row in enumerate(confusionMatrix):
        for j,column in enumerate(row):
            if j<=len(sumColumns)-1:
                a=sumColumns.pop(j)
                sumColumns.insert(j, (column+a))
            else:
                sumColumns.insert(j, column)
    return sumColumns
                                
def calculateKappa(confusionMatrix):
    # confusionMatrix = check_arrays(confusionMatrix)
    sumRows = calculateSumOfRows(confusionMatrix)
    sumColumns = calculateSumOfColumns(confusionMatrix)
    sumOfWeights=0
    for weight in sumRows:
        sumOfWeights +=weight
    
    correct=float(0)
    chanceAgreement=float(0)
    for i,row in enumerate(confusionMatrix):
        chanceAgreement += (sumRows[i] * sumColumns[i])
        correct += row[i]
    chanceAgreement /= (sumOfWeights * sumOfWeights)
    correct /= sumOfWeights
    print (correct-chanceAgreement)/(1-chanceAgreement)
    if chanceAgreement<1:
        return (correct-chanceAgreement)/(1-chanceAgreement)
    else:
        return 1

def calculateAccuracies(confusionMatrix):
    sumRows = calculateSumOfRows(confusionMatrix)
    sumColumns = calculateSumOfColumns(confusionMatrix)
    print sumRows
    print sumColumns
    print confusionMatrix
    producersAccuracy=[]
    usersAccuracy = []
    for i, row in enumerate(confusionMatrix):
        producersAccuracy.insert(i, "{0:.2f}".format(float(row[i])/(float(sumColumns[i]))))
        usersAccuracy.insert(i, "{0:.2f}".format(float(row[i])/(float(sumRows[i]))))
        
    return producersAccuracy, usersAccuracy

@login_required
def supervised(request):
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username
    print request.session['current_signature_file']
    
    if request.method == 'POST' and request.is_ajax():
        if request.FILES:
            testfile = request.FILES['testfile']
            request.session['current_test_file_name'] = testfile
            print testfile
            
            testFileAsArray = read_test_file_as_array(testfile)
            print testFileAsArray[0]
            test_array=numpy.array(testFileAsArray, dtype=numpy.float32)
            modelname = request.session['current_signature_file']
            clf = joblib.load('Category_Modeler/static/classificationmodel/%s' %modelname)
            predictedValue = clf.predict(test_array)
            savePredictedValues(testfile, predictedValue)
            
            #print predictedValue.shape
            return HttpResponse("done");
    
    
    if Classificationmodel.objects.exists(): # @UndefinedVariable
        classificationmodel_list = Classificationmodel.objects.all()  # @UndefinedVariable
    return render (request, 'supervised.html', {'user_name':user_name, 'classification_models': classificationmodel_list})

def savePredictedValues(filename, predictedValue):
    with BufferedWriter( FileIO( 'Category_Modeler/static/predictedvalues/%s' % filename, "wb" ) ) as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        for i in range(len(predictedValue)):
            spamwriter.writerow(predictedValue[i])
    csvfile.close();


def visualization(request):
    return render (request, 'visualization.html')