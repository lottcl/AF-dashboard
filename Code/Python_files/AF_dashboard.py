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


### Read in processed dataset
df=pd.read_csv('../../Data/risk.csv')


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
        # Allow multiple files to be uploaded
        multiple=False
    )
])


#### Create a form to calculate new risk scores <a id="form"></a>
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


#### Create display cards for the calculated risk scores <a id="cards"></a>
### --> AFRI Card
card1 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='afri-val', className="card-val1",style={'textAlign': 'center', 'color':'slateblue'}),
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
            html.H4(id='chads-val', className="card-val2",style={'textAlign': 'center', 'color':'slateblue'}),
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
                    html.H4(id='poaf-val', className="card-val3",style={'textAlign': 'center', 'color':'slateblue'}),
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
            html.H4(id='npoaf-val', className="card-val4",style={'textAlign': 'center', 'color':'slateblue'}),
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
            html.H4(id='simplified-val', className="card-val5",style={'textAlign': 'center', 'color':'slateblue'}),
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
            html.H4(id='comaf-val', className="card-val6",style={'textAlign': 'center', 'color':'slateblue'}),
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


#### Create a graph to compare risk scores two at a time <a id="compare"></a>
df['n'] = np.arange(len(df))
df_melt = df.melt(id_vars='n', value_vars=['chads2','afri','npoaf'])
df2 = pd.merge(df, df_melt, on='n')
fig = px.strip(df2, x="afri", y="npoaf", color="AF", 
                color_discrete_map = {0:'midnightblue',1:'lightsteelblue'},
                labels={'AF':'Atrial Fibrillation', 'npoaf':'NPOAF Score', 'afri': 'AFRI Score'})
newnames={'0': 'no', '1': 'yes'}
fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
fig.update_layout(title_text='Comparison of Two Scores', title_x=0.5)
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
fig.update_layout(xaxis=dict(
        linecolor="#BCCCDC",  # Sets color of X-axis line
        showgrid=False, # Removes X-axis grid lines
        fixedrange=True  
    ),
    yaxis=dict(  
        linecolor="#BCCCDC",  # Sets color of Y-axis line
        showgrid=False, # Removes Y-axis grid lines
        fixedrange=True      
    ))
fig.add_trace(
    go.Scatter(
        x=[3],
        y=[3],
        mode="markers",
        marker=dict(color="crimson"),
        showlegend=False)
)
# --> dropdown menus to select risk scores for comparison
dropdowns = html.Div([
    html.P("x-axis: ", className="crossfilter-xaxis-label", style={'margin-left': '10px'}),
    dcc.Dropdown(
        id='crossfilter-xaxis-column',
        options=['AFRI','CHA2DS2-VASc', 'POAF', 'NPOAF', 'Simplified POAF', 'COM-AF'],
        value='AFRI', 
        style={'margin-left': '5px'}
    ),
    html.P("y-axis: ", className="crossfilter-yaxis-label", style={'margin-left': '10px'}),
    dcc.Dropdown(
        id='crossfilter-yaxis-column',
        options=['AFRI','CHA2DS2-VASc', 'POAF', 'NPOAF', 'Simplified POAF', 'COM-AF'],
        value='NPOAF', 
        style={'margin-left': '5px'}
    )
])


#### Create miniature cards to display calculated scores on page 2 <a id="minicards"></a>
minicard1 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='afri-mini', className="card-val1",style={'textAlign': 'center', 'color':'slateblue'}),
            html.P(
                ["AFRI"], 
                className="card-text1",
                style={'textAlign': 'center'}
            )
        ])
)

minicard2 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='chads-mini', className="card-val2",style={'textAlign': 'center', 'color':'slateblue'}),
            html.P(
                ["CHA2DS2-VASc"], 
                className="card-text2",
                style={'textAlign': 'center'}
            )
        ])
)

minicard3 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='poaf-mini', className="card-val3",style={'textAlign': 'center', 'color':'slateblue'}),
            html.P(
                ["POAF"], 
                className="card-text3",
                style={'textAlign': 'center'}
            )
        ])
)

minicard4 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='npoaf-mini', className="card-val4",style={'textAlign': 'center', 'color':'slateblue'}),
            html.P(
                ["NPOAF"], 
                className="card-text4",
                style={'textAlign': 'center'}
            )
        ])
)

