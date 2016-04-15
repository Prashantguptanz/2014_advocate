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

    class Meta:
        managed = False
        db_table = 'computational_intension'

class ClassificationActivity(models.Model):
    model = models.ForeignKey(Classificationmodel)
    testfile_location = models.CharField(max_length=1024)
    testfile_name = models.CharField(max_length=100)
    classifiedfile_location = models.CharField(max_length=1024)
    classifiedfile_name = models.CharField(max_length=100)
    completed = models.DateTimeField(default=datetime.now)
    completed_by = models.ForeignKey(AuthUser, db_column='completed_by')

    class Meta:
        managed = False
        db_table = 'classification_activity'

class Extension(models.Model):
    id = models.IntegerField(primary_key=True)
    x = models.IntegerField(primary_key=True, db_column='X')  # Field name made lowercase.
    y = models.IntegerField(primary_key=True, db_column='Y')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'extension'

       
class Category(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_ver = models.IntegerField(primary_key=True)
    date_created = models.DateTimeField(default=datetime.now)
    date_expired = models.DateTimeField()
    description = models.TextField(blank=True)
    trainingset_id = models.IntegerField()
    trainingset_ver = models.IntegerField()
    creator = models.ForeignKey(AuthUser, db_column='creator')
    legend_concept_combination_id = models.ForeignKey(LegendConceptCombination, db_column='legend_concept_combination_id')
    computational_intension_id = models.ForeignKey(ComputationalIntension, db_column='computational_intension_id')
    extension_id = models.IntegerField()
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
    reason_for_change = models.CharField(max_length=1024)

    class Meta:
        managed = False
        db_table = 'change_trainingset_activity'
        unique_together = ("oldtrainingset_id", "oldtrainingset_ver")
        unique_together = ("newtrainingset_id", "newtrainingset_ver")




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
        ('trainingset collection', 'trainingset collection'),
        ('change trainingset', 'change trainingset'),
        ('learning', 'learning'),
        ('classification', 'classification')
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
        ('excludes', 'excludes')
    )
    relationship_name = models.CharField(choices=horizontal_relationship_type, max_length=256)
    expired = models.NullBooleanField()
    category1_id = models.IntegerField()
    category1_ver = models.IntegerField()
    category2_id = models.IntegerField()
    category2_ver = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'horizontal_relationship'
        unique_together = ("category1_id", "category1_ver")
        unique_together = ("category2_id", "category2_ver")





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
    description = models.TextField(blank=True)
    date_first_used = models.DateTimeField(default=datetime.now)
    date_expired = models.DateTimeField()
    trainingset_name = models.CharField(max_length=100)
    filelocation = models.CharField(max_length=1024)

    class Meta:
        managed = False
        db_table = 'trainingset'


class TrainingsetCollectionActivity(models.Model):
    date_started = models.DateField()
    date_finished = models.DateField()
    trainingset_location = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    collector = models.CharField(max_length=100)
    trainingset_id = models.IntegerField(blank=True, null=True)
    trainingset_ver = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trainingset_collection_activity'
        unique_together = ("trainingset_id", "trainingset_ver")

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
        ('create_legend_operation', 'create_legend_operation'),
        ('create_concept_operation', 'create_concept_operation'),
        ('add_concept_to_a_legend_operation', 'add_concept_to_a_legend_operation')
        
    )
    change_event_id = models.ForeignKey(ChangeEvent, db_column='change_event_id', primary_key=True)
    change_operation_id = models.IntegerField(primary_key=True)
    change_operation = models.CharField(choices=change_operation_type, max_length=256, primary_key=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'change_event_operations'
        
class AddConceptToALegendOperation(models.Model):
    legend_concept_combination_id = models.ForeignKey(LegendConceptCombination, db_column='legend_concept_combination_id')

    class Meta:
        managed = False
        db_table = 'add_concept_to_a_legend_operation'

class CreateConceptOperation(models.Model):
    concept_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'create_concept_operation'
        
class CreateLegendOperation(models.Model):
    legend_name = models.CharField(max_length=100)
    legend_id = models.IntegerField()
    legend_ver = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'create_legend_operation'
        unique_together = ("legend_id", "legend_ver")