import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import plotly.graph_objs as go

# https://htmlcheatsheet.com/css/

#####################################################Data##############################################################

data = pd.read_excel("DataF.xlsx")

energy_types = ['Total Renewable', 'Total Not Renewable']

sectors = ['Biofuels Production - TWh - Total', 'Electricity from hydro (TWh)', 'Electricity from solar (TWh)', 'Electricity from wind (TWh)', "Coal Consumption - TWh", "Oil Consumption - TWh", "Gas Consumption - TWh", "Nuclear Consumption - TWh"]

######################################################Interactive Components############################################

country_options = [dict(label=country, value=country) for country in data['Entity'].unique()]

energy_options = [dict(label=energy.replace('_', ' '), value=energy) for energy in energy_types]

sector_options = [dict(label=sector.replace('_', ' '), value=sector) for sector in sectors]


dropdown_country = dcc.Dropdown(
        id='country_drop',
        options=country_options,
        value=['Portugal'],
        multi=True
    )

dropdown_energy_types = dcc.Dropdown(
        id='energy_options',
        options=energy_options,
        value='Total Renewable',
    )

dropdown_sector = dcc.Dropdown(
        id='sector_option',
        options=sector_options,
        value=['Biofuels Production - TWh - Total', 'Coal Consumption - TWh'],
        multi=True
    )

slider_year = dcc.Slider(
        id='year_slider',
        min=data['Year'].min(),
        max=data['Year'].max(),
        marks={str(i): '{}'.format(str(i)) for i in
               [1965, 1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020]},
        value=data['Year'].min(),
        step=1
    )

radio_lin_log = dcc.RadioItems(
        id='lin_log',
        options=[dict(label='Linear', value=0), dict(label='log', value=1)],
        value=0
    )

radio_projection = dcc.RadioItems(
        id='projection',
        options=[dict(label='Equirectangular', value=0),
                 dict(label='Orthographic', value=1)],
        value=0
    )


##################################################APP###################################################################

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([

    html.Div([
        html.H1("Energy production Dashboard"),
    ], id='1st row', className='pretty_box'),
    html.Div([
        html.Div([
            html.Label('Country Choice'),
            dropdown_country,
            html.Br(),
            html.Label('Energy Choice'),
            dropdown_energy_types,
            html.Br(),
            html.Label('Sector Choice'),
            dropdown_sector,
            html.Br(),
            html.Label('Year Slider'),
            slider_year,
            html.Br(),
            html.Label('Linear Log'),
            radio_lin_log,
            html.Br(),
            html.Label('Projection'),
            radio_projection,
            html.Br(),
        ], id='Iteraction', style={'width': '30%'}, className='pretty_box'),
        html.Div([
            html.Div([
                html.Label(id='energy_1', className='box_emissions'),
                html.Br(),
                html.Label(id='energy_2', className='box_emissions'),
                html.Br(),
                html.Label(id='energy_3', className='box_emissions'),
                html.Br(),
                html.Label(id='energy_4', className='box_emissions'),
                html.Br(),
                html.Label(id='energy_5', className='box_emissions'),
                html.Br(),
                html.Label(id='energy_6', className='box_emissions'),
                html.Br(),
                html.Label(id='energy_7', className='box_emissions'),
                html.Br(),
                html.Label(id='energy_8', className='box_emissions'),
                html.Br(),
            ], id='Label', style={'display': 'flex'}),
            html.Div([
                dcc.Graph(id='choropleth'),
            ], id='Map', className='pretty_box')
        ], id='Else', style={'width': '70%'})
    ], id='2nd row', style={'display': 'flex'}),
    html.Div([
        html.Div([
            dcc.Graph(id='bar_graph'),
        ], id='Graph1', style={'width': '50%'}, className='pretty_box'),
        html.Div([
            dcc.Graph(id='aggregate_graph')
        ], id='Graph2', style={'width': '70%'}, className='pretty_box')
    ], id='3th row', style={'display': 'flex'}),

        html.Div([
            html.Div([
                html.Div([
                    html.P(['GroupPN', html.Br(),'Mafalda Garcia (20210763), Rui Ribeiro (20211017), Simão Pereira (20210250), Tiago Santos (20210548)'], style={'font-size':'20px'}),
                    ], style={'width':'60%'}),
                html.Div([
                    html.P(['Sources ', html.Br(), html.A('Our World in Data', href='https://ourworldindata.org/', target='_blank')], style={'font-size':'20px'})
                    ], style={'width':'37%'}),
                ], className = 'footer', style={'display':'flex'}),
            ], className='main'),
        ])


######################################################Callbacks#########################################################


@app.callback(
    [
        Output("bar_graph", "figure"),
        Output("choropleth", "figure"),
        Output("aggregate_graph", "figure"),
    ],
    [
        Input("year_slider", "value"),
        Input("country_drop", "value"),
        Input("energy_options", "value"),
        Input("lin_log", "value"),
        Input("projection", "value"),
        Input('sector_option', 'value')
    ]
)



############################################First Bar Plot##########################################################

