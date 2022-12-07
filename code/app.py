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
    pds_roles_df,
    cto_roles_df,
    consultant_roles_df,
    time_period_latest_company,
    num_roles_latest_company
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
            'text' : 'Top 30 Skills Listed By ' + profile_type,
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
            'text' : 'Distribution of "Months of Prior Experience Before Reaching Current Position"',
            'x' : 0.5,
            'font' : dict(
                size = 18
            )
        },
        yaxis = {'title': 'Percentage of People %'}
    )
    return fig

##################################################
### specific previous roles for all profile types
def previous_role_type_plot(profile_type, subset_profiles_roles_df,
                            role_title1 = '', role_title1_name = '', role1_details = '',
                            role_title2 = '', role_title2_name = '', role2_details = '',
                            role_title3 = '', role_title3_name = '', role3_details = '',):
    '''
    helper function for generating previous role donut plots
    '''
    
    if profile_type == 'Principal Data Scientists':
        list_cols = [role_title1_name, role_title2_name, role_title3_name]
        cols = 3
    else:
        list_cols = [role_title1_name, role_title2_name]
        cols = 2
        
    subplot_fig = make_subplots(
        rows = 1,
        cols = cols,
        specs = [[{'type':'domain'}]*cols],
        subplot_titles = (
            role_title1_name + '<br>' + role1_details,
            role_title2_name + '<br>' + role2_details,
            role_title3_name + '<br>' + role3_details
        )

    )

    col = 1
    for role in list_cols:
        plt_df = subset_profiles_roles_df.groupby(role)['profile_id_dummy'].nunique().reset_index()
        fig = px.pie(
            plt_df, 
            values = 'profile_id_dummy',
            color = role,
            labels = dict(
                major_type = "Most Popular Majors", 
                percent_people = "Percent of People %",
                profile_category = 'Profile Category'
            ),
            hole = 0.6,
            color_discrete_map = {
                True : 'OliveDrab',
                False : 'BurlyWood'
            }
        )
        subplot_fig.append_trace(fig['data'][0], row = 1, col = col)
        col += 1


    subplot_fig.update_layout(
        template = 'simple_white'
    )
    subplot_fig.update_layout(
        # title = {
        #     'text' : 'Previous Roles Held by ' + profile_type,
        #     'y' : 0.99,
        #     'x' : 0.5,
        #     'font' : dict(
        #         size = 18
        #     )
        # },
        height = 500,
        width = 1100
    )
    return subplot_fig


#############################################
### months of exp in latest company histogram
@app.callback(
    Output('yoe-graph-current-company', 'figure'),
    [Input("profile-type-multi-dropdown-current-company", "value")]
)
def current_company_yoe_histogram(profile_type):
    '''
    helper function for generating the years of experience histogram
    '''
    if type(profile_type) == str:
        profile_type = [profile_type]
    plt_df = time_period_latest_company[time_period_latest_company['profile_category'].isin(profile_type)]

    fig = px.histogram(
        plt_df, 
        x = 'months_of_exp_latest',
        color = 'profile_category',
        text_auto = '.1f',
        nbins = 20,
        height = 600,
        width = 1100,
        histnorm='percent',
        labels = dict(
            months_of_exp_latest = "Months of Experience at Current Comapny",
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
            'text' : 'Distribution of "Months of Experience at the Current Company"',
            'x' : 0.5,
            'font' : dict(
                size = 18
            )
        },
        yaxis = {'title': 'Percentage of People %'}
    )
    return fig


################################################
### number of positions held at current company
def current_company_num_positions():
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
            num_roles_latest_company[num_roles_latest_company['profile_category'] == pf],
            x = 'positions',
            y = 'percent_people',
            text = 'percent_people',
            facet_col = 'profile_category',
            color_discrete_sequence = [bar_color],
            hover_data = ['percent_people'],
            labels = dict(
                positions = "Number of Positions", 
                percent_people = "Percent of People %",
                profile_category = 'Profile Category'
            )
        )
        subplot_fig.append_trace(fig['data'][0], row = 1, col = col)
        col += 1


    subplot_fig.update_layout(
        template = 'simple_white'
    )
    subplot_fig.update_xaxes(tickangle=0)
    subplot_fig.update_layout(
        title = {
            'text' : 'Number of Positions Held at Current Company',
            'y' : 0.95,
            'x' : 0.5,
            'font' : dict(
                size = 18
            )
        },
        height = 550,
        width = 1200,
        barmode = 'stack',
        xaxis = {'title' : 'Number of Positions'},
        xaxis2 = {'title' : 'Number of Positions'},
        xaxis3 = {'title' : 'Number of Positions'},
        yaxis = {'title' : 'Percent of People %'}
    )
    return subplot_fig


##################################################
############# Define Dash Components #############
##################################################

