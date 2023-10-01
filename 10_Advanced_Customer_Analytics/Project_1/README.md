## Project 1: Review Summarization

Select an English-speaking website that hosts customer reviews on products. The website should also include 
a free-text search box that users can use to search for products. 
Create a Python Notebook which scrapes the reviews and saves them to a csv file.
Create a Second Python Notebook, which reads the csv file an creates a 1-page pdf file that includes 
a summary of all the reviews.


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

