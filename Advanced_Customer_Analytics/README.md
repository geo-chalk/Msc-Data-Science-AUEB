# Advanced Customer Analytics (Y2Q1)


Data-oriented techniques for extracting patterns from sales, marketing, and customer data in order to support 
personalized marketing and customer relationship management. Propensity modeling & classification, 
association/rules analysis, dimensionality reduction, data clustering, text mining, collaborative filtering 
and social network analysis tools and techniques will be applied. The main objective of the course is to explain 
in detail the methodologies used in relationship marketing in order to gain actionable insights from data.


## Project 1: Review Summarization

1. Select an English-speaking website that hosts customer reviews on products (or services, businesses, movies, events, etc).

2. Make sure that the website includes a free-text search box that users can use to search for products. 

3. Email me your selection at ****. Each student should work on a different website, so I will maintain the list of selected websites at the top of our Wiki. First come, first served. 

4. Create a first Python Notebook with a function called scrape( ). The function should accept as a parameter a query (a word or short phrase).  The function should then use selenium to:

   * submit the query to the website's search box and retrieve the list of matching products.
   access the first product on the list and download all its reviews into a csv file. For each review, the function should get the text, the rating, and the date. One line per review, 3 fields per line.
 
5. Create a second Python Notebook with a function called summarize( ). The function should accept as a parameter the path to a csv file created by the first Notebook. It should then create a 1-page pdf file that includes a summary of all the reviews in the csv. 

The nature of the summary is entirely up to you. It can be text-based, visual-based, or a combination of both. 
It is also up to you to define what is important enough to be included in the summary. 
Focus on creating a summary that you think would be the most informative for customers.
The creation of the pdf should be done through the notebook. 
You can use whatever Python-based library that you want. 

## Create environment
It is recommended to use conda. Create a new env:

```
conda create --name CA_reviews python=3.7
```

Activate the environment and run: 

```
pip3 install -U selenium
pip3 install webdriver-manager
```
