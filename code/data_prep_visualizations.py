'''
This file contains all the code for data cleaning and transformations
required for creating visualizations
'''

#################################################
#################### Imports ####################

import re
from datetime import datetime
import pandas as pd
import numpy as np

######################################################################
#################### Load the Created Final Files ####################

skills_df = pd.read_csv('data/final_cleaned_files/all_skills_info.csv')
edu_df = pd.read_csv('data/final_cleaned_files/all_education_info.csv')
exp_df = pd.read_csv('data/final_cleaned_files/all_name_and_experience_info.csv')

profile_category_mapping = {
    'DataScience' : 'Principal Data Scientists',
    'CTO': 'Chief Technology Officers',
    'Consultant' : 'Senior Consultants'
}

skills_df['profile_category'] = skills_df['profile_category'].map(profile_category_mapping)
edu_df['profile_category'] = edu_df['profile_category'].map(profile_category_mapping)
exp_df['profile_category'] = exp_df['profile_category'].map(profile_category_mapping)


##################################################################
#################### Education Level Analysis ####################
edu_df['degree_name'] = edu_df['degree_name'].str.lower()

### Bachelor
bachelor_pattern = (
    r'^(b\.{0,}\s{0,1}tech\.{0,}|b\.{0,}s\.{0,}|bachelor\’{0,}\'{0,}s{0,}|bachellor|'
    r'b\.{0,}sc\.{0,}|b\.{0,}a\.{0,}|b\.{0,}b\.{0,}a\.{0,}|b\.{0,}e\.{0,})(?:,|\)|\(|\s)'
)
print(bachelor_pattern)

edu_df['degree_bachelor'] = edu_df['degree_name'].apply(
    lambda x: 'bachelor' if re.match(bachelor_pattern, str(x)) is not None else None
)
print(edu_df.head())

### Master
master_pattern = (
    r"^(master\'{0,1}\’{0,1}s{0,1}|m\.{0,1}s\.{0,1}|m\.{0,1}a\.{0,1}|m\.{0,1}sc\.{0,1}|"
    r"m\.{0,1}eng\.{0,1}|mca|post graduate)(?:,|\)|\(|\s)"
)
edu_df['degree_master'] = edu_df['degree_name'].apply(
    lambda x: 'master' if re.match(master_pattern, str(x)) is not None else None
)
print(edu_df.head())

### PhD
phd_pattern = (
    r"^(p\.{0,1}h\.{0,1}d\.{0,1}|doctor of philosophy|doctorate)(?:,|\)|\(|\s)"
)
edu_df['degree_doctorate'] = edu_df['degree_name'].apply(
    lambda x: 'phd' if re.match(phd_pattern, str(x)) is not None else None
)
print(edu_df.head())

### MBA
mba_pattern = (
    r"(m\.{0,1}b\.{0,1}a\.{0,1}|master of business|p\.{0,1}g\.{0,1}d\.{0,1}m\.{0,1}|post graduate diploma in management|"
    r"post graduate programm{0,1}e{0,1} in management |pgp|pgpx)(?:,|\)|\(|\s)"
)
edu_df['degree_mba'] = edu_df['degree_name'].apply(
    lambda x: 'mba' if re.match(mba_pattern, str(x)) is not None else None
)
print(edu_df.head())

### Extract the Highest Level of Education for each Candidate
edu_df['education_degree_all'] = edu_df['degree_bachelor'].astype(str) + '#' + edu_df['degree_master'].astype(str) + '#' +\
        edu_df['degree_mba'].astype(str) + '#' + edu_df['degree_doctorate'].astype(str)

profile_level_education = edu_df.groupby(['profile_category', 'profile_id_dummy'])['education_degree_all'].agg(
    lambda x: list(dict.fromkeys(('#'.join(x)).split('#')))
).reset_index()

def get_highest_level_of_edu(x):
    if 'phd' in x:
        edu_level = 'PhD'
    elif 'mba' in x:
        edu_level = 'MBA'
    elif 'master' in x:
        edu_level = 'Master'
    elif 'bachelor' in x:
        edu_level = 'Bachelor'
    else:
        edu_level = 'Other'
   
    return edu_level

profile_level_education['highest_edu_level'] = profile_level_education['education_degree_all'].apply(get_highest_level_of_edu)

highest_education_level = profile_level_education.groupby(
    ['profile_category', 'highest_edu_level']
)['profile_id_dummy'].nunique().reset_index()

