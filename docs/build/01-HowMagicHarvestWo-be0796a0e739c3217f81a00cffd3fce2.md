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

* * *

![](./images/Slide7.jpg)</br>

During a time step of LANDIS-II, when it's time for B. Harvest to work, they're going to look at the implementation table line by line. For each line, they're going to look at the management area concerned; they're going to rank the stands according to the ranking criteria that goes with the prescription; and then, they're going to harvest stands until they reach the % of surface to harvest.

And that's it ! There are other nuances that B. Harvest can do, like the fact that they can use different ranking methods, that they can make different patterns of cuts size, or that they can plant species; I'm not going to good deeper here, and will stay simple.

* * *

![](./images/Slide8.jpg)</br>

One thing to remember is that the instructions of B. Harvest cannot change once the simulation has started. They cannot be dyamically changed, and its limited algorithm means that there is a lot that B. Harvest cannot do. It cannot react to disturbances and do salvage logging; it cannot make complex planting based on the species present in a given stand. It cannot adapt to changes in supply and demand of wood. It will just implement the same implementation table during the entire simulation.

## When Magic and B. Harvest work together

![](./images/Slide9.jpg)</br>

Now, what goes on when Magic and B. Harvest are working together ? First of all, you gotta make sure that Magic runs before B. Harvest at every timestep. This is done by specifying Magic right before B. Harvest in the disturbance extensions of your scenario file, and making sure that the disturbance extension order is not random.

* * *

![](./images/Slide10.jpg)</br>

During a time step, Magic will run before B. Harvest. As I said before, Magic will simply run a custom command defined by the user, and then re-load the parameters of B. Harvest by giving him new parameter files that the command has edited. This makes it possible to have management decisions that are dynamic, since Magic can take into account the content of the landscape before editing the files of B. Harvest.

* * *

![](./images/Slide11.jpg)</br>

Remember that the command launched by Magic can be anything : an R script, a Python script, another model, and so on. It's very easy to edit the text files and raster maps needed by B. Harvest with this.

The key thing to remember is thus this : **every management decision done by Magic will be done through your custom command, wherever it is a script or another program**. By default, Magic harvest does not have any algorithm to make decisions. **YOU have to create it from A to Z and run it through the custom command**. Luckily, I've already done a lot of scripts that I will give you and that will do most of the work for you. We will see that afterward.

* * *

![](./images/Slide12.jpg)</br>

The way that the custom command is launched is through the Magic Harvest parameter text file. It's a very simple text file that is the only parameter file that Magic Harvest requires : the rest will depend on the command that you want to launch. The file just contains the time step frequency at which Magic Harvest should be run, and indications about the command you want to launch.

A cool thing is that you can add "arguments" to your command, which can give additional information to the script you're trying to launch. Of course, you'll have to indicate the path to your script; but I've coded a `{timestep}` argument you can pass that will give the current timestep of LANDIS-II to your command. You'll have to gather this time step argument in your script or model. I'll show you afterward how this is done in Python.

* * *

![](./images/Slide13.jpg)</br>

Another important comment here : as we're launching a custom command, that means that the program launched by the command - wherever R, Python or anything else - must be present on the computer you're running the simulation on, and needs to be accessible to a command prompt. Some people have had issue with that because on windows, the Python or R programs are not always accessible through the command prompt.

To be sure, just open a command prompt, type "Python" or "Rscript"; and if these commands are not recognized, just look online on how to make sure that they are available in a command prompt.

* * *

![](./images/Slide14.jpg)</br>

So that also means that you will need, on your computer : LANDIS-II, the program you're running, but also any packages your script might use, like R or Python packages. The fact that you're depending on a complex environment with these different dependancies means that it can be near impossible for someone in the future to replicate your simulation. 

* * *

![](./images/Slide15.jpg)</br>

Luckily, there is a clear solution for that : use [Docker](https://www.docker.com/). Docker allows you to create a virtual machine that can be run on any computer, which is define by a text file that creates your environment. This will allow you to keep the environment where you run LANDIS-II and your scripts and all separate from the rest of your computer (and so less likely to be corrupted or edited), and will allow anybody in the future to replicate your results by simply re-creating your Docker virtual machine using the text file you used to create yours.

Check the official LANDIS-II repository [Tool-Docker-Apptainer](https://github.com/LANDIS-II-Foundation/Tool-Docker-Apptainer) to get Docker images with LANDIS-II on them, and all of the instructions you will need to run them. If you have questions, ask me after this workshop !

* * *

![](./images/Slide16.jpg)</br>

So now our command is launched, which will edit the files of B. Harvest with management instructions - because if you don't do that, then there's no point in using Magic Harvest after all. Now, by editing the files of B. Harvest, Magic can have different levels of controls other B. Harvest, that will leave different degrees of decisions to B. Harvest. This is due to the fact that we can play with the three categories of input of B. Harvest to more or less constrain what B. Harvest will do.

* * *

![](./images/Slide17.jpg)</br>


For example, we can simply edit existing harvest prescriptions or change a management area with Magic, and pass this to B. Harvest. In that case, B. Harvest will still try to implement its implementation table in the management areas. As such, it will still be the algorithm of B. Harvest that will decide what stands or pixels will be harvested through its ranking algorithm, and so on.

* * *

![](./images/Slide18.jpg)</br>

But we can completly bypass the decision algorithm of B. Harvest by indicating precisely what stands or pixels we want to harvest. To do this, we ask Magic to create a map where each pixel to harvest with a certain prescription is associated with a given code (e.g. `2` for clearcutting, `3` for clearcutting + planting of balsam fir, `4` for partial cutting, etc.). We will of course use a custom Python or R script to create this map; everything is done via scripting in Magic Harvest.

Then, we can give this map to B. Harvest as both his Management area map and his stand map. I know this can seem confusing; but by stay with me for a moment. So what B. Harvest will see is that all pixels with the same number are part of the same big management area AND the same big stand. And then, we simply have to edit the implementation table of B. Harvest to tell him that 100% (so, all) of the pixels with a given code must be harvested with the prescription that corresponds to the code. We do that by specifiying the codes we made as the management areas.

So what B. Harvest reads is "harvest all pixels of management area 1 at this timestep with this prescription". And since all of these pixels are in the same big stand according to him (because we're using the same map for management areas and stands), then he is simply going to harvest them all. So in essence, it's like Magic tells B. Harvest exactly what to do, and B. Harvest takes absolutly no decision anymore. By following its usual algorithm, it's simply going to harvest all of the pixels that Magic has indicated to him without asking any questions. Oh, and as we'll see later, we can also create whole new prescriptions dynamically if we need to !


* * *