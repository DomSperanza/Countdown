import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import datetime
import json

# Set your quitting date here
quit_date = datetime.datetime(2023, 11, 22, 15, 0, 0)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Countdown to New Chapter", style={"color": "darkred", "fontSize": "48px"}),
            dcc.Tabs(id="tabs", value="tab-1", children=[
                dcc.Tab(label="Total Time", value="tab-1"),
                dcc.Tab(label="Work Week Hours", value="tab-2")
            ]),
            html.Div(id="content"),
            dcc.Dropdown(
                id="time-format",
                options=[
                    {"label": "Days, Hours, Minutes, Seconds", "value": "dhms"},
                    {"label": "Total Hours", "value": "hours"},
                    {"label": "Total Minutes", "value": "minutes"},
                    {"label": "Total Seconds", "value": "seconds"},
                ],
                value="dhms",
                style={"width": "50%", "margin": "20px auto"}
            ),
            html.Div([
                dcc.DatePickerRange(
                    id="vacation-picker",
                    min_date_allowed=datetime.datetime.now(),
                    max_date_allowed=quit_date,
                    start_date=datetime.datetime.now(),
                    end_date=datetime.datetime.now()
                ),
                html.Button("Add Vacation", id="add-vacation", n_clicks=0),
                html.Div(id="vacation-container"),
                html.Button("Clear Vacations", id="clear-vacations", n_clicks=0)  # Add this line
            ]),

            html.Button("Submit Vacation Dates", id="submit-vacation", n_clicks=0),
            dcc.Interval(id="interval", interval=1000, n_intervals=0),
            html.Div(id="vacation-storage", style={"display": "none"})
        ], style={"textAlign": "center"})
    ], style={"height": "100vh", "alignItems": "center", "justifyContent": "center"})
], fluid=True)




#########################
@app.callback(
    Output("vacation-container", "children"),
    Input("add-vacation", "n_clicks"),
    Input("clear-vacations", "n_clicks"),
    State("vacation-picker", "start_date"),
    State("vacation-picker", "end_date"),
    State("vacation-container", "children"),
)
def update_vacations(add_n_clicks, clear_n_clicks, start_date, end_date, current_vacations):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "add-vacation" and add_n_clicks > 0:
        new_vacation = html.Div([
            html.Label(f"Vacation {add_n_clicks}"),
            html.Span(f"{start_date} - {end_date}", style={"margin-left": "10px"}),
            html.Hr()
        ])
        if current_vacations:
            return current_vacations + [new_vacation]
        else:
            return [new_vacation]
    elif triggered_id == "clear-vacations" and clear_n_clicks > 0:
        return []

    raise PreventUpdate

#######################

######################
@app.callback(
    Output("vacation-storage", "children"),
    Input("submit-vacation", "n_clicks"),
    State("vacation-container", "children"),
)
def store_vacation_dates(n_clicks, vacations):
    if n_clicks > 0:
        vacation_dates = []
        for vacation in vacations:
            date_range = vacation["props"]["children"][1]["props"]["children"].split(" - ")
            vacation_dates.append(date_range)
        return json.dumps(vacation_dates)
    raise PreventUpdate


#######################



#######################
@app.callback(
    Output("content", "children"),
    Input("interval", "n_intervals"),
    Input("tabs", "value"),
    Input("time-format", "value"),
    Input("vacation-storage", "children")
)
def update_countdown(_, selected_tab, time_format, vacation_dates):
    remaining_time = quit_date - datetime.datetime.now()
    days = remaining_time.days
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if vacation_dates:
        vacation_dates = json.loads(vacation_dates)
        vacation_work_week_days = 0
        for start_date, end_date in vacation_dates:
            vacation_start, vacation_end = [datetime.datetime.strptime(date, "%Y-%m-%d").date() for date in (start_date, end_date)]
            vacation_days = (vacation_end - vacation_start).days + 1
            vacation_work_week_days += sum([(vacation_start + datetime.timedelta(days=i)).weekday() < 5 for i in range(vacation_days)])
    else:
        vacation_work_week_days = 0

    work_week_days = remaining_time.days // 7 * 5 + min(remaining_time.days % 7, 5) - vacation_work_week_days  # Adjust work week days
    work_week_hours = work_week_days * 8  # Assumes 8 hours per work day

    if time_format == "dhms":
        time_display = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    elif time_format == "hours":
        time_display = f"{days * 24 + hours} hours"
    elif time_format == "minutes":
        time_display = f"{days * 24 * 60 + hours * 60 + minutes} minutes"
    elif time_format == "seconds":
        time_display = f"{days * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60 + seconds} seconds"

    if selected_tab == "tab-1":
        content = html.Div([
            html.H2("Time Remaining", style={"color": "darkred", "fontSize": "36px"}),
            html.P(time_display, style={"fontSize": "24px"}),
        ])
    elif selected_tab == "tab-2":
        if time_format == "dhms":
            work_week_hours_display = f"{work_week_days} days, {hours} hours,{minutes} minutes, {seconds} seconds"
        elif time_format == "hours":
            work_week_hours_display = f"{work_week_hours} hours"
        elif time_format == "minutes":
            work_week_minutes = work_week_hours * 60
            work_week_hours_display = f"{work_week_minutes} minutes"
        elif time_format == "seconds":
            work_week_seconds = work_week_hours * 60 * 60
            work_week_hours_display = f"{work_week_seconds} seconds"

        content = html.Div([
            html.H2("Work Week Hours Remaining", style={"color": "darkred", "fontSize": "36px"}),
            html.P(work_week_hours_display, style={"fontSize": "24px"}),
        ])

    return content

######################

if __name__ == "__main__":
    app.run_server(debug=True)