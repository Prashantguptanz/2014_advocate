from Category_Modeler.models import Trainingset, TrainingsetCollectionActivity, ChangeTrainingsetActivity, AuthUser, Classificationmodel, Classifier, LearningActivity 
from Category_Modeler.models import Confusionmatrix, ExplorationChain, ClassificationActivity, Concept, Legend, LegendConceptCombination, ComputationalIntension
from Category_Modeler.models import Extension, Category, HierarchicalRelationship, HorizontalRelationship
from datetime import datetime

class QueryDatabase:
    
    def __init__(self, request):
        self.authuser_instance = AuthUser.objects.get(id = int(request.session['_auth_user_id']))
        self.request = request
        if not self.request.session['new_taxonomy_name']:
            self.current_taxonomy = self.request.session['existing_taxonomy_name']
        else:
            self.current_taxonomy = self.request.session['new_taxonomy_name']
    
    def create_legend(self):
        legendId = Legend.objects.latest("legend_id").legend_id
        model_instance = Classificationmodel.object.get(id = int(self.request.session['current_model_id']))
        legend = Legend(legend_id = legendId, legend_ver = 1, legend_name= self.current_taxonomy, date_expired = datetime(9999, 9, 12), description = self.request.session['new_taxonomy_description'], created_by = self.authuser_instance, model_id = model_instance)
        legend.save()
        self.__create_root_concept(legendId, 1)
    
    def __create_root_concept(self, legendId, legendVer):
        details = "Root concept to legend " + self.current_taxonomy
        concept = Concept(concept_name = "root", description = details, date_expired = datetime(9999, 9, 12), created_by = self.authuser_instance)
        concept.save()
        conceptId = concept.id
        connectToLegend = LegendConceptCombination(legend_id = legendId, legend_ver = legendVer, concept_id = conceptId)
        connectToLegend.save()
        
    def create_concept(self, conceptName, details=""):
        concept = Concept(concept_name = conceptName, description = details, date_expired = datetime(9999, 9, 12), created_by = self.authuser_instance)
        concept.save()
        conceptId = concept.id
        legend = Legend.objects.get(legend_name =self.current_taxonomy)
        connectToLegend = LegendConceptCombination(legend_id = legend.legend_id, legend_ver = legend.legend_ver, concept_id = conceptId)
        connectToLegend.save()
    
    