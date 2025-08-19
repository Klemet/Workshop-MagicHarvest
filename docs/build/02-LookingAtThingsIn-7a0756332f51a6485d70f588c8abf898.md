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




