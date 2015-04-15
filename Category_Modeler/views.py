from django.shortcuts import render, HttpResponse
from django.core.servers.basehttp import FileWrapper
import csv, json, numpy, struct
import gdal
from gdalconst import *
from io import FileIO, BufferedWriter
import os


# Create your views here.

def index(request):
    return render(request, 'base.html')


# The method allow user to upload the training data file, which is then saved on the server and displayed in a tabular format on the page
def trainingsampleprocessing(request):
    if request.method == 'POST':
        if request.is_ajax():
            if request.FILES:
                trainingfile = request.FILES['trainingfile']
                request.session['current_training_file'] = trainingfile.name
                
                if trainingfile.name.split(".")[-1] == ".csv":
                    handle_uploaded_file(request, trainingfile)
                else:
                    print "I am here"
                    handle_raster_file(request, trainingfile)
                    fp = file("Category_Modeler/static/js/newfile.csv", 'rb')
                    wrapper = FileWrapper(fp)
                    response = HttpResponse( wrapper, content_type='text/plain')
                    response['Content-Disposition'] = 'attachment; filename="training File"'
                    return response
        return HttpResponse("")
    else:
        return render(request, 'trainingsample.html')


def savetrainingdatadetails(request):
    if request.method=='POST':
        data = request.POST;
        researcherName = data['FieldResearcherName'];
        trainingstart = data['TrainingTimePeriodStartDate'];
        trainingend = data['TrainingTimePeriodEndDate'];
        location = data['TrainingLocation'];
        otherDetails = data['OtherDeatils'];
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

def handle_raster_file(request, f):
    dataset = gdal.Open('Category_Modeler/static/data/%s' % f.name)
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    print cols, rows
    noOfBands = dataset.RasterCount
    print noOfBands
    bands = []
    
    final_array = []
    print "I am at first place"
    for i in range(1, noOfBands):
        bands.append(dataset.GetRasterBand(i).ReadAsArray(0,0,cols,rows))
    print bands[2][1][2]
    for j in range(rows):
        for k in range (cols):
            pixelValue = "\'"  + `j` + "\'" + ", " + "\'" + `k` + "\'" 
            for l in range(len(bands)):
                pixelValue = pixelValue +  ", " + "\'" + `bands[l][j][k]` + "\'"
            final_array.append(pixelValue)
            
    print final_array[0]
    print "I am at second place"
    
    with BufferedWriter( FileIO( 'Category_Modeler/static/js/newfile.csv', "wb" ) ) as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow(['X', 'Y', 'band1', 'band2', 'band3', 'band4', 'band5', 'band6', 'band7'])
        for i in range(1000):
            print (final_array[i])
            spamwriter.writerow(final_array[i])
            #csvfile.write(final_array[i] + '\n')
        csvfile.close();
        print "i am done"
        
#
def read_CSVFile(f):
    with open('Category_Modeler/static/uploaded_files/%s' % f, 'rU') as datafile:
        data = csv.reader(datafile, delimiter=',', quoting=csv.QUOTE_NONE)
        samples = []
        for eachinstance in data:
            samples.append(eachinstance);
        datafile.close();    
    return samples

def signaturefile(request):
    
    return render (request, 'signaturefile.html')

def supervised(request):
    return render (request, 'supervised.html')

def visualization(request):
    return render (request, 'visualization.html')