highest_education_level['percent_people'] = highest_education_level['profile_id_dummy']/highest_education_level.groupby(
    'profile_category'
)['profile_id_dummy'].transform('sum')
highest_education_level['percent_people'] = (highest_education_level['percent_people']*100).astype(int)
highest_education_level = highest_education_level.sort_values(
    ['profile_category', 'percent_people'], ascending = [True, False]
).reset_index(drop=True)
print(highest_education_level.head())



##################################################################
#################### Major Type Analysis #########################
def engineering_business_degree(x):
    '''
    Helper function for extracting the type of major pursued by the person
    '''
    stem_match = re.search(
        r"(computer|stat|physics|chem|math|data science|machine|quant|bio|operations research)",
        x
    )
    
    mba_match = re.search(
        r"(m\.{0,1}b\.{0,1}a\.{0,1}|pgdm|pgp)",
        x
    )
    
    if 'engineer' in x:
        major_type = 'Engineering'
    elif 'business' in x or 'econ' in x or mba_match is not None:
        major_type = 'Business/Economics'
    elif 'engineer' not in x and stem_match is not None:
        major_type = 'STEM (Non-Engineering)'
    else:
        major_type = ''
    
    return major_type

edu_df['major_type'] = edu_df['degree_name'].astype(str).apply(engineering_business_degree)

major_type_df = edu_df.groupby(
    ['profile_category', 'profile_id_dummy']
)['major_type'].agg(
    lambda x: ' & <br> '.join(
        [i for i in sorted(set(x)) if i!='']
    )
).reset_index(drop=False)

popular_major_type_df = major_type_df.groupby(
    ['profile_category', 'major_type']
)['profile_id_dummy'].nunique().reset_index(drop=False)

popular_major_type_df['major_type'] = np.where(
    popular_major_type_df['major_type'] == '',
    'Other',
    popular_major_type_df['major_type']
)

popular_major_type_df['percent_people'] = popular_major_type_df['profile_id_dummy']/popular_major_type_df.groupby(
    'profile_category'
)['profile_id_dummy'].transform('sum')
popular_major_type_df['percent_people'] = (popular_major_type_df['percent_people']*100).astype(int)
popular_major_type_df = popular_major_type_df.sort_values(
    ['profile_category', 'percent_people'], ascending = [True, False]
).reset_index(drop=True)
print(popular_major_type_df.head())



#################################################################################
#################### Total Years of Experience Analysis #########################

exp_df['positions'] = exp_df['positions'].str.lower()
exp_df['positions'].fillna('', inplace=True)

single_prof_exp = exp_df.copy()
single_prof_exp.sort_values(['profile_category', 'profile_id_dummy', 'start_date'], inplace=True)

single_prof_exp['start_date'] = pd.to_datetime(single_prof_exp['start_date'])
single_prof_exp['end_date'] = pd.to_datetime(single_prof_exp['end_date'])

single_prof_exp['exp_ranked'] = single_prof_exp.groupby(
    ['profile_category', 'profile_id_dummy']
)['start_date'].transform(lambda x: x.rank(method='first'))
single_prof_exp['max_end_date'] = single_prof_exp.groupby(
    ['profile_category', 'profile_id_dummy']
)['end_date'].transform('max')

single_prof_exp = single_prof_exp[
    (single_prof_exp['start_date'] > datetime.strptime('1930-01-01', '%Y-%m-%d')) &
    (single_prof_exp['end_date'] != single_prof_exp['max_end_date'])
]

overall_years_of_exp = single_prof_exp.groupby([
    'profile_category', 'profile_id_dummy', 'end_date'
])['start_date'].min().reset_index()

overall_years_of_exp['months_exp'] = ((
    (overall_years_of_exp['end_date'] - overall_years_of_exp['start_date']).dt.days)/30).astype(int)

overall_years_of_exp = overall_years_of_exp.groupby(
    ['profile_category', 'profile_id_dummy']
)['months_exp'].sum().reset_index()

upper_threshold = np.mean(overall_years_of_exp['months_exp']) + 3*np.std(overall_years_of_exp['months_exp'])
lower_threshold = np.mean(overall_years_of_exp['months_exp']) - 3*np.std(overall_years_of_exp['months_exp'])

overall_years_of_exp = overall_years_of_exp[
    (overall_years_of_exp['months_exp'] < upper_threshold) &
    (overall_years_of_exp['months_exp'] > lower_threshold)
].copy()

print(overall_years_of_exp.head())



##########################################################################
#################### Previous Role Type Analysis #########################

