'''
merging and concatenating_files
'''

import pandas as pd

#### Experience Table
ds = pd.read_csv('data/cleaned_data_science_files/name_and_experience_info.csv')
ds['profile_category'] = 'DataScience'
print(ds.head())

cto = pd.read_csv('data/cleaned_cto_files/name_and_experience_info.csv')
cto['profile_category'] = 'CTO'
print(cto.head())

consultant = pd.read_csv('data/cleaned_consultant_files/name_and_experience_info.csv')
consultant['profile_category'] = 'Consultant'
print(consultant.head())

exp_df = pd.concat(
    [ds, cto, consultant]
).reset_index(drop=True)

exp_df['profile_id_dummy'] = exp_df['profile_category'].astype(str) +  '_' + exp_df['profile_id_dummy'].astype(str)

print(exp_df.head())
print(exp_df.shape)
print(exp_df.columns)
exp_df.to_csv('data/final_cleaned_files/all_name_and_experience_info.csv', index=False)

#### Education Table
ds = pd.read_csv('data/cleaned_data_science_files/education_info.csv')
ds['profile_category'] = 'DataScience'
print(ds.head())

cto = pd.read_csv('data/cleaned_cto_files/education_info.csv')
cto['profile_category'] = 'CTO'
print(cto.head())

consultant = pd.read_csv('data/cleaned_consultant_files/education_info.csv')
consultant['profile_category'] = 'Consultant'
print(consultant.head())

edu_df = pd.concat(
    [ds, cto, consultant]
).reset_index(drop=True)

edu_df['profile_id_dummy'] = edu_df['profile_category'].astype(str) +  '_' + edu_df['profile_id_dummy'].astype(str)

print(edu_df.head())
print(edu_df.shape)
print(edu_df.columns)
edu_df.to_csv('data/final_cleaned_files/all_education_info.csv', index=False)


#### Education Table
ds = pd.read_csv('data/cleaned_data_science_files/skills_info.csv')
ds['profile_category'] = 'DataScience'
print(ds.head())
print(ds.shape)

cto = pd.read_csv('data/cleaned_cto_files/skills_info.csv')
cto['profile_category'] = 'CTO'
print(cto.head())
print(cto.shape)

consultant = pd.read_csv('data/cleaned_consultant_files/skills_info.csv')
consultant['profile_category'] = 'Consultant'
print(consultant.head())
print(consultant.shape)

skills_df = pd.concat(
    [ds, cto, consultant]
).reset_index(drop=True)

skills_df['profile_id_dummy'] = skills_df['profile_category'].astype(str) +  '_' + skills_df['profile_id_dummy'].astype(str)

print(skills_df.head())
print(skills_df.shape)
print(skills_df.columns)
print(skills_df.isna().sum())
skills_df.fillna(0, inplace=True)

skills_df.to_csv('data/final_cleaned_files/all_skills_info.csv', index=False)
