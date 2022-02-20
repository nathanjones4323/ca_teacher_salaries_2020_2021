#!/usr/bin/env python
# coding: utf-8

# # California School Teacher Wages by County and District

# ## Problem Statement
# 
# Gradutating California teachers and those who are getting their teaching credentials need to quickly and easily access  salary information at the county and district levels to help aid their job searching process. Most people want to maximize their earnings in their career, so knowing what counties and districts have the best salaries is key. 
# 
# Another component of choosing where to start your career is your geographic location. Money is important, but it is not everything. Say for instance you have family that lives in San Diego and you know for a fact that you do not want to move very far away. Or you just really don't want to live in the middle of the desert.
# 
# ## Goal
# 
# To best answer these questions, we should consider both *geographic* and *salary* data to make an informed decision. The best way to do this is by visualizing the salary data on a map ! Luckily, the California Department of Education provides both [geographic boundary shapefiles](https://gis.data.ca.gov/datasets/CDEGIS::california-school-district-areas-2020-21/explore) as well as a [database of teacher salary information](https://www.cde.ca.gov/ds/fd/cs/) all available off of [their website](https://www.cde.ca.gov/)
# 
# In addition to the school district data, we also utilized the [geographic county data](https://gis.data.ca.gov/datasets/8713ced9b78a4abb97dc130a691a8695/explore) (also found on CDE website) to view teacher salaries at the county level.
# 
# #### Notes
# 
# 1. In the following we are limiting our scope to new graduating / credentialling teachers in California, however the analysis can be easily adapted to any other teacher level position in California.
# 
# 
# 2. There are other factors such as school cultures, goals, teaching styles, etc. that play into where you want to work. While this is definitely true, we will mainly focus on the financial and geographical criteria for a good birds eye view of prospective jobs.

# ## Load libraries and read in data

# In[1]:


import geopandas as gpd
import pandas as pd
import folium
import numpy as np
from branca.element import Template, MacroElement
from folium.plugins import MeasureControl
from folium.plugins import geocoder


# In[2]:


# County Shapefile (Polygon boudaries for map visual)
counties = gpd.read_file("/Users/nathanjones/Downloads/ca_counties/cnty19_1.shp")
# This is the table name in the CDE database for Teacher Salary Information based on Step / Column in Form J-90
tsal321 = gpd.read_file("/Users/nathanjones/Downloads/tsal321.csv")
# This is the table name in the CDE database for Teacher Salary Information Column Descriptions in Form J-90
tsal221 = gpd.read_file("/Users/nathanjones/Downloads/tsal221.csv")
# This is the table name in the CDE database for District Level Data
tsal121 = pd.read_csv("/Users/nathanjones/Downloads/tsal121.csv")


# In[3]:


print("California Counties")
display(counties.head(3))
print("District Level Data")
display(tsal121.head(3))
print("Teacher Salary Education Level Descriptions")
display(tsal221.head(3))
print("Teacher Salary Data")
tsal321.head(3)


# ## Data Cleaning and light exploration
# 
# We can clean up part of the shapefile to remove the portions of land which are islands off the mainland US. In addition, we will need to clean up some of these strings in order to join our tables together.
# 
# Our `tsal321` and `tsal221` tables contain a leading 0 in their county numbers, so we need to pad the county number from our `counties` table to join all 3 of these up.
# 
# We also need to rename our columns to give them their real world meaning (check the database **.readme**). To do this we need to combine the education level description level columns `ts2_col1`, `ts2_col1a`, `ts2_col2` from the `tsal221` table which describe the education level for the column number given in the `ts3_col` column from the `tsal321` table.
# 
# I found the database documentation surrounding the years of experience and education level (step & column) to be difficult to understand. In my opinion, it wasn't easily clear how to answer the following question:
# 
# `Given a teacher's years of applicable experience and their education level, return the exact salary for that teacher at each district`
# 
# So, I reached out for the help to SACSINFO@cde.ca.gov and was given confirmation that this information was correct and joining these tables was the way to access the data I wanted (to the best of the government worker's knowledge).
# 
# **NOTE**: They did mention something weird I noticed with the Browns Elementary (CDS 5171365). They submitted multiple salaries under the same years of experience and education level. They were ommitted from this as a result.

