import csv
import numpy as np
from operator import itemgetter
import gdal, osr
from gdalconst import *
from io import FileIO, BufferedWriter
import csv

class TrainingSample:
    
    TRAINING_FILE_LOCATION = 'static/trainingfiles/'
    
    def __init__(self, training_file_name):
        self.training_file_name = training_file_name
        self.features, self.samples, self.target = self.__csv_file_conversion_to_numpy_arrays()
    
    def __repr__(self):
        return self.csv_file_name
    
    def __csv_file_conversion_to_numpy_arrays(self):
        with open('%s%s' % (TrainingSample.TRAINING_FILE_LOCATION, self.training_file_name), 'rU') as training_file:
            datareader = csv.reader(training_file, delimiter=',')
            features = next(datareader)
            training_samples = list(datareader)
            if self.__is_number(training_samples[0][-1]):
                training_samples = [c[:-1] + [float(c[-1])] for c in training_samples]
            training_samples.sort(key=itemgetter(len(features)-1))
            training_file.close();
            samples=[]
            target=[]
            for sample in training_samples:
                target.append(sample[-1])
                samples.append(sample[0:-1])
            features_as_nparray = np.asarray(features)
            target_as_nparray = np.asarray(target)
            samples_as_nparray = np.asarray(samples, dtype=np.float32)
        return features_as_nparray, samples_as_nparray, target_as_nparray

    
    def __is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    
        
    def split_training_samples_for_each_category(self):
        unique_categories, indices = np.unique(self.target, return_index=True)
        catgeories_with_sample_range = []
        for category in unique_categories:
            each_category_with_sample_range = []
            each_category_with_sample_range.append(category)
            index= np.where(unique_categories==category)[0][0]
            each_category_with_sample_range.append(indices[index])
            if index==len(unique_categories)-1:
                each_category_with_sample_range.append(len(self.target)-1)
            else:
                each_category_with_sample_range.append(indices[index+1]-1)
            catgeories_with_sample_range.append(each_category_with_sample_range)
        return catgeories_with_sample_range
            
    def compare_training_samples(self, old_training_sample):
        categories_with_sample_range_1 = self.split_training_samples_for_each_category()
        categories_with_sample_range_2 = old_training_sample.split_training_samples_for_each_category()
        common_categories_comparison = []
        new_categories_in_new_training_sample = []
        categories_not_in_new_training_sample = []
        for each_category_with_range_1 in categories_with_sample_range_1:
            if each_category_with_range_1[0] in categories_with_sample_range_2[:, 0]:
                index = np.where(categories_with_sample_range_2==each_category_with_range_1[0])[0][0]
                jaccard_index = self.__compare_training_sample_for_single_category(self.samples[each_category_with_range_1[1]:each_category_with_range_1[2]+1], \
                                                                old_training_sample.samples[categories_with_sample_range_2[index][1]:categories_with_sample_range_2[index][2]+1])
                common_categories_comparison.append([each_category_with_range_1[0], jaccard_index])
            else:
                new_categories_in_new_training_sample.append(each_category_with_range_1[0])
        for each_category_with_range_2 in categories_with_sample_range_2:
            if each_category_with_range_2[0] not in categories_with_sample_range_1[:, 0]:
                categories_not_in_new_training_sample.append(each_category_with_range_2[0])
        return common_categories_comparison, new_categories_in_new_training_sample, categories_not_in_new_training_sample
    
    
    def __compare_training_sample_for_single_category(self, ts1, ts2):
        common_elements_in_both_samples = np.intersect1d(ts1, ts2)
        union_of_both_training_samples = np.union1d(ts1, ts2)
        jaccard_index = float(len(common_elements_in_both_samples)/len(union_of_both_training_samples))
        return jaccard_index
        
        
class NormalDistributionIntensionalModel:
    
    def __init__(self, mean_vector, covariance_matrix):
        self.mean_vector = np.matrix(mean_vector)
        self.covariance_matrix = np.matrix(covariance_matrix)
    
    def jm_distance(self, other):
        bd = ((float(1/8))*((self.mean_vector-other.mean_vector).getT())*(((self.covariance_matrix+other.covariance_matrix)/2).getI())*(self.mean_vector-other.mean_vector)) + \
        ((float(1/2))* np.log((np.linalg.det(((self.covariance_matrix+other.covariance_matrix)/2)))/(np.sqrt(np.linalg.det(self.covariance_matrix)*np.linalg.det(other.covariance_matrix)))))
        jm = np.sqrt(2*(1-(np.exp(-bd))))
        return jm
    
