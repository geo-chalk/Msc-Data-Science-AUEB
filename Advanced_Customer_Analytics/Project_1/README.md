> Chalkiopoulos Georgios, Electrical and Computer Engineer NTUA <br />
> Data Science postgraduate Student <br />
> gchalkiopoulos [at] aueb [dot] gr
> 


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

Activate the environment. The notebook will install the required envs needed in reach case.
Alternatively you can use the `requirements.txt` file to import the required libraries 

## Execution
Here is a sample execution for each case:

### get_reviews.ipynb
```
query: str = "Beyond Order"

scrape(query=query)
```

You may edit the following parameters:

| arg                    | descrition                                               |
|------------------------|----------------------------------------------------------|
| query                  | the name of the product to search                        |
| driver (optional)      | a Webdriver object                                       |
| wait (optional)        | wait time. Set to 3 by default due to stable performance |
| output_path (optional) | output_path name. Default in amazon_reviews_{query}.csv  |
| max_pages (optional)   | max review pages to load. Each page contains 10 reviews  |

The output of this function is a csv file named `amazon_reviews_{product}.csv`
and an image of the product (if no error occured) named `{product}.png`

### generate_pdf.ipynb

Before proceeding make use to generate an OpenAi API Key and place your key ion the imports cell:
```
import openai
openai.api_key = "YOUR_API_KEY"
```

Provide the csv and (optionally) the png file that was generated from the get_reviews notebook as shown below:


```
csv_path: str = r"./backup/amazon_reviews_{product}.csv"
png_path : str = r"./{product}.png"

summarize(csv_path=csv_path, 
          png_path=png_path)
```

The program will generate a `.pdf` file named:  `{product}_summary.pdf` along with two `.png` files that will be deleted.