# In[4]:


# Clean up counties table to exclude Island portions off the mainland USA
counties = counties[counties["ISLAND"].isnull()]
counties["COUNTY_NUM"] = counties["COUNTY_NUM"].astype(str).str.rjust(2, '0')


# In[5]:


teacher_salary = tsal321[tsal321["cds"] != '5171365'].merge(tsal221[tsal221["cds"] != '5171365'], how = "left", left_on = ["cds", "ts3_col"], right_on = ["cds", "ts2_col"])
new_column_names = ["county", "district", "cds", "education_level_column", "education_level_desc_1","education_level_desc_2", "education_level_desc_3", "years_experience", "salary"]
teacher_salary = teacher_salary[["county_x", "district_x", "cds", "ts3_col", "ts2_col1", "ts2_col1a", "ts2_col2", "ts3_step", "ts3_salary", ]]
teacher_salary.columns = new_column_names
county_salary = counties.merge(teacher_salary, how = 'left', left_on = 'COUNTY_NUM', right_on = "county")
print("Combined Teacher Salary Data from Form J90")
display(teacher_salary.head(3))
print("County Teacher Salary Information")
display(county_salary.head(3))
county_salary["education_level_desc"] = county_salary[["education_level_desc_1", "education_level_desc_2", "education_level_desc_3"]].astype(str).agg(' '.join, axis=1)
county_salary.drop(columns = ["education_level_desc_1", "education_level_desc_2", "education_level_desc_3"], inplace = True)


# Now that we have our joined up tables, we have a starting point.
# 
# For the county level view, we filter out the all rows except for positions with

# In[6]:


df = county_salary[(county_salary["years_experience"] == '1') & (county_salary["education_level_desc"].str.contains('ba|ma', case= False))]

df['education_level_column'] = df['education_level_column'].astype(int)
df['salary'] = df['salary'].astype(float)


# In[7]:


county_avg_salary = df.groupby(["COUNTY_NAM"]).mean()[["salary"]]
county_avg_salary = county_avg_salary.sort_values(by = "salary", ascending = False).reset_index().reset_index().rename(columns = {"index" : "salary_rank"})


# In[8]:


county_df = counties.merge(county_avg_salary, how = 'left', on = ["COUNTY_NAM"])
county_df["COUNTY_NAM"] = county_df["COUNTY_NAM"] + " County"
county_df["salary_rank"] = county_df["salary_rank"] + 1


# In[9]:


# 3 Highest Salary Counties
county_df.sort_values(by = "salary", ascending = False).head(3)


# In[10]:


county_df = county_df[~(county_df["salary"]).isnull()]
# Make salary more readable
county_df["salary_formated"] = county_df["salary"].apply(lambda x: '${:,.2f}'.format(x))


# In[11]:


m = folium.Map(location=[37.411292, -118], zoom_start= 6)
# Set up Bins for number of drivers
bins = np.linspace(county_df["salary"].min(), county_df["salary"].max(), 8)
# Define Pallete for Choropleth
choropleth_colors = np.array(['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#990000'])
# Polygon Style Function

def style_function(feature):
    sal = feature['properties']['salary']
    return {'color':'black', 
            'fillOpacity': .8,
            'weight': 1,
            'fillColor':  
            '#d9d9d9' 
                if sal == np.nan
                else choropleth_colors[0] if sal >= bins[0] and sal < bins[1]
                else choropleth_colors[1] if sal >= bins[1] and sal < bins[2]
                else choropleth_colors[2] if sal >= bins[2] and sal < bins[3]
                else choropleth_colors[3] if sal >= bins[3] and sal < bins[4]
                else choropleth_colors[4] if sal >= bins[4] and sal < bins[5]
                else choropleth_colors[5] if sal >= bins[5] and sal < bins[6]
                else choropleth_colors[6] if sal >= bins[6] and sal < bins[7]
                else choropleth_colors[7] if sal >= bins[7]
                else 'black'}

