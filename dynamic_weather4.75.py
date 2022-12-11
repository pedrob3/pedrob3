from curses import COLOR_GREEN
import dash  
from dash import dcc, html 
from dash.dependencies import Input, Output, ALL, State, MATCH, ALLSMALLER
import dash_bootstrap_components as dbc
import plotly
import plotly.express as px
import pandas as pd
import numpy as np
import requests


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG]) #use_pages=True, 


df = pd.read_csv("caspar_envcan.csv", low_memory=False)
# df = pd.read_csv('http://127.0.0.1:8000/api/v1/forecasts/find?sources=envcan&startDate=2020-03-29T20%3A07%3A46.473340%2B00%3A00&endDate=2022-09-01T02%3A07%3A46.473434%2B00%3A00&predictionDate=2020-03-29T20%3A07%3A46.473470%2B00%3A00&format=csv')

df.rename(columns={'predictionTime': 'Date', 'source': 'Source', 'temp': 'Temperature',
                    'windDir': 'Wind direction', 'windSpeed': 'Wind speed', 
                    'pressure': 'Pressure', 'relHumidity': 'Relative humidity', 
                    'humidity': 'Humidity'}, inplace=True)

#df['predictionTime'] = pd.to_datetime(df['predictionTime'])

#all values >50 in temp column, are set = 50
for x in df.index:
    if df.loc[x, "Temperature"] > 50:
        df.loc[x, "Temperature"] = 50


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Environment Dashboard", 
                        className='text-info d-flex justify-content-right display-2 mb-3'),
                xs=3, sm=3, md=6, lg=8, xl=8, xxl=8),
    
        dbc.Col(html.Img(src="/assets/MDS.png",
                        className="d-flex justify-content-end w-100"),
                xs=2, sm=2, md=2, lg=3, xl=4, xxl=4),
        ]

    ),

    dbc.Row([
        
        dbc.Col(html.Div([html.Button('Add Chart', 
            id='add-chart', n_clicks=0)],))
        ]),
        
        
    dbc.Row([    
        html.Div(id='container', 
                className= "shadow p-3 mb-2 bg-light rounded",
                children=[]),
    ]), 

#To-do list
        html.Div('Weather Dash To-Do list'),
        dcc.Input(id="new-item"),
        html.Button("Add", id="add"),
        html.Button("Clear Done", id="clear-done"),
        html.Div(id="list-container"),
        html.Div(id="totals")
        
], fluid=False)



@app.callback(
    Output('container', 'children'),
    [Input('add-chart', 'n_clicks')],
    [State('container', 'children')]
)
def display_graphs(n_clicks, div_children):
    new_child = html.Div(
        style={'width': '98%', 'display': 'inline-block', 'outline': 'thin lightgrey solid', 'padding': 8},
        children=[
            dcc.Graph(
                id={
                    'type': 'dynamic-graph',
                    'index': n_clicks
                },
                figure={}
            ),
            dcc.RadioItems(
                id={
                    'type': 'dynamic-choice',
                    'index': n_clicks
                },
                options=[{'label': 'Line Chart', 'value': 'line'}],
                        #removed this graphics from radio items
                        #  {'label': 'Histogram', 'value': 'histogram'},
                        #  {'label': 'Pie Chart', 'value': 'pie'}],
                value='line',
            ),
            dcc.Dropdown(
                id={
                    'type': 'dynamic-dpn-s',
                    'index': n_clicks
                },
                options=[{'label': s, 'value': s} for s in np.sort(df['Source'].unique())],
                multi=True,
                className="bg-dark w-50 p-3",
                value=["caspar", "envcan"],
            ),
            dcc.Dropdown(
                id={
                    'type': 'dynamic-dpn-temp',
                    'index': n_clicks
                },
                options=[{'label': c, 'value': c} for c in ['Relative humidity', 'Humidity', 'Wind direction', 'Wind speed', 'Pressure', 'Source', 'Temperature']],
                className="bg-dark w-50 p-3",
                value='Source',
                clearable=True
            ),

            dcc.Dropdown(
                id={
                    'type': 'dynamic-dpn-win',
                    'index': n_clicks
                },
                options=[{'label': n, 'value': n} for n in ['Relative humidity', 'Humidity', 'Wind direction', 'Wind speed', 'Pressure', 'Source', 'Temperature']],
                className="bg-dark w-50 p-3",
                value='Temperature',
                clearable=True,
                style={'color': 'black'}
            )
        ]
    )
    div_children.append(new_child)
    return div_children


@app.callback(
    Output({'type': 'dynamic-graph', 'index': MATCH}, 'figure'),
    [Input(component_id={'type': 'dynamic-dpn-s', 'index': MATCH}, component_property='value'),
     Input(component_id={'type': 'dynamic-dpn-temp', 'index': MATCH}, component_property='value'),
     Input(component_id={'type': 'dynamic-dpn-win', 'index': MATCH}, component_property='value'),
     Input({'type': 'dynamic-choice', 'index': MATCH}, 'value')]
)
def update_graph(s_value, ctg_value, num_value, chart_choice):
    print(s_value)
    dff = df[df['Source'].isin(s_value)]

    if chart_choice == 'line':
        dff = dff.groupby([ctg_value, 'Date'], as_index=False)[['Relative humidity', 'Humidity', 'Wind direction', 'Wind speed', 'Pressure', 'Source', 'Temperature']].mean()
        fig = px.line(dff, x='Date', y=num_value, color=ctg_value)
        return fig
    elif chart_choice == 'bar':
        if len(s_value) == 0:
            return {}
        
        else:
            dff = dff.groupby([ctg_value], as_index=False)[['Relative humidity', 'Humidity', 'Wind direction', 'Wind speed', 'Pressure', 'Source', 'Temperature']].mean()
            fig = px.histogram(dff, x='Date', y=num_value, histfunc='avg')
            return fig

    elif chart_choice == 'pie':
        fig = px.pie(dff, names=ctg_value, values=num_value)
        return fig

#To-do open---------------------------------------------------->>>>>>>>>

style_todo = {"display": "inline", "margin": "10px"}
style_done = {"textDecoration": "line-through", "color": "#888"}
style_done.update(style_todo)


@app.callback(
    [
        Output("list-container", "children"),
        Output("new-item", "value")
    ],
    [
        Input("add", "n_clicks"),
        Input("new-item", "n_submit"),
        Input("clear-done", "n_clicks")
    ],
    [
        State("new-item", "value"),
        State({"index": ALL}, "children"),
        State({"index": ALL, "type": "done"}, "value")
    ]
)
def edit_list(add, add2, clear, new_item, items, items_done):
    triggered = [t["prop_id"] for t in dash.callback_context.triggered]
    adding = len([1 for i in triggered if i in ("add.n_clicks", "new-item.n_submit")])
    clearing = len([1 for i in triggered if i == "clear-done.n_clicks"])
    new_spec = [
        (text, done) for text, done in zip(items, items_done)
        if not (clearing and done)
    ]
    if adding:
        new_spec.append((new_item, []))
    new_list = [
        html.Div([
            dcc.Checklist(
                id={"index": i, "type": "done"},
                options=[{"label": "", "value": "done"}],
                value=done,
                style={"display": "inline"},
                labelStyle={"display": "inline"}
            ),
            html.Div(text, id={"index": i}, style=style_done if done else style_todo)
        ], style={"clear": "both"})
        for i, (text, done) in enumerate(new_spec)
    ]
    return [new_list, "" if adding else new_item]


@app.callback(
    Output({"index": MATCH}, "style"),
    Input({"index": MATCH, "type": "done"}, "value")
)
def mark_done(done):
    return style_done if done else style_todo


@app.callback(
    Output("totals", "children"),
    Input({"index": ALL, "type": "done"}, "value")
)
def show_totals(done):
    count_all = len(done)
    count_done = len([d for d in done if d])
    result = "{} of {} items completed".format(count_done, count_all)
    if count_all:
        result += " - {}%".format(int(100 * count_done / count_all))
    return result
# To-do close <<<<<<<<<<<<--------------------------------------

    # bar graph option 
    # if chart_choice == 'bar':
    #     dff = dff.groupby([ctg_value], as_index=False)[['detenues', 'under trial', 'convicts', 'others']].sum()
    #     fig = px.bar(dff, x=ctg_value, y=num_value)
    #     return fig
    # elif chart_choice == 'line':
    #     if len(s_value) == 0:
    #         return {}
    #     else:
    #         dff = dff.groupby([ctg_value, 'year'], as_index=False)[['detenues', 'under trial', 'convicts', 'others']].sum()
    #         fig = px.line(dff, x='year', y=num_value, color=ctg_value)
    #         return fig
    # elif chart_choice == 'pie':
    #     fig = px.pie(dff, names=ctg_value, values=num_value)
    #     return fig


if __name__ == '__main__':
    app.run_server(debug=True)
