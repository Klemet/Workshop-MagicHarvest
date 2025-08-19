# -*- coding: utf-8 -*-
"""
@author: Clément Hardy, PhD.
# -*- coding: utf-8 -*-

Goal : This is a script for the Magic Harvest
extension for LANDIS-II.

It contains a template for using Magic Harvest easily in different landscapes

"""

#%% IMPORTING MODULES

import sys, os, csv, json
import pandas as pd
from osgeo import gdal
from osgeo import ogr
import numpy as np
from tqdm import tqdm
import statistics
from collections import Counter
import random
import shutil
import pickle

#%% FUNCTIONS

def getRasterData(path):
    raster = gdal.Open(path)
    rasterData = raster.GetRasterBand(1)
    rasterData = rasterData.ReadAsArray()
    return(np.array(rasterData))

def getRasterDataAsList(path):
    return(getRasterData(path).tolist())

def writeNewRasterData(rasterDataArray, pathOfTemplateRaster, pathOfOutput):
    # Saves a raster in int16 with a nodata value of 0
    # Inspired from https://gis.stackexchange.com/questions/164853/reading-modifying-and-writing-a-geotiff-with-gdal-in-python
    # Loading template raster
    template = gdal.Open(pathOfTemplateRaster)
    driver = gdal.GetDriverByName("GTiff")
    [rows, cols] = template.GetRasterBand(1).ReadAsArray().shape
    outputRaster = driver.Create(pathOfOutput, cols, rows, 1, gdal.GDT_Int16)
    outputRaster.SetGeoTransform(template.GetGeoTransform())##sets same geotransform as input
    outputRaster.SetProjection(template.GetProjection())##sets same projection as input
    outputRaster.GetRasterBand(1).WriteArray(rasterDataArray)
    outputRaster.GetRasterBand(1).SetNoDataValue(0)##if you want these values transparent
    outputRaster.FlushCache() ##saves to disk!!
    outputRaster = None
    
def writeNewRasterDataFloat32(rasterDataArray, pathOfTemplateRaster, pathOfOutput):
    # Saves a raster in Float32 with a nodata value of 0.0
    # Inspired from https://gis.stackexchange.com/questions/164853/reading-modifying-and-writing-a-geotiff-with-gdal-in-python
    # Loading template raster
    template = gdal.Open(pathOfTemplateRaster)
    driver = gdal.GetDriverByName("GTiff")
    [rows, cols] = template.GetRasterBand(1).ReadAsArray().shape
    outputRaster = driver.Create(pathOfOutput, cols, rows, 1, gdal.GDT_Float32)
    outputRaster.SetGeoTransform(template.GetGeoTransform())##sets same geotransform as input
    outputRaster.SetProjection(template.GetProjection())##sets same projection as input
    outputRaster.GetRasterBand(1).WriteArray(rasterDataArray)
    outputRaster.GetRasterBand(1).SetNoDataValue(0)##if you want these values transparent
    outputRaster.FlushCache() ##saves to disk!!
    outputRaster = None

def writeExistingRasterData(rasterDataArray, pathOfRasterToEdit):
    # Edits the data of an existing raster
    rasterToEdit = gdal.Open(pathOfRasterToEdit, gdal.GF_Write)
    rasterToEdit.GetRasterBand(1).WriteArray(rasterDataArray)
    rasterToEdit.FlushCache() ##saves to disk!!
    rasterToEdit = None

# From https://pynative.com/python-write-list-to-file/
# write list to binary file
def write_list(a_list, filePath):
    # store list in binary file so 'wb' mode
    with open(filePath, 'wb') as fp:
        pickle.dump(a_list, fp)
        print('List saved at path :' + str(filePath))

# Read list to memory
def read_list(filePath):
    # for reading also binary mode is important
    with open(filePath, 'rb') as fp:
        n_list = pickle.load(fp)
        return n_list

def readingStandsCoordinates(standRasterDataAll, disableTQDM):
    '''Reads the stands map to get the coordinates of each pixel in a stand.
    Returns a dictionnary giving the coordinates for each pixel for a given
    stand ID. Locations are in (row, column) tuple format, as necessary to
    access a value in a numpy array made from a raster by Rasterio.
    standRasterDataAll must be a numpy array contained the data from your raster map.'''
    print("Reading stands coordinates...")
    standCoordinatesDict = dict()
    uniqueAllStandsID = np.unique(standRasterDataAll).tolist()
    # id 0 for stands = no forests
    uniqueAllStandsID.remove(0)
    for standID in tqdm(uniqueAllStandsID, disable = disableTQDM):
        # print(standID)
        standCoordinatesDict[standID] = list()
    for x in tqdm(range(standRasterDataAll.shape[0]), disable = disableTQDM):
        for y in range(standRasterDataAll.shape[1]):
            standID = standRasterDataAll[(x, y)]
            if standID != 0:
                standCoordinatesDict[standID].append((x, y))
    return(standCoordinatesDict)