class DecisionTreeIntensionalModel:
    
    def __init__(self, tree):
        self.decision_rules, self.values = self.__create_decision_rules(tree)
                                                           
    
    
    def __create_decision_rules(self, tree):
        left = tree.tree_.children_left
        right = tree.tree_.children_right
        threshold = tree.tree_.threshold
        features = tree.tree_.feature
        value = tree.tree_.value
        temp_rules=[]
        rules=[]
        values = []
        
        def recurse(left, right, threshold, features, node, temp_rules):
            if threshold[node] != -2:
                if left[node] != -1:
                    temp_rules.append([features[node], "<=", threshold[node]])
                    recurse(left, right, threshold, features, left[node], temp_rules)
                    temp_rules.pop()
                if right[node] != -1:
                    temp_rules.append([features[node], ">", threshold[node]])
                    recurse(left, right, threshold, features, right[node], temp_rules)
                    temp_rules.pop()
            else:
                rules.append(temp_rules)
                values.append(value[node])
                
        recurse(left, right, threshold, features, 0, temp_rules)
        return rules, values

  #  def compare_decision_rules(self, other):
        
                
class ManageRasterData:
    
    def __init__(self, raster_files, noOfBands):
        self.raster_files = raster_files
        self.countBands = noOfBands
    
    def read_raster_file(self, f):
        print f
        dataset = gdal.Open('static/data/%s' % f, GA_ReadOnly)
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        noOfBands = dataset.RasterCount
        bands = []
        
        final_array = []
        pixelValue=[]
        className = f.split('.', 1)[0]
    
    
        for i in range(1, self.countBands+1):
            bands.append(dataset.GetRasterBand(i).ReadAsArray(0,0,cols,rows))
        
        for j in range(rows):
            for k in range (cols): 
                pixelValue.append(j)
                pixelValue.append(k)
                for l in range(self.countBands):
                    pixelValue.append(bands[l][j][k])
                pixelValue.append(className)
                final_array.append(pixelValue)
                pixelValue=[]
        
        return final_array
    
    def read_test_file(self, f):
        dataset = gdal.Open('static/data/%s' % f, GA_ReadOnly)
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        noOfBands = dataset.RasterCount
        bands = []
        
        final_array = []
        pixelValue=[]
    
    
        for i in range(1, self.countBands+1):
            bands.append(dataset.GetRasterBand(i).ReadAsArray(0,0,cols,rows))
        
        for j in range(rows):
            for k in range (cols):
                for l in range(self.countBands):
                    pixelValue.append(bands[l][j][k])
                final_array.append(pixelValue)
                pixelValue=[]
        
        return final_array
    
    def combine_raster_files(self, filename):
        with BufferedWriter( FileIO( 'static/trainingfiles/%s' % filename, "wb" ) ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            if self.countBands==3:
                spamwriter.writerow(['X', 'Y', 'band1', 'band2', 'band3', 'class'])
            else:
                spamwriter.writerow(['X', 'Y', 'band1', 'band2', 'band3', 'band4', 'band5', 'band6', 'band7', 'band8', 'class'])
            
        
        for eachFile in self.raster_files:
            final_array = self.read_raster_file(eachFile)
              
            with BufferedWriter( FileIO( 'static/trainingfiles/%s' % filename, "a" ) ) as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',')
                for i in range(len(final_array)):
                    spamwriter.writerow(final_array[i])
    
    def create_csv_file(self):
        final_array = self.read_test_file(self.raster_files)
        filename = self.raster_files.split('.', 1)[0] + ".csv"
        with BufferedWriter( FileIO( 'static/testfiles/%s' % filename, "wb" ) ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            for i in range(len(final_array)):
                spamwriter.writerow(final_array[i])
            
            
            
    def read_raster_and_print(self):
        dataset = gdal.Open('static/data/%s' % self.raster_files, GA_ReadOnly)
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        noOfBands = dataset.RasterCount
        driver = dataset.GetDriver().LongName
        geotransform = dataset.GetGeoTransform()
        originX = geotransform[0]
        originY = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]
        prj = dataset.GetProjection()
        
        return cols, rows, noOfBands, driver, originX, originY, pixelWidth, pixelHeight, prj
            
    
    def create_raster(self):
        cols, rows, bands, driverName, originX, originY, pixelWidth, pixelHeight, prj = self.read_raster_and_print()
        driver = gdal.GetDriverByName(driverName)
        outRaster = driver.Create('test.tif', cols, rows, 1, gdal.GDT_Byte )
        outRaster.SetGeoTransform(originX, pixelWidth, 0, originY, 0, pixelHeight)
        outband = outRaster.GetRasterBand(1)
        outband.WriteArray()
        outRasterSRS = osr.SpatialReference(wkt=prj)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        outband.FlushCache()
            
a= ManageRasterData('final3b.tif', 3)
a.read_raster_and_print()
#a.create_csv_file()        
               
                
        
#a= ManageRasterData(['arti1_1.tif', 'arti1_2.tif', 'cloud1_3.tif', 'cloud1_2.tif', 'forest1.tif', 'grass1.tif', 'shado1_1.tif', 'shado1_2.tif', 'water1_1.tif', 'water1_2.tif', 'water1_3.tif', 'water1_4.tif'], 3)  
#a.combine_raster_files('akl_cbd_ts1_3bands.csv')
       
#a=TrainingSample("akl.csv")
#print a.training_samples_as_nparray.dtype
#a.split_training_samples_for_each_category()