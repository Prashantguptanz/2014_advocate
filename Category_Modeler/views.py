from django.shortcuts import render, HttpResponse
import csv, json
from io import FileIO, BufferedWriter


# Create your views here.

def index(request):
    return render(request, 'base.html')


# The method allow user to upload the training data file, which is then saved on the server and displayed in a tabular format on the page
def preprocess(request):
    if request.method == 'POST':
        if request.is_ajax():
            a = request.POST;
            print a;
            if request.FILES:
                trainingfile = request.FILES['trainingfile']
                print trainingfile;
                handle_uploaded_file(request, trainingfile);
            else:
                data = json.loads(request.body)
                f1 = open('Category_Modeler/static/js/training_ver.csv', 'w')
                writer = csv.writer(f1)
                for i in range(len(data)):
                    writer.writerow(data[i])
                f1.close()
        return HttpResponse("")
    else:
        return render(request, 'preprocess.html')


def savetrainingdatadetails(request):
    if request.method=='POST':
        data = request.POST;
        researcherName = data['FieldResearcherName'];
        trainingstart = data['TrainingTimePeriodStartDate'];
        trainingend = data['TrainingTimePeriodEndDate'];
        location = data['TrainingLocation'];
        otherDetails = data['OtherDeatils'];
       # print data.values();
    return HttpResponse("We got the data");

def saveNewTrainingVersion(request):
    if request.method=='POST':
        data = json.loads(request.body)
        f1 = open('Category_Modeler/static/js/training_ver.csv', 'w')
        writer = csv.writer(f1)
        for i in range(len(data)):
            writer.writerow(data[i])
        f1.close()
    return HttpResponse("Changed dataset is saved as a new version");
        
# create a file with similar name as provided in the static folder and copy all the contents    
def handle_uploaded_file(request, f):
    with BufferedWriter( FileIO( 'Category_Modeler/static/js/%s' % f, "wb" ) ) as dest:
        foo = f.read(1024)  
        while foo:
            dest.write(foo)
            foo = f.read(1024)
        dest.close();

#
def read_CSVFile(f):
    with open('Category_Modeler/static/uploaded_files/%s' % f, 'rU') as datafile:
        data = csv.reader(datafile, delimiter=',', quoting=csv.QUOTE_NONE)
        samples = []
        for eachinstance in data:
            samples.append(eachinstance);
        datafile.close();    
    return samples

def supervised(request):
    return render (request, 'supervised.html')

