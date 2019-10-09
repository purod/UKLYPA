
## Project
The project was created as part of the [Insight Data Science Fellows Program](https://www.insightdatascience.com/) in September 2019.

## Index

1. [Introduction](README.md#1-introduction)
 * 1.1 [Project Details](README.md#11-project-details)
2. [The Pipeline](README.md#2-the-pipeline)
 * 2.0 [Avro Schema](README.md#20-avro-schema)
 * 2.1 [Kafka Ingestion](README.md#21-kafka-ingestion)
 * 2.2 [Kafka Streams Application](README.md#22-kafka-streams-application)
 * 2.3 [Cassandra](README.md#23-cassandra)

## 1. Web App [UKLYPA](www.uklypa.com) 
The motivation of the App is that the political views of the public could be geographically influenced. For politicians or political
activists in UK, an App which can locate their policy audiences from 650 parliamentary regions could help them to optimize their Ad 
campaigns to gain more supporters.

# About the data
**Training dataset:** Using UK petition platform, people from differet regions in UK can directly express their political views by simply signing petitions they support. Since 2015, the platform has collected 18,732 petitions and 62,455,828 signatures in total. The data could be downloaded for each petition as a json file, which also contains the corresponding geographic distribution of signatures across 650 parliamentary regions in UK.

**Test dataset:**  To test whether or not our trained topic model can accurately assign a new petition into the correct topic, 7K petitions from the US petition platform 'we the people' were downloaded from a [github project](https://github.com/shivashankarrs/Petitions). Petitions in this file have been manually labelled by the people who submitted their petitions. Petitions from four topics which are similar as mine were used as the test dataset.

| Topics(we the people)        | Number of petitions          |
| ------------- |:-------------:|
| Energy & Environment      | 175 | 
| Education      | 83      | 
| Budget & Taxes,Economy & Jobs | 86     |
| Civil Rights & Equality,Criminal Justice Reform | 259      | 

**Map data:** The map information for all 650 UK parliamentay regions was downloaded from [Office for National Statistics](http://geoportal.statistics.gov.uk) and then converted to format Geojson using [mapshaper](https://mapshaper.org/).

# About the method
**Motivation:** Examining the geographic distribution of signatures for a specific petition on the platform would be tedious as there are thousands of petitions on the platform. Also, information from only one petition would be biased from the perspective of statistic sampling. In this project, I proposed to categorize thousands of petition texts into 11 major topics so that the geographic information associated with petitions could be summarized using topics. During the summarization of petitions, another factor that needs to be take into account is the opinions contained in petitions. Some exploratory analysis showed that even for the same topic, opposite opinions could have opposite distribution of signatures across the country. 

**Pipeline:** The model of UK-LYPA was trained on all historic petitions. After preprocessing, all petitions were categorized into 11 major topics by topic modeling LDA. In the meanwhile, opinion(positive, neutral, and negative) contained in each petition was analyzed with sentiment analysis. When a new petition is submitted by the user, the App calculates the probability of each topic it could be assigned as well as the opinion it contains. Integrating the above information, a supporting index was designed to show how much a region would support the submitted petition. Supporting indexes for all 650 parliamentary regions in UK were showed in an interactive map by UK-LYPA.
![Pipeline](https://github.com/purod/UKLYPA/blob/master/static/Pipeline_detail.png "Logo Title Text 1")

**App:** The interactive choropleth map is created by the tool folium and intergrated into UK-LYPA by flask. The App was employed launched and run on AWS EC2.

![App](https://github.com/purod/UKLYPA/blob/master/static/UK-LYPA.png "Logo Title Text 2")



 * [Slides](http://www.bit.ly/ads1989)
 * [Live Demo](http://www.adtstreams.info)

