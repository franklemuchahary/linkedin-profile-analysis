'''
Code for Initial Cleaning of Scraped LinkedIn Data
'''

############## IMPORTS ##############
import os
import ast
import re
import dateutil.parser
import pandas as pd
from nltk.stem import WordNetLemmatizer


############## INITIALIZATIONS ##############
BASE_PATH = 'data/individual_consultant_profiles/'

MAIN_PROFILE_CSV = 'data/cleaned_consultant_files/consultant_profile_links.csv'

CLEANED_FILES_PATH = 'data/cleaned_consultant_files/'

SKILLS_DF_COMBINED_FILE = ''

############## Load Files ##############
main_df = pd.read_csv(MAIN_PROFILE_CSV)
print(main_df.head())


all_files = os.listdir(BASE_PATH)
print(len(all_files))

education_files = [i for i in all_files if 'education' in i]
experience_files = [i for i in all_files if 'experience' in i]
skill_files = [i for i in all_files if 'skill' in i]

### helper function for concatenating
def concatenate_dfs_helper(filenames_list, base_path):
    '''
    helper function for concatenating csv files
    '''
    df_list = []

    for file in filenames_list:
        temp_df = pd.read_csv(base_path+file)
        df_list.append(temp_df)

    full_df = pd.concat(df_list).reset_index(drop=True)
    return full_df


### load all individual files and concatenate into a single df
education_df = concatenate_dfs_helper(
    education_files,
    BASE_PATH
)

experience_df = concatenate_dfs_helper(
    experience_files,
    BASE_PATH
)

if SKILLS_DF_COMBINED_FILE != '':
    skills_df = pd.read_csv(
        BASE_PATH + SKILLS_DF_COMBINED_FILE
    )
else:
    skills_df = concatenate_dfs_helper(
        skill_files,
        BASE_PATH
    )

print(len(education_df['profile_id_dummy'].unique()))
print(education_df.shape)
print(experience_df.shape)
print(skills_df.shape)


############## Clean Education DF ##############

print("................. Cleaning Education .................")

def clean_degree_list(df_temp):
    '''
    helper function for cleaning `degree_list` column in education
    '''
    single_degree_list = df_temp['degree_list']
    try:
        str_to_list = ast.literal_eval(single_degree_list)

        if len(str_to_list) == 1:
            #### handle cases where year is not available or degree name is not available
            if re.match(r'[0-9\-]', str_to_list[0]) is not None:
                time_period = str_to_list[0].strip()
                degree_name = ''
            else:
                degree_name = str_to_list[0].strip()
                time_period = ''
        else:
            #### both are available
            time_period = str_to_list[1]
            degree_name = str_to_list[0].strip()


        if time_period != '':
            #### split time period into start and end
            time_period_split = time_period.split('-')

            if len(time_period_split) == 1:
                #### if either end or start is not available make both the same
                end = int(re.search(r'\d+', time_period_split[0].strip()).group(0))
                start = end
            else:
                #### both start and end are available
                start = int(re.search(r'\d+', time_period_split[0].strip()).group(0))
                end = int(re.search(r'\d+', time_period_split[1].strip()).group(0))
        else:
            ### set arbitrary value in case nothing is available
            start = 1900
            end = 1900

        return degree_name, start, end

    except Exception as err_str:
        print(err_str)
        print(single_degree_list)

        return '', 1900, 1900


education_df[['degree_name', 'start_year_degree', 'end_year_degree']] = education_df.apply(
    clean_degree_list, result_type='expand', axis=1
)

education_df = education_df.sort_values('profile_id_dummy')
education_df.drop('degree_list', axis=1).to_csv(
    CLEANED_FILES_PATH+'education_info.csv',
    index = False
)


############## Clean Experience DF ##############

print("................. Cleaning Experience .................")

def extract_time_period_experience(item):
    '''
    helper function for cleaning duration
    '''
    temp_list = ast.literal_eval(item)
    new_list = []

    for single_item in temp_list:
        regex_match = re.match(
            '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|20\d{2}|19\d{2})',
            single_item
        )

        if regex_match is not None:
            new_list.append(single_item.split('·')[0].strip())

    return new_list


def experience_duration_splitter(df_temp):
    '''
    helper function for splitting duration to start and end
    '''
    single_date = df_temp['durations_cleaned']

    split_list = single_date.split('-')

    today_end_date = 'Nov 2022'

    if len(split_list)==2:
        start = split_list[0].strip()
        end = split_list[1].strip()

        if end.lower() == 'present':
            end = today_end_date
    else:
        start = split_list[0].strip()
        end = start = split_list[0].strip()

    try:
        start = dateutil.parser.parse(start)
        end = dateutil.parser.parse(end)
    except:
        start = ''
        end = ''

    return start, end


experience_df['durations_cleaned'] = experience_df['durations'].apply(
    extract_time_period_experience
)
experience_df['positions'] = experience_df['positions'].apply(ast.literal_eval)

