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


class Activity(models.Model):
    activity_id = models.IntegerField(primary_key=True)
    activity_name = models.TextField(blank=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'activity'


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
    id = models.IntegerField(primary_key=True)  # AutoField?
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
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


class Category(models.Model):
    category_id = models.IntegerField()
    category_ver = models.IntegerField()
    category_name = models.CharField(max_length=100, blank=True)
    startdate = models.DateTimeField(blank=True, null=True)
    enddate = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    concept = models.ForeignKey('Concept', blank=True, null=True)
    legend = models.ForeignKey('Legend')
    legend_ver = models.IntegerField()
    trainingset = models.ForeignKey('Trainingset', blank=True, null=True)
    trainingset_ver = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category'


class ChangeTrainingSetActivity(models.Model):
    change_training_set_activity_id = models.IntegerField(primary_key=True)
    oldtrainingset = models.ForeignKey('Trainingset', related_name='oldtrainingset')
    oldtrainingset_ver = models.IntegerField()
    newtrainingset = models.ForeignKey('Trainingset', related_name='newtrainingset')
    newtrainingset_ver = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'change_training_set_activity'


class Classificationmodel(models.Model):
    model_id = models.IntegerField(primary_key=True)
    accuracy = models.FloatField(blank=True, null=True)
    confusionmatrix = models.BinaryField(blank=True, null=True)
    classifier = models.ForeignKey('Classifier')

    class Meta:
        managed = False
        db_table = 'classificationmodel'


class ClassificationmodelTrianingsets(models.Model):
    model_trainingsets_id = models.IntegerField(primary_key=True)
    trainingset_id = models.IntegerField()
    trainingset_ver = models.IntegerField()
    model_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'classificationmodel_trianingsets'


class Classifier(models.Model):
    classifier_id = models.IntegerField(primary_key=True)
    classifier_name = models.CharField(max_length=100, blank=True)

    class Meta:
        managed = False
        db_table = 'classifier'


class Concept(models.Model):
    concept_id = models.BigIntegerField(primary_key=True)
    concept_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'concept'


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
    exploration_chain_id = models.IntegerField()
    step = models.IntegerField()
    current_activity = models.ForeignKey(Activity)
    current_activity_instance_id = models.IntegerField()

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


class Legend(models.Model):
    legend_id = models.IntegerField()
    legend_ver = models.IntegerField()
    legend_name = models.CharField(max_length=100, blank=True)
    startdate = models.DateTimeField(blank=True, null=True)
    enddate = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    model = models.ForeignKey(Classificationmodel)

    class Meta:
        managed = False
        db_table = 'legend'


class NewTrainingsetCollectionActivity(models.Model):
    new_trainingset_collection_activity_id = models.IntegerField(primary_key=True)
    trainingset = models.ForeignKey('Trainingset')
    trainingset_ver = models.IntegerField()
    startdate = models.DateTimeField(blank=True, null=True)
    enddate = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'new_trainingset_collection_activity'


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


class Relationship(models.Model):
    relationship_id = models.BigIntegerField(primary_key=True)
    relationship_name = models.TextField(blank=True)  # This field type is a guess.
    expired = models.NullBooleanField()
    category1 = models.ForeignKey(Category, related_name='category1')
    category1_ver = models.IntegerField()
    category2 = models.ForeignKey(Category, related_name='category2')
    category2_ver = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'relationship'


class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, blank=True)
    auth_srid = models.IntegerField(blank=True, null=True)
    srtext = models.CharField(max_length=2048, blank=True)
    proj4text = models.CharField(max_length=2048, blank=True)

    class Meta:
        managed = False
        db_table = 'spatial_ref_sys'


class TestdataClassificationActivity(models.Model):
    testdata_classification_activity_id = models.IntegerField(primary_key=True)
    model = models.ForeignKey(Classificationmodel)
    testfilelocation = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.testdata_classification_activity_id
    
    class Meta:
        managed = False
        db_table = 'testdata_classification_activity'


class TrainClassifierActivity(models.Model):
    train_classifier_activity_id = models.IntegerField(primary_key=True)
    classifier = models.ForeignKey(Classifier)
    model = models.ForeignKey(Classificationmodel)
    
    def __unicode__(self):
        return self.train_classifier_activity_id

    class Meta:
        managed = False
        db_table = 'train_classifier_activity'


class Trainingset(models.Model):
    trainingset_id = models.IntegerField(primary_key=True)
    trainingset_ver = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    startdate = models.DateTimeField()
    enddate = models.DateTimeField()
    location = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name
    
    class Meta:
        managed = False
        db_table = 'trainingset'