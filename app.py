import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import json
from collections import Counter

app = dash.Dash('')
app.title = 'Community Dashboard'
colors={'background': '#111111','text': '#7FDBFF','text2':'#FFFFFF','red':'#FF0000'}  #


pro_list = []
city_list = []
city_infos = []

f = open("data_csv/city_scale.txt","r", encoding='UTF-8')
lines = f.readlines()
for line in lines:
    city_infos.append(line)
    a = line.split(",")
    city_list.append(a[1])
    pro_list.append(a[2])

pro_list = sorted(set(pro_list))

styles = ['dark','light',"streets","satellite"]


TOPBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 8,
    'right':8,
    'height': '13%',
    'background-color': '#111111'
}

SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 100,
    'left': 8,
    'bottom': 8,
    'width': '18%',
    'padding': '20px 10px',
    'background-color': '#111111'
}

CONTAINER_STYLE = {
    'position': 'fixed',
    'bottom': 8,
    'right':8,
    'width': '18%',
    'height': '12%',
    'padding': '20px 10px',
    'background-color': '#111111'
}


TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#7FDBFF'

}

CONTENT_STYLE = {
    'margin-top': '6%',
    'margin-left': '5%',
    'margin-right': '50%',
    'background-color': '#111111'
}


title = html.Div(
    [
        html.H1(children='Community Dashboard', style={
            'textAlign': 'center',
            'color': colors['text'],
        }),
        html.Div(children='''Mapping the Contruction Year of Chinese Communities 🏡.''',
                 style={'textAlign': 'center', 'color': colors['text']}),
        html.Hr(),
    ],
    style = TOPBAR_STYLE,
)


sidebar = html.Div(
    [
        html.H2('Parameters', style=TEXT_STYLE),

        html.Label('*', style={'color': colors['red']}),
        html.Label('Province:', style={'color': colors['text2']}),
        dcc.Dropdown(
            id='province',
            options=[{'label': i, 'value': i} for i in pro_list],
            value='北京市 (Beijing)',  
            placeholder = 'Select the province...',
            style={'width': '90%'},
            clearable=False,
        ),
        html.Br(),

        html.Label('*', style={'color': colors['red']}),
        html.Label('City:', style={'color': colors['text2']}),
        dcc.Dropdown(
            id='city',
            options=[{'label': i, 'value': i} for i in city_list],
            value='北京市 (Beijing)',  
            style={'width': '90%'},
            placeholder = 'Select the city...',
            clearable=False,
        ),
        html.Br(),

        html.Label('Map Styles:', style={'color': colors['text2']}),
        dcc.Dropdown(
            id='style',
            options=[{'label': i, 'value': i} for i in styles],
            value='dark', 
            style={'width': '90%'}
        ),

        html.Br(),
        html.Label('Opacity:', style={'color': colors['text2']}),
        html.Div([
            dcc.Slider(
                id='opacity',
                min=0,
                max=1,
                step=0.1,
                value=0.9,
                marks={0: '0', 0.5: '0.5', 1: '1'}),
        ], style={'width': '90%'}),

        html.Br(),
        html.Div([
            dcc.Markdown(children='''
            #### Instructions
            ''', style={'color': colors['text2']}),
            dcc.Markdown(
                children='''
            \* Please select a city from the Dropdown box.\n
            \* Map styles and opacity are adjustable for different visual effect.\n
            \* The mapbox shows the community of the selected city.\n
            \* The histogram counts the number of newly-built communities per year.
            ''', style={'color': colors['text2']}),
        ]),


        html.Br(),
        html.Br(),


        html.Div([
            dcc.Markdown(children='''
            ### More Info
            ''', style={'color': colors['text']}),


        html.Label('😊 Codes avalible at ', style={'color': colors['text2']}),

        html.A(
            href='https://github.com/liumency/community-dashboard',
            children=[
                html.Span("github!")
            ]),

        ]),

    ],
    style=SIDEBAR_STYLE,
)


content =  html.Div(
    [
        dcc.Graph(
            id = 'fig',
            ),
        html.Label(' Code', style={'color': colors['text']}),
        dcc.Graph(
            id='table'),
    ], style= CONTENT_STYLE)

container =  html.Div(
    [
        html.H3(id = 'cityname', style={'color': colors['text2']}),
        html.H4(id = 'totalnum', style={'color': colors['text2']}),
    ],style= CONTAINER_STYLE)


app.layout = html.Div( style = dict(backgroundColor = colors['background']),
    children=[
        content,
        sidebar,
        title,
        container
]
)


@app.callback(
    Output('city', component_property='options'),
    [Input('province', 'value'),
     ]
)
def get_city(province):
    new_list = []
    for city_info in city_infos:
        if province in city_info:
            city_info = city_info.split(",")
            new_list.append(city_info[1])

    return [{'label': i, 'value': i} for i in new_list]


@app.callback(
    Output('fig', component_property='figure'),
    [
     Input('city', 'value'),
     Input('style','value'),
     Input('opacity', 'value'),
     ]
)
def get_figure(city,style,opacity):

    city_num = city_list.index(city)
    with open('data_json/'+str(city_num)+'.json') as f:
        jsonfile = json.load(f)
    df = pd.read_table('data_csv/'+str(city_num)+'.txt',  encoding='utf-8', sep=',')

    max_value = df['year'].max()
    min_value = df['year'].min()
    cen_lon = (df['lon'].max() + df['lon'].min()) / 2
    cen_lat = (df['lat'].max() + df['lat'].min()) / 2

    fig = px.choropleth_mapbox(df, geojson=jsonfile, featureidkey="properties.name", locations='name', color='year',
                               color_continuous_scale="Plasma",  # Plasma
                               range_color=(min_value, max_value),
                               zoom=9,
                               center={"lat": cen_lat, "lon": cen_lon},
                               opacity=opacity,
                               width = 1600,
                               height = 600,
                               )

    fig.update_layout(
        mapbox={'accesstoken': "put your accesstoken here",   #please put your accesstoken here
                'style': style},
        margin={'l':308, "r": 200, 't': 0, 'b': 0},
        plot_bgcolor=colors['background'],
        paper_bgcolor = colors['background'],
        font = dict(color=colors['text'])
    )
    return fig


@app.callback(
    Output('table', component_property='figure'),
    Output('cityname', component_property='children'),
    Output('totalnum', component_property='children'),

    Input('city', 'value'),
)
def get_table(city):
    city_num = city_list.index(city)
    df = pd.read_table('data_csv/'+str(city_num)+'.txt',  encoding='utf-8', sep=',')


    a = df['year'].value_counts()
    table = dict(
                data = [{'x': a.index, 'y': a.values, 'type': 'bar', 'name':'Newly-built communities'}],
                layout = dict(
                    plot_bgcolor = colors['background'],
                    paper_bgcolor = colors['background'],
                    font = dict(color = colors['text']),
                    margin = {'l': 380, "r": 0, 't': 5, 'b': 20},
                    width = 1400,
                    height = 226,
                ))

    label1 = '📍 City: '+city
    label2 = '🏠 Total: {}'.format(a.values.sum())

    return table, label1, label2

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)