highlight_function = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}

folium.GeoJson(
    data = county_df,
    style_function=style_function,
    highlight_function=highlight_function,
    name= "Avg. BA/MA Salary",
    overlay=True,
    control=True,
    show=True,
    smooth_factor=None,
    zoom_on_click= True,
    tooltip= folium.features.GeoJsonTooltip(
        fields=['COUNTY_NAM',"salary_formated"],
        aliases=['Name:',"Avg. Salary:"],
        style = """
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 2px,
        box-shadow: 3px; 
        """)
).add_to(m)


####################################### Adding in Manual Legend #######################################

template = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>jQuery UI Draggable - Default functionality</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  
  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            right: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>

 
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>
     
<div class='legend-title'>Avg. Salary for BA/MA Teachers by County</div>
<div class='legend-scale'>
  <ul class='legend-labels', style="font-weight: bold;">
    <li><span style='background:#fff7ec;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[0])) + """ - """ + str('${:,.2f}'.format(bins[1])) + """</li>
    <li><span style='background:#fee8c8;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[1])) + """ - """ + str('${:,.2f}'.format(bins[2])) + """</li>
    <li><span style='background:#fdd49e;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[2])) + """ - """ + str('${:,.2f}'.format(bins[3])) + """</li>
    <li><span style='background:#fdbb84;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[3])) + """ - """ + str('${:,.2f}'.format(bins[4])) + """</li>
    <li><span style='background:#fc8d59;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[4])) + """ - """ + str('${:,.2f}'.format(bins[5])) + """</li>
    <li><span style='background:#ef6548;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[5])) + """ - """ + str('${:,.2f}'.format(bins[6])) + """</li>
    <li><span style='background:#d7301f;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[6])) + """ - """ + str('${:,.2f}'.format(county_df['salary'].max())) + """</li>

  </ul>
</div>
</div>
 
</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 30px;
    margin-right: 5px;
    margin-left: 0;
    border: 1px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""

macro = MacroElement()
macro._template = Template(template)

loc = 'Average Salary by County for a 1st Year Teacher with a Masters or Bachelors'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(loc)
m.get_root().html.add_child(folium.Element(title_html))
m.get_root().add_child(macro)
m.add_child(MeasureControl(position = 'bottomleft', primary_length_unit='miles', secondary_length_unit='meters', primary_area_unit='sqmiles', secondary_area_unit=np.nan))
folium.plugins.Geocoder().add_to(m)

m.save("/Users/nathanjones/Downloads/ca_teacher_salary_by_county.html")


# ## Read in District Level Data
# 
# We can repeat the process with the district level data by joining on CDS, a identifier that combines the county id and the district id together.

# In[12]:


districts = gpd.read_file("/Users/nathanjones/Downloads/ca_school_districts/California_School_District_Areas_2020-21.shp")
districts.rename(columns = {"CDCode" : 'cds'}, inplace = True)
districts.head()


# In[13]:


# Add leading 0 to cds
tsal121["cds"] = tsal121["cds"].astype(str).str.rjust(7, '0')
# What kind of school
def f(col_type):
    if col_type == 0:
        return 'County Office of Education'
    elif col_type == 1:
        return 'Elementary'
    elif col_type == 2:
        return 'High School'
    elif col_type == 3:
        return 'Common Admin District'
    elif col_type == 4:
        return 'Unified'

tsal121["ts1_type"] = tsal121["ts1_type"].apply(f)


