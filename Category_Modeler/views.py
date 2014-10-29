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
            file = request.FILES['trainingfile']
            print(file)
            handle_uploaded_file(request, file);
            
       # handle_uploaded_file(request.FILES['file'])
   #     handle_uploaded_file(request.POST.get('FileName'))
   #     name = request.POST.get('FileName')
       # name = request.FILES['file'].name
   #     print(name)
   #     datafile = read_CSVFile(name)
   #     attributes = datafile[0]
   #     datafile.pop(0)
        

        # return render(request, 'preprocess.html', {'filename':name , 'csvfile': datafile, 'attributes':attributes})
    #    return HttpResponse(json.dumps(response_data), content_type="application/json")
        return HttpResponse("it's gud")
    else:
        return render(request, 'preprocess.html')


# create a file with similar name as provided in the static folder and copy all the contents    
def handle_uploaded_file(request, f):
    #with open('Category_Modeler/static/uploaded_files/%s' % f, 'wb+') as dest:
    with BufferedWriter( FileIO( 'Category_Modeler/static/js/%s' % f, "wb" ) ) as dest:
        foo = f.read(1024)
        print(foo)
        while foo:
            dest.write(foo)
            foo = f.read(1024)
 #       for chunk in f.chunks():
  #          dest.write(chunk)
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

def modeler(f):
    return 

