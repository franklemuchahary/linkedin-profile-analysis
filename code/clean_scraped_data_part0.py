'''
initial basic data cleaning on the scraped profile links data
'''

import pandas as pd

### cleaning cto profile link dataset
df = pd.read_csv('data/CTOProfiles.csv')


print(df.shape)
df = df.dropna(axis=0)
df.drop_duplicates(inplace=True)

if 'profile_id_dummy' not in df.columns:
    df = df.reset_index(drop=True).reset_index()
    df.rename(columns={'index':'profile_id_dummy'}, inplace=True)
else:
    print('Already Exists')

print(df.head(30))
print(df.shape)

df.to_csv('data/cleaned_cto_files/cto_profile_links.csv', index=False)


### cleaning and consolidating consultant profile link dataset
consultant_df = pd.concat(
    [
        pd.read_csv('data/ConsultantProfiles-V1.csv').head(60),
        pd.read_csv('data/ConsultantProfiles-V2.csv').head(70),
        pd.read_csv('data/ConsultantProfiles-V3.csv').head(70)
    ]
).reset_index(drop=True)

print(consultant_df.shape)
consultant_df.drop_duplicates(inplace=True)
consultant_df = consultant_df.dropna(axis=0)

if 'profile_id_dummy' not in consultant_df.columns:
    consultant_df = consultant_df.reset_index(drop=True).reset_index()
    consultant_df.rename(columns={'index':'profile_id_dummy'}, inplace=True)
else:
    print('Already Exists')

print(consultant_df.head(30))
print(consultant_df.shape)
consultant_df.to_csv('data/cleaned_consultant_files/consultant_profile_links.csv', index=False)


### Data Science Profile Links
df = pd.read_csv('data/DataScienceProfiles.csv')

print(df.shape)
df = df.dropna(axis=0)
df.drop_duplicates(inplace=True)

if 'profile_id_dummy' not in df.columns:
    df = df.reset_index(drop=True).reset_index()
    df.rename(columns={'index':'profile_id_dummy'}, inplace=True)
else:
    print('Already Exists')

print(df.head(30))
print(df.shape)
df.to_csv('data/cleaned_data_science_files/data_science_profile_links.csv', index=False)
