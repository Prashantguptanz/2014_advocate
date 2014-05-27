# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
#from __future__ import unicode_literals

from django.db import models

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    class Meta:
        managed = False
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')
    class Meta:
        managed = False
        db_table = 'auth_group_permissions'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)
    class Meta:
        managed = False
        db_table = 'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)
    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'

class Category(models.Model):
    idcategory = models.IntegerField()
    version = models.IntegerField()
    startdate = models.DateTimeField()
    enddate = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    label = models.CharField(max_length=45)
    concept_idconcept = models.ForeignKey('Concept', db_column='concept_idconcept')
    legend_idlegend = models.ForeignKey('Legend', db_column='legend_idlegend')
    training_set_idtraining_set = models.ForeignKey('TrainingSet', db_column='training_set_idtraining_set')
    class Meta:
        managed = False
        db_table = 'category'

class ClassificationModel(models.Model):
    idclassification_model = models.IntegerField(primary_key=True)
    accuracy = models.FloatField()
    classifier_idclassifier = models.ForeignKey('Classifier', db_column='classifier_idclassifier')
    training_set_idtraining_set = models.ForeignKey('TrainingSet', db_column='training_set_idtraining_set')
    class Meta:
        managed = False
        db_table = 'classification_model'

class Classifier(models.Model):
    idclassifier = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    class Meta:
        managed = False
        db_table = 'classifier'

class Concept(models.Model):
    idconcept = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    description = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'concept'

class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)
    action_time = models.DateTimeField()
    user = models.ForeignKey(AuthUser)
    content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.IntegerField()
    change_message = models.TextField()
    class Meta:
        managed = False
        db_table = 'django_admin_log'

class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'django_content_type'

class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'django_session'

class Legend(models.Model):
    idlegend = models.IntegerField()
    name = models.CharField(max_length=45)
    description = models.TextField(blank=True)
    version = models.IntegerField()
    classification_model_idclassification_model = models.ForeignKey(ClassificationModel, db_column='classification_model_idclassification_model')
    class Meta:
        managed = False
        db_table = 'legend'

class Relationships(models.Model):
    idrelationships = models.IntegerField(primary_key=True)
    expired = models.IntegerField()
    category_idcategory = models.ForeignKey(Category, db_column='category_idcategory', related_name='relationships_category1id')
    category_version = models.ForeignKey(Category, db_column='category_version', related_name='relationships_category1version')
    category_idcategory1 = models.ForeignKey(Category, db_column='category_idcategory1', related_name='relationships_category2id')
    category_version1 = models.ForeignKey(Category, db_column='category_version1', related_name='relationships_category2version')
    class Meta:
        managed = False
        db_table = 'relationships'

class TrainingSet(models.Model):
    idtraining_set = models.IntegerField(primary_key=True)
    data_file = models.TextField()
    description = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'training_set'