def splitLineAndRemoveTabsAndSpaces(lineString):
    """
    Used to parse certain lines of the biomass harvest txt parameter file
    (see harvestParameterFileParser).
    """
    lineStringList = lineString.replace('\t', ' ').replace("\n", "").replace(">>", "").split(" ")
    while "" in lineStringList:
        lineStringList.remove("")
    return(lineStringList)

def harvestParameterFileParser(path):
    """
    Parses the biomass harvest parameter file at the given path.
    Returns a dictionnary with the needed parameters.
    
    WARNING : To read the harvest file properly, make sure to :
    - Not use relative number of cohorts harvested for a given species, like
      "1/2" or "1/3". Since this script is made to be used with biomass harvest,
      use things like "11-999(50%)" to harvest half of the biomass of each cohort.
    - Make sure the biomass percentages are not separated from their respective
      age class, meaning write "11-999(50%)" rather than "11-999 (50%)"
    """
    print("Reading harvest parameter file...")
    
    dictToReturn = dict()
    
    speciesList = ["ABIE.BAL","ACER.RUB","ACER.SAH","BETU.ALL","BETU.PAP",
                   "FAGU.GRA","LARI.LAR","LARI.HYB","PICE.GLA","PICE.MAR",
                   "PICE.RUB","PINU.BAN","PINU.RES","PINU.STR","POPU.TRE",
                   "POPU.HYB","QUER.RUB","THUJ.SPP.ALL","TSUG.CAN"]
    
    with open(path, 'r') as file:
        prescriptionSelected = "none"
        prescriptionID = 1 # We start at 1 because the ID is for the raster;
        # 0 = not forest, 1 = forest not harvested, and then it's the prescriptions.
        for line in file:
            # print(line)
            # We start by recording the lines if we're reading a prescription
            if prescriptionSelected != "none" and "Prescription " not in line:
                dictToReturn[prescriptionSelected]["FullString"].append(line)
            if ">>-------------" in line:
                prescriptionSelected = "none"
                
            # We get the timestep used by the extension
            if "Timestep" in line:
                timestepLength = int(splitLineAndRemoveTabsAndSpaces(line)[1])
            # If we find a new prescription, we initialize everything needed
            if "Prescription " in line:
                prescriptionSelected = line[len("Prescription "):-1] #-1 removes the \n character at the end of each line
                if prescriptionSelected not in dictToReturn:
                    dictToReturn[prescriptionSelected] = dict()
                    dictToReturn[prescriptionSelected]["Planting"] = "none"
                    dictToReturn[prescriptionSelected]["RepeatMode"] = "none"
                    dictToReturn[prescriptionSelected]["MaximumStandAge"] = 999
                    dictToReturn[prescriptionSelected]["MinimumStandAge"] = 0
                    dictToReturn[prescriptionSelected]["Commercial"] = True # Does it generate merchantable wood ?
                    dictToReturn[prescriptionSelected]["FullString"] = [line] # We keep all the lines of the prescription to be able to copy it to make different plantings
                    prescriptionID += 1
                    dictToReturn["_MaxPrescriptionID"] = prescriptionID # Special counter used to create new planting prescriptions later
                    dictToReturn[prescriptionSelected]["PrescriptionID"] = prescriptionID
                singleRepeat = False
            
            # Else, we register the parameters of the prescription
            elif "MaximumAge" in line:
                maximumAge = splitLineAndRemoveTabsAndSpaces(line)[1]
                dictToReturn[prescriptionSelected]["MaximumStandAge"] = int(maximumAge)
            elif "MinimumAge" in line:
                minimumAge = splitLineAndRemoveTabsAndSpaces(line)[1]
                dictToReturn[prescriptionSelected]["MinimumStandAge"] = int(minimumAge)
            elif "SiteSelection" in line:
                # The line contains 2 words + the two numerical values we want
                # We remove everything we don't need to get the two values
                splittedLine = splitLineAndRemoveTabsAndSpaces(line)
                # print(splittedLine)
                dictToReturn[prescriptionSelected]["HarvestPropagation"] = [float(splittedLine[2]), float(splittedLine[3])]
            elif "CohortsRemoved" in line and not singleRepeat:
                dictToReturn[prescriptionSelected]["CohortRemoved"] = dict()
            elif "Planting" in line:
                plantingString = splitLineAndRemoveTabsAndSpaces(line)[1]
                dictToReturn[prescriptionSelected]["Planting"] = plantingString
            elif "Commercial" in line and "FALSE" in line.upper():
                dictToReturn[prescriptionSelected]["Commercial"] = False
            elif "SingleRepeat" in line:
                singleRepeat = True
                dictToReturn[prescriptionSelected]["CohortRemoved"]["SingleRepeat"] = dict()
                dictToReturn[prescriptionSelected]["RepeatMode"] = "SingleRepeat"
                repeatFrenquency = splitLineAndRemoveTabsAndSpaces(line)[1]
                dictToReturn[prescriptionSelected]["RepeatFrequency"] = int(repeatFrenquency)
            elif "MultipleRepeat" in line:
                dictToReturn[prescriptionSelected]["RepeatMode"] = "MultipleRepeat"
                repeatFrenquency = splitLineAndRemoveTabsAndSpaces(line)[1]
                dictToReturn[prescriptionSelected]["RepeatFrequency"] = int(repeatFrenquency)
                
            # If we get to the part about the cohort removed, it's a bit more tricky
            # to register
            # In particular, we will register the cohort removed in the case of a
            # second pass (via SingleRepeat) in a different nested dictionnary
            for species in speciesList:
                if species in line and "Prescription " not in line and "Plant" not in line:
                    if not singleRepeat:
                        dictToReturn[prescriptionSelected]["CohortRemoved"][species] = dict()
                    else:
                        dictToReturn[prescriptionSelected]["CohortRemoved"]["SingleRepeat"][species] = dict()
                    # 3 cases :
                    # just ages (11-999)
                    # "All" keyword
                    # ages categories with biomass percent (11-999(90%))
                    # print(line)
                    if "/" in line: # Just in case their are relative cohort numbers in the file
                        raise ValueError("Do not use relative number of cohort harvested for a given species, like \"1/2\" or \"1/3\". Since this script is made to be used with biomass harvest, use things like \"11-999(50%)\" to harvest half of the biomass of each cohort.")
                    elif "All" in line or "all" in line:
                        if not singleRepeat:
                            dictToReturn[prescriptionSelected]["CohortRemoved"][species] = "All"
                        else:
                            dictToReturn[prescriptionSelected]["CohortRemoved"]["SingleRepeat"][species] = "All"
                    else: # If not all, we have to break appart the age categories
                        if not singleRepeat:
                            dictToReturn[prescriptionSelected]["CohortRemoved"][species] = list()
                        else:
                            dictToReturn[prescriptionSelected]["CohortRemoved"]["SingleRepeat"][species] = list()
                        splittedLine = splitLineAndRemoveTabsAndSpaces(line)
                        # print(splittedLine)
                        for ageCategory in splittedLine[1:]:
                            if "%" not in ageCategory:
                                splitAgeCategory = ageCategory.split("-")
                                # We add a list describing 1) min age of category 2) max age of category 3) % of biomass harvested
                                if not singleRepeat:
                                    dictToReturn[prescriptionSelected]["CohortRemoved"][species].append([int(splitAgeCategory[0]), int(splitAgeCategory[1]), 100])
                                else:
                                    dictToReturn[prescriptionSelected]["CohortRemoved"]["SingleRepeat"][species].append([int(splitAgeCategory[0]), int(splitAgeCategory[1]), 100])
                            else:
                                splitAgeCategory = ageCategory.replace("(", "-").replace("%)", "").split("-")
                                if not singleRepeat:
                                    dictToReturn[prescriptionSelected]["CohortRemoved"][species].append([int(splitAgeCategory[0]), int(splitAgeCategory[1]), int(splitAgeCategory[2])])
                                else:
                                    dictToReturn[prescriptionSelected]["CohortRemoved"]["SingleRepeat"][species].append([int(splitAgeCategory[0]), int(splitAgeCategory[1]), int(splitAgeCategory[2])])
                        
            if "HarvestImplementations" in line:
                break
                
    return(dictToReturn, timestepLength)

