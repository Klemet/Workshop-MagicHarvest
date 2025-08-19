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

