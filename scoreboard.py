import dash
import flask
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

def generate_table(dataframe, max_rows=100):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

df = pd.read_csv('score.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H4(children='BEURS-Hobby Rally 2019'),
    generate_table(df)
])

if __name__ == '__main__':
    app.run_server(debug=True)
