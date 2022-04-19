## Dashboard Creation

### Import necessary packages
import dash
from waitress import serve 
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import statsmodels.api as sm


### Define the app and set the style guide
#### stylesheet pulls from Dash Bootstrap Components LUX theme
external_stylesheets = [dbc.themes.LUX]

#### Define the app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, assets_external_path='assets')

### App Features
#### Create a data upload button
upload = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'textAlign': 'center',
            'margin' : '10px'
        },
        # Prevent multiple files from being uploaded
        multiple=False
    )
])

#### Store the data locally
store_data = dcc.Store(id='input-dataset', storage_type='local')


#### Create a form to calculate new risk scores 
age_input = html.Div([
    dbc.Input(id='age-state', type='number')
])

gender_input = html.Div([
    dbc.RadioItems(
        options=[
            {'label':'Male', 'value':'M'},
            {'label':'Female', 'value':'F'}
        ],
        value='M',
        id='gender-state',
    )
])

vitals_input = html.Div([
    dbc.Input(placeholder='Input weight (kg)', id='weight-state', type='number'),
    dbc.Input(placeholder='Input height (cm)', id='height-state', type='number'),
    dbc.Input(placeholder='Input ejection fraction (percent)',id='ef-state', type='number'),
    dbc.Input(placeholder='Input eGFR',id='eGFR-state', type='number'),
    dbc.Checklist(
        options=[{'label':'Emergency', 'value':1}],
        id='emergency-state',
        switch=True
    )
])

conditions_input = html.Div([
    dbc.Label("Select all that apply", html_for="vitals-list"),
    dbc.Checklist(
        options=[
            {"label": "COPD", "value": 'copd'},
            {"label": "Hypertension", "value": 'hbp'},
            {"label": "Diabetes Mellitus", "value": 'dm'},
            {"label": "Congestive Heart Failure", "value": 'chf'},
            {"label": "Left Ventricular Dysfunction", "value": 'lvd'},
            {"label": "History of Stroke", "value": 'stroke'},
            {"label": "Peripheral Vascular Disease", "value": 'pvd'},
            {"label": "Vascular Disease", "value": 'vd'},
            {"label": "Left Atrial Dilation", "value": 'lad'},
            {"label": "Mild Mitral Valve Disease", "value": 'mmvd'},
            {"label": "Mod-to-Severe Mitral Valve Disease", "value": 'smvd'},
            {"label": "Myocardial Infarction", "value":'mi'}
        ],
        id="conditions-state",
        label_checked_style={"color": "success"}
    ),
])

procedures_input = html.Div([
    dbc.Label("Select all that apply", html_for="conditions-list"),
    dbc.Checklist(
        options=[
            {"label": "Intra-aortic Balloon Pump", "value": 'iabp'},
            {"label": "Combined Valve/Artery Surgery", "value": 'cvas'},
            {"label": "Dialysis", "value": 'dialysis'},
        ],
        id="procedures-state",
        label_checked_style={"color": "success"}
    ),
])

accordion = html.Div(
    dbc.Accordion(
        [
            dbc.AccordionItem(
                [age_input],
                title="Age",
                item_id="item-1",
            ),
            dbc.AccordionItem(
                [gender_input],
                title="Gender",
                item_id="item-2",
            ),
            dbc.AccordionItem(
                [vitals_input],
                title="Vitals",
                item_id="item-3",
            ),
            dbc.AccordionItem(
                [conditions_input],
                title="Underlying Conditions",
                item_id="item-4",
            ),
            dbc.AccordionItem(
                [procedures_input],
                title="Procedures",
                item_id="item-5",
            ),
        ],
        active_item="item-4",
    ),
    style={'margin-left' : '10px ', 'margin-top': '10px'}
)

calculate_button = html.Div(
    dbc.Button(
        "Calculate", 
        id="submit-button", 
        className="button", 
        n_clicks=0,
        outline=True,
        color="secondary"
    ),
    style={'margin-left' : '10px ', 'margin-top': '10px', 'margin-bottom': '10px'}
)

#### Store the calculated values locally
afri_state = dcc.Store(id='afri-state', storage_type='local')
chads_state = dcc.Store(id='chads-state', storage_type='local')
poaf_state = dcc.Store(id='poaf-state', storage_type='local')
npoaf_state = dcc.Store(id='npoaf-state', storage_type='local')
simplified_state = dcc.Store(id='simplified-state', storage_type='local')
comaf_state = dcc.Store(id='comaf-state', storage_type='local')

#### Create display cards for the calculated risk scores 
### --> AFRI Card
card1 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='afri-card', className="card-val1"),
            html.P(
                ["Atrial Fibrillation Risk Index"], 
                className="card-text1",
                style={'textAlign': 'center'}
            )
        ]),
    style={
        'margin-right' : '10px', 
        'margin-top': '10px',
    }
)
### --> CHADS Card
card2 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='chads-card', className="card-val2"),
            html.P(
                ["CHA2DS2-VASc Score"], 
                className="card-text2",
                style={'textAlign': 'center'}
            )
        ]),
    style={
        'margin-right' : '10px', 
        'margin-top': '10px',
    }
)
### --> POAF Card
card3 = html.Div([
        dbc.Card(
            dbc.CardBody(
                [
                    html.H4(id='poaf-card', className="card-val3"),
                    html.P(
                        ["Postoperative Atrial Fibrillation Score"], 
                        className="card-text3",
                        style={'textAlign': 'center'}
                    )
                ]),
            style={
                'margin-right' : '10px', 
                'margin-top': '10px',
            },
            id='Poaf-card'
    )
 ])
### --> NPOAF Card
card4 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='npoaf-card', className="card-val4"),
            html.P(
                ["New-onset Postoperative Atrial Fibrillation Score"], 
                className="card-text4",
                style={'textAlign': 'center'}
            )
        ]),
    style={
        'margin-right' : '10px', 
        'margin-top': '10px',
    }
)
### -->  Simplified POAF Card
card5 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='simplified-card', className="card-val5"),
            html.P(
                ["Simplified Postoperative Atrial Fibrillation Score"], 
                className="card-text5",
                style={'textAlign': 'center'}
            )
        ]),
    style={
        'margin-right' : '10px', 
        'margin-top': '10px',
    }
)
### --> COM-AF Card
card6 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='comaf-card', className="card-val6"),
            html.P(
                ["Combined Risk Score to Predict Atrial Fibrillation "], 
                className="card-text6",
                style={'textAlign': 'center'}
            )
        ]),
    style={
        'margin-right' : '10px', 
        'margin-top': '10px',
        'margin-bottom': '10px'
    }
)

#### Create a dropdown menu for the risk score comparison graph
dropdowns = html.Div([
    html.P("x-axis: ", className="crossfilter-xaxis-label", style={'margin-left': '10px'}),
    dcc.Dropdown(
        id='crossfilter-xaxis-column',
        options=[
            {'label': 'AFRI', 'value': 'afri'},
            {'label': 'CHA2DS2-VASc', 'value': 'chads'},
            {'label': 'POAF', 'value': 'poaf'},
            {'label': 'NPOAF', 'value': 'poaf'},
            {'label': 'Simplified', 'value': 'simplified'},
            {'label': 'COM-AF', 'value': 'comaf'}
        ],
        value='afri', 
        style={'margin-left': '5px'}
    ),
    html.P("y-axis: ", className="crossfilter-yaxis-label", style={'margin-left': '10px'}),
    dcc.Dropdown(
        id='crossfilter-yaxis-column',
        options=[
            {'label': 'AFRI', 'value': 'afri'},
            {'label': 'CHA2DS2-VASc', 'value': 'chads'},
            {'label': 'POAF', 'value': 'poaf'},
            {'label': 'NPOAF', 'value': 'npoaf'},
            {'label': 'Simplified', 'value': 'simplified'},
            {'label': 'COM-AF', 'value': 'comaf'}
        ],
        value='npoaf', 
        style={'margin-left': '5px'}
    )
])


#### Create miniature cards to display calculated scores on page 2 
### --> AFRI Minicard
minicard1 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='afri-mini', className="card-val1"),
            html.P(
                ["AFRI"], 
                className="card-text1",
                style={'textAlign': 'center'}
            )
        ])
)

### --> CHADS Minicard
minicard2 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='chads-mini', className="card-val2"),
            html.P(
                ["CHA2DS2-VASc"], 
                className="card-text2",
                style={'textAlign': 'center'}
            )
        ])
)

### --> POAF Minicard
minicard3 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='poaf-mini', className="card-val3"),
            html.P(
                ["POAF"], 
                className="card-text3",
                style={'textAlign': 'center'}
            )
        ])
)

### --> NPOAF Minicard
minicard4 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='npoaf-mini', className="card-val4"),
            html.P(
                ["NPOAF"], 
                className="card-text4",
                style={'textAlign': 'center'}
            )
        ])
)

### --> Simplified Minicard
minicard5 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='simplified-mini', className="card-val5"),
            html.P(
                ["Simplified POAF"], 
                className="card-text5",
                style={'textAlign': 'center'}
            )
        ])
)

### --> COM-AF Minicard
minicard6 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='comaf-mini', className="card-val6"),
            html.P(
                ["COM-AF"], 
                className="card-text6",
                style={'textAlign': 'center'}
            )
        ])
)

minicards = html.Div([
    dbc.Row([
        dbc.Col(minicard1, width=2),
        dbc.Col(minicard2, width=2),
        dbc.Col(minicard3, width=2),
        dbc.Col(minicard4, width=2),
        dbc.Col(minicard5, width=2),
        dbc.Col(minicard6, width=2)
    ])
], style={'margin-top': '10px','margin-left': '10px'})


