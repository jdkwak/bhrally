import dash
import flask
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H4(children='BEURS-Hobby Rally 2019'),
    html.Table(id='bench-dataframe'),
    html.Table(id='score-dataframe'),
    dcc.Interval(
	id='interval-component',
	interval=10*1000,
	n_intervals=0
   )
])


@app.callback(Output('score-dataframe', 'children'),
		[Input('interval-component', 'n_intervals')])
def generate_score_table(dataframe, max_rows=100):
    dataframe = pd.read_csv('score.csv')
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

@app.callback(Output('bench-dataframe', 'children'),
		[Input('interval-component', 'n_intervals')])
def generate_bench_table(dataframe, max_rows=100):
    dataframe = pd.read_csv('bench.csv')
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )



if __name__ == '__main__':
    app.run_server(debug=True)
