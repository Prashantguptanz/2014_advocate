import gdal
import numpy as np
from gdalconst import *
from io import FileIO, BufferedWriter
import csv

class ManageRasterData:
    
    RASTER_DATA_LOCATION = 'Category_Modeler/static/data/'
    
    def __init__(self, files):
        self.raster_files = files
        print self.raster_files
        print self.raster_files[0]

    def extract_raster_info(self, filename):
        dataset = gdal.Open('%s%s' %(ManageRasterData.RASTER_DATA_LOCATION, filename), GA_ReadOnly)
        columns = dataset.RasterXSize
        rows = dataset.RasterYSize
        noOfBands = dataset.RasterCount
        driver = dataset.GetDriver().LongName
        geotransform = dataset.GetGeoTransform()
        originX = geotransform[0]
        originY = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]
        prj = dataset.GetProjection()
        return columns, rows, noOfBands, driver, originX, originY, pixelWidth, pixelHeight, prj


# If raster file has a single band, the numpy array will be a 2D array, where each cell contains a single value. However, if the raster file has multiple bands, each cell of the array
# has a tuple containing the pixel values from each band
    def convert_raster_to_array(self, fileName, className=""):
        dataset = gdal.Open('%s%s' %(ManageRasterData.RASTER_DATA_LOCATION, fileName), GA_ReadOnly)
        columns = dataset.RasterXSize
        rows = dataset.RasterYSize
        noOfBands = dataset.RasterCount
        dataFromEachBand = []
        rasterArray = []   
    
        for eachBand in range(1, noOfBands+1):
            dataFromEachBand.append(dataset.GetRasterBand(eachBand).ReadAsArray(0,0,columns,rows))
            
        tempArray = []
        
        if className=="":
            for i in range(rows):
                for j in range (columns):
                    for k in range(noOfBands):
                        tempArray.append(dataFromEachBand[k][i][j])
                    rasterArray.append(tempArray)
                    tempArray=[]
        else:
            for i in range(rows):
                for j in range (columns):
                    for k in range(noOfBands):
                        tempArray.append(dataFromEachBand[k][i][j])
                    tempArray.append(className)
                    rasterArray.append(tempArray)
                    tempArray=[]
        
        return rasterArray
    
    def convert_raster_to_csv_file(self, fileName, targetFileLocation):
        rasterToArray = self.convert_raster_to_array(fileName)
        CSVfileName = fileName.split('.', 1)[0] + ".csv"
        
        with BufferedWriter( FileIO( '%s/%s' % (targetFileLocation, CSVfileName), "wb" ) ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            for i in range(len(rasterToArray)):
                spamwriter.writerow(rasterToArray[i])

# The method combines multiple training raster files to create a csv file. Here we assume that each file has same number of bands. 
# Each pixel is stored as a row in the csv file along with its class attribute. The class name is taken from the raster file name.         
    def combine_multiple_raster_files_to_csv_file(self, targetFileName, targetFileLocation):
        
        columns, rows, noOfBands, driver, originX, originY, pixelWidth, pixelHeight, prj = self.extract_raster_info(self.raster_files[0])
        
        with BufferedWriter( FileIO( '%s/%s' % (targetFileLocation, targetFileName), "wb" ) ) as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            
            if noOfBands == 3:
                spamwriter.writerow(['band1', 'band2', 'band3', 'class'])
            else:
                spamwriter.writerow(['band1', 'band2', 'band3', 'band4', 'band5', 'band6', 'band7', 'band8', 'class'])
            csvfile.close();
        
    
            for eachFile in self.raster_files:
                className = eachFile.split('.', 1)[0]
                rasterArray = self.convert_raster_to_array(eachFile, className)
                  
                with BufferedWriter( FileIO( '%s%s' % (targetFileLocation, targetFileName), "a" ) ) as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',')
                    for i in range(len(rasterArray)):
                        spamwriter.writerow(rasterArray[i])
                    csvfile.close();
                
    
    
    def convert_raster_csv_file_to_array(self, fileName, fileLocation, rows, columns, numOfBands):
        with open('%s%s' % (fileLocation, fileName ), 'rU') as datafile:
            dataReader = csv.reader(datafile, delimiter=',', quoting=csv.QUOTE_NONE)
            each_band_array = [[0 for i in range(columns)] for j in range(rows)]
            final_array = [each_band_array for band in range(numOfBands)]
            checkColumns=0
            k=0
            for row in dataReader:
                for band in range(numOfBands):
                    final_array[band][k][checkColumns] = row[band]
                checkColumns=checkColumns+1
                if checkColumns==columns:
                    k=k+1
                    checkColumns=0
            return final_array
    
    def find_and_replace_data_in_csv_file(self, configFile, srcFile, srcFileLocation, dstFile, dstFileLocation):
        config = open(configFile, 'r')
        findList = config.readline().split(";")
        replaceList = config.readline().split(";")
        config.close()
        
        inputfile = open('%s%s' % (srcFileLocation, srcFile), 'rb')
        outputfile = open('%s/%s' % (dstFileLocation, dstFile), 'wb')
        
        inputReader = inputfile.read()
        for item, replacement in zip(findList, replaceList):
            inputReader = inputReader.replace(item, replacement)
        outputfile.write(inputReader)
        inputfile.close()
        outputfile.close()
    
    def create_raster_from_csv_file(self, csvFile, referenceRasterFile, csvFileLocation, outputRasterFileName, outputRasterFileLocation):
        columns, rows, noOfBands, driver, originX, originY, pixelWidth, pixelHeight, prj = self.extract_raster_info(referenceRasterFile)
        rasterBandValuesArrays = self.convert_raster_csv_file_to_array(csvFile, csvFileLocation, rows, columns, 3)
        
        driver = gdal.GetDriverByName('GTiff')
        driver.Register()
        outRaster = driver.Create('%s%s' % (outputRasterFileLocation, outputRasterFileName), columns, rows, 3, gdal.GDT_Byte )
        outRaster.SetGeoTransform((originX, pixelWidth, 0.0, originY, 0.0, pixelHeight))
        outbandR = outRaster.GetRasterBand(1)
        outbandG = outRaster.GetRasterBand(2)
        outbandB = outRaster.GetRasterBand(3)
        
        outbandR.WriteArray(np.array(rasterBandValuesArrays[0], dtype=np.uint8))
        outbandG.WriteArray(np.array(rasterBandValuesArrays[1], dtype=np.uint8))
        outbandB.WriteArray(np.array(rasterBandValuesArrays[2], dtype=np.uint8))
        outRaster.SetProjection(prj)
        outbandR.FlushCache()
        outbandG.FlushCache()
        outbandB.FlushCache()
    
    
        

#b= ManageRasterData("final3b.tif")
#b.convert_raster_csv_file_to_array("final3b.csv", "static/predictedvaluesinnumbers/", 865, 1171, 3)
    
    
    
    