def readCommunitiesComplete(communityCsvPath,
                            communityMapPath,
                            standCoordinatesDict,
                            disableTQDM):
    """
    Reads the communities csv and raster map made by Output Biomass Community
    to make a dictionnary containing the species and age cohorts for each
    species and biomass for these cohorts for all of the pixels of a stand.
    WARNING : the dictionnary doesn't contain entries for stands that have
    no cohorts/no biomass, and no entries for species that are not in a stand
    or cohorts that do not exist for a species. This saves on a lot of space,
    but one got to check if the entries are there when using the dictionnary.
    """

    # communityCsvPath = "./community-input-file-" + str(timestep) + ".csv"
    # communityMapPath = "./output-community-" + str(timestep) + ".img"
    print("Reading communities csv and map...")
    # We only need the mapcode column from the csv from now.
    communityCsv = pd.read_csv(communityCsvPath, usecols=['MapCode'])
    communityMapCodeData = getRasterData(communityMapPath)

    # We make the dictionnary of the amount of times a stand is associated
    # to a mapcode
    print("Creating mapcode community dictionnary...")
    dictMapCodeStands = dict()
    for uniqueMapCode in communityCsv["MapCode"].unique():
        dictMapCodeStands[uniqueMapCode] = dict()
        
    for standID in standCoordinatesDict.keys():
        for pixel in standCoordinatesDict[standID]:
            mapcode = communityMapCodeData[pixel]
            # If the mapcode is not already in the dictionnary, it was not in
            # the CSV; and if it's not in the CSV, it's because it's a mapcode
            # associated to no cohorts at all(total biomass of 0)
            if mapcode in dictMapCodeStands:
                if standID not in dictMapCodeStands[mapcode]:
                    dictMapCodeStands[mapcode][standID] = 1
                else:
                    dictMapCodeStands[mapcode][standID] += 1
    
    # Now, we can read the CSV file and fill in a second dictionnary with the
    # information for each stand
    # To lighten it, we won't put stands that have no biomass
    # (IMPORTANT FOR OTHER FUNCTIONS : have to check if stand is in dictionnary)
    print("Creating stand community dictionnary...")
    
    standCommunitiesDict = dict()
    with open(communityCsvPath, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Read the header row
        for row in tqdm(reader, total=len(communityCsv["MapCode"]), disable = disableTQDM):
            # 0 is mapcode; 1 is species; 2 is cohort; 3 is biomass.
            for standID in dictMapCodeStands[int(row[0])]:
                if standID not in standCommunitiesDict:
                    standCommunitiesDict[standID] = dict()
                    standCommunitiesDict[standID][row[1]] = dict()
                    standCommunitiesDict[standID][row[1]][int(row[2])] = 0
                # If species not indicated for this stand, we put it
                elif row[1] not in standCommunitiesDict[standID]:
                    standCommunitiesDict[standID][row[1]] = dict()
                    standCommunitiesDict[standID][row[1]][int(row[2])] = 0
                # If age cohort not indicated for this stand/species, we put it
                elif int(row[2]) not in standCommunitiesDict[standID][row[1]]:
                    standCommunitiesDict[standID][row[1]][int(row[2])] = 0
                # Finally, we enter the biomass for the stand/species/cohort
                # If the stand has multiple pixel with this mapcode, we multiply
                # the biomass with the number of pixels
                # WARNING : Need to transform biomass from g/m2 to Mg/ha by dividing by 100
                standCommunitiesDict[standID][row[1]][int(row[2])] += (int(row[3])/100)*dictMapCodeStands[int(row[0])][standID]
        
    return(standCommunitiesDict)
    
def GetBiomassInstand(standCompositionDict, standID, listOfSpecies):
    """Retrieves the total biomass in a stand for a list of species.
    Returns a single biomass value."""
    sumOfBiomass = 0
    for species in listOfSpecies:
        if species in standCompositionDict[standID]:
            sumOfBiomass += sum(standCompositionDict[standID][species].values())
    return(sumOfBiomass)

def readingStandsAges(standMapPath, maxAgeMapsFolderPath, timestep, timestepLength, disableTQDM):
    '''Uses the stand maps and max age map to compute the mean age of each stand
    (average of the age of the oldest cohorts in each pixels of the stand).
    Returns a dictionnary associating an age to a stand ID.
    The max age map is taken from the previous timestep to the current one.'''
    print("Reading stands age...")
    
    standData = getRasterData(standMapPath)
    uniqueAllStandsID = np.unique(standData).tolist()
    # id 0 for stands = no forests
    uniqueAllStandsID.remove(0)
    cohortMaxAgeData = getRasterData(maxAgeMapsFolderPath + "AGE-MAX-" + str(timestep - timestepLength) + ".img")
    maxAgeDict = dict()
    # Little trick to use the power of numpy below
    # We make an array with the pixels we want the value of, and another
    # with the values
    pixelCoordinates = np.where(standData != 0)
    standIDinPixelCoordinates = standData[pixelCoordinates]
    for standID in tqdm(uniqueAllStandsID, disable = disableTQDM):
        maxAgeDict[standID] = list()
    # We get the data for the harvestable pixels
    cohortMaxAgeInForestPixel = cohortMaxAgeData[pixelCoordinates]
    # We fill the dictionnary with the different values of max cohort age for each
    # pixels in a stand
    for i in tqdm(range(0, len(pixelCoordinates[0])), disable = disableTQDM):
        maxAgeDict[standIDinPixelCoordinates[i]].append(cohortMaxAgeInForestPixel[i])
    # We make a dictionnary containing the mean max age for each stand
    standAgeDict = dict()
    for standID in tqdm(uniqueAllStandsID, disable = disableTQDM):
        standAgeDict[standID] = statistics.mean(maxAgeDict[standID])
    return(standAgeDict)

def readingStandManagementUnit(standMapPath, managementUnitsMapPath, disableTQDM):
    '''Assign a management unit (UA) code to each stand. This is not used to define
    management units per say in our landscape, but rather to get the conversion
    values from raw to net merchantable volume harvested, based on data from
    the ministry of forest (the data changes by species and by management unit).
    See coefficientRawToNetVolumes object for more info.'''
    print("Reading stands management units (used for volume conversion)...")
    
    standData = getRasterData(standMapPath)
    uniqueAllStandsID = np.unique(standData).tolist()
    # id 0 for stands = no forests
    uniqueAllStandsID.remove(0)
    managementUnitsMap = getRasterData(managementUnitsMapPath)
    managementUnitDict = dict()
    # Little trick to use the power of numpy below
    # We make an array with the pixels we want the value of, and another
    # with the values
    pixelCoordinates = np.where(standData != 0)
    standIDinPixelCoordinates = standData[pixelCoordinates]
    for standID in tqdm(uniqueAllStandsID, disable = disableTQDM):
        managementUnitDict[standID] = list()
    # We get the data for the harvestable pixels
    managementUnitInPixel = managementUnitsMap[pixelCoordinates]
    # We fill the dictionnary with the different values of max cohort age for each
    # pixels in a stand
    for i in tqdm(range(0, len(pixelCoordinates[0])), disable = disableTQDM):
        managementUnitDict[standIDinPixelCoordinates[i]].append(managementUnitInPixel[i])
    # We make a dictionnary containing the mean max age for each stand
    standManagementUnitDict = dict()
    for standID in tqdm(uniqueAllStandsID, disable = disableTQDM):
        standManagementUnitDict[standID] = Counter(managementUnitDict[standID]).most_common(1)[0][0]
    return(standManagementUnitDict)

def harvestStands(managementMap, standsList, standCoordinatesDict, prescriptionID):
    """Edits the management map to indicate a list of stands as harvested with
    a given prescription ID. Returns the modified management map."""
    numberOfPixelsHarvested = 0
    for standID in standsList:
        for pixel in standCoordinatesDict[standID]:
            managementMap[pixel] = prescriptionID
            numberOfPixelsHarvested += 1
    return(managementMap, numberOfPixelsHarvested)

def DetermineForestTypesOfStands(standCompositionDict,
                                 standCoordinatesDict,
                                 disableTQDM = True):
    """
    Determines the forest type (deciduous, confirous or mixed) of the stand.
    Needed to know what prescription is more adapted to it.
    The list of species for each is currently hard coded here, and should
    be changed for other studies areas.
    The code for each type (F, R, M) currently represent the ones used
    in the ministry of forests of Quebec's ecoforest polygons.
    """
    print("Computing the forest type (deciduous, coniferous or mixed) of stands...")

    # Here, replace by the species you are using.
    deciduousSpecies = ["ACER.RUB","ACER.SAH","BETU.ALL","BETU.PAP",
                        "FAGU.GRA", "POPU.TRE", "POPU.HYB","QUER.RUB",]
    coniferousSpecies = ["ABIE.BAL", "LARI.LAR","LARI.HYB","PICE.GLA","PICE.MAR",
                         "PICE.RUB","PINU.BAN","PINU.RES","PINU.STR", "THUJ.SPP.ALL",
                         "TSUG.CAN"]

    dictForestTypes = dict()
    for standID in tqdm(standCoordinatesDict.keys(), disable = disableTQDM):
        if standID not in standCompositionDict:
            dictForestTypes[standID] = "none"
        else:
            deciduousBiomass = GetBiomassInstand(standCompositionDict, standID, deciduousSpecies)
            coniferousBiomass = GetBiomassInstand(standCompositionDict, standID, coniferousSpecies)
            totalBiomass = deciduousBiomass + coniferousBiomass
            if deciduousBiomass/totalBiomass > 0.7:
                dictForestTypes[standID] = "F"
            elif coniferousBiomass/totalBiomass > 0.7:
                dictForestTypes[standID] = "R"
            else:
                dictForestTypes[standID] = "M"
                
    return(dictForestTypes)

def readingStandsNeighbors(standRasterDataAll,
                           standCoordinatesDict,
                           disableTQDM = True):
    '''Reads the neighbors of each stand by looking at the surrounding
    pixels of those of the stands, and getting their stand ID. Returns a dictionnary
    with the list of neighbors's stand ID for each stand.'''
    print("Reading stand neighbors...")
    
    # Making a dictionnary which tells what stand is a neighbor of which one.
    # We only need it for harvestable stands, since this is for the propagation
    # of cuts.
    standNeighboursDict = dict()
    minXRange = range(standRasterDataAll.shape[0])[0]
    maxXRange = range(standRasterDataAll.shape[0])[-1]
    minYRange = range(standRasterDataAll.shape[1])[0]
    maxYRange = range(standRasterDataAll.shape[1])[-1]
    for standID in tqdm(standCoordinatesDict.keys(), disable = disableTQDM):
        listOfNeighbouringStands = list()
        for pixel in standCoordinatesDict[standID]:
            listOfStandsAroundPixel = list()
            # We look at the 8 neighbors of the pixel, if not out of range,
            # to try to detect another stand number
            # First, we prepare the ranges around which we'll loop, and make sure
            # we're not out of bounds
            xMinus1 = max(pixel[0] - 1, minXRange)
            xPlus1 = min(pixel[0] + 1, maxXRange)
            yMinus1 = max(pixel[1] - 1, minYRange)
            yPlus1 = min(pixel[1] + 1, maxYRange)
            # Now, we loop to find values
            for x in [xMinus1, pixel[0], xPlus1]:
                for y in [yMinus1, pixel[1], yPlus1]:
                    listOfStandsAroundPixel.append(standRasterDataAll[(x, y)])
            uniqueNeighbouringStands = set(listOfStandsAroundPixel)
            # We remove mentions of the present stand and of the value 0
            uniqueNeighbouringStands.discard(standID)
            uniqueNeighbouringStands.discard(0)
            listOfNeighbouringStands.extend(list(uniqueNeighbouringStands))
        # We add the resulting unique standID that we found as neighbors to this stand
        standNeighboursDict[standID] = set(listOfNeighbouringStands)
    return(standNeighboursDict)
    
def standHarvestPropagation(standID,
                            prescription,
                            prescriptionParameters,
                            standNeighboursDict,
                            standCoordinatesDict,
                            standAgeDict):
    """
    Propagate a harvest prescription from a stand to the neigbouring stands,
    depending on the selection criteria + min/max harvest size for the
    prescription.
    Returns a list of harvested stands.
    """
    listOfHarvestedStands = list()
    frontier = [standID]
    surfaceHarvested = 0
    while surfaceHarvested < prescriptionParameters[prescription]["HarvestPropagation"][1] and len(frontier) > 0:
        focusStand = frontier.pop(0)
        # If we overeach the maximum surface, we stop here.
        if surfaceHarvested + len(standCoordinatesDict[focusStand]) > prescriptionParameters[prescription]["HarvestPropagation"][1]:
            break
        else:
            listOfHarvestedStands.append(focusStand)
            # TO UPDATE : Surface harvested here is dealt in pixels. But in harvest parameter
            # file, might be in different units than pixel. See how to adapt to that. Need cell length ?
            surfaceHarvested += len(standCoordinatesDict[standID])
            for neighbor in standNeighboursDict[focusStand] :
                if neighbor not in listOfHarvestedStands and standAgeDict[neighbor] > prescriptionParameters[prescription]["MinimumStandAge"] and standAgeDict[neighbor] < prescriptionParameters[prescription]["MaximumStandAge"]:
                   frontier.append(neighbor) 
    return(listOfHarvestedStands)

def writeHarvestParameterFile(managementMap,
                              folderWithDHarvestata,
                              templateHarvestFileName,
                              realHarvestFileName,
                              prescriptionParameters,
                              managementMapName,
                              timestep):
    '''Edits the template harvest extension parameter file with the new parameters
    created at this timestep by the script.'''
    print("Writing harvest parameter file...")
    
    # We get all of the unique prescription ID put in the map this timestep
    uniquePrescriptionsForTimestep = np.unique(managementMap)
    # We remove 0 from the prescriptions, as it's only indicative of no prescription
    uniquePrescriptionsForTimestep = np.delete(uniquePrescriptionsForTimestep, np.where(uniquePrescriptionsForTimestep == 0))
    # For each prescription, we write in the harvest.txt parameter file.
    # Whatever the timestep, we reset the harvest.txt file to the initial one, to fill
    # it up again.
    shutil.copyfile((os.getcwd() + folderWithDHarvestata + templateHarvestFileName),
                    (os.getcwd() + folderWithDHarvestata + realHarvestFileName))
    # We read the text of the parameter file
    BioHarvestParameterFile = open((os.getcwd() + folderWithDHarvestata + realHarvestFileName),'r')
    BioHarvestParameterFileText = BioHarvestParameterFile.readlines()
    
    # We prepare the lines that we will write to force the harvesting where we want it
    # We just create a dict to find the right prescription name for the ID in the map
    prescriptionsNameDict = dict()
    for prescription in prescriptionParameters:
        if prescription != "PlantingPrescriptions" and prescription != "_MaxPrescriptionID":
            prescriptionsNameDict[prescriptionParameters[prescription]["PrescriptionID"]] = prescription
    if "PlantingPrescriptions" in prescriptionParameters:
        for plantingPrescription in prescriptionParameters["PlantingPrescriptions"]:
            prescriptionsNameDict[prescriptionParameters["PlantingPrescriptions"][plantingPrescription]["PrescriptionID"]] = plantingPrescription
    # Now we insert the lines
    linesToInsert = list()
    for prescriptionID in uniquePrescriptionsForTimestep:
        linesToInsert.append("\t" + str(prescriptionID) +
                             "\t\t" + str(prescriptionsNameDict[prescriptionID]) +
                             "\t\t100%\t\t" +
                             str(timestep) + "\t" + str(timestep) + "\n")
    # We detect where we will write
    insertionLine = BioHarvestParameterFileText.index(">> Mgmt Area Prescription   Harvest Area   Begin Time   End Time\n") + 2
    # We reverse the list to keep the same order of writing in the final file
    linesToInsert.reverse()
    # We write the lines
    for line in linesToInsert:
        BioHarvestParameterFileText.insert(insertionLine, line)
        
    # We also write the lines with the plantation prescriptions
    if "PlantingPrescriptions" in prescriptionParameters: 
        linesToInsert = list()
        for prescription in prescriptionParameters["PlantingPrescriptions"]:
            linesToInsert.extend(prescriptionParameters["PlantingPrescriptions"][prescription]["FullString"])
            linesToInsert.append("\n\n")
        insertionLine = BioHarvestParameterFileText.index(">> PASTE_PLANTING_HERE\n")
        linesToInsert.reverse()
        for line in linesToInsert:
            BioHarvestParameterFileText.insert(insertionLine, line)
    
    # We finish by changing the name of the maps that we will give to Biomass harvest
    lineToChange = BioHarvestParameterFileText.index("ManagementAreas \"../../sharedRasters/management_areas_v1.0.tif\"\n")
    # We replace it
    BioHarvestParameterFileText[lineToChange] = "ManagementAreas \"" + managementMapName + "\"\n"
    # We also replace the name of the stand map
    # Actually, it causes errors with the system of partial stand spread ? To delete if resolved.
    # lineToChange = BioHarvestParameterFileText.index("Stands \"../../sharedRasters/stands_v2.0.tif\"\n")
    # BioHarvestParameterFileText[lineToChange] = "Stands \"" + managementMapName + "\"\n"
    # We save the parameter file
    BioHarvestParameterFile = open((os.getcwd() + folderWithDHarvestata + realHarvestFileName), "w")
    BioHarvestParameterFileText = "".join(BioHarvestParameterFileText)
    BioHarvestParameterFile.write(BioHarvestParameterFileText)

def WriteTableOfPrescriptionsID(pathToTable,
                                prescriptionParameters):
    """Writes a csv file that indicate the prescriptions IDs in the
    biomass harvest output maps."""
    print("Writing prescription ID table for Biomass Harvest output maps...")
    
    # We make a quick dictionnary giving the name of a prescription for the corresponding ID
    prescriptionsNameDict = dict()
    for prescription in prescriptionParameters:
        if prescription != "PlantingPrescriptions" and prescription != "_MaxPrescriptionID":
            prescriptionsNameDict[prescriptionParameters[prescription]["PrescriptionID"]] = prescription
    if "PlantingPrescriptions" in prescriptionParameters:
        for plantingPrescription in prescriptionParameters["PlantingPrescriptions"]:
            prescriptionsNameDict[prescriptionParameters["PlantingPrescriptions"][plantingPrescription]["PrescriptionID"]] = plantingPrescription
    # We make a sorted list of ID
    listOfID = list(prescriptionsNameDict.keys())
    listOfID = sorted(listOfID)
    listOfOuputs = list()
    listOfOuputs.append(["Prescription name", "Prescription ID"])
    for prescriptionID in listOfID:
        # We add +1 to the ID because in the outputs maps of Biomass Harvest,
        # 0 = Non forest, 1 = forest not harvested, and then it's the ID of each
        # prescription (their order in the harvest txt file) + 1.
        listOfOuputs.append([prescriptionsNameDict[prescriptionID], prescriptionID+1])
    
    # We write what we need for the .csv file
    with open(pathToTable, 'w+', newline='') as file:
        writer = csv.writer(file)
    
        # Write the data to the CSV file
        writer.writerows(listOfOuputs)
    
#%% DEBUG

# Just put "False" unless you're tinkering with this script.
debug = False
# debug = True

# If debugging, we prepare a dummy situation
if debug:
    os.chdir(r"path/to/your/folder/with/simulation/files/landis-ii")
    timestep = 15
    BAU_Modifier = 1
    disableTQDM = False
    import matplotlib.pyplot as plt
else:
    # If not debugging, this Python script is normally called in a command prompt by specifying
    # some arguments, like the location of the folders containing the files that
    # we need relative to the LANDIS-II scenario file
    if __name__ == "__main__":
        # Remember : argument at index 0 contains the program name.
        # The arguments that we want come after
        timestep = sys.argv[1]
        timestep = int(timestep)
        # You can retrieve other arguments here; just use sys.argv[2], sys.argv[3], etc. 
    # We disable the progress bars of TQDM to not display them in the LANDIS log
    disableTQDM = True

# Should you remove the community files made at each time step ? (they are heavy)
removeCommunitiesFiles = True

#%% DEFINING PARAMETERS FOR EACH PRESCRIPTION

# We read the template harvest parameter file, which also contains the parameters needed
# for magic harvest
prescriptionParameters, timestepLength = harvestParameterFileParser("./input/disturbances/harvesting/harvest_BAU_v2.0_TEMPLATE.txt")

#%% READING DATA FOR TIME STEP

# Reading files for stand coordinates
standRasterData = getRasterData("../../sharedRasters/stands_v2.0.tif")
standCoordinatesDict = readingStandsCoordinates(standRasterData,
                                                disableTQDM)

# Reading raster of Management units (UAs)
standUADict = readingStandManagementUnit("../../sharedRasters/stands_v2.0.tif",
                                         "../../sharedRasters/rasterUAInterpolated.tif",
                                         disableTQDM)

# Reading JSON files for repeated prescriptions
repeatPrescriptionPath = "./input/disturbances/harvesting/temp/repeatedPrescriptions.pickle"
if os.path.exists("repeatPrescriptionPath"):
    with open(repeatPrescriptionPath) as repeatedPrescriptionFile:
        pickle.load(repeatPrescriptionsDict, repeatedPrescriptionFile)
else:
    repeatPrescriptionsDict = "noRepeatsForNow"

# Reading vegetation communities
standCompositionDict = readCommunitiesComplete("./community-input-file-" + str(timestep- timestepLength) + ".csv",
                                            "./output-community-" + str(timestep- timestepLength) + ".img",
                                            standCoordinatesDict,
                                            disableTQDM)

# Reading stand ages
standAgeDict = readingStandsAges("../../sharedRasters/stands_v2.0.tif",
                         "./output/cohort-stats/",
                         timestep,
                         timestepLength,
                         disableTQDM)

# Determining forest types
forestTypesStandsDict = DetermineForestTypesOfStands(standCompositionDict,
                                                     standCoordinatesDict,
                                                     disableTQDM)

# Determining management unit for each stand (used for the conversion of
# raw to net merchantable volume harvested)

# stand neighbors dict (used for stand propagation)
standNeighboursDict = readingStandsNeighbors(standRasterData,
                                            standCoordinatesDict,
                                            disableTQDM)

# Removing vegetation communities files if needed
if not debug and removeCommunitiesFiles:
    if os.path.exists("./output-community-" + str(timestep- timestepLength) + ".img"):
        os.remove("./output-community-" + str(timestep- timestepLength) + ".img")
    if os.path.exists("./community-input-file-" + str(timestep- timestepLength) + ".csv"):
        os.remove("./community-input-file-" + str(timestep- timestepLength) + ".csv")
    if os.path.exists(("./community-input-file-" + str(timestep- timestepLength) + ".csv")[0:-3] + "txt"):
        os.remove(("./community-input-file-" + str(timestep- timestepLength) + ".csv")[0:-3] + "txt")

#%% PREPARING OTHER OBJECTS WE NEED

# We prepare the empty management map that we will fill with the values of the pixels where we want to harvest.
managementMap = np.zeros_like(getRasterData("../../sharedRasters/stands_v2.0.tif"))




#%% MAKING THE HARVEST DECISIONS

# This is where you should write functions that will define where you want to harvest.
# So, doing your repeated prescriptions, ranking the stands and then applying new prescriptions until you 
# reach a given target, etc., etc.








#%% OUTPUTS

# This is where we create the files that we will give back to Biomass Harvest

print("Creating outputs...")

# We prepare the folder with temporary files
if not os.path.exists("./input/disturbances/harvesting/tempMagicHarvest/"):
    os.mkdir("./input/disturbances/harvesting/tempMagicHarvest/")

# We save the pickle file with the data for the next repeated harvests
# Wanted to use JSON, but doesn't work well with the complex dictionnaries I use.
# WARNING : pickle is not human-readable. It is made to be read by a Python script.
if repeatPrescriptionsDict!= "noRepeatsForNow":
    with open('./input/disturbances/harvesting/tempMagicHarvest/repeatedPrescriptions.pickle', "wb+") as outfile:
        pickle.dump(repeatPrescriptionsDict, outfile)

# Create harvest maps
print("Magic harvest Python script : WRITING PRESCRIPTION MAP")
writeNewRasterData(managementMap,
                    "../../sharedRasters/stands_v2.0.tif",
                    "./input/disturbances/harvesting/tempMagicHarvest/prescriptions-" + str(timestep) + ".tif")

# Create harvest txt file
# We add to the txt file :
# - The new plantation prescriptions
# - The surface to harvest for each prescription ID / fake management areas to contrain harvesting
writeHarvestParameterFile(managementMap,
                            "/input/disturbances/harvesting/",
                            "harvest_BAU_v2.0_TEMPLATE.txt",
                            "harvest_BAU_v2.0.txt",
                            prescriptionParameters,
                            "./input/disturbances/harvesting/tempMagicHarvest/prescriptions-" + str(timestep) + ".tif",
                            timestep)

# Update table that gives the prescription names for each prescription ID
# for easy identification in GIS softwares of the harvest output maps
WriteTableOfPrescriptionsID("./input/disturbances/harvesting/tempMagicHarvest/prescriptionIDTable-" + str(timestep) + ".csv",
                            prescriptionParameters)

# We make a log of the harvested surfaces and volumes.
csvFileOutputPath = "./output/magicHarvest/logMagicHarvest.csv"


# If first timestep, we create the file.
if timestep == timestepLength:
    if os.path.exists(csvFileOutputPath):
        os.remove(csvFileOutputPath)
    
    # We make the output directories if they don't already exist
    if not os.path.exists(os.path.dirname(csvFileOutputPath)):
        os.makedirs(os.path.dirname(csvFileOutputPath))
        
    listOfHeaders = ["Timestep", "Surface Harvested"]
    for target in volumeTargetDicts:
        listOfHeaders.append("Volume " + str(target) + " harvested")
    
    with open(csvFileOutputPath, 'w+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(listOfHeaders)

# Then, we write the values
newRow = [str(timestep), str(np.count_nonzero(managementMap))]
for target in volumeTargetDicts:
    newRow.append(str(volumeTargetCounterDict[target]))
with open(csvFileOutputPath, 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(newRow)