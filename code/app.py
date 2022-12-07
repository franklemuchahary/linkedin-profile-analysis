'''
this file contains all the code required for generating the visualizations and building a 
plotly dash app for the visualizations
'''

############# Imports #############
import sys
import os
import plotly.express as px
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from data_prep_visualizations import (
    skills_df,
    highest_education_level,
    popular_major_type_df,
    overall_years_of_exp,
    exp_df
)

sys.path.append(os.path.join(os.path.dirname(__file__)))

############# Initialize Dash App #############

app = Dash(__name__)

############# Define Plot Functions #############

###########################
###### skills plot 1 ######
@app.callback(
    Output('skills-graph', 'figure'),
    [Input("profile-type-dropdown", "value")]
)
def skills_barplot(profile_type):
    '''
    helper function for generating the skills barplot
    '''
    single_profile_type_skills = skills_df[skills_df['profile_category'] == profile_type].copy()
    skills_cols = single_profile_type_skills.columns.difference(
        ['profile_id_dummy', 'all_skills_link', 'skills_list', 'profile_category']
    )

    top_skills = single_profile_type_skills[skills_cols].sum(axis=0).sort_values(ascending=False).reset_index()
    top_skills.columns = ['skill_name', 'count_people']
    top_skills['percent_people'] = round((top_skills['count_people']/single_profile_type_skills.shape[0])*100,0)

    plt_df = top_skills.head(30)
    
    fig = px.bar(
        plt_df,
        x = 'skill_name',
        y = 'percent_people',
        text = 'percent_people',
        hover_data = ['percent_people'],
        height = 700,
        width = 1200,
        labels = dict(
            skill_name = "Skill Name", 
            percent_people = "Percent of People %"
        ),
        title = 'Top 30 Skills for ' + profile_type,
        template = 'simple_white'
    )
    fig.update_xaxes(tickangle=270)
    fig.update_layout(
        title={
            'text' : 'Top 30 Skills for ' + profile_type,
            'y' : 0.9,
            'x' : 0.5,
            'font' : dict(
                size = 18
            )
        }
    )
    return fig

###########################
### highest edu level plot
def highest_education_barplot():
    '''
    helper function for generating the highest level of education barplot
    '''
    subplot_fig = make_subplots(
        rows = 1,
        cols = 3,
        shared_yaxes = False,
        subplot_titles = ('Principal Data Scientists',  'Senior Consultants', 'Chief Technology Officers')

    )

    col = 1
    for pf, bar_color in [('Principal Data Scientists', 'DarkSeaGreen'), 
                          ('Senior Consultants', 'SteelBlue'), ('Chief Technology Officers', 'LightSalmon')]:
        fig = px.bar(
            highest_education_level[highest_education_level['profile_category'] == pf], 
            x = 'highest_edu_level',
            y = 'percent_people',
            text = 'percent_people',
            facet_col = 'profile_category',
            color_discrete_sequence = [bar_color],
            hover_data = ['percent_people'],
            labels = dict(
                highest_edu_level = "Highest Education Level", 
                percent_people = "Percent of People %",
                profile_category = 'Profile Category'
            )
        )
        subplot_fig.append_trace(fig['data'][0], row = 1, col = col)
        col += 1


    subplot_fig.update_layout(
        template = 'simple_white'
    )
    subplot_fig.update_xaxes(tickangle=270)
    subplot_fig.update_layout(
        title = {
            'text' : 'Higest Education Level for All Profile Categories',
            'y' : 0.95,
            'x' : 0.5,
            'font' : dict(
                size = 18
            )
        },
        height = 550,
        width = 1200,
        barmode = 'stack',
        xaxis = {'title' : 'Highest Education Level'},
        xaxis2 = {'title' : 'Highest Education Level'},
        xaxis3 = {'title' : 'Highest Education Level'},
        yaxis = {'title' : 'Percent of People %'}
    )
    return subplot_fig

