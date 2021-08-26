"""
Lung Andreea Cristina
Created: 01/05/2021
------------
Dissertation project
Re-usability index analyzer
"""
# -*- coding: utf-8 -*-

# Run this app with `python main.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from dash_utils import get_project_versions_info, get_reusability_per_version_figure, \
    get_empty_text_figure, get_bubble_chart_figure, get_reusability_per_number_of_classes_fig, \
    get_quality_factors_evolution_fig
from utils.graph_data_utils import get_selected_version_for_project, get_selected_version_index, \
    get_min_max_average_reusability

external_stylesheets = ['https://fonts.googleapis.com/css?family=Nunito:400,700',
                        'https://fonts.googleapis.com/css?family=Abel']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

version_info = get_project_versions_info()
reusability_per_version_fig = get_reusability_per_version_figure()


def get_version_slider(selected_project, selected_version):
    return dcc.Slider(
        id='version-slider',
        min=0,
        max=len(version_info[selected_project]) - 1,
        value=get_selected_version_index(selected_project, selected_version),
        marks={index: {'label': list(version_info[selected_project].keys())[index],
                       'style': {"transform": "rotate(45deg)"}} for index in
               range(len(version_info[selected_project]))},
        step=None
    )


app.layout = html.Div(className='app-container', children=[
    html.Div(className='app-header', children=[
        html.H4(className='align-center app-title', children='Reusability Analytics Dashboard'),

        html.Div(
            className='align-center header-description', children='''
        A series of interactive graphs to track reusability evolution over several versions of software.
        '''),
    ]),

    html.Div(className='info-tiles-section', children=[
        html.Div(className='white-card info-tile', children=[
            html.Div(className='white-card-header info-tile-header', children='Average Reusability'),
            html.Div(id='average-reusability-tile', className='white-card-body info-tile-body', children='-')
        ]),
        html.Div(className='white-card info-tile', children=[
            html.Div(className='white-card-header info-tile-header', children='Lowest Reusability'),
            html.Div(id='lowest-reusability-tile', className='white-card-body info-tile-body', children='-')
        ]),
        html.Div(className='white-card info-tile', children=[
            html.Div(className='white-card-header info-tile-header', children='Highest Reusability'),
            html.Div(id='highest-reusability-tile', className='white-card-body info-tile-body', children='-')
        ])
    ]),

    html.Div(className='selected-text-info', children=[
        html.P(className='selected-text-pill',
               children=['Selected Project: ',
                         html.Span(id='selected-project', className='bold-text', children='-')]),
        html.P(className='selected-text-pill',
               children=['Selected Model: ',
                         html.Span(id='selected-model', className='bold-text', children='-')]),
        html.P(className='selected-text-pill',
               children=['Selected Version ',
                         html.Span(id='selected-version', className='bold-text', children='-')])
    ]),

    html.Div(className='reusability-analysis-section', children=[
        html.Div(className='white-card',
                 children=[
                     html.Div(className='white-card-header', children='Reusability Distribution per Number of Classes'),
                     html.Div(className='white-card-body', children=[
                         dcc.Graph(id='reusability-per-number-of-classes', figure=get_empty_text_figure())])]),
        html.Div(className='white-card',
                 children=[
                     html.Div(className='white-card-header', children='Reusability vs Quality Factors Evolution'),
                     html.Div(className='white-card-body', children=[
                         dcc.Graph(id='reusability-vs-quality-factors', figure=get_empty_text_figure())])]),
    ]),

    html.Div(className='white-card', children=[
        html.Div(className='white-card-header', children='Average Reusability per Version Evolution'),
        html.Div(className='white-card-body', children=[
            dcc.Graph(
                id='reusability-per-version-graph',
                figure=reusability_per_version_fig
            )
        ])
    ]),

    html.Div(className='white-card', children=[
        html.Div(className='white-card-header', children='Class Reusability Overview'),
        html.Div(className='reusability-overview-section white-card-body', children=[
            dcc.Graph(id='bubble-chart', figure=get_empty_text_figure()),
            html.Div(id='version-slider-container')
        ])
    ]),
])


@app.callback(
    Output('version-slider-container', 'children'),
    Input('reusability-per-version-graph', 'clickData'),
    prevent_initial_call=True)
def show_version_slider(click_data):
    point_data = click_data['points'][0]
    selected_project = point_data['customdata'][0]
    return get_version_slider(selected_project, point_data['x'])


@app.callback(
    Output('selected-project', 'children'),
    Output('selected-model', 'children'),
    Output('selected-version', 'children'),
    Output('bubble-chart', 'figure'),
    Output('lowest-reusability-tile', 'children'),
    Output('highest-reusability-tile', 'children'),
    Output('average-reusability-tile', 'children'),
    Output('reusability-per-number-of-classes', 'figure'),
    Output('reusability-vs-quality-factors', 'figure'),
    Input('reusability-per-version-graph', 'clickData'),
    Input('version-slider-container', 'children'),
    Input('version-slider', 'value'),
    prevent_initial_call=True)
def update_data_on_point_select(click_data, version_slider_children, version_slider_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    selected_version_index = version_slider_value or version_slider_children['props']['value']

    point_data = click_data['points'][0]
    selected_project = point_data['customdata'][0]
    selected_model = point_data['customdata'][1]

    if trigger_id == 'reusability-per-version-graph':
        version_number = point_data['x']
        version_index = None
    else:
        version_number = None
        version_index = selected_version_index

    selected_version_label = get_selected_version_for_project(selected_project, version_number=version_number,
                                                              version_index=version_index)
    bubble_chart_figure = get_bubble_chart_figure(selected_project, selected_model, selected_version_label)

    min, max, average = get_min_max_average_reusability(selected_project, selected_model, selected_version_label)

    reusability_per_number_of_classes_fig = get_reusability_per_number_of_classes_fig(selected_project,
                                                                                      selected_version_label)

    reusability_vs_quality_factors_fig = get_quality_factors_evolution_fig(selected_project, selected_model)

    return selected_project, selected_model, selected_version_label, bubble_chart_figure, min, max, average, \
           reusability_per_number_of_classes_fig, reusability_vs_quality_factors_fig


if __name__ == '__main__':
    app.run_server(debug=True)
