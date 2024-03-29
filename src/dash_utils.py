import plotly.express as px
import plotly.graph_objects as go

from utils.graph_data_utils import GraphDataHandler, models
from utils.pds_utils.pds_vars import property_metrics_dict as pds_property_metrics_dict
from utils.taibi_utils.taibi_vars import property_metrics_dict as taibi_property_metrics_dict
from utils.qmood_utils.qmood_vars import property_metrics_dict as qmood_property_metrics_dict


class DashUtils:
    def __init__(self):
        self.graph_data_handler = GraphDataHandler()

    def get_reusability_per_version_figure(self):
        avg_reusability_df = self.graph_data_handler.get_average_reusability_dataframe()
        version_label_to_index_dict = self.graph_data_handler.get_project_versions_info()

        reusability_per_version_fig = px.line(avg_reusability_df, x="Version", y="Average Reusability Score",
                                              height=700,
                                              color="Reusability Model", custom_data=["Project", "Reusability Model"],
                                              facet_row="Project",
                                              category_orders={"Project": ['Atmosphere', 'Mockito', 'JUnit4']},
                                              facet_row_spacing=0.07,
                                              markers=True)
        reusability_per_version_fig.update_xaxes(showticklabels=True, row=1, tickangle=45)
        reusability_per_version_fig.update_xaxes(showticklabels=True, row=2, tickangle=45)
        reusability_per_version_fig.update_xaxes(showticklabels=True, row=3, tickangle=45)

        reusability_per_version_fig.update_layout(
            {
                'xaxis': {'tickmode': 'array',
                          'tickvals': list(version_label_to_index_dict['JUnit4'].values()),
                          'ticktext': list(version_label_to_index_dict['JUnit4'].keys())},
                'xaxis2': {'tickmode': 'array',
                           'tickvals': list(version_label_to_index_dict['Mockito'].values()),
                           'ticktext': list(version_label_to_index_dict['Mockito'].keys())},
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

    @staticmethod
    def get_bubble_chart_custom_data(model):
        custom_data = {'PDS': ['Name', 'Complexity', 'Documentation', 'Coupling', 'Cohesion'],
                       'Taibi': ['Name', 'Modularity', 'Understandability', 'Low Complexity'],
                       'QMOOD': ['Name', 'Coupling', 'Cohesion', 'Messaging', 'Design Size']}
        return custom_data[model]

    @staticmethod
    def get_model_quality_factors(model):
        quality_factors_list = {'PDS': list(map(lambda key: key.capitalize(), pds_property_metrics_dict.keys())),
                                'Taibi': list(taibi_property_metrics_dict.keys()),
                                'QMOOD': list(qmood_property_metrics_dict.keys())}
        return quality_factors_list[model]

    @staticmethod
    def get_bubble_hover_template(model):
        common_lines = [
            "<b>%{customdata[0]}</b><br>"
            "--------------------------<br>"
            "Reusability: %{y}",
            "Lines of Code: %{x}"
        ]
        hover_templates = {
            'PDS':
                "<br>".join(common_lines + [
                    "Complexity: %{customdata[1]}",
                    "Documentation: %{customdata[2]}",
                    "Coupling: %{customdata[3]}",
                    "Cohesion: %{customdata[4]}<br>",
                ]),
            'Taibi':
                "<br>".join(common_lines + [
                    "Modularity: %{customdata[1]}",
                    "Understandability: %{customdata[2]}",
                    "Low Complexity: %{customdata[3]}",
                ]),
            'QMOOD':
                "<br>".join(common_lines + [
                    "Coupling: %{customdata[1]}",
                    "Cohesion: %{customdata[2]}",
                    "Messaging: %{customdata[3]}",
                    "Design Size: %{customdata[4]}<br>",
                ])}
        return hover_templates[model]

    @staticmethod
    def get_hover_label_style():
        return dict(
            bgcolor='black',
            font_color='white',
            font_family='"Abel", "Open Sans", sans-serif'
        )

    @staticmethod
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

    def get_bubble_chart_figure(self, selected_project, selected_model, selected_version):
        class_reusability_dataframes = self.graph_data_handler.get_class_reusability_dataframes()
        selected_project_dataframe = class_reusability_dataframes[selected_model][selected_project]
        filtered_df = selected_project_dataframe[selected_project_dataframe.Version == selected_version]

        custom_data = self.get_bubble_chart_custom_data(selected_model)
        hover_template = self.get_bubble_hover_template(selected_model)

        sizeref = 2. * max(filtered_df['Lines of Code']) / (150 ** 2)

        fig = px.scatter(filtered_df, x="Lines of Code", y="Reusability Score",
                         size=filtered_df['Lines of Code'].to_list(), color='Reusability Score', hover_name="Name",
                         custom_data=custom_data,
                         height=750, color_continuous_scale='rdylgn', log_x=True)

        fig.update_traces(mode='markers', marker=dict(sizemode='area',
                                                      sizeref=sizeref, line_width=1.5),
                          hovertemplate=hover_template)

        fig.update_layout(
            title=f'<i>Project:</i> <b>{selected_project}</b> | <i>Model:</i> <b>{selected_model}</b> | <i>Version:</i> <b>{selected_version}</b>',
            title_font_size=14,
            hoverlabel=self.get_hover_label_style()
        )

        fig.update_xaxes(showspikes=False)

        fig.update_layout(transition_duration=500)

        return fig

    def get_reusability_per_number_of_classes_fig(self, selected_project, selected_version):
        reusability_per_number_of_classes_distributions = self.graph_data_handler.get_reusability_per_number_of_classes_distributions(
            selected_project, selected_version)
        fig = go.Figure()
        marker_colors = {'PDS': '#EB89B5', 'Taibi': '#330C73', 'QMOOD': '#afad3c'}

        for model in models:
            fig.add_trace(go.Histogram(
                x=reusability_per_number_of_classes_distributions[model],
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
            title=f'<i>Project:</i> <b>{selected_project}</b> | <i>Version:</i> <b>{selected_version}</b>',
            title_font_size=14,
            xaxis_title_text='Reusability Score',
            yaxis_title_text='Number of Classes',
            bargap=0.01,
            bargroupgap=0.01,
            hoverlabel={'font_color': 'white', "bordercolor": 'white',
                        "font_family": '"Abel", "Open Sans", sans-serif'}
        )
        return fig

    def get_quality_factors_evolution_fig(self, selected_project, selected_model):
        plot_dataframe = self.graph_data_handler.get_average_quality_factors_df(selected_project, selected_model)
        fig = px.line(plot_dataframe, x='Version', y=self.get_model_quality_factors(selected_model) + ['Reusability Score'],
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
            title=f'<i>Project:</i> <b>{selected_project}</b> | <i>Model:</i> <b>{selected_model}</b>',
            title_font_size=14,
            yaxis_title_text='Quality Factor Score',
            legend_title_text='Quality Factor',
            hoverlabel={'font_color': 'white', "bordercolor": 'white',
                        "font_family": '"Abel", "Open Sans", sans-serif'}
        )
        return fig

    def get_maintainability_complexity_documentation_figure(self, selected_project):
        plot_df = self.graph_data_handler.get_average_maintainability_complexity_documentation(selected_project)
        reusability_per_version_fig = px.line(plot_df, x="Version",
                                              y=['Reusability', 'Maintainability', 'Complexity', 'Documentation'],
                                              height=400,
                                              facet_col="Model", facet_row_spacing=0.07, markers=True)
        reusability_per_version_fig.update_layout(
            {
                'title': f'<i>Project:</i> <b>{selected_project}</b>',
                "title_font_size": 14,
                'yaxis': {'title': {'text': 'Quality Attribute Score'}},
                'xaxis2': {'title': {'text': ''}},
                'xaxis3': {'title': {'text': ''}},
                'hoverlabel': {'font_color': 'white', "bordercolor": 'white',
                               "font_family": '"Abel", "Open Sans", sans-serif'},
                "legend": {
                    'title': 'Quality Attribute',
                    'orientation': "h", 'yanchor': 'bottom', 'xanchor': 'right', 'y': 1.1, 'x': 1}
            }
        )
        return reusability_per_version_fig
