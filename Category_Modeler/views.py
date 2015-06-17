from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.servers.basehttp import FileWrapper
from django.contrib import auth
from django.http import JsonResponse
import csv, json, numpy, struct
import gdal
from gdalconst import *
from io import FileIO, BufferedWriter
from Category_Modeler.models import Trainingset, NewTrainingsetCollectionActivity, ChangeTrainingSetActivity, AuthUser
import os, pickle
from datetime import datetime
from sklearn.naive_bayes import GaussianNB
from sklearn import tree, svm, cross_validation, metrics
from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib
import matplotlib.pyplot as plt

# Create your views here.

def register_view(request):
    if request.method == 'POST':
    # form = UserCreationForm(request.POST)
    # print form
    # if form.is_valid():
    #      print "it's fine"
    #      new_user = form.save()
    #      return HttpResponseRedirect("/AdvoCate/")
    # print "it's not"
    # return HttpResponseRedirect("/AdvoCate/")
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



def index(request):
    if '_auth_user_id' in request.session:
        user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username  # @UndefinedVariable
        print user_name
        return render(request, 'base.html', {'user_name': user_name})
    form = UserCreationForm()
    return render(request, 'base.html', {'form': form})


# The method allow user to upload the training data file, which is then saved on the server and displayed in a tabular format on the page
@login_required
def trainingsampleprocessing(request):
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username # @UndefinedVariable
     
    if request.method == 'POST' and request.is_ajax():
        if request.is_ajax():
            if request.FILES:
                trainingfile = request.FILES['trainingfile']
                request.session['current_training_file_name'] = trainingfile.name
                
                if trainingfile.name.split(".")[-1] == ".csv":
                    handle_uploaded_file(request, trainingfile)
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
                trainingfilelocation = (Trainingset.objects.get(trainingset_id=trid, trainingset_ver=ver)).location # @UndefinedVariable
                fp = file (trainingfilelocation+trainingfilename, 'rb')
                response = HttpResponse( fp, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="training File"'
                return response
        return HttpResponse("")
    else:
        if Trainingset.objects.exists(): # @UndefinedVariable
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
        
        #add training dataset details in trainingset table and a collection activity in new_trainingset_collection_activity table
        latestid = (Trainingset.objects.all().order_by("-trainingset_id")[0]).trainingset_id # @UndefinedVariable
        tr = Trainingset(trainingset_id=int(latestid)+1, trainingset_ver =1, name=request.session['current_training_file_name'], description=otherDetails, startdate=datetime.now(), enddate=datetime(9999, 9, 12), location="Category_Modeler/static/trainingfiles/")
        tr.save(force_insert=True)
        tr_activity = NewTrainingsetCollectionActivity( trainingset_id= int(latestid)+1, trainingset_ver =1, startdate = datetime.strptime(trainingstart, '%Y-%m-%d'), enddate= datetime.strptime(trainingend, '%Y-%m-%d'))
        tr_activity.save()
        request.session['current_training_file_id'] = int(latestid)+1
        request.session['current_training_file_ver'] = 1
    return HttpResponse("We got the data");


def saveNewTrainingVersion(request):
    if request.method=='POST':
        data = json.loads(request.body)
        filename= request.session['current_training_file_name']
        version = request.session['current_training_file_ver']
        id= request.session['current_training_file_id']
        newfilename = filename.split('.', 1)[0] + "_ver" + str(int(version)+1) + ".csv"
        f1 = open('Category_Modeler/static/trainingfiles/%s' % newfilename, 'w')
        writer = csv.writer(f1)
        for i in range(len(data)):
            writer.writerow(data[i])
        f1.close()
        
        oldversion = Trainingset.objects.get(trainingset_id=int(id), trainingset_ver =int(version)) # @UndefinedVariable
        oldversion.enddate = datetime.now()
        oldversion.save()
        tr = Trainingset(trainingset_id=id, trainingset_ver =int(version)+1, name=newfilename, startdate=datetime.now(), enddate=datetime(9999, 9, 12), location="Category_Modeler/static/trainingfiles/")
        tr.save(force_insert=True)
        tr_activity = ChangeTrainingSetActivity( oldtrainingset_id= id, oldtrainingset_ver =version, newtrainingset_id=id, newtrainingset_ver=int(version)+1)
        tr_activity.save()
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
    dataset = gdal.Open('Category_Modeler/static/data/%s' % f.name)
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    noOfBands = dataset.RasterCount
    bands = []
    
    final_array = []
    pixelValue=[]

    for i in range(1, noOfBands):
        bands.append(dataset.GetRasterBand(i).ReadAsArray(0,0,cols,rows))
    
    for j in range(rows):
        for k in range (cols):
            pixelValue.append(j)
            pixelValue.append(k)
            for l in range(len(bands)):
                pixelValue.append(bands[l][j][k])
            final_array.append(pixelValue)
            pixelValue=[]

    head = f.name.split('.', 1)[0]
    filename = head + '.csv'    
    with BufferedWriter( FileIO( 'Category_Modeler/static/trainingfiles/%s' % filename, "wb" ) ) as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow(['X', 'Y', 'band1', 'band2', 'band3', 'band4', 'band5', 'band6', 'band7'])
        for i in range(5000):
            spamwriter.writerow(final_array[i])
        csvfile.close();

@login_required
def signaturefile(request):
    user_name = (AuthUser.objects.get(id=request.session['_auth_user_id'])).username # @UndefinedVariable

    if 'current_training_file_name' not in request.session:
        return render (request, 'signaturefile.html', {'user_name':user_name})
    
    trainingfile = request.session['current_training_file_name']
    trainingFileAsArray = read_CSVFile(trainingfile)
    features = trainingFileAsArray[0]  
    
    if request.method=='POST' and 'current_training_file_name' in request.session:
        data = request.POST;
        
        classifiername = data['classifiertype']
        targetattribute = data['targetattribute']
        validationoption = data['validationoption']

        if (validationoption=='2'):   
            validationfile = request.FILES['validationfile']
        elif(validationoption=='3'):
            folds = data['fold']
        elif(validationoption=='4'):
            percentsplit = float(data['Percentage'])
            
        
        classifier = chooseClassifier(classifiername)
        targetAttributeIndex = features.index(targetattribute)
        
        trainingSampleDataWithTargetValues = createSampleArray(trainingFileAsArray, targetAttributeIndex)
        data_array=numpy.asarray(trainingSampleDataWithTargetValues[0], dtype=numpy.float)
        target_array=numpy.asarray(trainingSampleDataWithTargetValues[1], dtype=numpy.float)
        classifier.fit(data_array, target_array)
        print len(classifier.classes_)
        print len(classifier.theta_)
        print len(classifier.theta_[1])
        print len(classifier.sigma_)
        print len(classifier.sigma_[1])
        print classifier.sigma_[1]
       # model = Classificationmodel()
        modelname = "model_" + str(datetime.now())
        joblib.dump(classifier, 'Category_Modeler/static/signaturefile/%s'%modelname)
        request.session['current_signature_file']= modelname
        clf = joblib.load('Category_Modeler/static/signaturefile/%s' % (request.session['current_signature_file']))
        
        if (validationoption=='1'):
            y_pred= clf.predict(data_array)
            score= metrics.accuracy_score(target_array, y_pred)
            cm = confusion_matrix(target_array, y_pred)
            numpy.set_printoptions(precision=2)
            print('Confusion matrix')
            print(cm)
            plt.figure()
            plot_confusion_matrix(cm)
        elif (validationoption=='2'):
            print "test"
        elif (validationoption=='3'):
            scores=cross_validation.cross_val_score(clf, data_array, target_array, cv=int(folds))
            score = scores.mean()
            print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        else:
            x_train, x_test, y_train, y_test = cross_validation.train_test_split(data_array, target_array, test_size=percentsplit/100.0)
            clf.fit(x_train, y_train)
            score = clf.score(x_test, y_test)
            print score
        return JsonResponse({'attributes': features, 'user_name':user_name, 'score': score, 'listofclasses': json.dumps(clf.classes_.tolist()), 'meanvectors':json.dumps(clf.theta_.tolist())})
        
    else:
        return render (request, 'signaturefile.html', {'attributes': features, 'user_name':user_name})

def plot_confusion_matrix(cm, title='Confusion matrix', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

def read_CSVFile(f):
    with open('Category_Modeler/static/trainingfiles/%s' % f, 'rU') as datafile:
        data = csv.reader(datafile, delimiter=',', quoting=csv.QUOTE_NONE)
        samples = []
        for eachinstance in data:
            samples.append(eachinstance);
        datafile.close();    
    return samples

def chooseClassifier(classifiername):
    if classifiername=='NaiveBayes':
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
    newArray=[]
    for sample in trainingsample:
        targetValueArray.append(sample[targetAttributeIndex])
        sample.pop(targetAttributeIndex)
        trainingSampleArray.append(sample)
    newArray.append(trainingSampleArray)
    newArray.append(targetValueArray)
    return newArray

def supervised(request):
    return render (request, 'supervised.html')

def visualization(request):
    return render (request, 'visualization.html')