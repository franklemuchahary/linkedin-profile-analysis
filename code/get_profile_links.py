'''
Code for fetching profile links based on the Profile Title

Note:
- This code runs sequentially
- Change the variable `SEARCH_TERM` to search profiles for a different profile title
- List of Terms:
    - Data Science: Principal Data Scientist
    - Management Consultant, Partner McKinsey, Principal BCG
    - Chief Technology Officer
    - Chief Executive Officer
'''

### generic imports
import logging
import time
import traceback
import os
import pandas as pd
from dotenv import load_dotenv

### selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


############# Initializations #############
SEARCH_TERM = "Chief Executive Officer"
PROFILE_CSV_FILENAME = 'data/CEOProfiles.csv'
NUM_PAGES_TO_FETCH_FOR_PROFILES = 20

ERROR_LOG_STRING_FORMAT = '''
    {section_title}
    ---
    {description}
    ---
    {error_message}
''' + '='*60 + '\n\n'

cwd_path = os.getcwd()
load_dotenv()

email = os.environ['USERNAME']
password = os.environ['PASS']



############# Define Helper Function #############
def error_logging_helper(log_filename:str = 'all_logs.log', logger_name:str = 'error_logger'):
    '''
    helper function for logging errors
    '''
    logger = logging.getLogger(logger_name)
    handler = logging.FileHandler(
        filename=log_filename,
        mode='a+'
    )
    log_format = logging.Formatter('%(asctime)s - %(message)s')
    handler.setLevel(logging.INFO)
    handler.setFormatter(log_format)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    print(logger.getEffectiveLevel())

    return logger

logger = error_logging_helper('assets/all_logs.log')


############### Selenium Code Block ###############

### Open Chrome Driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

### Go to linkedin URL
driver.get("https://linkedin.com")

### Enter Username and Password and Click on Login
input_elements = driver.find_elements(
    By.XPATH,
    "//input[contains(@class, 'input__input' )][1]"
)
input_elements[0].send_keys(email)
input_elements[1].send_keys(password)

submit_button = driver.find_elements(
    By.XPATH,
    "//button[contains(@class, 'sign-in-form__submit-button')]"
)
submit_button[0].click()

time.sleep(7)

### Focus on Search Button, Enter Search Term, and Press Enter
try:
    ### find search button
    search_button = driver.find_elements(
        By.XPATH,
        "//button[contains(@class, 'search-global-typeahead__collapsed-search-button')]"
    )
    search_button[0].click()
    
except:
    ### input search term in the search field
    input_search_field_xpath = "//input[contains(@class, 'search-global-typeahead__input always-show-placeholder')]"
    search_input_field = driver.find_elements(
        By.XPATH, 
        input_search_field_xpath
    )

    search_input_field[0].clear()
    search_input_field[0].send_keys(SEARCH_TERM + "\n")
    
time.sleep(7)


### Get All Single User Profile Links and Names - click "Next" to move to further pages

all_profile_urls = []
all_profile_names = []
all_profile_headings = []

for page_num in range(1, NUM_PAGES_TO_FETCH_FOR_PROFILES+1):    
    try:
        print("###"*10, " Page Num: ", page_num, "###"*10, end="\n\n")
        single_page_profiles = driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'entity-result__item')]"
        )
        print(len(single_page_profiles))

        for idx, single_person in enumerate(single_page_profiles):
            try:
                single_person_block = single_person.find_element(
                    By.XPATH, 
                    ".//span[contains(@class, 'entity-result__title-text')]"   
                )

                try:
                    single_person_profile_url = single_person_block.find_element(
                        By.TAG_NAME, 
                        'a'
                    ).get_attribute('href')
                except Exception as e:
                    single_person_profile_url = ''
                    logger.error(
                        ERROR_LOG_STRING_FORMAT.format(
                            section_title = 'Fetching Single User Profile URL',
                            description = 'Error for Person Num: ' + str(idx+1) + " in Page Num: " + str(page_num),
                            error_message = str(e)
                        )
                    )

                try:
                    single_person_name = single_person_block.find_element(
                        By.XPATH,
                        './/a/span/span'
                    ).text
                except Exception as e:
                    single_person_name = ''
                    logger.error(
                        ERROR_LOG_STRING_FORMAT.format(
                            section_title = 'Fetching Single User Profile Name',
                            description = 'Error for Person Num: ' + str(idx+1) + " in Page Num: " + str(page_num),
                            error_message = str(e)
                        )
                    )

                try:
                    single_person_heading = single_person.find_element(
                        By.XPATH,
                        ".//div[contains(@class, 'entity-result__primary-subtitle')]"
                    ).text
                except Exception as e:
                    single_person_heading = ''
                    logger.error(
                        ERROR_LOG_STRING_FORMAT.format(
                            section_title = 'Fetching Single User Profile Heading',
                            description = 'Error for Person Num: ' + str(idx+1) + " in Page Num: " + str(page_num),
                            error_message = str(e)
                        )
                    )

            except Exception as e:
                logger.error(
                    ERROR_LOG_STRING_FORMAT.format(
                        section_title = 'Fetching Single User Overall Item',
                        description = 'Error for Person Num: ' + str(idx+1) + " in Page Num: " + str(page_num),
                        error_message = str(e)
                    )
                )

                single_person_profile_url = ''
                single_person_name = ''
                single_person_heading = ''

            all_profile_urls.append(single_person_profile_url)
            all_profile_names.append(single_person_name)
            all_profile_headings.append(single_person_heading)
    
        ### click next button
        time.sleep(5)
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(5)
        
        next_button = driver.find_elements(
            By.XPATH,
            "//button[contains(@class, 'artdeco-pagination__button--next')]"
        )[0]
        next_button.click()
        
        time.sleep(7)

    except Exception as e:
        logger.error(
            ERROR_LOG_STRING_FORMAT.format(
                section_title = 'Error in Fetching Entire Page Profiles or Clicking Next Page',
                description = 'Error for  Page Num: ' + str(page_num),
                error_message = str(e) + "\n" + str(traceback.format_exc())
            )
        )

################### Save Profile Links into CSV Files ###################

APPEND = False

if APPEND:
    old_df = pd.read_csv(PROFILE_CSV_FILENAME)

final_user_info_df = pd.DataFrame({
    'names': all_profile_names,
    'profile_url': all_profile_urls,
    'profile_heading': all_profile_headings
})

if APPEND:
    final_user_info_df = pd.concat([old_df, final_user_info_df]).reset_index(drop=True)

print(final_user_info_df['profile_url'].nunique())
final_user_info_df = final_user_info_df.drop_duplicates()
print(final_user_info_df.shape)
print(final_user_info_df.head())

final_user_info_df.to_csv(PROFILE_CSV_FILENAME, index=False)