############################
### popular major types plot
def popular_majors_barplot():
    '''
    helper function for generating the popular majors barplot
    '''
    subplot_fig = make_subplots(
        rows = 1,
        cols = 3,
        shared_yaxes = False,
        subplot_titles = ('Principal Data Scientists',  'Senior Consultants', 'Chief Technology Officers')

    )

    col = 1
    for pf, bar_color in [('Principal Data Scientists', 'DarkSeaGreen'), 
                          ('Senior Consultants', 'SteelBlue'), ('Chief Technology Officers', 'LightSalmon')]:
        fig = px.bar(
            popular_major_type_df[popular_major_type_df['profile_category'] == pf], 
            x = 'major_type',
            y = 'percent_people',
            text = 'percent_people',
            facet_col = 'profile_category',
            color_discrete_sequence = [bar_color],
            hover_data = ['percent_people'],
            labels = dict(
                major_type = "Most Popular Majors", 
                percent_people = "Percent of People %",
                profile_category = 'Profile Category'
            ),
            orientation = 'v'
        )
        subplot_fig.append_trace(fig['data'][0], row = 1, col = col)
        col += 1


    subplot_fig.update_layout(
        template = 'simple_white'
    )
    subplot_fig.update_xaxes(tickangle=270)
    subplot_fig.update_layout(
        title = {
            'text' : 'Most Popular Majors For Each Profile Category',
            'y' : 0.95,
            'x' : 0.5,
            'font' : dict(
                size = 18
            )
        },
        height = 650,
        width = 1400,
        barmode = 'stack',
        xaxis = {'title' : 'Type of Major', 'tickfont' : dict(size=11)},
        xaxis2 = {'title' : 'Type of Major', 'tickfont' : dict(size=11)},
        xaxis3 = {'title' : 'Type of Major', 'tickfont' : dict(size=11)},
        yaxis = {'title' : 'Percent of People %'}
    )
    return subplot_fig

#################################
### years of exp histogram - v1
@app.callback(
    Output('yoe-graph-v1', 'figure'),
    [Input("profile-type-multi-dropdown", "value")]
)
def yoe_histogram_v1(profile_type):
    '''
    helper function for generating the years of experience histogram
    '''
    if type(profile_type) == str:
        profile_type = [profile_type]
    plt_df = overall_years_of_exp[overall_years_of_exp['profile_category'].isin(profile_type)]

    fig = px.histogram(
        plt_df, 
        x = 'months_exp',
        color = 'profile_category',
        text_auto = '.1f',
        nbins = 20,
        height = 600,
        width = 1100,
        histnorm='percent',
        labels = dict(
            months_exp = "Months of Experience",
            profile_category = 'Profile Type'
        ),
        template = 'simple_white',
        barmode = 'relative',
        color_discrete_map = {
            'Principal Data Scientists' : 'DarkSeaGreen', 
            'Senior Consultants' : 'SteelBlue',
            'Chief Technology Officers' : 'LightSalmon'
        }
    )
    fig.update_xaxes(tickangle=270)
    fig.update_layout(
        title = {
            'text' : 'Distribution of "Years of Experience Before Reaching Latest Position"',
            'x' : 0.5,
            'font' : dict(
                size = 18
            )
        },
        yaxis = {'title': 'Percentage of People %'}
    )
    return fig

##################################################
### specific roles analysis for data science - v1
def specific_previous_roles_v1(profile_type):
    n_roles = 3
    role_title1 = 'intern'
    role_title2 = 'analyst'
    role_title3, role_title3_neg = 'engineer', 'machine learning'
    single_prof_exp = exp_df[exp_df['profile_category'] == profile_type].copy()
    single_prof_exp['positions'].fillna('', inplace = True)
    single_prof_exp[role_title1] = single_prof_exp['positions'].str.contains(role_title1)
    single_prof_exp[role_title2] = single_prof_exp['positions'].str.contains(role_title2)
    single_prof_exp[role_title3] = (
        (single_prof_exp['positions'].str.contains(role_title3)) & 
        ~(single_prof_exp['positions'].str.contains(role_title3_neg))
    )
    subset_profiles_roles = single_prof_exp.groupby(
            'profile_id_dummy'
    )[[role_title1, role_title2, role_title3]].max().reset_index()
   
    subplot_fig = make_subplots(
        rows = 1,
        cols = n_roles,
        specs = [[{'type':'domain'}]*n_roles],
        subplot_titles = (
            role_title1.capitalize() + '<br>(Data Science/Analyst)',
            role_title2.capitalize() + '<br>(Data/Business/Research Analyst)',
            role_title3.capitalize() + '<br>(SDE/Other Engineer)'
        )

    )

    col = 1
    for role in [role_title1, role_title2, role_title3]:
        plt_df = subset_profiles_roles.groupby(role)['profile_id_dummy'].nunique().reset_index()
        fig = px.pie(
            plt_df,
            values = 'profile_id_dummy',
            color = role,
            labels = dict(
                profile_id_dummy = "Number of People", 
                profile_category = 'Profile Category'
            ),
            hole = 0.6,
            color_discrete_map = {
                True : 'DodgerBlue', 
                False : 'LightSalmon'
            }
        )
        subplot_fig.append_trace(fig['data'][0], row = 1, col = col)
        col += 1


    subplot_fig.update_layout(
        template = 'simple_white'
    )
    subplot_fig.update_layout(
        height = 500,
        width = 1100
    )
    return subplot_fig