def previous_role_type_analysis(profile_type, exp_df,
                                role_title1 = '', role_title1_name = '',
                                role_title2 = '', role_title2_name = '',
                                role_title3 = '', role_title3_name = ''):
    '''
    helper function for analyzing previous role types
    '''

    single_prof_exp = exp_df[exp_df['profile_category'] == profile_type].copy()
    single_prof_exp['positions'].fillna('', inplace = True)

    single_prof_exp[role_title1_name] = single_prof_exp['positions'].str.contains(role_title1)
    single_prof_exp[role_title2_name] = single_prof_exp['positions'].str.contains(role_title2)
    
    if profile_type == 'Principal Data Scientists':
        role_title3_neg = 'machine learning'
        single_prof_exp[role_title3_name] = (
            (single_prof_exp['positions'].str.contains(role_title3)) & 
            ~(single_prof_exp['positions'].str.contains(role_title3_neg))
        )
        
        list_cols = [role_title1_name, role_title2_name, role_title3_name]
    else:
        list_cols = [role_title1_name, role_title2_name]
        
    subset_profiles_roles = single_prof_exp.groupby(
        'profile_id_dummy'
    )[list_cols].max().reset_index()

    plt_df = subset_profiles_roles.groupby(role_title1_name)['profile_id_dummy'].nunique().reset_index()
    print(plt_df)
    
    return subset_profiles_roles

### principal data scientists
pds_roles_df = previous_role_type_analysis(
    profile_type = 'Principal Data Scientists',
    exp_df = exp_df.copy(),
    role_title1 = 'intern',
    role_title1_name = 'Intern Roles',
    role_title2 = 'analyst',
    role_title2_name = 'Analyst Roles',
    role_title3 = 'engineer',
    role_title3_name = 'Engineer Roles'
)

### chief technology officers
cto_roles_df = previous_role_type_analysis(
    profile_type = 'Chief Technology Officers',
    exp_df = exp_df.copy(),
    role_title1 = r'(manager|lead|head)',
    role_title1_name = 'Managerial Roles',
    role_title2 = r'software engineer|architect|staff engineer|scientist',
    role_title2_name = 'Software Engineer/Architect/Research Scientist'
)

### senior consultants
consultant_roles_df = previous_role_type_analysis(
    profile_type = 'Senior Consultants',
    exp_df = exp_df.copy(),
    role_title1 = r'(analyst|trainee|business analytics)',
    role_title1_name = 'Analyst Roles',
    role_title2 = r'intern',
    role_title2_name = 'Intern Roles'
)


##########################################################################################
#################### Length of Relationship With Current Company #########################

exp_df['positions'] = exp_df['positions'].str.lower()
exp_df['positions'].fillna('', inplace=True)
exp_df['start_date'] = pd.to_datetime(exp_df['start_date'])
exp_df['end_date'] = pd.to_datetime(exp_df['end_date'])

exp_df['company_max_end_date'] = exp_df.groupby(
        ['profile_id_dummy', 'company']
    )['end_date'].transform('max')

exp_df['company_exp_ranked'] = exp_df.groupby(
    ['profile_category', 'profile_id_dummy']
)['company_max_end_date'].transform(lambda x: x.rank(method='dense', ascending=False))


###### Number of Months in Latest Company ######
# get the latest company
latest_company_info = exp_df[exp_df['company_exp_ranked'] == 1].copy()

# calculate time in latest company
time_period_latest_company = latest_company_info.groupby(
    ['profile_category', 'profile_id_dummy'])[['start_date', 'end_date']].agg({
        'start_date': 'min', 
        'end_date': 'max'
    }).reset_index()

time_period_latest_company['months_of_exp_latest'] = round(
    ((time_period_latest_company['end_date'] - time_period_latest_company['start_date']).dt.days)/30, 0
).astype(int)

print(time_period_latest_company.head())

###### Number of Roles in Latest Company ######
num_roles_latest_company = latest_company_info.groupby(
    ['profile_category', 'profile_id_dummy']
)['positions'].nunique().reset_index()

num_roles_latest_company = num_roles_latest_company.groupby(
    ['profile_category', 'positions']
)['profile_id_dummy'].nunique().reset_index()

num_roles_latest_company['percent_people'] = round((num_roles_latest_company['profile_id_dummy']/num_roles_latest_company.groupby(
    ['profile_category']
)['profile_id_dummy'].transform('sum'))*100,1)
num_roles_latest_company['positions'] = num_roles_latest_company['positions'].astype(str)

print(num_roles_latest_company.head())



##########################################################################################
print("************* Done *************")