for i,j in experience_df.iterrows():
    if len(j.positions) < len(j.durations_cleaned):
        experience_df.loc[i, 'durations_cleaned'] = j['durations_cleaned'][0:len(j['positions'])]
        print(j)
    elif len(j.positions) > len(j.durations_cleaned):
        experience_df.loc[i, 'durations_cleaned'] = experience_df.loc[i, 'durations_cleaned'] + (
            [''] * (len(j['positions']) - len(j['durations_cleaned']))
        )
        print(j)

long_experience_df = experience_df.explode(
    ['positions', 'durations_cleaned']
).reset_index(drop=True)

long_experience_df[['start_date', 'end_date']] = long_experience_df.apply(
    experience_duration_splitter,
    axis=1,
    result_type='expand'
)

name_and_experience_df = pd.merge(
    long_experience_df,
    main_df,
    on = 'profile_id_dummy',
    how = 'left'
)

name_and_experience_df = name_and_experience_df.drop('durations', axis=1, errors='ignore')
name_and_experience_df.sort_values('profile_id_dummy', inplace=True)

name_and_experience_df.to_csv(
    CLEANED_FILES_PATH+'name_and_experience_info.csv',
    index = False
)

############## Clean Skills DF ##############

print("................. Cleaning Skills .................")

lemmatizer = WordNetLemmatizer()

skills_df['skills_list_cleaned'] = skills_df['skills_list'].apply(
    lambda x: [lemmatizer.lemmatize(i.lower()) for i in ast.literal_eval(x)]
)

# skills_df.to_csv(
#     CLEANED_FILES_PATH+'skills_info.csv',
#     index=False
# )

skills_remapping_dict = {
    'artificial intelligence (ai)':'artificial intelligence',
    'ai':'artificial intelligence',
    'agile methodologies':'agile',
    'agile project management':'agile',
    'amazon ebs' : 'amazon web services (aws)',
    'amazon ec2' : 'amazon web services (aws)',
    'amazon s3' : 'amazon web services (aws)',
    'aws' : 'amazon web services (aws)',
    'aws command line interface (cli)' : 'amazon web services (aws)',
    'aws s3' : 'amazon web services (aws)',
    'c' : 'c (programming language)',
    'c language' : 'c (programming language)',
    'c programming' : 'c (programming language)',
    'c++ language' : 'c++',
    'c++11' : 'c++',
    'c/c++ stl' : 'c++',
    'c\\c++' : 'c++',
    'data manipulation' : 'data cleaning',
    'data warehouse architecture' : 'data warehousing',
    'data wrangling' : 'data cleaning',
    'data structures' : 'data structures and algorithms',
    'data warehousing' : 'data warehouse architecture',
    'database design' : 'database development',
    'datawarehousing' : 'data warehousing',
    'dbms' : 'database management system (dbms)',
    'etl' : 'extract, transform, load (etl)',
    'eda' : 'exploratory data analysis',
    'java enterprise edition' : 'java',
    'jquery ui' : 'jquery',
    'high performance computing' : 'high performance computing (hpc)',
    'advanced excel' : 'microsoft excel',
    'excel' : 'microsoft excel',
    'powerbi' : 'power bi',
    'machine learning algorithms' : 'machine learning',
    'oracle pl/sql development' : 'oracle sql',
    'oracle sql developer' : 'oracle sql',
    'python' : 'python (programming language)',
    'python programming' : 'python (programming language)',
    'presentation' : 'presentation skills',
    'r' : 'r (programming language)',
    'r programing' : 'r (programming language)',
    'r programming' : 'r (programming language)',
    'r shiny application development' : 'r shiny',
    'sas certified base programmer' : 'sas (programming language)',
    'sas programming' : 'sas (programming language)',
    'sci-kit learn' : 'scikit-learn'
}

def remap_skills_basic(skills_list):
    '''
    helper function for remapping skills
    '''
    new_list = sorted(list(set(
        [
            skills_remapping_dict[i] if i in skills_remapping_dict.keys() else i 
            for i in skills_list
        ]
    )))
    return new_list

skills_df['skills_list_cleaned'] = skills_df['skills_list_cleaned'].apply(remap_skills_basic)

exploded_skills_df = skills_df.explode('skills_list_cleaned').reset_index(drop=True)
exploded_skills_df['skills_list'] = exploded_skills_df['skills_list'].astype(str)
exploded_skills_df['val'] = 1
skills_wide_df = pd.pivot(
    exploded_skills_df,
    index=['profile_id_dummy', 'all_skills_link', 'skills_list'],
    columns='skills_list_cleaned',
    values='val'
).reset_index()
pd.set_option('display.max_columns', 1000)
skills_wide_df.fillna(0, inplace=True)

print(skills_wide_df.head())
skills_wide_df.to_csv(CLEANED_FILES_PATH+'skills_info.csv', index=False)
