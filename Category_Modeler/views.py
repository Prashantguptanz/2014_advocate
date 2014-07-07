from django.shortcuts import render
import csv



# Create your views here.

def index(request):
    return render(request, 'base.html')

def preprocess(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES['file'])
        name = request.FILES['file'].name
        datafile = read_CSVFile(name)
        attributes = datafile[0]
        datafile.pop(0)
        
        request.session['current_trainingfile'] = name
        return render(request, 'preprocess.html', {'filename':name , 'csvfile': datafile, 'attributes':attributes})
    else:
        return render(request, 'preprocess.html')
    
def handle_uploaded_file(f):
    with open('Category_Modeler/static/uploaded_files/%s' % f.name, 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
        dest.close();

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