# Here we need to narrow in on applicable salaries based on the column descriptions. Unfortunately, each school districts Salary and Benefits Schedule for the Certificated Bargaining Unit (Form J-90) can have a number of different education level columns.
# 
# Say we want to filter out for a specific degree, to really demonstrate how we can identify a teachers salary **given their years of experience and education level.**
# 
# For this example, we will look at teachers with the lowest level of experience (listed as step 1) with a masters degree. Since the data is not in a standardized format, we will need to wrangle and pattern match some of this text data to retrieve the information we want.

# In[14]:


# Which CDS's are missing
print(f'{len(list(set(districts["cds"]) - set(tsal121["cds"])))} Missing CDS codes from the school districts shapefile')
district_salary = districts.merge(tsal121, how = "left", on = "cds").merge(teacher_salary, how = "left", on = "cds")

print("District Teacher Salary Information")
display(district_salary.head(3))
district_salary["education_level_desc"] = district_salary[["education_level_desc_1", "education_level_desc_2", "education_level_desc_3"]].astype(str).agg(' '.join, axis=1)
district_salary.drop(columns = ["education_level_desc_1", "education_level_desc_2", "education_level_desc_3"], inplace = True)
df = district_salary[(district_salary["years_experience"] == '1') & (district_salary["education_level_desc"].str.contains('ba|ma', case= False))]

df['education_level_column'] = df['education_level_column'].astype(int)
df['salary'] = df['salary'].astype(float)


# ### To keep things simple, we won't make our filters perfect.
# 
# **We can use the following rules**:
# * 1 year of experience
# * Anything that includes a BA
# * Anything that inlcudes an MA, unless it is of the form $MA+UNITS$

# In[15]:


import re
first_year = district_salary[district_salary["years_experience"] == '1']
first_year["education_level_desc"] = first_year["education_level_desc"].str.strip()
# 4190 Possible Salaries to sift through
print(first_year.shape)


# No ma+{units} unless there is a ba as well
indexes = first_year[(first_year["education_level_desc"].str.contains('ba\+\d+|^ma|\+ma| *ma', case = False)) & ~(first_year["education_level_desc"].str.contains('ma\+| *ma\+', case = False))].index.values

df = first_year[first_year.index.isin(indexes)].reset_index(drop = True)
df["salary"] = df["salary"].astype(int)
df.head()


# In[16]:


district_avg_salary = df.groupby(["DistrictNa"]).mean()[["salary"]]
district_avg_salary = district_avg_salary.sort_values(by = "salary", ascending = False).reset_index().reset_index().rename(columns = {"index" : "salary_rank"})
district_avg_salary


# In[17]:


district_df = districts.merge(district_avg_salary, how = 'left', on = ["DistrictNa"])
district_df["DistrictNa"] = district_df["DistrictNa"] + " School District"
district_df["salary_rank"] = district_df["salary_rank"] + 1
district_df["salary"] = district_df["salary"].fillna(0)
district_df["salary_formated"] = district_df["salary"].apply(lambda x: '${:,.2f}'.format(x))


# In[18]:


# 3 Highest Salary Districts
district_df.sort_values(by = "salary", ascending = False).head(3)


# In[20]:


m = folium.Map(location=[37.5, -117], zoom_start= 6)
# Set up Bins for number of drivers
bins = np.linspace(district_df["salary"].min(), district_df["salary"].max(), 8).round(2)
# Define Pallete for Choropleth
choropleth_colors = np.array(['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#990000'])
# Polygon Style Function