### skills barplot
skills_dash_component = [
    html.H1("SKILLS"),
    html.Br(),
    html.H3("Analyzing the Top Skills Listed By Each Profile Type"),
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

### intermediate
intermediate_component = [
    html.Br(),
    html.Hr(
        style = {
            'width': '80%', 'height': '1px', 'color': 'gray', 'background': 'black'
        }
    ),
    html.Br()
]

### intermediate large
intermediate_component_large = [
    html.Br(),
    html.Hr(
        style = {
            'width': '98%', 'height': '2.5px', 'color': 'red', 'background': 'red'
        }
    ),
    html.Br()
]

### header
header_component = [
    html.H1("ANALYSIS OF LINKEDIN PROFILES FOR CREATING A CAREER GUIDE"),
    html.P('MSIS-5193 Final Project, Created By - The Data Janitors (Frankle Muchahary, Jayke Ratliff, Kushal Kulshreshtha, Rachel Puls)'),
    html.Hr(
        style = {
            'width': '98%', 'height': '2.5px', 'color': 'red', 'background': 'red'
        }
    ),
    html.Br(),
]

### education
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

### experience 1
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

### experience 2
previous_roles_v1_dash_component = [
    html.H3("Previous Roles Held By Principal Data Scientists"),
    html.P("(% of people that held these roles)"),
    html.Div(
        [
            dcc.Graph(
                id = 'ds-roles-v1-graph', 
                figure = previous_role_type_plot(
                    profile_type = 'Principal Data Scientists',
                    subset_profiles_roles_df = pds_roles_df,
                    role_title1 = 'intern',
                    role_title1_name = 'Intern Roles',
                    role1_details = '(Data Science/Analyst Interns)',
                    role_title2 = 'analyst',
                    role_title2_name = 'Analyst Roles',
                    role2_details = '(Data/Business/Research Analyst)',
                    role_title3 = 'engineer',
                    role_title3_name = 'Engineer Roles',
                    role3_details = '(SDE/Other Engineer)',
                )
            )
        ],
        style = {
            'width': '100%'
        }
    ),
    html.Hr(
        style = {
            'width': '50%', 'height': '0.3px', 'color': 'LightGray', 'background': 'LightGray'
        }
    ),
    html.H3("Previous Roles Held By Top Chief Technology Officers"),
    html.P("(% of people that held these roles)"),
    html.Div(
        [
            dcc.Graph(
                id = 'cto-roles-v1-graph',
                figure = previous_role_type_plot(
                    profile_type = 'Chief Technology Officers',
                    subset_profiles_roles_df = cto_roles_df,
                    role_title1 = r'(manager|lead|head)',
                    role_title1_name = 'Managerial Roles',
                    role1_details = '(Manager or Lead of a Team)',
                    role_title2 = r'software engineer|architect|staff engineer|scientist',
                    role_title2_name = 'Software Engineer/Architect/Research Scientist',
                    role2_details = '(Senior Engineering, Architect, or Research Roles)',
                )
            )
        ],
        style = {
            'width': '100%'
        }
    ),
    html.Hr(
        style = {
            'width': '50%', 'height': '0.3px', 'color': 'LightGray', 'background': 'LightGray'
        }
    ),
    html.H3("Previous Roles Held By Senior Consultants"),
    html.P("(% of people that held these roles)"),
    html.Div(
        [
            dcc.Graph(
                id = 'consultant-roles-v1-graph', 
                figure = previous_role_type_plot(
                    profile_type = 'Senior Consultants',
                    subset_profiles_roles_df = consultant_roles_df,
                    role_title1 = r'(analyst|trainee|business analytics)',
                    role_title1_name = 'Analyst Roles',
                    role1_details = '(Associate Analyst/Business Analyst/Research Analyst)',
                    role_title2 = r'intern',
                    role_title2_name = 'Intern Roles',
                    role2_details = '(Any Internship Position)',
                )
            )
        ],
        style = {
            'width': '100%'
        }
    )
]

### experience 3
current_company_yoe_dash_component = [
    html.H3("Analyzing Months of Experience at the Current Company"),
    html.Div(
        [
            dcc.Dropdown(
                id = 'profile-type-multi-dropdown-current-company',
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
        [dcc.Graph(id = 'yoe-graph-current-company')],
        style = {
            'width': '100%'
        }
    )
]

### experience 4
current_company_num_positions_component = [
    html.H3("Analyzing the Number of Positions Held at Current Company"),
    html.Br(),
    html.Div(
        [dcc.Graph(id = 'current-company-positions-graph', figure = current_company_num_positions())],
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
    intermediate_component + previous_roles_v1_dash_component +\
    intermediate_component + current_company_yoe_dash_component +\
    intermediate_component + current_company_num_positions_component +\
    intermediate_component_large,
    style = {
        'justify' : 'center', 'align' : 'center'
    }
)

############################################
############# Run the Dash App #############

if __name__ == '__main__':
    app.run_server(
        port = 3300,
        debug = False
    )
    