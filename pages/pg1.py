import dash  # version 1.13.1
from dash import dcc, html
from dash.dependencies import Input, Output, ALL, State, MATCH, ALLSMALLER
import dash_bootstrap_components as dbc
import plotly
import plotly.express as px
import pandas as pd
import numpy as np

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB]) #use_pages=True, 

'''
sidebar = dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True,
            className="bg-light",
)
'''
dash.register_page(__name__,
                   path='/',  # '/' is home page and it represents the url
                   name='Home',  # name of page, commonly used as name of link
                   title='Index',  # title that appears on browser's tab
                   image='pg1.png',  # image in the assets folder
                #    description='Histograms are the new bar charts.'
)

df = pd.read_csv("caspar_envcan.csv", low_memory=False)
df.rename(columns={'predictionTime': 'date', 'source': 'source', 'temp': 'temp',
                    'windDir': 'wind direction', 'windSpeed': 'wind speed', 
                    'pressure': 'pressure', 'relHumidity': 'relative humidity', 
                    'humidity': 'humidity'}, inplace=True)
#update pd 
#df['predictionTime'] = pd.to_datetime(df['predictionTime'])

#all values >50 in temp column, are set = 50
# for x in df.index:
#     if df.loc[x, "temp"] > 50:
#         df.loc[x, "temp"] = 50

#removes all rows with cells empty or NaN
# df.dropna(inplace = True)

# print(df.to_string())


#Header_component = html.H1("Environment Dashboard") #, style={'color':'darkred'}



layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Environment Dashboard", 
                        className='text-danger text-center, mb-4'),
                width=10),
        #dbc.Col()
    ),

    dbc.Row([
        
        dbc.Col(html.Div([html.Button('Add Chart', 
            id='add-chart', n_clicks=0)],))
        ]),
        
        
    dbc.Row([    
        html.Div(id='container', children=[]),
    ]), 

        #To-do
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
        style={'width': '85%', 'display': 'inline-block', 'outline': 'thin lightgrey solid', 'padding': 10},
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
                options=[{'label': 'Line Chart', 'value': 'line'},
                         {'label': 'Histogram', 'value': 'histogram'},
                         {'label': 'Pie Chart', 'value': 'pie'}],
                value='line',
            ),
            dcc.Dropdown(
                id={
                    'type': 'dynamic-dpn-s',
                    'index': n_clicks
                },
                options=[{'label': s, 'value': s} for s in np.sort(df['source'].unique())],
                multi=True,
                value=["caspar", "envcan"],
            ),
            dcc.Dropdown(
                id={
                    'type': 'dynamic-dpn-temp',
                    'index': n_clicks
                },
                options=[{'label': c, 'value': c} for c in ['relative humidity', 'humidity', 'wind direction', 'wind speed', 'pressure', 'source', 'temp']],
                value='source',
                clearable=True
            ),

            dcc.Dropdown(
                id={
                    'type': 'dynamic-dpn-win',
                    'index': n_clicks
                },
                options=[{'label': n, 'value': n} for n in ['relative humidity', 'humidity', 'wind direction', 'wind speed', 'pressure', 'source', 'temp']],
                value='temp',
                clearable=True
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
    dff = df[df['source'].isin(s_value)]

    if chart_choice == 'line':
        dff = dff.groupby([ctg_value, 'date'], as_index=False)[['relative humidity', 'humidity', 'wind direction', 'wind speed', 'temp', 'pressure']].mean()
        fig = px.line(dff, x='date', y=num_value, color=ctg_value)
        return fig
    elif chart_choice == 'bar':
        if len(s_value) == 0:
            return {}
        
        else:
            dff = dff.groupby([ctg_value], as_index=False)[['relative humidity', 'humidity', 'wind direction', 'wind speed', 'pressure', 'source', 'temp']].mean()
            fig = px.histogram(dff, x='date', y=num_value, histfunc='avg')
            return fig

    elif chart_choice == 'pie':
        fig = px.pie(dff, names=ctg_value, values=num_value)
        return fig

#To-do open---------------------------------------------------->>>>>>>>>
#To-do
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
## To-do close <<<<<<<<<<<<--------------------------------------


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


# if __name__ == '__main__':
#     app.run_server(debug=True)

    
    
# https://youtu.be/4gDwKYaA6ww