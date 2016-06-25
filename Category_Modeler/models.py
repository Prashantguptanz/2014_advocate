# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models
from datetime import datetime

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'


class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(null=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'


class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'


class ChangeEvent(models.Model):
    exploration_chain_id = models.IntegerField()
    created_by = models.ForeignKey(AuthUser, db_column='created_by')
    date_created = models.DateTimeField(default=datetime.now)

    class Meta:
        managed = False
        db_table = 'change_event'

class Confusionmatrix(models.Model):
    confusionmatrix_name = models.CharField(max_length=256)
    confusionmatrix_location = models.CharField(max_length=1024)

    class Meta:
        managed = False
        db_table = 'confusionmatrix'

class Classifier(models.Model):
    classifier_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'classifier'

class Concept(models.Model):
    concept_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(default=datetime.now)
    date_expired = models.DateTimeField()
    created_by = models.ForeignKey(AuthUser, db_column='created_by')
    change_event_id = models.ForeignKey(ChangeEvent, db_column='change_event_id')
    
    class Meta:
        managed = False
        db_table = 'concept'

class Classificationmodel(models.Model):
    model_name = models.CharField(max_length=256)
    model_location = models.CharField(max_length=1024)
    accuracy = models.FloatField(blank=True, null=True)
    model_type = models.CharField(max_length=256)

    class Meta:
        managed = False
        db_table = 'classificationmodel'

class LearningActivity(models.Model):
    validation_type = (
        ('training data', 'training data'),
        ('validation data', 'validation data'),
        ('cross validation', 'cross validation'),
        ('train test split', 'train test split')
    )    
    classifier = models.ForeignKey(Classifier)
    model = models.ForeignKey(Classificationmodel, blank=True, null=True)
    validation = models.CharField(choices=validation_type, max_length=256)
    validation_score = models.FloatField()
    completed = models.DateTimeField(default=datetime.now)
    completed_by = models.ForeignKey(AuthUser, db_column='completed_by')
    confusionmatrix = models.ForeignKey(Confusionmatrix, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'learning_activity'



class Legend(models.Model):
    legend_id = models.IntegerField(primary_key=True)
    legend_ver = models.IntegerField(primary_key=True)
    legend_name = models.CharField(max_length=100)
    date_created = models.DateTimeField(default=datetime.now)
    date_expired = models.DateTimeField()
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(AuthUser, db_column='created_by')
    model = models.ForeignKey(Classificationmodel)
    change_event_id = models.ForeignKey(ChangeEvent, db_column='change_event_id')

    def __unicode__(self):
        return self.legend_name
    
    class Meta:
        managed = False
        db_table = 'legend'


class LegendConceptCombination(models.Model):
    legend_id = models.IntegerField()
    legend_ver = models.IntegerField()
    concept = models.ForeignKey(Concept)
    change_event_id = models.ForeignKey(ChangeEvent, db_column='change_event_id')

    class Meta:
        managed = False
        db_table = 'legend_concept_combination'
        unique_together = ("legend_id", "legend_ver", "concept")
        
class ComputationalIntension(models.Model):
    mean_vector_id = models.IntegerField(blank=True, null=True)
    covariance_matrix_id = models.IntegerField(blank=True, null=True)
    learning_activity_id = models.ForeignKey(LearningActivity, db_column='learning_activity_id')
    producer_accuracy = models.FloatField(blank=True, null=True)
    user_accuracy = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'computational_intension'

class SatelliteImage(models.Model):
    name = models.CharField(max_length=256)
    location = models.CharField(max_length=256)
    columns = models.IntegerField()
    rows = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'satellite_image'

class ClassifiedSatelliteImage(models.Model):
    name = models.CharField(max_length=256)
    location = models.CharField(max_length=256)

    class Meta:
        managed = False
        db_table = 'classified_satellite_image'

class ClassificationActivity(models.Model):
    model = models.ForeignKey(Classificationmodel)
    satellite_image_id  = models.ForeignKey(SatelliteImage, db_column='satellite_image_id')
    classified_satellite_image_id  = models.ForeignKey(ClassifiedSatelliteImage, db_column='classified_satellite_image_id')
    completed = models.DateTimeField(default=datetime.now)
    completed_by = models.ForeignKey(AuthUser, db_column='completed_by')

    class Meta:
        managed = False
        db_table = 'classification_activity'
        
class ClusteringActivity(models.Model):
    clustered_file_name = models.CharField(max_length=256)
    clustered_file_location = models.CharField(max_length=256)
    scatterplot_image_name = models.CharField(max_length=256)
    scatterplot_image_location = models.CharField(max_length=256)
    completed = models.DateTimeField(default=datetime.now)
    completed_by = models.ForeignKey(AuthUser, db_column='completed_by')

    class Meta:
        managed = False
        db_table = 'clustering_activity'

class SetOfOccurences(models.Model):
    id = models.IntegerField(primary_key=True)
    x_coordinate = models.IntegerField(primary_key=True)
    y_coordinate = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'set_of_occurences'

class Extension(models.Model):
    set_of_occurences_id = models.IntegerField()
    classification_activity_id = models.ForeignKey(ClassificationActivity, db_column='classification_activity_id')

    class Meta:
        managed = False
        db_table = 'extension'

       
class Category(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_evol_ver = models.IntegerField(primary_key=True)
    category_comp_ver = models.IntegerField(primary_key=True)
    date_created = models.DateTimeField(default=datetime.now)
    date_expired = models.DateTimeField()
    description = models.TextField(blank=True)
    trainingset_id = models.IntegerField()
    trainingset_ver = models.IntegerField()
    creator = models.ForeignKey(AuthUser, db_column='creator')
    legend_concept_combination_id = models.ForeignKey(LegendConceptCombination, db_column='legend_concept_combination_id')
    computational_intension_id = models.ForeignKey(ComputationalIntension, db_column='computational_intension_id')
    extension_id = models.ForeignKey(Extension, db_column='extension_id')
    change_event_id = models.ForeignKey(ChangeEvent, db_column='change_event_id')
    
    class Meta:
        managed = False
        db_table = 'category'
        unique_together = ("trainingset_id", "trainingset_ver")

class ChangeTrainingsetActivity(models.Model):
    oldtrainingset_id = models.IntegerField()
    oldtrainingset_ver = models.IntegerField()
    newtrainingset_id = models.IntegerField()
    newtrainingset_ver = models.IntegerField()
    completed = models.DateTimeField(default=datetime.now)
    completed_by = models.ForeignKey(AuthUser, db_column='completed_by')

    class Meta:
        managed = False
        db_table = 'change_trainingset_activity'
        unique_together = ("oldtrainingset_id", "oldtrainingset_ver")
        unique_together = ("newtrainingset_id", "newtrainingset_ver")


class ChangeTrainingsetActivityDetails(models.Model):
    edit_trainingset_activity_type = (
        ('add', 'add'),
        ('remove', 'remove'),
        ('rename', 'rename'),
        ('edit', 'edit'),
        ('split', 'split'),
        ('merge', 'merge'),
        ('group', 'group')
    )
    
    
    activity_id = models.ForeignKey(ChangeTrainingsetActivity, db_column='activity_id')
    operation = models.CharField(choices=edit_trainingset_activity_type, max_length=256) # This field type is a guess.
    concept1 = models.CharField(max_length=256, blank=True, null=True)
    concept2 = models.CharField(max_length=256, blank=True, null=True)
    concept3 = models.CharField(max_length=256, blank=True, null=True)
    concept4 = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'change_trainingset_activity_details'


class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
    user = models.ForeignKey(AuthUser)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'


class DjangoMigrations(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class ExplorationChain(models.Model):
    activity_type = (
        ('create trainingset', 'create trainingset'),
        ('change trainingset', 'change trainingset'),
        ('learning', 'learning'),
        ('classification', 'classification'),
        ('clustering', 'clustering')
    )
    id = models.IntegerField(primary_key=True)
    step = models.IntegerField(primary_key=True)
    activity = models.CharField(choices=activity_type, max_length=256)
    activity_instance = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'exploration_chain'


class GeographyColumns(models.Model):
    f_table_catalog = models.TextField(blank=True)  # This field type is a guess.
    f_table_schema = models.TextField(blank=True)  # This field type is a guess.
    f_table_name = models.TextField(blank=True)  # This field type is a guess.
    f_geography_column = models.TextField(blank=True)  # This field type is a guess.
    coord_dimension = models.IntegerField(blank=True, null=True)
    srid = models.IntegerField(blank=True, null=True)
    type = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'geography_columns'


class GeometryColumns(models.Model):
    f_table_catalog = models.CharField(max_length=256, blank=True)
    f_table_schema = models.CharField(max_length=256, blank=True)
    f_table_name = models.CharField(max_length=256, blank=True)
    f_geometry_column = models.CharField(max_length=256, blank=True)
    coord_dimension = models.IntegerField(blank=True, null=True)
    srid = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=30, blank=True)

    class Meta:
        managed = False
        db_table = 'geometry_columns'

class HierarchicalRelationship(models.Model):
    hierarchical_relationship_type = (
        ('child-of', 'child-of'),
        ('parent-of', 'parent-of'),
        ('sibling-of', 'sibling-of')
    )
    relationship_name = models.CharField(choices=hierarchical_relationship_type, max_length=256)
    expired = models.NullBooleanField()
    concept1 = models.ForeignKey(LegendConceptCombination, related_name='concept1')
    concept2 = models.ForeignKey(LegendConceptCombination, related_name='concept2')

    class Meta:
        managed = False
        db_table = 'hierarchical_relationship'


class HorizontalRelationship(models.Model):
    horizontal_relationship_type = (
        ('same as', 'same as'),
        ('includes', 'includes'),
        ('is included in', 'is included in'),
        ('overlaps with', 'overlaps with'),
        ('excludes', 'excludes'),
        ('unknown', 'unknown')
    )
    comp_intension_relationship_name = models.CharField(choices=horizontal_relationship_type, max_length=256)
    extension_relationship_name = models.CharField(choices=horizontal_relationship_type, max_length=256) 
    expired = models.NullBooleanField()
    category1_id = models.IntegerField()
    category1_evol_ver = models.IntegerField()
    category1_comp_ver = models.IntegerField()
    category2_id = models.IntegerField()
    category2_evol_ver = models.IntegerField()
    category2_comp_ver = models.IntegerField()
    intensional_similarity = models.FloatField(blank=True, null=True)
    extensional_similarity = models.FloatField(blank=True, null=True)
    extensional_containment = models.FloatField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'horizontal_relationship'
        unique_together = ("category1_id", "category1_evol_ver", "category1_comp_ver")
        unique_together = ("category2_id", "category2_evol_ver", "category2_comp_ver")

class RasterColumns(models.Model):
    r_table_catalog = models.TextField(blank=True)  # This field type is a guess.
    r_table_schema = models.TextField(blank=True)  # This field type is a guess.
    r_table_name = models.TextField(blank=True)  # This field type is a guess.
    r_raster_column = models.TextField(blank=True)  # This field type is a guess.
    srid = models.IntegerField(blank=True, null=True)
    scale_x = models.FloatField(blank=True, null=True)
    scale_y = models.FloatField(blank=True, null=True)
    blocksize_x = models.IntegerField(blank=True, null=True)
    blocksize_y = models.IntegerField(blank=True, null=True)
    same_alignment = models.NullBooleanField()
    regular_blocking = models.NullBooleanField()
    num_bands = models.IntegerField(blank=True, null=True)
    pixel_types = models.TextField(blank=True)  # This field type is a guess.
    nodata_values = models.TextField(blank=True)  # This field type is a guess.
    out_db = models.TextField(blank=True)  # This field type is a guess.
    extent = models.TextField(blank=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'raster_columns'


class RasterOverviews(models.Model):
    o_table_catalog = models.TextField(blank=True)  # This field type is a guess.
    o_table_schema = models.TextField(blank=True)  # This field type is a guess.
    o_table_name = models.TextField(blank=True)  # This field type is a guess.
    o_raster_column = models.TextField(blank=True)  # This field type is a guess.
    r_table_catalog = models.TextField(blank=True)  # This field type is a guess.
    r_table_schema = models.TextField(blank=True)  # This field type is a guess.
    r_table_name = models.TextField(blank=True)  # This field type is a guess.
    r_raster_column = models.TextField(blank=True)  # This field type is a guess.
    overview_factor = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'raster_overviews'


class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, blank=True)
    auth_srid = models.IntegerField(blank=True, null=True)
    srtext = models.CharField(max_length=2048, blank=True)
    proj4text = models.CharField(max_length=2048, blank=True)

    class Meta:
        managed = False
        db_table = 'spatial_ref_sys'


class Trainingset(models.Model):
    trainingset_id = models.IntegerField(primary_key=True)
    trainingset_ver = models.IntegerField(primary_key=True)
    date_created = models.DateTimeField(default=datetime.now)
    date_expired = models.DateTimeField()
    trainingset_name = models.CharField(max_length=100)
    filelocation = models.CharField(max_length=1024)

    class Meta:
        managed = False
        db_table = 'trainingset'

class CreateTrainingsetActivity(models.Model):

    trainingset_id = models.IntegerField(blank=True, null=True)
    trainingset_ver = models.IntegerField(blank=True, null=True)
    reference_trainingset_id = models.IntegerField(blank=True, null=True)
    reference_trainingset_ver = models.IntegerField(blank=True, null=True)
    creator_id = models.ForeignKey(AuthUser, db_column='creator_id')
    collector = models.CharField(max_length=256, blank=True)
    data_collection_start_date = models.DateField(blank=True, null=True)
    data_collection_end_date = models.DateField(blank=True, null=True)
    other_details = models.CharField(max_length=256, blank=True)


    class Meta:
        managed = False
        db_table = 'create_trainingset_activity'
        unique_together = ("trainingset_id", "trainingset_ver")
        unique_together = ("reference_trainingset_id", "reference_trainingset_ver")


class CreateTrainingsetActivityOperations(models.Model):
    create_trainingset_activity_type = (
    ('add new', 'add new'),
    ('add existing', 'add existing'),
    ('split', 'split'),
    ('merge', 'merge')
        
    )
    create_trainingset_activity_id = models.ForeignKey(CreateTrainingsetActivity, db_column= 'create_trainingset_activity_id')
    operation = models.CharField(choices=create_trainingset_activity_type, max_length=256) 
    concept1 = models.CharField(max_length=256)
    concept2 = models.CharField(max_length=256, blank=True, null=True)
    concept3 = models.CharField(max_length=256, blank=True, null=True)
    concept4 = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'create_trainingset_activity_operations'


class MeanVector(models.Model):
    band1 = models.FloatField()
    band2 = models.FloatField()
    band3 = models.FloatField()
    band4 = models.FloatField(blank=True, null=True)
    band5 = models.FloatField(blank=True, null=True)
    band6 = models.FloatField(blank=True, null=True)
    band7 = models.FloatField(blank=True, null=True)
    band8 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mean_vector'


class CovarianceMatrix(models.Model):
    covariance_matrix_id  = models.IntegerField(primary_key=True)
    matrix_row = models.IntegerField(primary_key=True)
    matrix_column = models.IntegerField(primary_key=True)
    cell_value = models.FloatField()

    class Meta:
        managed = False
        db_table = 'covariance_matrix'



class ChangeEventOperations(models.Model):
    change_operation_type = (
        ('Add_Taxonomy', 'Add_Taxonomy'),
        ('Add_Concept', 'Add_Concept'),
        ('Add_Taxonomy_Version', 'Add_Taxonomy_Version'),
        ('Add_Existing_Concept_To_New_Version_Of_Legend', 'Add_Existing_Concept_To_New_Version_Of_Legend'),
        ('Add_Concept_Split_From_Existing_To_New_Version_Of_Legend', 'Add_Concept_Split_From_Existing_To_New_Version_Of_Legend'),
        ('Add_Merged_Concept_To_New_Version_Of_Legend', 'Add_Merged_Concept_To_New_Version_Of_Legend'),
        ('Add_Generalized_Concept_To_New_Version_Of_Legend', 'Add_Generalized_Concept_To_New_Version_Of_Legend'),
        ('Add_Evolutionary_Version', 'Add_Evolutionary_Version'),
        ('Add_Competing_Version', 'Add_Competing_Version')
        
    )
    change_event_id = models.ForeignKey(ChangeEvent, db_column='change_event_id', primary_key=True)
    change_operation_id = models.IntegerField(primary_key=True)
    change_operation = models.CharField(choices=change_operation_type, max_length=256, primary_key=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'change_event_operations'


class CategoryInstantiationOperation(models.Model):
    legend_concept_id = models.ForeignKey(LegendConceptCombination, db_column='legend_concept_id')
    comp_int_id = models.ForeignKey(ComputationalIntension, db_column='comp_int_id')
    ext_id = models.ForeignKey(Extension, db_column='ext_id')
    category_id = models.IntegerField()
    category_evol_ver = models.IntegerField()
    category_comp_ver = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Category_Instantiation_operation'
        unique_together = ("category_id", "category_evol_ver", "category_comp_ver")

class AddConceptOperation(models.Model):
    concept_id = models.ForeignKey(Concept, db_column='concept_id')
    legend_concept_comb_id = models.ForeignKey(LegendConceptCombination, db_column='legend_concept_comb_id')
    hierarchical_relationship_id = models.ForeignKey(HierarchicalRelationship, db_column='hierarchical_relationship_id')
    category_instantiation_op_id = models.ForeignKey(CategoryInstantiationOperation, db_column='category_instantiation_op_id')

    class Meta:
        managed = False
        db_table = 'Add_Concept_operation'
        
class AddTaxonomyOperation(models.Model):
    legend_id = models.IntegerField()
    legend_ver = models.IntegerField()
    root_concept_id = models.ForeignKey(Concept, db_column='root_concept_id')
    legend_root_concept_combination_id = models.ForeignKey(LegendConceptCombination, db_column='legend_root_concept_combination_id')

    class Meta:
        managed = False
        db_table = 'Add_Taxonomy_operation'
        unique_together = ("legend_id", "legend_ver")

class AddTaxonomyVersionOperation(models.Model):
    legend_id = models.IntegerField()
    old_legend_ver = models.IntegerField()
    new_legend_ver = models.IntegerField()
    root_concept_id = models.ForeignKey(Concept, db_column='root_concept_id')
    legend_root_concept_combination_id = models.ForeignKey(LegendConceptCombination, db_column='legend_root_concept_combination_id')

    class Meta:
        managed = False
        db_table = 'Add_Taxonomy_Version_operation'
        unique_together = ("legend_id", "old_legend_ver")
        unique_together = ("legend_id", "new_legend_ver")

class AddExistingConceptToNewVersion(models.Model):
    concept_id = models.ForeignKey(Concept, db_column='concept_id')
    legend_concept_comb_id = models.ForeignKey(LegendConceptCombination, db_column='legend_concept_comb_id')
    hierarchical_relationship_id = models.ForeignKey(HierarchicalRelationship, db_column = 'hierarchical_relationship_id')
    category_instantiation_op_id = models.ForeignKey(CategoryInstantiationOperation, db_column = 'category_instantiation_op_id')

    class Meta:
        managed = False
        db_table = 'Add_Existing_Concept_To_New_Version_Of_Legend_operation'
        
class AddConSplitFrmExistToNewVer(models.Model):
    concept_id = models.ForeignKey(Concept, db_column='concept_id')
    existing_split_concept_id = models.IntegerField()
    legend_concept_comb_id = models.ForeignKey(LegendConceptCombination, db_column='legend_concept_comb_id')
    hierarchical_relationship_id = models.ForeignKey(HierarchicalRelationship, db_column = 'hierarchical_relationship_id')
    category_instantiation_op_id = models.ForeignKey(CategoryInstantiationOperation, db_column = 'category_instantiation_op_id')

    class Meta:
        managed = False
        db_table = 'Add_Concept_Split_From_Existing_To_New_Legend_Ver_operation'
        
class AddMergedConToNewVerOp(models.Model):
    concept_id = models.ForeignKey(Concept, db_column='concept_id')
    existing_concept_id1 = models.IntegerField()
    existing_concept_id2 = models.IntegerField()
    existing_concept_id3 = models.IntegerField(blank=True, null=True)
    legend_concept_comb_id = models.ForeignKey(LegendConceptCombination, db_column='legend_concept_comb_id')
    hierarchical_relationship_id = models.ForeignKey(HierarchicalRelationship, db_column = 'hierarchical_relationship_id')
    category_instantiation_op_id = models.ForeignKey(CategoryInstantiationOperation, db_column = 'category_instantiation_op_id')

    class Meta:
        managed = False
        db_table = 'Add_Merged_Concept_To_New_Legend_Ver_operation'
        

class AddCompetingCategoryOperation(models.Model):
    category_instantiation_op_id = models.ForeignKey(CategoryInstantiationOperation, db_column='category_instantiation_op_id')

    class Meta:
        managed = False
        db_table = 'Add_Competing_Category_Operation'
        
class AddEvolutionaryCategoryOperation(models.Model):
    category_instantiation_op_id = models.ForeignKey(CategoryInstantiationOperation, db_column='category_instantiation_op_id')

    class Meta:
        managed = False
        db_table = 'Add_Evolutionary_Category_Operation'
        
class AddGenConToNewVerOp(models.Model):
    concept_id = models.ForeignKey(Concept, db_column='concept_id')
    existing_concept_id1 = models.IntegerField()
    existing_concept_id2 = models.IntegerField()
    legend_concept_comb_id = models.ForeignKey(LegendConceptCombination, db_column='legend_concept_comb_id')
    hierarchical_relationship_id = models.ForeignKey(HierarchicalRelationship, db_column = 'hierarchical_relationship_id')
    category_instantiation_op_id = models.ForeignKey(CategoryInstantiationOperation, db_column = 'category_instantiation_op_id')

    class Meta:
        managed = False
        db_table = 'Add_Generalized_Concept_To_New_Legend_Ver_operation'