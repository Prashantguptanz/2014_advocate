from Category_Modeler.models import Trainingset, TrainingsetCollectionActivity, ChangeTrainingsetActivity, AuthUser, Classificationmodel, Classifier, LearningActivity 
from Category_Modeler.models import Confusionmatrix, ExplorationChain, ClassificationActivity, Concept, Legend, LegendConceptCombination, ComputationalIntension
from Category_Modeler.models import Extension, Category, HierarchicalRelationship, HorizontalRelationship, MeanVector, CovarianceMatrix, ChangeEvent, ChangeEventOperations
from Category_Modeler.models import CreateLegendOperation, CreateConceptOperation, AddConceptToALegendOperation
from datetime import datetime
import numpy
from django.db import transaction, connection

class UpdateDatabase:
    
    def __init__(self, request):
        self.authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
        self.request = request
        if 'new_taxonomy_name' not in self.request.session:
            self.current_taxonomy = self.request.session['existing_taxonomy_name']
        else:
            self.current_taxonomy = self.request.session['new_taxonomy_name']
        self.change_event = self.__create_change_event()
    
    def __create_change_event(self):
        exp_chain = self.request.session['exploration_chain_id']
        change_event = ChangeEvent(exploration_chain_id = exp_chain, created_by= self.authuser_instance)
        change_event.save()
        return change_event
    
    def create_legend(self):
        if Legend.objects.all().exists():
            legendId = Legend.objects.latest("legend_id").legend_id +1
        else:
            legendId =0
        model_instance = Classificationmodel.objects.get(id = int(self.request.session['current_model_id']))
        legend = Legend(legend_id = legendId, legend_ver = 1, legend_name= self.current_taxonomy, date_expired = datetime(9999, 9, 12), description = self.request.session['new_taxonomy_description'], created_by = self.authuser_instance, model = model_instance, change_event_id = self.change_event)
        legend.save()
        createLegend = CreateLegendOperation(legend_name = legend.legend_name, legend_id = legend.legend_id, legend_ver = legend.legend_ver)
        createLegend.save()
        newOperationForChangeEvent = ChangeEventOperations(change_event_id = self.change_event, change_operation_id = createLegend.id, change_operation='create_legend_operation')
        newOperationForChangeEvent.save()
        self.__create_root_concept(legendId, 1)
    
    def __create_root_concept(self, legendId, legendVer):
        details = "Root concept to legend " + self.current_taxonomy
        root_concept = Concept(concept_name = "root_"+self.current_taxonomy, description = details, date_expired = datetime(9999, 9, 12), created_by = self.authuser_instance, change_event_id = self.change_event)
        root_concept.save()
        createConcept = CreateConceptOperation(concept_name = root_concept.concept_name)
        createConcept.save()
        newOperationForChangeEvent = ChangeEventOperations(change_event_id = self.change_event, change_operation_id = createConcept.id, change_operation='create_concept_operation')
        newOperationForChangeEvent.save()
        connectToLegend = LegendConceptCombination(legend_id = legendId, legend_ver = legendVer, concept = root_concept, change_event_id = self.change_event)
        connectToLegend.save()
        conceptLegendCombination = AddConceptToALegendOperation(legend_concept_combination_id = connectToLegend)
        conceptLegendCombination.save()
        newOperationForChangeEvent = ChangeEventOperations(change_event_id = self.change_event, change_operation_id = conceptLegendCombination.id, change_operation='add_concept_to_a_legend_operation')
        newOperationForChangeEvent.save()
    
       
    def create_concept(self, conceptName, mean_vector, covariance_matrix, extension, parentName="", details=""):
        current_concept = Concept(concept_name = conceptName, description = details, date_expired = datetime(9999, 9, 12), created_by = self.authuser_instance, change_event_id = self.change_event)
        current_concept.save()
        createConcept = CreateConceptOperation(concept_name = conceptName)
        createConcept.save()
        newOperationForChangeEvent = ChangeEventOperations(change_event_id = self.change_event, change_operation_id = createConcept.id, change_operation='create_concept_operation')
        newOperationForChangeEvent.save()
        legend = Legend.objects.get(legend_name =self.current_taxonomy)
        connectToLegend = LegendConceptCombination(legend_id = legend.legend_id, legend_ver = legend.legend_ver, concept = current_concept, change_event_id = self.change_event)
        connectToLegend.save()
        conceptLegendCombination = AddConceptToALegendOperation(legend_concept_combination_id = connectToLegend)
        conceptLegendCombination.save()
        newOperationForChangeEvent = ChangeEventOperations(change_event_id = self.change_event, change_operation_id = conceptLegendCombination.id, change_operation='add_concept_to_a_legend_operation')
        newOperationForChangeEvent.save()
        if parentName == "":
            parentName = "root_"+self.current_taxonomy
        parent_concept_connection_to_legend = LegendConceptCombination.objects.get(concept__concept_name = parentName,  legend_id = legend.legend_id, legend_ver = legend.legend_ver)
        addRelationship = HierarchicalRelationship(relationship_name='parent-of', expired=False, concept1 =  parent_concept_connection_to_legend, concept2 = connectToLegend)
        addRelationship.save()
        extension_id = self.create_extension(extension)
        cov_mat_id = self.create_covariance_matrix(covariance_matrix)
        vector_id = self.create_mean_vector(mean_vector)
        comp_int = self.create_computational_intension(vector_id, cov_mat_id)
        self.create_categories(connectToLegend, comp_int, extension_id)
        
        
    def create_categories(self, legend_concept_id, comp_int_id, ext_id):
        if Category.objects.all().exists():
            CId = Category.objects.latest("category_id").category_id + 1
        else:
            CId =0
        cat = Category(category_id = CId, category_ver=1, date_expired= datetime(9999, 9, 12), trainingset_id= self.request.session['current_training_file_id'], trainingset_ver=self.request.session['current_training_file_ver'], creator= self.authuser_instance, legend_concept_combination_id = legend_concept_id, computational_intension_id= comp_int_id, extension_id= ext_id, change_event_id = self.change_event)
        
        cat.save(force_insert=True)
            
    
    def create_extension(self, extension):
        if Extension.objects.all().exists():
            Extensionid = Extension.objects.latest("id").id + 1
        else:
            Extensionid =0
        ext = [Extension(id = Extensionid, x = row[0], y=row[1]) for row in extension]
        Extension.objects.bulk_create(ext)
        return Extensionid
        
    def create_mean_vector(self, mean_vector):
        
        if len(mean_vector)==3:
            meanVector = MeanVector(band1 = mean_vector[0], band2 = mean_vector[1], band3 = mean_vector[2])
        else:
            meanVector = MeanVector(band1 = mean_vector[0], band2 = mean_vector[1], band3 = mean_vector[2], band4 = mean_vector[3], band5 = mean_vector[4], band6 = mean_vector[5], band7 = mean_vector[6], band8 = mean_vector[7])
        meanVector.save()
        return meanVector.id
    
    def create_covariance_matrix(self, covariance_matrix):
        if CovarianceMatrix.objects.all().exists():
            CM_id = CovarianceMatrix.objects.latest("covariance_matrix_id").covariance_matrix_id + 1
        else:
            CM_id =0
        row=0
        column=0
        
        cm =[]
        matrix = numpy.array(covariance_matrix)
        for eachRow in matrix:
            for eachCell in eachRow:
                cm.append(CovarianceMatrix(covariance_matrix_id = CM_id, matrix_row = row, matrix_column = column, cell_value = eachCell))
                column = column+1
            row = row +1
        CovarianceMatrix.objects.bulk_create(cm)
        return CM_id
    
    def create_computational_intension(self, meanvector_id, cov_mat_id):
        comp_int = ComputationalIntension(mean_vector_id = meanvector_id, covariance_matrix_id = cov_mat_id)
        comp_int.save()
        return comp_int

