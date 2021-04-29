#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px


"""

df = players

teams = team stats

top_5_teams = top 5 teams sorted by points

top_5_players = top 5 players sorted by points

"""

df = pd.read_excel('nhlstats.xlsx')
df = df.sort_values('Pts', ascending=False)

#For the prupose of this analysis, we will not consider free agents. Since they are not on a team, they skew the statistics. They will be removed.
df = df[~df.Team.str.contains("FA")]

teams = df.groupby('Team').sum()
teams['PPG'] = teams.Pts / teams.Games
teams = teams.sort_values('PPG', ascending=False)
teams = teams.round({'PPG': 2})
teams.reset_index(inplace=True)
top_5_teams = teams[0:5]
top_5_players = df[0:5]
PIM_chart = teams.sort_values('PIM', ascending=False)
teams['shg%']= teams.SHG / teams.G
df['shg%']= df.SHG/ df.G
teams['ppg%']= teams.PPG / teams.G
df['ppg%']= df.PPG  / teams.G
teams = teams.round({'PPG': 2, 'ppg%':2, 'shg%':2})
df = df.round({'PPG': 2, 'ppg%':2, 'shg%':2})

"""
Dash
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# pandas dataframe to html table
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


app = dash.Dash(__name__, external_stylesheets=stylesheet)

fig = px.bar(top_5_teams, x='Team', y='Pts', color='Team', title='Top 5 NHL Teams by Points')
fig1= px.bar(top_5_players, x='Player Name', y='Pts', color='Team', title='Top 5 Players in the NHL by Total Points')
all_players = px.scatter(df, x='Player Name',y='Pts', color='Team', title='NHL Players and Their Points')
all_teams = px.scatter(teams, x='G', y='A', color='Team', title ='NHL Teams: Goals v. Assists')
penalty_mins=px.bar(PIM_chart, x='Team', y='PIM', color='Team',title='Which NHL team spends the most time in the box?')

team_labels = [{'label' : team, 'value' : team} for team in teams.Team]

app.layout = html.Div([
    html.H1('Welcome to the NHL Fan Zone Dashboard!'),
    html.H2('Where fans come to look at statistics about their favorite players and teams.'),
    html.H3('This is an interactive site for you to see statistics about your favorite players and teams!'),
    html.A('Click here to see the data source for the statistics', href='https://www.rotowire.com/hockey/stats.php', 
           target='_blank'),
    generate_table(teams[teams.Team.isin(['CHI', 'OTT'])]),
    dcc.Graph(figure=fig),
    dcc.Graph(figure=fig1),
    dcc.Graph(figure=all_teams),
    dcc.Graph(id='player_points', figure=all_players),
    dcc.Slider(min=0, max=75, step=5, value=50, id='point_slider', tooltip = { 'always_visible': True }),
    dcc.Graph(id='PIM', figure=penalty_mins),
    dcc.Checklist(id='PIMlist',
        options=team_labels, 
        value = ['BOS','MON'], 
        labelStyle={'display': 'inline-block'})
])     

#slider callback
@app.callback(
    Output('player_points','figure'),
    Input('point_slider', 'value'))    

def update_graph(selected_points):
    filtered_df = df[df.Pts >= selected_points]
    
    fig = px.bar(filtered_df, x='Player Name', y='Pts', color='Team', title='Who has the most points? Adjust the slider to see!')
    
    fig.update_layout(transition_duration=500)
    
    return fig

#PIM callback
@app.callback(
    Output('PIM','figure'),
    Input('PIMlist', 'value'))  

def update_graph(PIM_team):
    PIM_df = teams[teams.Team.isin(PIM_team)]
    
    fig1 = px.bar(PIM_df, x='Team', y='PIM', color='Team', title='Penalty minutes')
    
    fig1.update_layout(transition_duration=500)
    
    return fig1
    

#table callback
@app.callback(
    Output(component_id='table_div', component_property='children'),
    [Input(component_id='PIMlist', component_property='value')]
)

def update_table(team_list):
    df2 = teams[teams.Team.isin(team_list)]
    return(generate_table(df2))
    
    
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:




