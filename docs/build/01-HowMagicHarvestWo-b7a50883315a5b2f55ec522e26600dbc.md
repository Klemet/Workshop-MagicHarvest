# How Magic Harvest Works

**Authors:** Clément Hardy<sup>1</sup> \
**Affiliations:** <sup>1</sup>Université du Québec en Outaouais (UQO)\

[![Made with MyST](https://img.shields.io/badge/made%20with-myst-orange)](https://myst.tools)

## A metaphor : Magic and B. Harvest

![](./images/Slide5.jpg)</br>

First, and for the rest of this workshop, I'm going to use a metaphor to represent Magic Harvest and Biomass Harvest : **Biomass Harvest, being the Biomass Harvest extension of LANDIS-II, is a forester**. We'll call them "B. Harvest" from now on. B. Harvest being a forester, their main skill is in harvesting trees, and they have all of the tools for that. They can do some forest management decisions, but it's not their main strength. When they do forest management decisions, they has a pretty simply algorithm that they learned from school.

**Magic Harvest, that we'll just call "Magic" for short, is a forest engineer**. They don't have the tools to cut trees at all. They can't cut trees ! That why they have to rely on B. Harvest to do it. But they're a genius at forest planning : unlike B. Harvest, Magic they do anything ! They can use any type of models, do any kind of instruction.

As such, B. Harvest can work alone to do the management decisions and the harvesting. Magic has to work with B. Harvest because they cannot harvest trees by themselves; but they can really help B. Harvest do better at management decisions.

## What happens when B. Harvest works alone ?

![](./images/Slide6.jpg)</br>

So let's see what happens when B. Harvest works alone. This is basically a visual summary of what you will find in the [user guide of Biomass Harvest](https://github.com/LANDIS-II-Foundation/Extension-Biomass-Harvest/tree/master/docs). However, this is important so that we can understand how he is going to work with Magic afterwards.


B. Harvest has a simple algorithm based on three things : a set of maps showing the management areas and the stand in the landscape; a list of harvest prescriptions and the way to choose the stands that they will harvest with this prescription; and an implementation table giving the % of management areas that must be harvested with a given prescription. The rasters are given as raster files; the prescription instruction and harvest implementation table are inside a single parameter text file.

![](./images/Slide7.jpg)</br>

During a time step of LANDIS-II, when it's time for B. Harvest to work, they're going to look at the implementation table line by line. For each line, they're going to look at the management area concerned; they're going to rank the stands according to the ranking criteria that goes with the prescription; and then, they're going to harvest stands until they reach the % of surface to harvest.

And that's it ! There are other nuances that B. Harvest can do, like the fact that they can use different ranking methods, that they can make different patterns of cuts size, or that they can plant species; I'm not going to good deeper here, and will stay simple.

![](./images/Slide8.jpg)</br>

One thing to remember is that the instructions of B. Harvest cannot change once the simulation has started. They cannot be dyamically changed, and its limited algorithm means that there is a lot that B. Harvest cannot do. It cannot react to disturbances and do salvage logging; it cannot make complex planting based on the species present in a given stand. It cannot adapt to changes in supply and demand of wood. It will just implement the same implementation table during the entire simulation.