class CustomQueries:

    def get_trainingset_name_for_current_version_of_legend(self, legendName):
        cursor = connection.cursor()
        
        cursor.execute("select t.trainingset_name from trainingset t, category c, legend l, legend_concept_combination lcc \
                        where l.legend_name = %s and c.trainingset_id = t.trainingset_id and c.trainingset_ver = t.trainingset_ver and c.legend_concept_combination_id = lcc.id and \
                        lcc.id = (select lcc1.id from legend_concept_combination lcc1 where lcc1.legend_id = l.legend_id and lcc1.legend_ver= l.legend_ver order by lcc1.id DESC limit 1)", [legendName])
        
        row = cursor.fetchone()
        return row
        
        
    def get_model_name_and_accuracy_from_a_legend(self, lid, ver):
        cursor = connection.cursor()
        
        cursor.execute("select classifier.classifier_name, classificationmodel.accuracy from classifier, learning_activity, classificationmodel, legend where \
                        classifier.id = learning_activity.classifier_id and learning_activity.model_id = classificationmodel.id and legend.model_id = classificationmodel.id \
                        and legend.legend_id = %s and legend.legend_ver = %s", [lid, ver])
        
        row = cursor.fetchone()
        return row
        
    
    def get_concepts_list_for_a_legend(self, lid, ver):
        cursor = connection.cursor()
            
        cursor.execute("select concept.id, concept.concept_name from concept, legend_concept_combination where legend_concept_combination.legend_id = %s and \
                        legend_concept_combination.legend_ver = %s and legend_concept_combination.concept_id = concept.id and concept_name NOT LIKE 'root%%'", [lid, ver])
        
        row = cursor.fetchall()
        return row
    
    def get_concept_details(self, clid):
        cursor = connection.cursor()
            
        cursor.execute("select concept.id, concept.concept_name from concept, legend_concept_combination where legend_concept_combination.legend_id = %s and \
                        legend_concept_combination.legend_ver = %s and legend_concept_combination.concept_id = concept.id and concept_name NOT LIKE 'root%%'", [lid, ver])
        
        row = cursor.fetchall()
        return row
        