def plots(year, countries, energy, scale, projection, sector):
    data_bar = []
    for country in countries:
        df_bar = data.loc[(data['Entity'] == country)]

        x_bar = df_bar['Year']
        y_bar = df_bar[energy]

        data_bar.append(dict(type='bar', x=x_bar, y=y_bar, name=country))

    layout_bar = dict(title=dict(text=str(
                                            energy) + " energy production from 1965 until 2020"),
                      yaxis=dict(title='Energy production', type=['linear', 'log'][scale]),
                      paper_bgcolor='rgba(0,0,0,0)',
                      font_color="white"
                      )

    #############################################Second Choropleth######################################################

    df_emission_0 = data.loc[data['Year'] == year]

    z = np.log(df_emission_0[energy])

    data_choropleth = dict(type='choropleth',
                           locations=df_emission_0['Entity'],
                           # There are three ways to 'merge' your data with the data pre embedded in the map
                           locationmode='country names',
                           z=z,
                           text=df_emission_0['Entity'],
                           colorscale='mint',
                           colorbar=dict(title=str(energy.replace('_', ' ')) + ' (log scaled)'),

                           hovertemplate='Country: %{text} <br>' + str(energy.replace('_', ' ')) + ': %{z}',
                           name=''
                           )

    layout_choropleth = dict(geo=dict(scope='world',  # default
                                      projection=dict(type=['equirectangular', 'orthographic'][projection]
                                                      ),
                                      # showland=True,   # default = True
                                      landcolor='white',
                                      lakecolor='white',
                                      showocean=True,  # default = False
                                      oceancolor='azure',
                                      bgcolor='#f9f9f9'
                                      ),

                             title=dict(
                                 text='World ' + str(energy.replace('_', ' ')) + ' Choropleth Map on the year ' + str(
                                     year),
                                 x=.5,
                                 font_color ="white",# Title relative position according to the xaxis, range (0,1)


                             ),
                             paper_bgcolor='rgba(0,0,0,0)'
                             )


    ############################################Third Scatter Plot######################################################

    df_loc = data.loc[data['Entity'].isin(countries)].groupby('Year').sum().reset_index()

    data_agg = []

    for place in sector:
        data_agg.append(dict(type='scatter',
                             x=df_loc['Year'].unique(),
                             y=df_loc[place],
                             name=place.replace('_', ' '),
                             mode='markers'
                             )
                        )

    layout_agg = dict(title=dict(text='Aggregate energy production by Sector'),
                      yaxis=dict(title=['Total energy', 'Total energy(log scaled)'][scale],
                                 type=['linear', 'log'][scale]),
                      xaxis=dict(title='Year'),
                      paper_bgcolor='rgba(0,0,0,0)',
                      font_color="white",
                      )

    return go.Figure(data=data_bar, layout=layout_bar), \
           go.Figure(data=data_choropleth, layout=layout_choropleth), \
           go.Figure(data=data_agg, layout=layout_agg)


@app.callback(
    [
        Output("energy_1", "children"),
        Output("energy_2", "children"),
        Output("energy_3", "children"),
        Output("energy_4", "children"),
        Output("energy_5", "children"),
        Output("energy_6", "children"),
        Output("energy_7", "children"),
        Output("energy_8", "children")
    ],
    [
        Input("country_drop", "value"),
        Input("year_slider", "value"),
    ]
)
def indicator(countries, year):
    df_loc = data.loc[data['Entity'].isin(countries)].groupby('Year').sum().reset_index()

    value_1 = round(df_loc.loc[df_loc['Year'] == year][sectors[0]].values[0], 2)
    value_2 = round(df_loc.loc[df_loc["Year"] == year][sectors[1]].values[0], 2)
    value_3 = round(df_loc.loc[df_loc['Year'] == year][sectors[2]].values[0], 2)
    value_4 = round(df_loc.loc[df_loc['Year'] == year][sectors[3]].values[0], 2)
    value_5 = round(df_loc.loc[df_loc['Year'] == year][sectors[4]].values[0], 2)
    value_6 = round(df_loc.loc[df_loc['Year'] == year][sectors[5]].values[0], 2)
    value_7 = round(df_loc.loc[df_loc['Year'] == year][sectors[6]].values[0], 2)
    value_8 = round(df_loc.loc[df_loc['Year'] == year][sectors[7]].values[0], 2)

    return str(sectors[0]).replace('_', ' ') + ': ' + str(value_1), \
           str(sectors[1]).replace('_', ' ') + ': ' + str(value_2), \
           str(sectors[2]).replace('_', ' ') + ': ' + str(value_3), \
           str(sectors[3]).replace('_', ' ') + ': ' + str(value_4), \
           str(sectors[4]).replace('_', ' ') + ': ' + str(value_5), \
           str(sectors[5]).replace('_', ' ') + ': ' + str(value_6), \
           str(sectors[6]).replace('_', ' ') + ': ' + str(value_7), \
           str(sectors[7]).replace('_', ' ') + ': ' + str(value_8),



if __name__ == '__main__':
    app.run_server(debug=True)