def style_function(feature):
    sal = feature['properties']['salary']
    return {'color':'black', 
            'fillOpacity': .8,
            'weight': 1,
            'fillColor':  
            '#d9d9d9' 
                if sal == 0
                else choropleth_colors[0] if sal >= bins[0] and sal < bins[1]
                else choropleth_colors[1] if sal >= bins[1] and sal < bins[2]
                else choropleth_colors[2] if sal >= bins[2] and sal < bins[3]
                else choropleth_colors[3] if sal >= bins[3] and sal < bins[4]
                else choropleth_colors[4] if sal >= bins[4] and sal < bins[5]
                else choropleth_colors[5] if sal >= bins[5] and sal < bins[6]
                else choropleth_colors[6] if sal >= bins[6] and sal < bins[7]
                else choropleth_colors[7] if sal >= bins[7]
                else 'black'}

highlight_function = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}

folium.GeoJson(
    data = district_df,
    style_function=style_function,
    highlight_function=highlight_function,
    name= "Salary Per District for BA/MA 1st Year Positions",
    overlay=True,
    control=True,
    show=True,
    smooth_factor=None,
    zoom_on_click= True,
    tooltip= folium.features.GeoJsonTooltip(
        fields=['DistrictNa',"salary_formated"],
        aliases=['Name:',"Avg. Salary:"],
        style = """
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 2px,
        box-shadow: 3px; 
        """)
).add_to(m)


# NIL = folium.features.GeoJson(
#     data = df,
#     style_function=style_function, 
#     control=False,
#     zoom_on_click = True,
#     highlight_function=highlight_function, 
#     tooltip=folium.features.GeoJsonTooltip(
#         fields=['COUNTY_NAM',"salary"],
#         aliases=['Name:',"Avg. Salary:"],
#         style = """
#         background-color: #d9d9d9;
#         border: 2px solid black;
#         border-radius: 2px,
#         box-shadow: 3px; 
#         """,
#     max_width = 500,
#     sticky = True,
#     labels = True,
#     show = True
# ))
# m.add_child(NIL)
# m.keep_in_front(NIL)

####################################### Adding in Manual Legend #######################################

template = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>jQuery UI Draggable - Default functionality</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  
  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            right: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>

 
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>
     
<div class='legend-title'>Avg. Salary for BA/MA Teachers by School District</div>
<div class='legend-scale'>
  <ul class='legend-labels', style="font-weight: bold;">
  <li><span style='background:#d9d9d9;opacity:0.8;'></span>Missing data represented as $ 0</li>
    <li><span style='background:#fff7ec;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[0])) + """ - """ + str('${:,.2f}'.format(bins[1])) + """</li>
    <li><span style='background:#fee8c8;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[1])) + """ - """ + str('${:,.2f}'.format(bins[2])) + """</li>
    <li><span style='background:#fdd49e;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[2])) + """ - """ + str('${:,.2f}'.format(bins[3])) + """</li>
    <li><span style='background:#fdbb84;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[3])) + """ - """ + str('${:,.2f}'.format(bins[4])) + """</li>
    <li><span style='background:#fc8d59;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[4])) + """ - """ + str('${:,.2f}'.format(bins[5])) + """</li>
    <li><span style='background:#ef6548;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[5])) + """ - """ + str('${:,.2f}'.format(bins[6])) + """</li>
    <li><span style='background:#d7301f;opacity:0.9;'></span>""" + str('${:,.2f}'.format(bins[6])) + """ - """ + str('${:,.2f}'.format(district_df['salary'].max())) + """</li>

  </ul>
</div>
</div>
 
</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 30px;
    margin-right: 5px;
    margin-left: 0;
    border: 1px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""

macro = MacroElement()
macro._template = Template(template)

m.get_root().add_child(macro)
m.add_child(MeasureControl(position = 'bottomleft', primary_length_unit='miles', secondary_length_unit='meters', primary_area_unit='sqmiles', secondary_area_unit=np.nan))
folium.plugins.Geocoder().add_to(m)
loc = 'Average District Salary for a 1st Year Teacher with a Masters (or Bachelors with significant units)'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(loc)
m.get_root().html.add_child(folium.Element(title_html))

m.save("/Users/nathanjones/Downloads/ca_teacher_salary_by_district.html")


# In[ ]:




