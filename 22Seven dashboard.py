import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

df = pd.read_csv("data.csv")

df['Transaction ID'] = df['Transaction ID'].astype(str)
df['Customer ID'] = df['Customer ID'].astype(str)
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
df['Year'] = df['Transaction Date'].dt.year
df['Month'] = df['Transaction Date'].dt.month
df['Day'] = df['Transaction Date'].dt.day
df['Time'] = df['Transaction Date'].dt.time
df['YearMonth'] = df['Transaction Date'].dt.to_period('M')
df['DayOfWeek'] = df['Transaction Date'].dt.day_name()
df['IsWeekend'] = df['Transaction Date'].dt.dayofweek // 5 == 1  

app = dash.Dash(__name__)

app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'font-family': 'Lucida Sans'}, children=[
    html.H1("22seven Insights Dashboard", style={'border': '2px solid lime', 'box-shadow': '0 4px 8px rgba(0, 128, 0, 0.5)'}),

    html.Div([
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': 'All Years', 'value': 'all_years'}] +
                    [{'label': str(year), 'value': year} for year in df['Year'].unique()],
            value='all_years', 
            multi=False, 
            style={'width': '33%', 'backgroundColor': 'white', 'color': 'black', 'border': '2px solid lime', 'box-shadow': '0 4px 8px rgba(0, 128, 0, 0.5)'}
        ),
        dcc.Dropdown(
            id='merchant-dropdown',
            options=[{'label': 'All Merchants', 'value': 'all_merchants'}] +
                    [{'label': merchant, 'value': merchant} for merchant in df['Merchant'].unique()],
            value='all_merchants',
            multi=False,
            style={'width': '33%', 'backgroundColor': 'white', 'color': 'black', 'border': '2px solid lime', 'box-shadow': '0 4px 8px rgba(0, 128, 0, 0.5)'}
        ),
        dcc.Dropdown(
            id='client-id-dropdown',
            options=[{'label': 'All Customers', 'value': 'all_customers'}] +
                    [{'label': str(client_id), 'value': client_id} for client_id in df['Customer ID'].unique()],
            value='all_customers',
            multi=False,
            style={'width': '33%', 'backgroundColor': 'white', 'color': 'black', 'border': '2px solid lime', 'box-shadow': '0 4px 8px rgba(0, 128, 0, 0.5)'}
        ),
    ], style={'display': 'flex', 'justify-content': 'center', 'background-color': 'black'}),
    html.Div([
        html.Div([
            dcc.Graph(id='merchant-pie-chart', style={'width': '50%', 'display': 'inline-block', 'backgroundColor': 'white', 'border-radius': '10px', 'border': '2px solid blue', 'box-shadow': '0 4px 8px rgba(0, 128, 0, 0.5)'}),
            dcc.Graph(id='amount-bar-chart', style={'width': '50%', 'display': 'inline-block', 'backgroundColor': 'white', 'border-radius': '10px', 'border': '2px solid blue', 'box-shadow': '0 4px 8px rgba(0, 128, 0, 0.5)'})
        ]),
        html.Div([
            dcc.Graph(id='transaction-line-chart', style={'width': '50%', 'display': 'inline-block', 'backgroundColor': 'white', 'border-radius': '10px', 'border': '2px solid blue', 'box-shadow': '0 4px 8px rgba(0, 128, 0, 0.5)'}),
            dcc.Graph(id='transaction-amount-histogram', style={'width': '50%', 'display': 'inline-block', 'backgroundColor': 'white', 'border-radius': '10px', 'border': '2px solid blue', 'box-shadow': '0 4px 8px rgba(0, 128, 0, 0.5)'})
        ])
    ], style={'display': 'flex', 'justify-content': 'center', 'flex-direction': 'row', 'align-items': 'center','background-color': 'black'})
])

@app.callback(
    [Output('merchant-pie-chart', 'figure'),
     Output('amount-bar-chart', 'figure'),
     Output('transaction-line-chart', 'figure'),
     Output('transaction-amount-histogram', 'figure')],
    [Input('year-dropdown', 'value'),
     Input('merchant-dropdown', 'value'),
     Input('client-id-dropdown', 'value')]
)
def update_graphs(selected_years, selected_merchant, selected_client_id):
    # Check if all options are selected
    all_years_selected = 'all_years' in selected_years
    all_merchants_selected = selected_merchant == 'all_merchants'
    all_customers_selected = selected_client_id == 'all_customers'

    # Filter data based on selection
    if all_years_selected and all_merchants_selected and all_customers_selected:
        df_filtered = df
    else:
        if not all_years_selected:
            df_filtered = df[df['Year'].isin(selected_years)]
        else:
            df_filtered = df

        if not all_merchants_selected:
            df_filtered = df_filtered[df_filtered['Merchant'] == selected_merchant]

        if not all_customers_selected:
            df_filtered = df_filtered[df_filtered['Customer ID'] == selected_client_id]

    df_filtered = df_filtered.reset_index(drop=True)

    # Create graphs
    merchant_counts = df_filtered['Merchant'].value_counts()
    pie_chart = px.pie(merchant_counts, names=merchant_counts.index, title=f'Merchant Distribution')

    amount_bar_chart = px.bar(df_filtered, x='Merchant', y='Amount', title='Amount Spent at Each Merchant',
                              labels={'Amount': 'Amount (ZAR)', 'Merchant': 'Merchant'},
                              color='Merchant', color_discrete_sequence=px.colors.qualitative.Set3)

    df_filtered['Transaction Date'] = pd.to_datetime(df_filtered['Transaction Date'])
    monthly_trends = df_filtered.groupby(pd.Grouper(key='Transaction Date', freq='M')).size()
    transaction_line_chart = go.Figure()
    transaction_line_chart.add_trace(go.Scatter(x=monthly_trends.index, y=monthly_trends.values, mode='lines+markers', marker=dict(symbol='circle-open')))
    transaction_line_chart.update_layout(title='Transaction Trends Over Time', xaxis_title='Date', yaxis_title='Transaction Count')

    transaction_amount_histogram = px.histogram(df_filtered, x='Amount', nbins=30, title='Transaction Amount Distribution',
                                                labels={'Amount': 'Amount (ZAR)', 'Frequency': 'Frequency'})

    return pie_chart, amount_bar_chart, transaction_line_chart, transaction_amount_histogram

if __name__ == '__main__':
    app.run_server(debug=True)
