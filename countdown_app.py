import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import datetime

# Set your quitting date here
quit_date = datetime.datetime(2023, 11, 22, 15, 0, 0)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Countdown to New Chapter", style={"color": "red", "fontSize": "48px"}),
    html.H2(id="countdown", style={"color": "red", "fontSize": "36px"}),
    dcc.Interval(id="interval", interval=1000, n_intervals=0)
], style={
    "display": "flex",
    "flexDirection": "column",
    "alignItems": "center",
    "justifyContent": "center",
    "height": "100vh",
    "textAlign": "center"
})

@app.callback(
    Output("countdown", "children"),
    Input("interval", "n_intervals")
)
def update_countdown(_):
    remaining_time = quit_date - datetime.datetime.now()
    days = remaining_time.days
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"


if __name__ == "__main__":
    app.run_server(debug=True)
