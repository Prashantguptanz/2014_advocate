from django.shortcuts import render, HttpResponse
import csv, json, numpy, struct
import gdal
from gdalconst import *
from io import FileIO, BufferedWriter


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
                    handle_uploaded_file(request, trainingfile);
                else:
                    dataset = gdal.Open('Category_Modeler/static/data/%s' % trainingfile.name)
                    cols = dataset.RasterXSize
                    rows = dataset.RasterYSize
                    print cols, rows
                    noOfBands = dataset.RasterCount
                    bands = {}
                    a=0
                    final_array = {}
                    print "I am at first place"
                    for i in range(1, noOfBands):
                        bands[i] = dataset.GetRasterBand(i).ReadAsArray(0,0,cols,rows)
                    for j in range(rows):
                        for k in range (cols):
                            pixelValue = `j` + " " + `k` + " "
                            for l in range(1, noOfBands):
                                final_array[a] = pixelValue + `bands[l][j][k]` + " "
                                a= a+1
                    print final_array
                    print "I am at second place"
                    
            #        with BufferedWriter( FileIO( 'Category_Modeler/static/js/newfile.csv', "wb" ) ) as dest:
            #            dest.write("x y band1 band2 band3 band4 band5 band6 band7 band8")
            #            for i in range(100):
            #                #print (final_array[i])
            #                dest.write(final_array[i])
            #            dest.close();
            #            print "i am done"
                    
                     
                
            #test code to check if GDAL can be used to read raster data    
            #dataset = gdal.Open('Category_Modeler/static/com74085cc1/hdr.adf')
            #dataset = gdal.Open('Category_Modeler/static/data/akl.tif')
            #cols = dataset.RasterXSize
            #rows = dataset.RasterYSize
            #print cols, rows
            #count = dataset.RasterCount
            #print count
            #band = dataset.GetRasterBand(2)
            #print band
            #bandtype = gdal.GetDataTypeName(band.DataType)
            #print bandtype
            #scanline = band.ReadRaster(0, 0, band.XSize, 1, band.XSize, 1, band.DataType)
            #print scanline
            #data = band.ReadAsArray(0,0,cols,rows)
            #print data
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
    dataset = gdal.Open(f)
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    noOfBands = dataset.RasterCount
    bands = {}
    
    for i in range(1, noOfBands):
        bands[i] = dataset.GetRasterBand(i).ReadAsArray(0,0,cols,rows)
    for j in range(rows):
        for k in range (cols):
            pixelValue = `j` + " " + `k` + ""
            for l in range(1, noOfBands):
                pixelValue = pixelValue + `bands[l][j][k]` + " "
            print pixelValue
    
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