minicard5 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='simplified-mini', className="card-val5",style={'textAlign': 'center', 'color':'slateblue'}),
            html.P(
                ["Simplified POAF"], 
                className="card-text5",
                style={'textAlign': 'center'}
            )
        ])
)

minicard6 = dbc.Card(
    dbc.CardBody(
        [
            html.H4(id='comaf-mini', className="card-val6",style={'textAlign': 'center', 'color':'slateblue'}),
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


#### Create a tab for AFRI results <a id="afri"></a>
# --> AFRI results calculation
### --> classify predicted AF outcome based on cut point
df['a_AF'] = np.where((df['afri']>=2),1,0)
### --> tabulate totals for TP, FP, FN, and TN
a_TP = len(df[(df['AF']==1) & (df['a_AF']==1)])
a_FP = len(df[(df['AF']==0) & (df['a_AF']==1)])
a_FN = len(df[(df['AF']==1) & (df['a_AF']==0)])
a_TN = len(df[(df['AF']==0) & (df['a_AF']==0)])
### --> define the independent and response variables
independent1 = df['afri']
response1 = df['AF']
### --> bulid the logistic regression model
log1 = sm.Logit(response1,sm.add_constant(independent1)).fit() #use 'add_constant' to add the intercept to the model
### --> format the CI for the estimate
ci1 = np.exp(log1.conf_int(alpha=0.05)).drop(index="const", axis=0)
ci1.columns = ["2.5%", "97.5%"]
or1 = np.exp(log1.params['afri'].item())
ci1_lower = ci1['2.5%'].item()
ci1_higher = ci1['97.5%'].item()
### --> format the results for the card
AFRI_OR = round(or1, 2)
AFRI_lower = round(ci1_lower,2)
AFRI_higher = round(ci1_higher,2)
AFRI_se = round((a_TP/(a_TP+a_FN))*100)
AFRI_sp = round((a_TN/(a_TN+a_FP))*100)
AFRI_ppv = round((a_TP/(a_TP+a_FP))*100)
AFRI_npv = round((a_TN/(a_TN+a_FN))*100)

# --> AFRI histogram
### --> apply dashboard formatting to figure
load_figure_template("lux")
### --> establish histogram
fig1 = px.histogram(df, x="afri", histnorm="probability", color="AF", 
                   color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                   labels={'AF':'Atrial Fibrillation', 'afri':'AFRI Score'})
### --> update formatting
newnames={'0': 'no', '1': 'yes'}
fig1.for_each_trace(lambda t: t.update(name = newnames[t.name]))
fig1.update_layout(title_text='AFRI Scores by Atrial Fibrillation Outcome', title_x=0.5)
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

# --> AFRI results card and tab format
### --> output the results on a card
card_afri = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                [
                    html.P(["Odds Ratio: ", AFRI_OR, " (95% CI: ", AFRI_lower, "-", AFRI_higher, ")"], className="afri1"),
                    html.P("Cut Point: 2"),
                    html.P(["Sensitivity: ", AFRI_se, "%"], className="afri2"),
                    html.P(["Specificity: ", AFRI_sp, "%"], className="afri3"),
                    html.P(["Positive Predictive Value: ", AFRI_ppv, "%"], className="afri4"),
                    html.P(["Negative Predictive Value: ", AFRI_npv, "%"], className="afri5")
                ]), 
                style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the AFRI tab
afri_tab = html.Div([
    dcc.Graph(figure=fig1, style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_afri
])


#### Create a tab for CHADS results 
# --> CHADS results calculation
### --> classify predicted AF outcome based on cut point
df['c_AF'] = np.where((df['chads2']>=4),1,0)
### --> tabulate totals for TP, FP, FN, and TN
c_TP = len(df[(df['AF']==1) & (df['c_AF']==1)])
c_FP = len(df[(df['AF']==0) & (df['c_AF']==1)])
c_FN = len(df[(df['AF']==1) & (df['c_AF']==0)])
c_TN = len(df[(df['AF']==0) & (df['c_AF']==0)])
### --> define the independent and response variables
independent2 = df['chads2']
response2 = df['AF']
### --> bulid the logistic regression model
log2 = sm.Logit(response2,sm.add_constant(independent2)).fit() #use 'add_constant' to add the intercept to the model
### --> format the CI for the estimate
ci2 = log2.conf_int(alpha=0.05).drop(index="const", axis=0)
ci2.columns = ["2.5%", "97.5%"]
or2 = np.exp(log2.params['chads2'].item())
ci2_lower = ci2['2.5%'].item()
ci2_higher = ci2['97.5%'].item()
### --> format the results for the card
CHADS_OR = round(or2, 2)
CHADS_lower = round(ci2_lower,2)
CHADS_higher = round(ci2_higher,2)
CHADS_se = round((c_TP/(c_TP+c_FN))*100)
CHADS_sp = round((c_TN/(c_TN+c_FP))*100)
CHADS_ppv = round((c_TP/(c_TP+c_FP))*100)
CHADS_npv = round((c_TN/(c_TN+c_FN))*100)

# --> CHADS histogram
### --> apply dashboard formatting to figure
load_figure_template("lux")
### --> establish histogram
fig2 = px.histogram(df, x="chads2", histnorm="probability", color="AF", 
                   color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                   labels={'AF':'Atrial Fibrillation', 'chads2':'CHA2DS2-VASc Score'})
### --> update formatting
newnames={'0': 'no', '1': 'yes'}
fig2.for_each_trace(lambda t: t.update(name = newnames[t.name]))
fig2.update_layout(title_text='CHA2DS2-VASc Scores by Atrial Fibrillation Outcome', title_x=0.5)
fig2.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
fig2.update_layout(xaxis=dict(
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
fig2.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.85
))

# --> CHADS results card and tab format
### --> output the results on a card
card_chads = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                [
                    html.P(["Odds Ratio: ", CHADS_OR, " (95% CI: ", CHADS_lower, "-", CHADS_higher, ")"], className="chads1"),
                    html.P("Cut Point: 4"),
                    html.P(["Sensitivity: ", CHADS_se, "%"], className="chads2"),
                    html.P(["Specificity: ", CHADS_sp, "%"], className="chads3"),
                    html.P(["Positive Predictive Value: ", CHADS_ppv, "%"], className="chads4"),
                    html.P(["Negative Predictive Value: ", CHADS_npv, "%"], className="chads5")
                ]), 
                style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the CHADS tab
chads_tab = html.Div([
    dcc.Graph(figure=fig2, style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_chads
])


#### Create a tab for POAF results
# --> POAF results calculation
### --> classify predicted AF outcome based on cut point
df['p_AF'] = np.where((df['poaf']>=3),1,0)
### --> tabulate totals for TP, FP, FN, and TN
p_TP = len(df[(df['AF']==1) & (df['p_AF']==1)])
p_FP = len(df[(df['AF']==0) & (df['p_AF']==1)])
p_FN = len(df[(df['AF']==1) & (df['p_AF']==0)])
p_TN = len(df[(df['AF']==0) & (df['p_AF']==0)])
### --> define the independent and response variables
independent3 = df['poaf']
response3 = df['AF']
### --> bulid the logistic regression model
log3 = sm.Logit(response3,sm.add_constant(independent3)).fit() #use 'add_constant' to add the intercept to the model
### --> format the CI for the estimate
ci3 = np.exp(log3.conf_int(alpha=0.05)).drop(index="const", axis=0)
ci3.columns = ["2.5%", "97.5%"]
or3 = np.exp(log3.params['poaf'].item())
ci3_lower = ci3['2.5%'].item()
ci3_higher = ci3['97.5%'].item()
### --> format the results for the card
POAF_OR = round(or3, 2)
POAF_lower = round(ci3_lower,2)
POAF_higher = round(ci3_higher,2)
POAF_se = round((p_TP/(p_TP+p_FN))*100)
POAF_sp = round((p_TN/(p_TN+p_FP))*100)
POAF_ppv = round((p_TP/(p_TP+p_FP))*100)
POAF_npv = round((p_TN/(p_TN+p_FN))*100)

# --> POAF histogram
### --> apply dashboard formatting to figure
load_figure_template("lux")
### --> establish histogram
fig3 = px.histogram(df, x="poaf", histnorm="probability", color="AF", 
                   color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                   labels={'AF':'Atrial Fibrillation', 'poaf':'POAF Score'})
### --> update formatting
newnames={'0': 'no', '1': 'yes'}
fig3.for_each_trace(lambda t: t.update(name = newnames[t.name]))
fig3.update_layout(title_text='POAF Scores by Atrial Fibrillation Outcome', title_x=0.5)
fig3.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
fig3.update_layout(xaxis=dict(
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
fig3.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.85
))

# --> POAF results card and tab format
### --> output the results on a card
card_poaf = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                [
                    html.P(["Odds Ratio: ", POAF_OR, " (95% CI: ", POAF_lower, "-", POAF_higher, ")"], className="poaf1"),
                    html.P("Cut Point: 3"),
                    html.P(["Sensitivity: ", POAF_se, "%"], className="poaf2"),
                    html.P(["Specificity: ", POAF_sp, "%"], className="poaf3"),
                    html.P(["Positive Predictive Value: ", POAF_ppv, "%"], className="poaf4"),
                    html.P(["Negative Predictive Value: ", POAF_npv, "%"], className="poaf5")
                ]), 
                style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the POAF tab
poaf_tab = html.Div([
    dcc.Graph(figure=fig3, style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_poaf
])


#### Create a tab for NPOAF results
# --> NPOAF results calculation
### --> classify predicted AF outcome based on cut point
df['n_AF'] = np.where((df['npoaf']>=2),1,0)
### --> tabulate totals for TP, FP, FN, and TN
n_TP = len(df[(df['AF']==1) & (df['n_AF']==1)])
n_FP = len(df[(df['AF']==0) & (df['n_AF']==1)])
n_FN = len(df[(df['AF']==1) & (df['n_AF']==0)])
n_TN = len(df[(df['AF']==0) & (df['n_AF']==0)])
### --> define the independent and response variables
independent4 = df['npoaf']
response4 = df['AF']
### --> bulid the logistic regression model
log4 = sm.Logit(response4,sm.add_constant(independent4)).fit() #use 'add_constant' to add the intercept to the model
### --> format the CI for the estimate
ci4 = np.exp(log4.conf_int(alpha=0.05)).drop(index="const", axis=0)
ci4.columns = ["2.5%", "97.5%"]
or4 = np.exp(log4.params['npoaf'].item())
ci4_lower = ci4['2.5%'].item()
ci4_higher = ci4['97.5%'].item()
### --> format the results for the card
NPOAF_OR = round(or4, 2)
NPOAF_lower = round(ci4_lower,2)
NPOAF_higher = round(ci4_higher,2)
NPOAF_se = round((n_TP/(n_TP+n_FN))*100)
NPOAF_sp = round((n_TN/(n_TN+n_FP))*100)
NPOAF_ppv = round((n_TP/(n_TP+n_FP))*100)
NPOAF_npv = round((n_TN/(n_TN+n_FN))*100)

# --> NPOAF histogram
### --> apply dashboard formatting to figure
load_figure_template("lux")
### --> establish histogram
fig4 = px.histogram(df, x="npoaf", histnorm="probability", color="AF", 
                   color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                   labels={'AF':'Atrial Fibrillation', 'npoaf':'NPOAF Score'})
### --> update formatting
newnames={'0': 'no', '1': 'yes'}
fig4.for_each_trace(lambda t: t.update(name = newnames[t.name]))
fig4.update_layout(title_text='NPOAF Scores by Atrial Fibrillation Outcome', title_x=0.5)
fig4.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
fig4.update_layout(xaxis=dict(
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
fig4.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.85
))

# --> NPOAF results card and tab format
### --> output the results on a card
card_npoaf = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                [
                    html.P(["Odds Ratio: ", NPOAF_OR, " (95% CI: ", NPOAF_lower, "-", NPOAF_higher, ")"], className="poaf1"),
                    html.P("Cut Point: 2"),
                    html.P(["Sensitivity: ", NPOAF_se, "%"], className="poaf2"),
                    html.P(["Specificity: ", NPOAF_sp, "%"], className="poaf3"),
                    html.P(["Positive Predictive Value: ", NPOAF_ppv, "%"], className="poaf4"),
                    html.P(["Negative Predictive Value: ", NPOAF_npv, "%"], className="poaf5")
                ]), 
                style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the NPOAF tab
npoaf_tab = html.Div([
    dcc.Graph(figure=fig4, style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_npoaf
])


#### Create a tab for Simplified POAF results <a id="simplified"></a>
# --> Simplified POAF results calculation
### --> classify predicted AF outcome based on cut point
df['s_AF'] = np.where((df['simplified']>=3),1,0)
### --> tabulate totals for TP, FP, FN, and TN
s_TP = len(df[(df['AF']==1) & (df['s_AF']==1)])
s_FP = len(df[(df['AF']==0) & (df['s_AF']==1)])
s_FN = len(df[(df['AF']==1) & (df['s_AF']==0)])
s_TN = len(df[(df['AF']==0) & (df['s_AF']==0)])
### --> define the independent and response variables
independent5 = df['simplified']
response5 = df['AF']
### --> bulid the logistic regression model
log5 = sm.Logit(response5,sm.add_constant(independent5)).fit() #use 'add_constant' to add the intercept to the model
### --> format the CI for the estimate
ci5 = np.exp(log5.conf_int(alpha=0.05)).drop(index="const", axis=0)
ci5.columns = ["2.5%", "97.5%"]
or5 = np.exp(log5.params['simplified'].item())
ci5_lower = ci5['2.5%'].item()
ci5_higher = ci5['97.5%'].item()
### --> format the results for the card
Simplified_OR = round(or5, 2)
Simplified_lower = round(ci5_lower,2)
Simplified_higher = round(ci5_higher,2)
Simplified_se = round((s_TP/(s_TP+s_FP))*100)
Simplified_sp = round((s_TN/(s_TN+s_FP))*100)
Simplified_ppv = round((s_TP/(s_TP+s_FP))*100)
Simplified_npv = round((s_TN/(s_TN+s_FN))*100)


# --> Simplified POAF histogram
### --> apply dashboard formatting to figure
load_figure_template("lux")
### --> establish histogram
fig5 = px.histogram(df, x="simplified", histnorm="probability", color="AF", 
                   color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                   labels={'AF':'Atrial Fibrillation', 'simplified':'Simplified POAF Score'})
### --> update formatting
newnames={'0': 'no', '1': 'yes'}
fig5.for_each_trace(lambda t: t.update(name = newnames[t.name]))
fig5.update_layout(title_text='Simplified POAF Scores by Atrial Fibrillation Outcome', title_x=0.5)
fig5.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
fig5.update_layout(xaxis=dict(
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
fig5.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.85
))


# --> Simplified POAF results card and tab format
### --> output the results on a card
card_simplified = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                [
                    html.P(["Odds Ratio: ", Simplified_OR, " (95% CI: ", Simplified_lower, "-", Simplified_higher, ")"], className="sim1"),
                    html.P("Cut Point: 3"),
                    html.P(["Sensitivity: ", Simplified_se, "%"], className="sim2"),
                    html.P(["Specificity: ", Simplified_sp, "%"], className="sim3"),
                    html.P(["Positive Predictive Value: ", Simplified_ppv, "%"], className="sim4"),
                    html.P(["Negative Predictive Value: ", POAF_npv, "%"], className="sim5")
                ]), 
                style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the AFRI tab
simplified_tab = html.Div([
    dcc.Graph(figure=fig5, style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_simplified
])


#### Create a tab for COM-AF results
# --> COM-AF results calculation
### --> classify predicted AF outcome based on cut point
df['co_AF'] = np.where((df['comaf']>=3),1,0)
### --> tabulate totals for TP, FP, FN, and TN
co_TP = len(df[(df['AF']==1) & (df['co_AF']==1)])
co_FP = len(df[(df['AF']==0) & (df['co_AF']==1)])
co_FN = len(df[(df['AF']==1) & (df['co_AF']==0)])
co_TN = len(df[(df['AF']==0) & (df['co_AF']==0)])
### --> define the independent and response variables
independent6 = df['comaf']
response6 = df['AF']
### --> bulid the logistic regression model
log6 = sm.Logit(response6,sm.add_constant(independent6)).fit() #use 'add_constant' to add the intercept to the model
### --> format the CI for the estimate
ci6 = np.exp(log6.conf_int(alpha=0.05)).drop(index="const", axis=0)
ci6.columns = ["2.5%", "97.5%"]
or6 = np.exp(log6.params['comaf'].item())
ci6_lower = ci6['2.5%'].item()
ci6_higher = ci6['97.5%'].item()
### --> format the results for the card
COMAF_OR = round(or6, 2)
COMAF_lower = round(ci6_lower,2)
COMAF_higher = round(ci6_higher,2)
COMAF_se = round((co_TP/(co_TP+co_FN))*100)
COMAF_sp = round((co_TN/(co_TN+co_FP))*100)
COMAF_ppv = round((co_TP/(co_TP+co_FP))*100)
COMAF_npv = round((co_TN/(co_TN+co_FN))*100)


# --> COM-AF histogram
### --> apply dashboard formatting to figure
load_figure_template("lux")
### --> establish histogram
fig6 = px.histogram(df, x="comaf", histnorm="probability", color="AF", 
                   color_discrete_map = {0:'midnightblue',1:'lightsteelblue'}, barmode='overlay', 
                   labels={'AF':'Atrial Fibrillation', 'comaf':'COM-AF Score'})
### --> update formatting
newnames={'0': 'no', '1': 'yes'}
fig6.for_each_trace(lambda t: t.update(name = newnames[t.name]))
fig6.update_layout(title_text='COM-AF Scores by Atrial Fibrillation Outcome', title_x=0.5)
fig6.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
fig6.update_layout(xaxis=dict(
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
fig6.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.85
))


# --> COM-AF results card and tab format
### --> output the results on a card
card_comaf = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                [
                    html.P(["Odds Ratio: ", COMAF_OR, " (95% CI: ", COMAF_lower, "-", COMAF_higher, ")"], className="comaf1"),
                    html.P("Cut Point: 3"),
                    html.P(["Sensitivity: ", COMAF_se, "%"], className="comaf2"),
                    html.P(["Specificity: ", COMAF_sp, "%"], className="comaf3"),
                    html.P(["Positive Predictive Value: ", COMAF_ppv, "%"], className="comaf4"),
                    html.P(["Negative Predictive Value: ", COMAF_npv, "%"], className="comaf5")
                ]), 
                style={'margin-right': '10px', 'margin-bottom': '10px'})
        ], 
        width=10)
    ],
    justify='center')
])
### --> establish the format for the AFRI tab
comaf_tab = html.Div([
    dcc.Graph(figure=fig6, style={'margin-right': '10px', 'margin-bottom': '10px'}),
    card_comaf
])


### App Layout
#### Define the tabs for the risk scores
score_tab = dbc.Tabs(
            [
                dbc.Tab(afri_tab, label="AFRI", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center"),
                dbc.Tab(chads_tab, label="CHADS", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center"),
                dbc.Tab(poaf_tab, label="POAF", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center"),
                dbc.Tab(npoaf_tab, label="NPOAF", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center"),
                dbc.Tab(simplified_tab, label="Simplified POAF", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center"),
                dbc.Tab(comaf_tab, label="COM-AF", activeTabClassName="fw-bold", tabClassName="flex-grow-1 text-center"),
            ]
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
                    dcc.Graph(figure=fig, style={'margin-left': '10px'}),
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
        )
    ],
    style={'background-color': '#EEF3F8'}
)


### App Callbacks and Configuration
#### Establish a callback for AFRI Calculation
@app.callback(
    [
        dash.dependencies.Output('afri-val', 'children'),
        dash.dependencies.Output('afri-mini', 'children'),
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
    return afri, afri2


#### Establish a callback for CHADS Calculation
@app.callback(
    [
        dash.dependencies.Output('chads-val', 'children'),
        dash.dependencies.Output('chads-mini', 'children'),
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
    return chads, chads2


#### Establish a callback for POAF Calculation
@app.callback(
    [
        dash.dependencies.Output('poaf-val', 'children'),
        dash.dependencies.Output('poaf-mini', 'children'),
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
    return poaf, poaf2


#### Establish a callback for NPOAF Calculation
@app.callback(
    [
        dash.dependencies.Output('npoaf-val', 'children'),
        dash.dependencies.Output('npoaf-mini', 'children'),
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
    return npoaf, npoaf2


#### Establish a callback for Simplified POAF Calculation
@app.callback(
    [
        dash.dependencies.Output('simplified-val', 'children'),
        dash.dependencies.Output('simplified-mini', 'children'),
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
    return simplified, simplified2


#### Establish a callback for COM-AF Calculation
@app.callback(
    [
        dash.dependencies.Output('comaf-val', 'children'),
        dash.dependencies.Output('comaf-mini', 'children'),
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
    return comaf, comaf2


#### Define a function for running the server with an option for specifying the port
def run_server(self,
               port=8050):
    serve(self, host="0.0.0.0", port=port)


#### Configure the settings to avoid an attribute error when using JupyterDash
del app.config._read_only["requests_pathname_prefix"]


#### Run the app (modify port as necessary to find one that is not in use)
app.run_server(port=8050)

