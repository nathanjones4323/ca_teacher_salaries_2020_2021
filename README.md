# California Teacher Salary Data

This repository serves as a source of data and knowledge on teacher salaries for the state of California. 


## Problem Statement

Graduating California teachers and those who are getting their teaching credentials need to quickly and easily access  salary information at the county and district levels to help aid their job searching process. Most people want to maximize their earnings in their career, so knowing what counties and districts have the best salaries is key. 

Another component of choosing where to start your career is your geographic location. Money is important, but it is not everything. Say for instance you have family that lives in San Diego and you know for a fact that you do not want to move very far away. Or you just really don't want to live in the middle of the desert.

## Proposed Solution and Resources

To best answer these questions, we should consider both *geographic* and *salary* data to make an informed decision. The best way to do this is by visualizing the salary data on a map ! Luckily, the California Department of Education provides both [geographic boundary shapefiles](https://gis.data.ca.gov/datasets/CDEGIS::california-school-district-areas-2020-21/explore) as well as a [database of teacher salary information](https://www.cde.ca.gov/ds/fd/cs/) all available off of [their website](https://www.cde.ca.gov/)

In addition to the school district data, we also utilized the [geographic county data](https://gis.data.ca.gov/datasets/8713ced9b78a4abb97dc130a691a8695/explore) (also found on CDE website) to view teacher salaries at the county level.


## Goal

* Find the entry level salary for newly graduated educators based on the 2020-2021 Salary Schedules submitted by each district across California
* Display the information on a map with interactive components, including an informative tooltip.

#### Notes

1. In the following we are limiting our scope to new graduating / credentialing teachers in California, however the analysis can be easily adapted to any other teacher level position in California.


2. There are other factors such as school cultures, goals, teaching styles, etc. that play into where you want to work. While this is definitely true, we will mainly focus on the financial and geographical criteria for a good birds eye view of prospective jobs.

## Tech Stack Used

To perform all of our data analysis, we will be using Python. Specifically, the following libraries:

1. Geopandas (Reading in of geographic data)
2. Pandas (Data manipulation and cleaning)
3. Folium (Mapping of geographic data, overlaid with salary data)
4. Numpy (Computations)
5. Branca (Fancying up Folium maps)

The source code for the maps is included in the **`code`** directory of this repository, and the source data is contained in the **`data`** directory of this repository. Additionally, I will provide a Jupyter Notebook of all the code with minimal comments. 

Modifications and new analysis are highly encouraged, these maps are just an example of what you can do with this data ! 

## See the Maps Live in Action

Since Folium produces static HTML files, I chose to host the maps on Netlify as a way to share the content. 

You can see the county level map live at https://ca-county-teacher-salaries.netlify.app/
&
You can see the district level map live at https://ca-district-teacher-salaries.netlify.app/

## References
1. [Geographic boundary shapefiles](https://gis.data.ca.gov/datasets/CDEGIS::california-school-district-areas-2020-21/explore) provided by the California government
2. [Database of teacher salary information](https://www.cde.ca.gov/ds/fd/cs/) provided by the California government and available to the public off of [their website](https://www.cde.ca.gov/)

3. [Geographic county data](https://gis.data.ca.gov/datasets/8713ced9b78a4abb97dc130a691a8695/explore) provided by the California government. (Used to view teacher salaries at the county level)

## Final Words
If you know someone that is going to become a teacher or is thinking about changing districts / counties, this is a great resource for them. This allows an education professional to make informed decisions about their career, and highlights the facts that teachers are underpaid for their work (something I personally believe). Sharing, critics, and general comments are all encouraged. Thanks for reading : )