#### Create a tab for AFRI results 
# --> AFRI results card and tab format
### --> output the results on a card
card_afri = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(id="afri-val", style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the AFRI tab
afri_tab = html.Div([
    html.Div(id="afri-hist", style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_afri
])

#### Create a tab for CHADS results 
# --> CHADS results card and tab format
### --> output the results on a card
### --> output the results on a card
card_chads = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(id="chads-val", style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the CHADS tab
chads_tab = html.Div([
    html.Div(id="chads-hist", style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_chads
])

#### Create a tab for POAF results
# --> POAF results card and tab format
### --> output the results on a card
card_poaf = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(id="poaf-val", style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the POAF tab
poaf_tab = html.Div([
    html.Div(id="poaf-hist", style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_poaf
])

#### Create a tab for NPOAF results
# --> NPOAF results card and tab format
### --> output the results on a card
card_npoaf = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(id="npoaf-val", style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the NPOAF tab
npoaf_tab = html.Div([
    html.Div(id="npoaf-hist", style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_npoaf
])

#### Create a tab for Simplified POAF results
# --> Simplified POAF results card and tab format
### --> output the results on a card
card_simplified = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(id="simplified-val", style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the Simplified tab
simplified_tab = html.Div([
    html.Div(id="simplified-hist", style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_simplified
])

#### Create a tab for COM-AF results
# --> COM-AF results card and tab format
### --> output the results on a card
card_comaf = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(id="comaf-val", style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the COM-AF tab
comaf_tab = html.Div([
    html.Div(id="comaf-hist", style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_comaf
])


### App Layout
#### Define the tabs for the risk scores
score_tab = dbc.Tabs(
            [
                dbc.Tab(afri_tab, label="AFRI", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center", tab_id="afri-tab"),
                dbc.Tab(chads_tab, label="CHADS", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center", tab_id="chads-tab"),
                dbc.Tab(poaf_tab, label="POAF", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center", tab_id="poaf-tab"),
                dbc.Tab(npoaf_tab, label="NPOAF", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center", tab_id="npoaf-tab"),
                dbc.Tab(simplified_tab, label="Simplified POAF", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center", tab_id="simplified-tab"),
                dbc.Tab(comaf_tab, label="COM-AF", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center", tab_id="comaf-tab"),
            ], id="score-tab"
        )


#### Define the layout of the two pages
tab1 = dbc.Row(
            [
                dbc.Col([accordion, calculate_button], width=8),
                dbc.Col([card1, card2, card3, card4, card5, card6], width=4),
            ]
        )
tab2 = dbc.Row(
            [
                dbc.Col([
                    dcc.Graph(id="stripchart", style={'margin-left': '10px'}),
                    dropdowns,
                    minicards
                ], width=6),
                dbc.Col(score_tab, width=6),
            ]
        )

#### Define the app layout
app.layout = html.Div(
    [
        html.H1(children='Atrial Fibrillation Risk Prediction', 
            style={
                'textAlign': 'center',
                'margin': '10px'
            }),
        dbc.Row(
            [
                dbc.Col(upload, width=4),
            ],
            justify="center",
        ),
        dbc.Tabs(
            [
                dbc.Tab(tab1, label="Calculate Patient Scores", active_tab_style={"textTransform": "uppercase"}),
                dbc.Tab(tab2, label="Compare Scores", active_tab_style={"textTransform": "uppercase"}),
            ]
        ),
        store_data,
        afri_state,
        chads_state,
        poaf_state,
        npoaf_state,
        simplified_state,
        comaf_state
    ],
    style={'background-color': '#EEF3F8'}
)


### App Callbacks and Configuration
#### Establish a function for the input dataset
default_data = pd.read_csv('../../Data/risk.csv')

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        return df
    except Exception as e:
        print(e)

#### Establish a callback for AFRI Calculation
@app.callback(
    [
        dash.dependencies.Output('afri-card', 'children'),
        dash.dependencies.Output('afri-card', 'style'),
        dash.dependencies.Output('afri-mini', 'children'),
        dash.dependencies.Output('afri-mini', 'style'),
        dash.dependencies.Output('afri-state', 'data')
    ],
    [
        dash.dependencies.Input('submit-button', 'n_clicks')
    ],
    [
        dash.dependencies.State('age-state', 'value'),
        dash.dependencies.State('gender-state', 'value'),
        dash.dependencies.State('weight-state', 'value'),
        dash.dependencies.State('height-state', 'value'),
        dash.dependencies.State('ef-state', 'value'),
        dash.dependencies.State('eGFR-state', 'value'),
        dash.dependencies.State('emergency-state', 'value'),
        dash.dependencies.State('conditions-state', 'value'),
        dash.dependencies.State('procedures-state', 'value')
    ],
)
def afri_calc(button_click, age_state, gender_state, weight_state, height_state, ef_state, eGFR_state, emergency_state, conditions_state, procedures_state):
    ctx = dash.callback_context
    changed_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ('submit-button' in changed_id):
        afri=0
        if (gender_state=='M'):
            if (age_state > 60):
                afri=afri+1
            if (weight_state > 76):
                afri=afri+1
            if (height_state > 176):
                afri=afri+1
            if ('pvd' in conditions_state):
                afri=afri+1
        elif (gender_state == 'F'):
            if (age_state > 66):
                afri=afri+1
            if (weight_state > 64):
                afri=afri+1
            if (height_state > 169):
                afri=afri+1
            if ('pvd' in conditions_state):
                afri=afri+1              
    else: 
        afri=None
    afri2 = afri
    afri3 = afri
    if afri==None:
        style={'textAlign': 'center', 'color':'slateblue'}
    elif afri>=2:
        style={'textAlign': 'center', 'color':'crimson'}
    else:
        style={'textAlign': 'center', 'color':'slateblue'}
    style2 = style
    return afri, style, afri2, style2, afri3


#### Establish a callback for CHADS Calculation
@app.callback(
    [
        dash.dependencies.Output('chads-card', 'children'),
        dash.dependencies.Output('chads-card', 'style'),
        dash.dependencies.Output('chads-mini', 'children'),
        dash.dependencies.Output('chads-mini', 'style'),
        dash.dependencies.Output('chads-state', 'data')
    ],
    [
        dash.dependencies.Input('submit-button', 'n_clicks')
    ],
    [
        dash.dependencies.State('age-state', 'value'),
        dash.dependencies.State('gender-state', 'value'),
        dash.dependencies.State('weight-state', 'value'),
        dash.dependencies.State('height-state', 'value'),
        dash.dependencies.State('ef-state', 'value'),
        dash.dependencies.State('eGFR-state', 'value'),
        dash.dependencies.State('emergency-state', 'value'),
        dash.dependencies.State('conditions-state', 'value'),
        dash.dependencies.State('procedures-state', 'value')
    ],
)
def chads_calc(button_click, age_state, gender_state, weight_state, height_state, ef_state, eGFR_state, emergency_state, conditions_state, procedures_state):
    ctx = dash.callback_context
    changed_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ('submit-button' in changed_id):
        chads=0
        if ('chf' in conditions_state):
            chads=chads+1
        if ('hbp' in conditions_state):
            chads=chads+1
        if (age_state >= 75):
            chads=chads+2
        if ('dm' in conditions_state):
            chads=chads+1
        if ('stroke' in conditions_state):
            chads=chads+2
        if ('pvd' in conditions_state):
            chads=chads+1
        if (65 <= age_state <= 74):
            chads=chads+1
        if (gender_state == 'F'):
            chads=chads+1
    else: 
        chads=None
    chads2 = chads
    chads3 = chads
    if chads==None:
        style={'textAlign': 'center', 'color':'slateblue'}
    elif chads>=4:
        style={'textAlign': 'center', 'color':'crimson'}
    else:
        style={'textAlign': 'center', 'color':'slateblue'}
    style2 = style
    return chads, style, chads2, style2, chads3


#### Establish a callback for POAF Calculation
@app.callback(
    [
        dash.dependencies.Output('poaf-card', 'children'),
        dash.dependencies.Output('poaf-card', 'style'),
        dash.dependencies.Output('poaf-mini', 'children'),
        dash.dependencies.Output('poaf-mini', 'style'),
        dash.dependencies.Output('poaf-state', 'data')
    ],
    [
        dash.dependencies.Input('submit-button', 'n_clicks')
    ],
    [
        dash.dependencies.State('age-state', 'value'),
        dash.dependencies.State('gender-state', 'value'),
        dash.dependencies.State('weight-state', 'value'),
        dash.dependencies.State('height-state', 'value'),
        dash.dependencies.State('ef-state', 'value'),
        dash.dependencies.State('eGFR-state', 'value'),
        dash.dependencies.State('emergency-state', 'value'),
        dash.dependencies.State('conditions-state', 'value'),
        dash.dependencies.State('procedures-state', 'value')
    ],
)
def poaf_calc(button_click, age_state, gender_state, weight_state, height_state, ef_state, eGFR_state, emergency_state, conditions_state, procedures_state):
    ctx = dash.callback_context
    changed_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ('submit-button' in changed_id):
        poaf=0
        if (60 <= age_state <= 69):
            poaf=poaf+1
        if (760 <= age_state <= 79): 
            poaf=poaf+2
        if (age_state >= 80):
            poaf=poaf+3
        if ('copd' in conditions_state):
            poaf=poaf+1
        if (eGFR_state < 15):
            poaf=poaf+1
        elif ('dialysis' in procedures_state):
            poaf=poaf+1
        if (emergency_state == 1):
            poaf=poaf+1
        if ('iabp' in procedures_state):
            poaf=poaf+1
        if ('cvas' in procedures_state):
            poaf=poaf+1
    else: 
        poaf=None
    poaf2 = poaf
    poaf3 = poaf
    if poaf==None:
        style={'textAlign': 'center', 'color':'slateblue'}
    elif poaf>=3:
        style={'textAlign': 'center', 'color':'crimson'}
    else:
        style={'textAlign': 'center', 'color':'slateblue'}
    style2 = style
    return poaf, style, poaf2, style2, poaf3


#### Establish a callback for NPOAF Calculation
@app.callback(
    [
        dash.dependencies.Output('npoaf-card', 'children'),
        dash.dependencies.Output('npoaf-card', 'style'),
        dash.dependencies.Output('npoaf-mini', 'children'),
        dash.dependencies.Output('npoaf-mini', 'style'),
        dash.dependencies.Output('npoaf-state', 'data')
    ],
    [
        dash.dependencies.Input('submit-button', 'n_clicks')
    ],
    [
        dash.dependencies.State('age-state', 'value'),
        dash.dependencies.State('gender-state', 'value'),
        dash.dependencies.State('weight-state', 'value'),
        dash.dependencies.State('height-state', 'value'),
        dash.dependencies.State('ef-state', 'value'),
        dash.dependencies.State('eGFR-state', 'value'),
        dash.dependencies.State('emergency-state', 'value'),
        dash.dependencies.State('conditions-state', 'value'),
        dash.dependencies.State('procedures-state', 'value')
    ],
)
def npoaf_calc(button_click, age_state, gender_state, weight_state, height_state, ef_state, eGFR_state, emergency_state, conditions_state, procedures_state):
    ctx = dash.callback_context
    changed_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ('submit-button' in changed_id):
        npoaf=0
        if (65 <= age_state <= 74):
            npoaf=npoaf+2
        if (age_state >= 75):
            npoaf=npoaf+3
        if ('mmvd' in conditions_state):
            npoaf=npoaf+1
        if ('smvd' in conditions_state):
            npoaf=npoaf+3
        if ('lad' in conditions_state):
            npoaf=npoaf+1
    else: 
        npoaf=None
    npoaf2 = npoaf
    npoaf3 = npoaf
    if npoaf==None:
        style={'textAlign': 'center', 'color':'slateblue'}
    elif npoaf>=2:
        style={'textAlign': 'center', 'color':'crimson'}
    else:
        style={'textAlign': 'center', 'color':'slateblue'}
    style2 = style
    return npoaf, style, npoaf2, style2, npoaf3


#### Establish a callback for Simplified POAF Calculation
@app.callback(
    [
        dash.dependencies.Output('simplified-card', 'children'),
        dash.dependencies.Output('simplified-card', 'style'),
        dash.dependencies.Output('simplified-mini', 'children'),
        dash.dependencies.Output('simplified-mini', 'style'),
        dash.dependencies.Output('simplified-state', 'data')
    ],
    [
        dash.dependencies.Input('submit-button', 'n_clicks')
    ],
    [
        dash.dependencies.State('age-state', 'value'),
        dash.dependencies.State('gender-state', 'value'),
        dash.dependencies.State('weight-state', 'value'),
        dash.dependencies.State('height-state', 'value'),
        dash.dependencies.State('ef-state', 'value'),
        dash.dependencies.State('eGFR-state', 'value'),
        dash.dependencies.State('emergency-state', 'value'),
        dash.dependencies.State('conditions-state', 'value'),
        dash.dependencies.State('procedures-state', 'value')
    ],
)
def simplified_calc(button_click, age_state, gender_state, weight_state, height_state, ef_state, eGFR_state, emergency_state, conditions_state, procedures_state):
    ctx = dash.callback_context
    changed_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ('submit-button' in changed_id):
        simplified=0
        if (age_state >= 65):
            simplified=simplified+2
        if ('hbp' in conditions_state):
            simplified=simplified+2
        if ('MI' in conditions_state):
            simplified=simplified+1
        if ('chf' in conditions_state):
            simplified=simplified+2
    else: 
        simplified=None
    simplified2 = simplified
    simplified3 = simplified
    if simplified==None:
        style={'textAlign': 'center', 'color':'slateblue'}
    elif simplified>=3:
        style={'textAlign': 'center', 'color':'crimson'}
    else:
        style={'textAlign': 'center', 'color':'slateblue'}
    style2 = style
    return simplified, style, simplified2, style2, simplified3


#### Establish a callback for COM-AF Calculation
@app.callback(
    [
        dash.dependencies.Output('comaf-card', 'children'),
        dash.dependencies.Output('comaf-card', 'style'),
        dash.dependencies.Output('comaf-mini', 'children'),
        dash.dependencies.Output('comaf-mini', 'style'),
        dash.dependencies.Output('comaf-state', 'data')
    ],
    [
        dash.dependencies.Input('submit-button', 'n_clicks')
    ],
    [
        dash.dependencies.State('age-state', 'value'),
        dash.dependencies.State('gender-state', 'value'),
        dash.dependencies.State('weight-state', 'value'),
        dash.dependencies.State('height-state', 'value'),
        dash.dependencies.State('ef-state', 'value'),
        dash.dependencies.State('eGFR-state', 'value'),
        dash.dependencies.State('emergency-state', 'value'),
        dash.dependencies.State('conditions-state', 'value'),
        dash.dependencies.State('procedures-state', 'value')
    ],
)
def comaf_calc(button_click, age_state, gender_state, weight_state, height_state, ef_state, eGFR_state, emergency_state, conditions_state, procedures_state):
    ctx = dash.callback_context
    changed_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if ('submit-button' in changed_id):
        comaf=0
        if (65 <= age_state <= 74):
            comaf=comaf+1
        if (age_state >= 65):
            comaf=comaf+2
        if (gender_state == 'F'):
            comaf=comaf+1
        if ('hbp' in conditions_state):
            comaf=comaf+1
        if ('dm' in conditions_state):
            comaf=comaf+1
        if ('stroke' in conditions_state):
            comaf=comaf+2
    else: 
        comaf=None
    comaf2 = comaf
    comaf3 = comaf
    if comaf==None:
        style={'textAlign': 'center', 'color':'slateblue'}
    elif comaf>=3:
        style={'textAlign': 'center', 'color':'crimson'}
    else:
        style={'textAlign': 'center', 'color':'slateblue'}
    style2 = style
    return comaf, style, comaf2, style2, comaf3

#### Establish a callback for the comparison graph
@app.callback(
    dash.dependencies.Output('stripchart', 'figure'),
    [
        dash.dependencies.Input('upload-data', 'contents'),
        dash.dependencies.Input('upload-data', 'filename'),
        dash.dependencies.Input('afri-state', 'data'),
        dash.dependencies.Input('chads-state', 'data'),
        dash.dependencies.Input('poaf-state', 'data'),
        dash.dependencies.Input('npoaf-state', 'data'),
        dash.dependencies.Input('simplified-state', 'data'),
        dash.dependencies.Input('comaf-state', 'data'),
        dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
        dash.dependencies.Input('crossfilter-yaxis-column', 'value')
    ]
    )
def compare_graph(contents, filename, afri_val, chads_val, poaf_val, npoaf_val, simplified_val, comaf_val, xaxis, yaxis):
    #### Create a graph to compare risk scores two at a time 
    if contents is not None:
        df = parse_contents(contents, filename)
    else:
        df = default_data
    fig = px.strip(x=df[xaxis], y=df[yaxis], color=df['AF'], 
                    color_discrete_map = {0:'midnightblue',1:'lightsteelblue'},
                    labels={'AF':'Atrial Fibrillation', 'npoaf':'NPOAF Score', 'afri': 'AFRI Score'})
    newnames={'0': 'no', '1': 'yes'}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
    fig.update_layout(title_text='Comparison of Two Scores', title_x=0.5)
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig.update_layout(
        xaxis=dict(
            title=xaxis,
            linecolor="#BCCCDC",  # Sets color of X-axis line
            showgrid=False, # Removes X-axis grid lines
            fixedrange=True  
        ),
        yaxis=dict(
            title=yaxis,
            linecolor="#BCCCDC",  # Sets color of Y-axis line
            showgrid=False, # Removes Y-axis grid lines
            fixedrange=True      
        ))
    if afri_val is not None:
        if xaxis=='afri':
            xval=afri_val
        elif xaxis=='chads':
            xval=chads_val
        elif xaxis=='poaf':
            xval=poaf_val
        elif xaxis=='npoaf':
            xval=npoaf_val
        elif xaxis=='simplified':
            xval=simplified_val
        elif yaxis=='comaf':
            xval=comaf_val
        if yaxis=='afri':
            yval=afri_val
        elif yaxis=='chads':
            yval=chads_val
        elif yaxis=='poaf':
            yval=poaf_val
        elif yaxis=='npoaf':
            yval=npoaf_val
        elif yaxis=='simplified':
            yval=simplified_val
        elif yaxis=='comaf':
            yval=comaf_val
        figa = fig
        figa.add_trace(
            go.Scatter(
                x=[xval],
                y=[yval],
                mode="markers",
                marker=dict(color="crimson"),
                showlegend=False)
        )
        return figa
    else:
        return fig


#### Establish a callback for calculating validation metrics
@app.callback(
    [
        dash.dependencies.Output('afri-val', 'children'),
        dash.dependencies.Output('chads-val', 'children'),
        dash.dependencies.Output('poaf-val', 'children'),
        dash.dependencies.Output('npoaf-val', 'children'),
        dash.dependencies.Output('simplified-val', 'children'),
        dash.dependencies.Output('comaf-val', 'children')
    ],
    [
        dash.dependencies.Input('upload-data', 'contents'),
        dash.dependencies.Input('upload-data', 'filename'),
        dash.dependencies.Input('afri-state', 'data'),
        dash.dependencies.Input('chads-state', 'data'),
        dash.dependencies.Input('poaf-state', 'data'),
        dash.dependencies.Input('npoaf-state', 'data'),
        dash.dependencies.Input('simplified-state', 'data'),
        dash.dependencies.Input('comaf-state', 'data'),
        dash.dependencies.Input('score-tab', 'active_tab')
    ]
)
def score_val(contents, filename, afri_val, chads_val, poaf_val, npoaf_val, simplified_val, comaf_val, score_tab):
    if contents is not None:
        df = parse_contents(contents, filename)
    else:
        df = default_data
    if score_tab == "afri-tab":
        df['score'] = df['afri']
        val = afri_val
        cut = 2
    elif score_tab == "chads-tab":
        df['score'] = df['chads']
        val = chads_val
        cut = 4
    elif score_tab == 'poaf-tab':
        df['score'] = df['poaf']
        val = poaf_val
        cut = 3
    elif score_tab == 'npoaf-tab':
        df['score'] = df['npoaf']
        val = npoaf_val
        cut = 2
    elif score_tab == 'simplified-tab':
        df['score'] = df['simplified']
        val = simplified_val
        cut = 3
    elif score_tab == 'comaf-tab':
        df['score'] = df['comaf']
        val = comaf_val
        cut = 3
    ### --> calculate percentile
    if val is not None:
        n_total = len(df)
        n_less = len(df[df['score']<val])
        percentile = round((n_less/n_total)*100)
    else:
        percentile=None
    ### --> classify predicted AF outcome based on cut point
    df['AF_cut'] = np.where((df['score']>=cut),1,0)
    ### --> tabulate totals for TP, FP, FN, and TN
    TP = len(df[(df['AF']==1) & (df['AF_cut']==1)])
    FP = len(df[(df['AF']==0) & (df['AF_cut']==1)])
    FN = len(df[(df['AF']==1) & (df['AF_cut']==0)])
    TN = len(df[(df['AF']==0) & (df['AF_cut']==0)])
    ### --> define the independent and response variables
    independent1 = df['score']
    response1 = df['AF']
    ### --> bulid the logistic regression model
    log1 = sm.Logit(response1,sm.add_constant(independent1)).fit() #use 'add_constant' to add the intercept to the model
    ### --> format the CI for the estimate
    ci1 = np.exp(log1.conf_int(alpha=0.05)).drop(index="const", axis=0)
    ci1.columns = ["2.5%", "97.5%"]
    or1 = np.exp(log1.params['score'].item())
    ci1_lower = ci1['2.5%'].item()
    ci1_higher = ci1['97.5%'].item()
    ### --> format the results for the card
    OR = round(or1, 2)
    lower = round(ci1_lower,2)
    higher = round(ci1_higher,2)
    sensitivity = round((TP/(TP+FN))*100)
    specificity = round((TN/(TN+FP))*100)
    PPV = round((TP/(TP+FP))*100)
    NPV = round((TN/(TN+FN))*100)
    afri_val = dbc.CardBody([
                    html.P(["Percentile: ", percentile, "%"]),
                    html.P(["Odds Ratio: ", OR, " (95% CI: ", lower, "-", higher, ")"]),
                    html.P(["Cut Point: ", cut]),
                    html.P(["Sensitivity: ", sensitivity, "%"]),
                    html.P(["Specificity: ", specificity, "%"]),
                    html.P(["Positive Predictive Value: ", PPV, "%"]),
                    html.P(["Negative Predictive Value: ", NPV, "%"])
                ])
    chads_val = dbc.CardBody([
                    html.P(["Percentile: ", percentile, "%"]),
                    html.P(["Odds Ratio: ", OR, " (95% CI: ", lower, "-", higher, ")"]),
                    html.P(["Cut Point: ", cut]),
                    html.P(["Sensitivity: ", sensitivity, "%"]),
                    html.P(["Specificity: ", specificity, "%"]),
                    html.P(["Positive Predictive Value: ", PPV, "%"]),
                    html.P(["Negative Predictive Value: ", NPV, "%"])
                ])
    poaf_val = dbc.CardBody([
                    html.P(["Percentile: ", percentile, "%"]),
                    html.P(["Odds Ratio: ", OR, " (95% CI: ", lower, "-", higher, ")"]),
                    html.P(["Cut Point: ", cut]),
                    html.P(["Sensitivity: ", sensitivity, "%"]),
                    html.P(["Specificity: ", specificity, "%"]),
                    html.P(["Positive Predictive Value: ", PPV, "%"]),
                    html.P(["Negative Predictive Value: ", NPV, "%"])
                ])
    npoaf_val = dbc.CardBody([
                    html.P(["Percentile: ", percentile, "%"]),
                    html.P(["Odds Ratio: ", OR, " (95% CI: ", lower, "-", higher, ")"]),
                    html.P(["Cut Point: ", cut]),
                    html.P(["Sensitivity: ", sensitivity, "%"]),
                    html.P(["Specificity: ", specificity, "%"]),
                    html.P(["Positive Predictive Value: ", PPV, "%"]),
                    html.P(["Negative Predictive Value: ", NPV, "%"])
                ])
    simplified_val = dbc.CardBody([
                    html.P(["Percentile: ", percentile, "%"]),
                    html.P(["Odds Ratio: ", OR, " (95% CI: ", lower, "-", higher, ")"]),
                    html.P(["Cut Point: ", cut]),
                    html.P(["Sensitivity: ", sensitivity, "%"]),
                    html.P(["Specificity: ", specificity, "%"]),
                    html.P(["Positive Predictive Value: ", PPV, "%"]),
                    html.P(["Negative Predictive Value: ", NPV, "%"])
                ])
    comaf_val = dbc.CardBody([
                    html.P(["Percentile: ", percentile, "%"]),
                    html.P(["Odds Ratio: ", OR, " (95% CI: ", lower, "-", higher, ")"]),
                    html.P(["Cut Point: ", cut]),
                    html.P(["Sensitivity: ", sensitivity, "%"]),
                    html.P(["Specificity: ", specificity, "%"]),
                    html.P(["Positive Predictive Value: ", PPV, "%"]),
                    html.P(["Negative Predictive Value: ", NPV, "%"])
                ])
    return afri_val, chads_val, poaf_val, npoaf_val, simplified_val, comaf_val

#### Establish a callback for producing score histograms
@app.callback(
    [
        dash.dependencies.Output('afri-hist', 'children'),
        dash.dependencies.Output('chads-hist', 'children'),
        dash.dependencies.Output('poaf-hist', 'children'),
        dash.dependencies.Output('npoaf-hist', 'children'),
        dash.dependencies.Output('simplified-hist', 'children'),
        dash.dependencies.Output('comaf-hist', 'children')
    ],
    [
        dash.dependencies.Input('upload-data', 'contents'),
        dash.dependencies.Input('upload-data', 'filename'),
        dash.dependencies.Input('score-tab', 'active_tab')
    ]
)
def afri_val(contents, filename, score_tab):
    if contents is not None:
        df = parse_contents(contents, filename)
    else:
        df = default_data
    if score_tab == "afri-tab":
        ### --> establish histogram
        fig1 = px.histogram(df, x="afri", histnorm="probability", color="AF", 
                           color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                           labels={'AF':'Atrial Fibrillation', 'afri':'AFRI Score'})
        ### --> change figure title
        fig1.update_layout(title_text='AFRI Scores by Atrial Fibrillation Outcome', title_x=0.5)
    elif score_tab == "chads-tab":
        ### --> establish histogram
        fig1 = px.histogram(df, x="chads", histnorm="probability", color="AF", 
                           color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                           labels={'AF':'Atrial Fibrillation', 'chads':'CHA2DS2-VASc Score'})
        ### --> change figure title
        fig1.update_layout(title_text='CHA2DS2-VASc Scores by Atrial Fibrillation Outcome', title_x=0.5)
    elif score_tab == "poaf-tab":
        ### --> establish histogram
        fig1 = px.histogram(df, x="poaf", histnorm="probability", color="AF", 
                           color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                           labels={'AF':'Atrial Fibrillation', 'poaf':'POAF Score'})
        ### --> change figure title
        fig1.update_layout(title_text='POAF Scores by Atrial Fibrillation Outcome', title_x=0.5)
    elif score_tab == "npoaf-tab":
        ### --> establish histogram
        fig1 = px.histogram(df, x="npoaf", histnorm="probability", color="AF", 
                           color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                           labels={'AF':'Atrial Fibrillation', 'npoaf':'NPOAF Score'})
        ### --> change figure title
        fig1.update_layout(title_text='NPOAF Scores by Atrial Fibrillation Outcome', title_x=0.5)
    elif score_tab == "simplified-tab":
        ### --> establish histogram
        fig1 = px.histogram(df, x="simplified", histnorm="probability", color="AF", 
                           color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                           labels={'AF':'Atrial Fibrillation', 'simplified':'Simplified POAF Score'})
        ### --> change figure title
        fig1.update_layout(title_text='Simplified POAF Scores by Atrial Fibrillation Outcome', title_x=0.5)
    elif score_tab == "comaf-tab":
        ### --> establish histogram
        fig1 = px.histogram(df, x="comaf", histnorm="probability", color="AF", 
                           color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                           labels={'AF':'Atrial Fibrillation', 'comaf':'COM-AF Score'})
        ### --> change figure title
        fig1.update_layout(title_text='COM-AF Scores by Atrial Fibrillation Outcome', title_x=0.5)
    ### --> update formatting of the figure
    newnames={'0': 'no', '1': 'yes'}
    fig1.for_each_trace(lambda t: t.update(name = newnames[t.name]))
    fig1.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig1.update_layout(xaxis=dict(
            linecolor="#BCCCDC",  # Sets color of X-axis line
            showgrid=False, # Removes X-axis grid lines
            fixedrange=True  
        ),
        yaxis=dict(
            title="Probability",  
            linecolor="#BCCCDC",  # Sets color of Y-axis line
            showgrid=False, # Removes Y-axis grid lines
            fixedrange=True      
        ))
    fig1.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.85
    ))
    afri_hist=dcc.Graph(figure=fig1)
    chads_hist=dcc.Graph(figure=fig1)
    poaf_hist=dcc.Graph(figure=fig1)
    npoaf_hist=dcc.Graph(figure=fig1)
    simplified_hist=dcc.Graph(figure=fig1)
    comaf_hist=dcc.Graph(figure=fig1)
    return afri_hist, chads_hist, poaf_hist, npoaf_hist, simplified_hist, comaf_hist



#### Define a function for running the server with an option for specifying the port
def run_server(self, host,
               port=8050):
    serve(self, host=host, port=port)


#### Configure the settings to avoid an attribute error when using JupyterDash
del app.config._read_only["requests_pathname_prefix"]


#### Run the app (modify port as necessary to find one that is not in use; macOS users should change host to host='')
app.run_server(host='', port=8050)

