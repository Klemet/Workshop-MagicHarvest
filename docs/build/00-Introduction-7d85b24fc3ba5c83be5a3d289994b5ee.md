# Introduction

**Authors:** Clément Hardy<sup>1</sup> \
**Affiliations:** <sup>1</sup>Université du Québec en Outaouais (UQO)\

[![Made with MyST](https://img.shields.io/badge/made%20with-myst-orange)](https://myst.tools)

This small website contains a workshop to help you use the [Magic Harvest](https://github.com/Klemet/LANDIS-II-Magic-Harvest) extension for the [LANDIS-II forest](https://www.landis-ii.org/) landscape model. It's simply an implementation of the powerpoint presentation I did in the summer of 2025 at the University of Toronto. You'll have both the slides and the text of the slides in a readable format.

**Magic Harvest is a small extension that I develloped during my PhD thesis**. My work required me to compare the effect of several forest management scenarios in LANDIS-II; but at the time, LANDIS-II lacked several important features that I needed to implement forest management in the model. I created Magic Harvest in order to solve the issue.

![](./images/Slide2.jpg)</br>

**The Magic Harvest extension is both simple and complicated**. Simple, because its functionning can be summarized in two sentences : it's a companion extension for Biomass Harvest (the main harvest extension for LANDIS-II; the other ones are almost never used) who's goal is to run before Biomass Harvest. **When running, it will simply launch a custom command defined by the user - for example an R or Python script - and will then force Biomass Harvest to re-load its parameters**. That's it.

The complex part is understanding the consequences of this and learning to play with it. The consequences is that we can control what Biomass Harvest does at different degrees : complete and total control, or still letting Biomass Harvest do some choices based on its own algorithm. Learning to play with Magic Harvest mostly means learning to write scripts that will do what you want to do.


## Plan of the workshop

![](./images/Slide3.jpg)</br>





This repository contains the files used in the [quickstart guide](https://mystmd.org/guide/quickstart), and can be used to follow that guide, before trying MyST with your own content.

> **Note** This is **not** a good example of an actual MyST project! The repositories purpose is to be a simple markdown + notebook repository that can be transformed throughout a tutorial.

The goals of the [quickstart guide](https://myst.tools/docs/mystjs/quickstart) are:

1. Create a `myst` site, using the standard template
2. Improve the frontmatter, to add authors, affiliations and other metadata
3. Export the paper as a PDF, Word document, and LaTeX files
4. Integrate a Jupyter Notebook output into our paper, to improve reproducibility
5. Publish a website of with our work 🚀

## Improving Frontmatter and MyST Site

![](./images/frontmatter-after.png)

## Export as a PDF

![](./images/export-pdf.png)
