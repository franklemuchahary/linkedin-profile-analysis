'''
Code for Scraping Individual Profiles

Note:
- Uses multiprocessing to speed things up. Will create multiple instances of selenium
- Change the multiprocessing section into a for loop to not use multiprocessing and run sequentially
'''

######### Imports #########

### generic imports
import logging
import re
import time
import traceback
import os
import multiprocessing as mp
import numpy as np
import pandas as pd
from dotenv import load_dotenv

### beautiful soup
from bs4 import BeautifulSoup

### selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


######### Initializations #########
cwd_path = os.getcwd()
load_dotenv()

email = os.environ['USERNAME']
password = os.environ['PASS']

#profiles_df = pd.read_csv('data/ConsultantProfiles-V1.csv')

profiles_df = pd.read_csv('data/cleaned_consultant_files/consultant_profile_links.csv')

# profiles_df = profiles_df.reset_index()
# profiles_df.rename(columns={'index':'profile_id_dummy'}, inplace=True)
# print(profiles_df.head())

LOG_FILENAME = 'assets/all_logs_individual_profiles_consultant.log'

SUB_FOLDER_PATH = 'data/individual_consultant_profiles/'

ERROR_LOG_STRING_FORMAT = '''
    {section_title}
    ---
    {description}
    ---
    {error_message}
''' + '='*60 + '\n\n'


######### Define Helper Functions #########

def error_logging_helper(log_filename:str = 'all_logs.log', logger_name:str = 'error_logger'):
    '''
    Helper function for logging errors

    Inputs:
    - log_filename: string, filename where to log the errors
    - logger_name: string, name of the logger initialized
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


logger = error_logging_helper(LOG_FILENAME)


def scrape_single_profile_helper(single_profile_batch_df, email_linkedin, password_linkedin):
    '''
    Helper function for scraping individual profiles.
    Mainly created for use in multiprocessing

    Inputs:
    - single_profile_batch_df: pandas dataframe, one batch of dataframes with profile links
    - email: string, linkedin email
    - password: string, linkedin password
    '''

    ######## login ########
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://linkedin.com")

    time.sleep(5)

    input_elements = driver.find_elements(
        By.XPATH,
        "//input[contains(@class, 'input__input' )][1]"
    )
    input_elements[0].send_keys(email_linkedin)
    input_elements[1].send_keys(password_linkedin)

    submit_button = driver.find_elements(
        By.XPATH,
        "//button[contains(@class, 'sign-in-form__submit-button')]"
    )
    submit_button[0].click()

    time.sleep(10)

    ######## loop through profiles ########

    for profile_idx in single_profile_batch_df.profile_id_dummy:
        try:
            single_profile_id = single_profile_batch_df['profile_id_dummy'][profile_idx]
            single_profile_url = single_profile_batch_df['profile_url'][profile_idx]

            ######## get single user page ########
            driver.get(single_profile_url)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 50);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 700);")

            time.sleep(5)
            soup_html = BeautifulSoup(driver.page_source)


            work_ex_section = soup_html.find(name='div', attrs={'id':'experience'}).parent
            exp_list = work_ex_section.find_all(name='li', attrs={'class':'artdeco-list__item'})

            companies_list_single_user = []
            companies_titles_single_user = []
            companies_durations_single_user = []

            ######## Experience Section ########
            for single_exp in exp_list:
                company_titles = [i.find('span').text.strip() for i in single_exp.find_all(name='span', attrs={'class':'mr1'})]
                company_name = company_titles[0]

                titles = company_titles[1:]
                if len(titles) == 0:
                    company_name = [i.find('span').text.strip() for i in single_exp.find_all(
                        name='span', attrs={'class':['t-14 t-normal']})][0]
                    titles = company_titles

                durations = [i.select('span')[0].text.strip() for i in single_exp.select('span.t-14.t-normal.t-black--light')]

                companies_titles_single_user.append(titles)
                companies_list_single_user.append(company_name)
                companies_durations_single_user.append(durations)

                print(company_name)
                print(titles)
                print(durations)

            single_user_all_experience_df = pd.DataFrame({
                'profile_id_dummy': single_profile_id,
                'company' : companies_list_single_user,
                'positions' : companies_titles_single_user,
                'durations' : companies_durations_single_user
            })

            print(single_user_all_experience_df)


            ######## Education Section ########
            education_section = soup_html.find(name='div', attrs={'id':'education'}).parent
            education_list = education_section.find_all(
                name='li', attrs={'class':'artdeco-list__item'}
            )

            education_institution_list = []
            education_degrees_list = []

            for single_edu in education_list:
                single_institute = [
                    i.find('span').text.strip() for i in single_edu.find_all(
                        name='span', attrs={'class':'mr1'}
                    )
                ]
                single_institute = single_institute[0]
                print(single_institute)
                education_institution_list.append(single_institute)

                education_degrees = [
                    i.find('span').text.strip() for i in single_edu.select('span.t-14.t-normal')
                ]
                print(education_degrees)
                education_degrees_list.append(education_degrees)


            single_user_all_education_df = pd.DataFrame({
                'profile_id_dummy': single_profile_id,
                'education_institute' : education_institution_list,
                'degree_list' : education_degrees_list
            })

            print(single_user_all_education_df)

            ######## all skills section ########
            all_skills_link = [
                i for i in
                soup_html.find_all("span", attrs={'class':'pvs-navigation__text'})
                if re.search(r'(Show all \d+ skills)', i.text) != None
            ]
            all_skills_link = all_skills_link[0].parent.parent.find('a')['href']
            #print(all_skills_link)

            driver.get(all_skills_link)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.execute_script("window.scrollTo(0, 500);")

            time.sleep(7)
            soup_html_skills_page = BeautifulSoup(driver.page_source)
            all_skills_list = [
                i.text.strip() for i in soup_html_skills_page.select('span.mr1.t-bold > span.visually-hidden')
            ]

            single_user_all_skills_df = pd.DataFrame({
                'profile_id_dummy': single_profile_id,
                'all_skills_link' : all_skills_link,
                'skills_list' : [all_skills_list]
            })

            #single_user_all_skills_df

            single_user_all_experience_df.to_csv(
                SUB_FOLDER_PATH+str(profile_idx)+'_experience.csv', index=False
            )
            single_user_all_education_df.to_csv(
                SUB_FOLDER_PATH+str(profile_idx)+'_education.csv', index=False
            )
            single_user_all_skills_df.to_csv(
                SUB_FOLDER_PATH+str(profile_idx)+'_skills.csv', index=False
            )

        except Exception as err_str:
            logger.error(
                ERROR_LOG_STRING_FORMAT.format(
                    section_title = 'Error in Fetching Profile',
                    description = 'Error for  Profile Dummy ID: ' + str(profile_idx),
                    error_message = str(err_str) + "\n" + str(traceback.format_exc())
                )
            )

    return ['Done']



######### Main block for combining everything together #########

if __name__ == '__main__':
    list_of_profile_dfs = np.array_split(profiles_df[0:160], 4)
    print(list_of_profile_dfs[3])
    print(mp.cpu_count())

    start = time.time()

    with mp.Pool(processes = mp.cpu_count()) as pool:
        result = pool.starmap(
            scrape_single_profile_helper,
            iterable = [
                (single_batch_df, email, password) for single_batch_df in list_of_profile_dfs
            ]
        )

    print(result)

    end = time.time()
    print(end-start)
