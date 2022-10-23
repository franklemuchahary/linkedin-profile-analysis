# Project Title Here
Use this file `README.md` as a template. Delete the text under the headers and subheaders, replace with your own. 

The executive summary goes here, right after the project title. A straight-forward summary of your project. Be sure to include relevant citations and links.

The following directories are available:
* `/assets`: Please store image files, pdf, and other non-programming files here.
* `/code`: Store your Python or R script files here.
* `/data`: Any data file you create or retrieve for your project goes here.

## Statement of Scope
This is where your statement of scope goes.

## Project Schedule
Your project schedule with discussion.

## Data Preparation
Place a summary of your data preparation here. This is just an overview of what you did below.

Include a link to your final data in the `data` directory and links to all of your Python/R files at the end of your summary. For example, like this: 
* [placeholder.csv](data/placeholder.csv) The final dataset generated for this project
* [some_code.py](code/some_code.py) Python file used to scrape data from website *x*
* [some_other.py](code/some_other.py) Python file used to clean, consolidate, and transform the data from website *x*

### Data Access
Text about data access. We scraped data from Canvas using the Firefox geckodriver, as seen here:

```Python
driver = webdriver.Firefox(executable_path=r'C:\Users\bryanih\Documents\GitHub\geckodriver.exe')
canvas_url = 'https://stwcas.okstate.edu/cas/login?service=https%3A%2F%2Fcanvas.okstate.edu%2Flogin%2Fcas'
driver.get(canvas_url)
```

### Data Cleaning
Discuss how you cleaned your data here.

### Data Transformation
The transformation of your data.

### Data Reduction
A discussion of how you reduced your data.

### Data Consolidation
Your data consolidation discussion.

### Data Dictionary
A short description of the table below. Be sure to link each row to a data file in your directory `data` so I know where it is stored.

| Attribute Name | Description | Data Type | Source | Data | Example |
|:---|:---|:---:|:---|:---|:---:|
| Some Variable | Unique identifier for a widget | integer | http://www.company.org | [placeholder.csv](data/placeholder.csv) | More things to say |
| Another Variable | Text description of this variable | char(50) | http://www.company.org | [placeholder.csv](data/placeholder.csv) | All your base |

## Conclusion and Discussion
Discuss your findings and summarize.

What are the implications of your research upon the people, businesses, or community related to the project?