##################################################
############# Define Dash Components #############
##################################################

skills_dash_component = [
    html.H1("SKILLS"),
    html.Br(),
    html.H3("Analyzing the Top Skills for Each Profile Type"),
    html.Div(
        [
            dcc.Dropdown(
                id = 'profile-type-dropdown',
                clearable=False,
                value = 'Principal Data Scientists',
                options = [
                    {'label': item, 'value': item}
                    for item in ['Principal Data Scientists',  'Senior Consultants', 'Chief Technology Officers']
                ]
            )
        ],
        style = {
            'width': '30%', 'display': 'inline-block'
        }
    ),
    html.Br(),
    html.Div(
        [dcc.Graph(id = 'skills-graph')], 
        style = {
            'width': '100%'
        }
    ),
]

intermediate_component = [
    html.Br(),
    html.Hr(
        style = {
            'width': '80%', 'height': '1px', 'color': 'gray', 'background': 'black'
        }
    ),
    html.Br()
]

intermediate_component_large = [
    html.Br(),
    html.Hr(
        style = {
            'width': '98%', 'height': '2.5px', 'color': 'red', 'background': 'red'
        }
    ),
    html.Br()
]

header_component = [
    html.H1("ANALYSIS OF LINKEDIN PROFILES FOR CREATING A CAREER GUIDE"),
    html.Hr(
        style = {
            'width': '98%', 'height': '2.5px', 'color': 'red', 'background': 'red'
        }
    ),
    html.Br(),
]

highest_edu_dash_component = [
    html.H1("EDUCATION"),
    html.Br(),
    html.H3("Analyzing the Most Popular Highest Education Levels for Each Profile Type"),
    html.Br(),
    html.Div(
        [dcc.Graph(id = 'highest-edu-graph', figure = highest_education_barplot())],
        style = {
            'width': '100%'
        }
    )
]

popular_majors_dash_component = [
    html.H3("Analyzing the Most Popular Major Types for Each Profile Type"),
    html.Br(),
    html.Div(
        [dcc.Graph(id = 'most-popular-majors-graph', figure = popular_majors_barplot())],
        style = {
            'width': '100%'
        }
    )
]


yoe_v1_dash_component = [
    html.H1("EXPERIENCE"),
    html.Br(),
    html.H3("Analyzing Years of Experience Required to Reach Latest Position"),
    html.Div(
        [
            dcc.Dropdown(
                id = 'profile-type-multi-dropdown',
                clearable = False,
                value = 'Principal Data Scientists',
                options = [
                    {'label': item, 'value': item}
                    for item in ['Principal Data Scientists',  'Senior Consultants', 'Chief Technology Officers']
                ],
                multi = True
            )
        ],
        style = {
            'width': '30%', 'display': 'inline-block'
        }
    ),
    html.Div(
        [dcc.Graph(id = 'yoe-graph-v1')],
        style = {
            'width': '100%'
        }
    )
]


ds_roles_v1_dash_component = [
    html.H3("Previous Roles Held By Top Data Scientists"),
    html.Br(),
    html.Div(
        [dcc.Graph(id = 'ds-roles-v1-graph', figure = specific_previous_roles_v1('Principal Data Scientists'))],
        style = {
            'width': '100%'
        }
    )
]

#############################################################
############# Bind Dash App Components Together #############

app.layout = html.Center(
    header_component +\
    skills_dash_component +\
    intermediate_component_large +\
    highest_edu_dash_component +\
    intermediate_component + popular_majors_dash_component +\
    intermediate_component_large +\
    yoe_v1_dash_component +\
    intermediate_component + ds_roles_v1_dash_component,
    style = {
        'justify' : 'center', 'align' : 'center'
    }
)

if __name__ == '__main__':
    app.run_server(
        #mode = 'external',
        port = 3300,
        debug = False
    )
    