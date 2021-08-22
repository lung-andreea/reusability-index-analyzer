import plotly.express as px
import plotly.graph_objects as go

from utils.graph_data_utils import get_average_reusability_dataframe, get_project_versions_info, \
    get_class_reusability_dataframes, get_reusability_per_number_of_classes_distributions, models, \
    get_average_quality_factors_df
from utils.pds_utils.pds_vars import property_metrics_dict


def get_reusability_per_version_figure():
    avg_reusability_df = get_average_reusability_dataframe()
    version_label_to_index_dict = get_project_versions_info()

    reusability_per_version_fig = px.line(avg_reusability_df, x="Version", y="Average Reusability Score", height=500,
                                          color="Reusability Model", custom_data=["Project", "Reusability Model"],
                                          facet_row="Project", facet_row_spacing=0.07,
                                          markers=True)
    reusability_per_version_fig.update_xaxes(showticklabels=True, row=1)
    reusability_per_version_fig.update_xaxes(showticklabels=True, row=2)
    reusability_per_version_fig.update_xaxes(showticklabels=True, row=3)
    reusability_per_version_fig.update_layout(
        {
            'xaxis': {'tickmode': 'array',
                      'tickvals': list(version_label_to_index_dict['Mockito'].values()),
                      'ticktext': list(version_label_to_index_dict['Mockito'].keys())},
            'xaxis2': {'tickmode': 'array',
                       'tickvals': list(version_label_to_index_dict['JUnit4'].values()),
                       'ticktext': list(version_label_to_index_dict['JUnit4'].keys())},
            'xaxis3': {'tickmode': 'array',
                       'tickvals': list(version_label_to_index_dict['Atmosphere'].values()),
                       'ticktext': list(version_label_to_index_dict['Atmosphere'].keys())},
            'yaxis': {'title': {'text': ''}},
            'yaxis3': {'title': {'text': ''}},
            'hoverlabel': {'font_color': 'white', "bordercolor": 'white',
                           "font_family": '"Abel", "Open Sans", sans-serif'}
        }
    )
    return reusability_per_version_fig


def get_bubble_chart_custom_data(model):
    custom_data = {'PDS': ['Name', 'Complexity', 'Documentation', 'Coupling', 'Cohesion'], 'Taibi': [], 'QMOOD': []}
    return custom_data[model]


def get_model_quality_factors(model):
    quality_factors_list = {'PDS': list(map(lambda key: key.capitalize(), property_metrics_dict.keys())), 'Taibi': [],
                            'QMOOD': []}
    return quality_factors_list[model]


def get_bubble_hover_template(model):
    hover_templates = {'PDS': "<br>".join([
        "<b>%{customdata[0]}</b><br>"
        "--------------------------<br>"
        "Reusability: %{y}",
        "Lines of Code: %{x}",
        "Complexity: %{customdata[1]}",
        "Documentation: %{customdata[2]}",
        "Coupling: %{customdata[3]}",
        "Cohesion: %{customdata[4]}<br>",
    ]), 'Taibi': None, 'QMOOD': None}
    return hover_templates[model]


def get_hover_label_style():
    return dict(
        bgcolor='black',
        font_color='white',
        font_family='"Abel", "Open Sans", sans-serif'
    )


def get_empty_text_figure():
    fig = go.Figure()
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        paper_bgcolor='white',
        plot_bgcolor='white',
        annotations=[
            {
                "text": "No data to display. <br>Select a point in the <b>Average Reusability per Version</b> <br>graph to see data "
                        "showing up.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 15
                },
                "bgcolor": '#FFFFFF'
            }
        ]
    )
    return fig


def get_bubble_chart_figure(selected_project, selected_model, selected_version):
    class_reusability_dataframes = get_class_reusability_dataframes()
    selected_project_dataframe = class_reusability_dataframes[selected_model][selected_project]
    filtered_df = selected_project_dataframe[selected_project_dataframe.Version == selected_version]

    custom_data = get_bubble_chart_custom_data(selected_model)
    hover_template = get_bubble_hover_template(selected_model)

    sizeref = 2. * max(filtered_df['Lines of Code']) / (150 ** 2)

    fig = px.scatter(filtered_df, x="Lines of Code", y="Reusability Score",
                     size=filtered_df['Lines of Code'].to_list(), color='Reusability Score', hover_name="Name",
                     custom_data=custom_data,
                     height=750, color_continuous_scale='rdylgn', log_x=True)

    fig.update_traces(mode='markers', marker=dict(sizemode='area',
                                                  sizeref=sizeref, line_width=1.5),
                      hovertemplate=hover_template)

    fig.update_layout(
        hoverlabel=get_hover_label_style()
    )

    fig.update_xaxes(showspikes=False)

    fig.update_layout(transition_duration=500)

    return fig


def get_reusability_per_number_of_classes_fig(selected_project, selected_version):
    reusability_per_number_of_classes_distributions = get_reusability_per_number_of_classes_distributions(
        selected_project, selected_version)
    fig = go.Figure()
    marker_colors = {'PDS': '#EB89B5', 'Taibi': '#330C73', 'QMOOD': '#afad3c'}

    for model in models:
        fig.add_trace(go.Histogram(
            x=reusability_per_number_of_classes_distributions['PDS'],
            name=model,
            histfunc='count',
            xbins=dict(
                start=0.0,
                end=1.0,
                size=0.02
            ),
            hovertemplate='<br>'.join(["Reusability: %{x}",
                                       "Number of Classes: %{y}",
                                       f'Model: {model}']),
            marker_color=marker_colors[model],
            opacity=0.75
        ))
    fig.update_layout(
        xaxis_title_text='Reusability Score',
        yaxis_title_text='Number of Classes',
        bargap=0.2,
        bargroupgap=0.1,
        hoverlabel={'font_color': 'white', "bordercolor": 'white',
                    "font_family": '"Abel", "Open Sans", sans-serif'}
    )
    return fig


def get_quality_factors_evolution_fig(selected_project, selected_model):
    plot_dataframe = get_average_quality_factors_df(selected_project, selected_model)
    fig = px.line(plot_dataframe, x='Version', y=get_model_quality_factors(selected_model) + ['Reusability Score'],
                  color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_traces(mode='lines+markers', hovertemplate='<br>'.join(["Factor: %{data.name}",
                                                                       "Version: %{x}",
                                                                       'Factor value: %{y}', '<extra></extra>']))
    fig.add_annotation(x=plot_dataframe['Version'].get(0), y=plot_dataframe['Reusability Score'].get(0),
                       text="Reusability",
                       showarrow=False,
                       yshift=10,
                       xshift=30)
    fig.update_layout(
        yaxis_title_text='Quality Factor Score',
        legend_title_text='Quality Factor',
        hoverlabel={'font_color': 'white', "bordercolor": 'white',
                    "font_family": '"Abel", "Open Sans", sans-serif'}
    )
    return fig
