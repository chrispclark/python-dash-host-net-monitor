import dash
from dash import Dash
import dash_labs as dl
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
from dash import dash_table
from callbacks import get_callbacks

# dash.register_page(__name__, path="/")

colors = {'background': 'rgb(50, 50, 50)', 'text': '#FFFFFF'}

layitout_host_status = (
    html.Div(
        html.H3(
            'Checking Host Status...',
            id='hoststatus_label',
            style={'display': 'inline-block'},
        ),
    ),
)

layitout_arp_status = (
    html.Div(
        html.H3(
            'Checking Arp Status...',
            id='arpstatus_label',
            style={'display': 'inline-block', 'margin-left': '60px'},
        ),
    ),
)


layitout_logs = (
    html.Div(
        [
            html.H3(
                'Status Logs...',
                id='status_label',
                style={'display': 'inline-block'},
            ),
            dcc.Textarea(
                className='custom-tabs-container',
                id='textarea-example',
                value='Textarea content initialized',
                style=dict(
                    width='100%',
                    height=300,
                    backgroundColor=colors['background'],
                    color=colors['text'],
                    font_size='.8em',
                    font_family='sans-serif',
                ),
            ),
        ],
    ),
)

layitout_sync = (
    html.Div(
        [
            html.Button(
                'Sync Config',
                id='my-button',
                style={'display': 'inline-block', 'margin-left': '60px'},
            ),
            html.H3(
                id='button-clicks',
                style={
                    'display': 'inline-block',
                    'font-size': '1em',
                    'margin-left': '15px',
                },
            ),
        ],
    ),
)

layitout_arp = (
    html.Div(
        [
            html.Div(id='arp-table-layout'),
            html.H3('arp status check', style={'textAlign': 'left'}),
            dash_table.DataTable(
                id='arp-table',
                columns=[
                    {
                        'name': 'DateAndTime',
                        'id': 'DateAndTime',
                        'editable': False,
                    },
                    {
                        'name': 'descriptive_name',
                        'id': 'descriptive_name',
                        'editable': False,
                    },
                    {'name': 'host', 'id': 'host', 'editable': False},
                    {'name': 'mask', 'id': 'mask', 'editable': False},
                    {'name': 'check', 'id': 'check', 'editable': False},
                    {'name': 'type', 'id': 'type', 'editable': False},
                    {'name': 'Status', 'id': 'Status', 'editable': False},
                    {'name': 'Reason', 'id': 'Reason', 'editable': False},
                    {
                        'name': 'Last Moved To Up',
                        'id': 'last_up',
                        'editable': False,
                    },
                    {
                        'name': 'last Moved To down',
                        'id': 'last_down',
                        'editable': False,
                    },
                ],
                # data=db.readtable(ARP_TABLE_NAME.__name__),
                sort_action='native',
                sort_mode='multi',
                # Set cell color dependant or marked UP or DOWN
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{Status} ="UP"',
                            'column_id': 'Status',
                        },
                        'color': 'LawnGreen',
                    },
                    {
                        'if': {
                            'filter_query': '{Status} !="UP"',
                            'column_id': 'Status',
                        },
                        'backgroundColor': 'tomato',
                        'color': 'white',
                    },
                ],
                style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                style_cell={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white',
                    'font_size': '14px',
                    'text_align': 'left',
                    'font_size': '.8em',
                    'font_family': 'sans-serif',
                },
                fill_width=False,
                editable=False,
            ),
        ],
    ),
)


#  ----------------------- Host Table Layout --------------------- #
layitout_hosts = (
    html.Div(
        [
            html.Div(id='host-table-layout'),
            html.H3('Host status check', style={'textAlign': 'left'}),
            dash_table.DataTable(
                id='host-table',
                columns=[
                    {
                        'name': 'DateAndTime',
                        'id': 'DateAndTime',
                        'editable': False,
                    },
                    {
                        'name': 'descriptive_name',
                        'id': 'descriptive_name',
                        'editable': False,
                    },
                    {'name': 'host', 'id': 'host', 'editable': False},
                    {'name': 'mask', 'id': 'mask', 'editable': False},
                    {'name': 'check', 'id': 'check', 'editable': False},
                    {'name': 'type', 'id': 'type', 'editable': False},
                    {'name': 'Status', 'id': 'Status', 'editable': False},
                    {'name': 'Reason', 'id': 'Reason', 'editable': False},
                    {
                        'name': 'Last Moved To Up',
                        'id': 'last_up',
                        'editable': False,
                    },
                    {
                        'name': 'last Moved To down',
                        'id': 'last_down',
                        'editable': False,
                    },
                ],
                #  Read data from the dictionary that has been created
                #  from the
                # current sql table.
                # data=db.readtable(HOST_TABLE_NAME.__name__),
                sort_action='native',
                sort_mode='multi',
                # Set cell color dependant or marked UP or DOWN
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{Status} ="UP"',
                            'column_id': 'Status',
                        },
                        'color': 'LawnGreen',
                    },
                    {
                        'if': {
                            'filter_query': '{Status} !="UP"',
                            'column_id': 'Status',
                        },
                        'backgroundColor': 'tomato',
                        'color': 'white',
                    },
                ],
                style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                style_cell=dict(
                    backgroundColor='rgb(50, 50, 50)',
                    color='white',
                    text_align='left',
                    font_size='.8em',
                    font_family='sans-serif',
                ),
                fill_width=False,
                editable=True,
            ),
            #  ----------------------- Interval Timers --------------------- #
            dcc.Interval(
                id='host-table-interval',
                interval=20 * 1000,  # in milliseconds
                n_intervals=0,
            ),
            dcc.Interval(
                id='log-interval',
                interval=10 * 1000,  # in milliseconds
                n_intervals=0,
            ),
            dcc.Interval(
                id='host-status-update-interval',
                interval=60 * 1000,
                n_intervals=0,
            ),
            dcc.Interval(
                id='arp-table-interval',
                interval=20 * 1000,  # in milliseconds
                n_intervals=0,
            ),
            dcc.Interval(
                id='arp-status-update-interval',
                interval=60 * 1000,
                n_intervals=0,
            ),
        ],
    ),
)
