# Introduction

**Authors:** Clément Hardy<sup>1</sup> \
**Affiliations:** <sup>1</sup>Université du Québec en Outaouais (UQO)\

[![Made with MyST](https://img.shields.io/badge/made%20with-myst-orange)](https://myst.tools)

This small website contains a workshop to help you use the [Magic Harvest](https://github.com/Klemet/LANDIS-II-Magic-Harvest) extension for the [LANDIS-II forest](https://www.landis-ii.org/) landscape model. It's simply an implementation of the powerpoint presentation I did in the summer of 2025 at the University of Toronto. You'll have both the slides and the text of the slides in a readable format.

## What is Magic Harvest ?

**Magic Harvest is a small extension that I develloped during my PhD thesis**. My work required me to compare the effect of several forest management scenarios in LANDIS-II; but at the time, LANDIS-II lacked several important features that I needed to implement forest management in the model. I created Magic Harvest in order to solve the issue.

![](./images/Slide2.jpg)</br>

**The Magic Harvest extension is both simple and complicated**. Simple, because its functionning can be summarized in two sentences : it's a companion extension for Biomass Harvest (the main harvest extension for LANDIS-II; the other ones are almost never used) who's goal is to run before Biomass Harvest. **When running, it will simply launch a custom command defined by the user - for example an R or Python script - and will then force Biomass Harvest to re-load its parameters**. That's it.

The complex part is understanding the consequences of this and learning to play with it. The consequences is that we can control what Biomass Harvest does at different degrees : complete and total control, or still letting Biomass Harvest do some choices based on its own algorithm. Learning to play with Magic Harvest mostly means learning to write scripts that will do what you want to do.


## Plan of the workshop

![](./images/Slide3.jpg)</br>

So today, we're going to see :
- How Magic Harvest works in a bit more details
- Some visual examples of how much control we can achieve
- Taking a look at a Python script I've made to use Magic Harvest
- And then do a couple of exercises together to get familliar with how to do what you want to do with it

We are not going to run Magic Harvest; you have test files accessible on the repository, and it's very easy to run if you know how to run LANDIS-II. As we're going to see, the parameter file is very small. Today, I prefer that we focus on understanding the model and understanding what you can do with it.

## Credits

Visuals for this presentation come from :

- [Storyset on Freepik](https://www.freepik.com/author/stories) (characters of Magic Harvest and Biomass Harvest; original images from Storyset have been edited)
- Different icons from 