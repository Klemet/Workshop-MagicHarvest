# Using Magic Harvest in practice
**Authors:** Clément Hardy<sup>1</sup> \
**Affiliations:** <sup>1</sup>Université du Québec en Outaouais (UQO)\

[![Made with MyST](https://img.shields.io/badge/made%20with-myst-orange)](https://myst.tools)

## Getting on the field !

![](./images/Slide22.jpg)</br>

Here, we're going to see the more technical details of using Magic Harvest :

- How to access the state of the LANDIS-II landscape in a Python or R script run with Magic Harvest ?
- How to edit the parameter files of Biomass Harvest to control harvesting ?
- Etc.

## Looking at some example files for a simple simulation

![](./images/Slide23.jpg)</br>

First of all, I'm going to show you some screenshots of a test scenario with Magic Harvest, with [the test files that are on the repository of Magic Harvest](https://github.com/Klemet/LANDIS-II-Magic-Harvest/tree/main/Examples/Core-v8/Biomass%20Harvest). Just so that you have a visual idea of what it looks like in action.

Here is the scenario file that we have quickly seen before; as you see, Magic Harvest is indicated before B. Harvest, and the disturbance order is not random. The path points to the parameter text file of magic harvest. Here is the magic harvest parameter file, that we also have seen before; it's very simple, and launches a Python script that simply switches the name of files to activate a different B. Harvest parameter text files. 

* * *

![](./images/Slide24.jpg)</br>

Here is the Python script launched by Magic Harvest everytime it runs. You see, it's very simple. It simply renames files to switch between two sets of input files for B. Harvest. This is one of the simplest ways you can influence B. Harvest; you don't even edit files, you just switch them.

* * *

![](./images/Slide25.jpg)</br>

And finally, here is the log of LANDIS-II when it is running. As you see, Magic Harvest writes in the log when it activates, when it's done running, and when it re-loads the parameters of B. Harvest. We can even see the "print" statements that come from the Python script, and which indicate what the script is doing ! **This is great for debugging**. If B. Harvest is not installed or used in the simulation, Magic Harvest will warn you of it.

:::{caution}
The print statements from your R or Python script will not be recorded in the LANDIS-II log text file that LANDIS-II generates during the simulation. But they will be seen in your console.
:::

## Taking a look at a Python script template

![](./images/Slide26.jpg)</br>

Now, I'm going to show you a "template" of a Python script I've been using in my PhD thesis and my post-doctoral work. This template reads the state of the landscape and other things, and then writes some files to give to B. Harvest. The rest (the management decisions based on the state of the landscape) are up to you to write. We'll use this template as a base for the following exercice. [You can download the full file here](./files/magicHarvest_pythonTemplate.py).

So first off, a warning : **the template I'm about to show you is complex**, even though I have removed any management decisions. You have to understand that I've spent years working on this script through two chapters of my thesis, and then my post-doc work. It's full of functions made to do things quickly and in an optimized way. It's also made to adapt to the pretty complex forms of management decision I've been making. So what I am about to show you is going to be overwelming. As such, **I propose that you to not try to understand or read or remember everything**. In the future, you might use this template for your own work; it is very heavily commented, and you will have the time to understand it piece by piece. **Here, I simply want to give you a glimpse under the hood to show you what the engine can look like**.

You might also feel like it's not normal for this methodology to get this complicated; that Magic Harvest is nice, but that this is just too much work and complexity. It's something I have often felt when working on this. But here, we are working a trade-off : Magic Harvest allow us to become free from the restrictive and pre-defined algorithms of LANDIS-II and do whatever we want, which is essential to our research; but the trade-off is that we have to write the code for that, and it gets complex; just like the code inside LANDIS-II is. It's just that usually, we don't touch the LANDIS-II code as users. Here, we have to code everything. That's the trade-off.

We could, of course, code a whole new harvest extension for LANDIS-II instead of using a script like this; but this become restrictive again because you have to deal with the complex building process of extensions in the C# langage that LANDIS-II uses, you have to maintain them, and then future users become restricted by your algorithm. By using R or Python scripts, we can use simpler programming langages that most ecologist know to some degree, and we can share our scripts easily, and they can be re-used easily. So, no solution is perfect; but while this one is complex, it works realiably and gives us a high level of control.

So, ready ? Let's dig in.

### Defining functions for everything

The beginning of this template is simply a section where a lot of functions are defined so that we can use them afterwards. I really advise you define functions like this. It makes the rest of the code much clearer. In Python, it is really easy to describe each function you're writting, in particular its inputs and outputs, via a "docstring", a string of text that documents the function. Modern text editors allow you to write it quickly. AI can write it for you too.

Here is an example in the script :

```python
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
```

There's a lot of functions here. The first ones are used to easily read and write raster map data. When we read raster map data, we put it in a "numpy" array - numpy being a very famous Python package that allows for extremely efficient vectorial, matricial, or generally multi-dimensional array computation. So we put the values of the raster in a 2-dimensional array.

```python
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
```

Then, we have functions that read the state and structure of the landscape in LANDIS-II. To do that, we use input and output raster maps and files from LANDIS-II that will be in our simulation folder. Of course, when LANDIS-II runs, it has its own internal variables that contain the information on the landscape; but sadly, we cannot access these. These variables are contained in the RAM of your computer, and they are only accessible to the program. Since the script we are using is outside LANDIS-II - it's run through Python, not LANDIS-II -, then we cannot access these internal variables of LANDIS-II.

But that's fine, because we can use output extensions and some input files of LANDIS-II to get everything we need.

For example, to get the forest stands in the landscape, we can read the map of forest stands - the one that is usually given to B. Harvest.

```python
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
```

For informations about the harvest prescriptions, we can simple "parse" the B. Harvest parameters text file. This is a bit more tricky, but the function is already there, and allows us to put all informations into a Python dictionnary. The dictionnaries of Python is an object that I love very much and use very often : it simply associate an object (e.g. a number, a sentence or a word, or any other object) with another. Here, by reading the harvest parameter text file, I created a big dictionnary that contains the information and rules about each prescription in there. This can be useful, for example, to estimate how much biomass these prescription will harvest in the cells. Making this estimation can be used to know if we have reached the targets we have for the current timestep.

```python
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
```

Now, I've shown a function to read the stands, and one to read the B. Harvest parameter text file; but how do we get the vegetation data ? How do we know exactly what's inside each cell in the landscape ? The age cohorts and their biomass ? Took me a while, but I found a great way. There is an output extension called [Biomass Community Output](https://github.com/LANDIS-II-Foundation/Extension-Output-Biomass-Community) that, at each time step, exports the entire landscape as a raster map + a communities csv file that is exactly like the ones that are used for the initial conditions of LANDIS-II. These files are very large, as they contain the most "raw" data that LANDIS-II can output. But with a bit of optimisation, Python can read them very quickly and put them into a dictionnary. In this dictionnary, we can access the age cohorts of each pixels of a given stand, their age, and their biomass. That gives us all of the information we will ever need to make management decisions.

```python
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
```

We then have other functions that can retrieve data we might need for management decisions : 

- Getting the biomass of a list of species we want to harvest in a stand (based on the vegetation data we have put in a dictionnary).reading the age of the stands (to see what stand are the oldest)



- Reading the management unit associated to each stand (remember that we are going to give non-sensical management area maps to B. Harvest if we want to control its behaviour, but we might still want to use management areas in our Python script to make our management decisions)



- A function to write in the raster map that we are going to create what pixels will be harvested with a given prescriptios


- A function to get what are the stands that are the neighbours of a stand if we want to propagate a cut accross several stand



- A function to propagate the cuts from stand to stand until we reach a certain size


There are other functions that I won't discuss here.



