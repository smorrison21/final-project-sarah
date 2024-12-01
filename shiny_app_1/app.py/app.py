from shiny import App, render, ui, reactive
import pandas as pd
import anywidget
from shinywidgets import render_altair, output_widget 
import altair as alt
import json
import geopandas as gpd

app_ui = ui.page_fluid(
    ui.input_select(id = 'state', 
                    label = 'Choose a state:',
                    choices = ["Alabama", "Alaska", 
                               "Arizona", "Arkansas", 
                               "California", "Colorado", 
                               "Connecticut", "Delaware", 
                               "Florida", "Georgia", "Hawaii", 
                               "Idaho", "Illinois", "Indiana", 
                               "Iowa", "Kansas", "Kentucky", 
                               "Louisiana", "Maine", "Maryland", 
                               "Massachusetts", "Michigan", 
                               "Minnesota", "Mississippi", "Missouri", 
                               "Montana", "Nebraska", "Nevada", 
                               "New Hampshire", "New Jersey", 
                               "New Mexico", "New York", 
                               "North Carolina", "North Dakota", 
                               "Ohio", "Oklahoma", "Oregon", 
                               "Pennsylvania", "Rhode Island", 
                               "South Carolina", "South Dakota", 
                               "Tennessee", "Texas", "Utah", "Vermont", 
                               "Virginia", "Washington", "West Virginia", 
                               "Wisconsin", "Wyoming"]),
    ui.input_radio_buttons(id = 'measure', 
                           label = 'Choose a measure:', 
                           choices = ["Enrollment", "Quality Standards"]),
    ui.panel_conditional(
                    "input.measure === 'Enrollment'",
                    output_widget('scatter_plot_enrollment'),
                    ui.output_table("filtered_table_enrollment"),
    ),
    ui.panel_conditional(
                    "input.measure === 'Quality Standards'",
                    output_widget('scatter_plot_qs'),
                    ui.output_table("filtered_table_qs"),
    ),
)


def server(input, output, session):
    @reactive.calc
    def full_data():
        return pd.read_csv("data/preschool_stats.csv")

    @reactive.calc
    def filtered_data_enrollment():
        # Filter data based on user input
        df = full_data()
        selected_measure = input.measure()
        selected_state = input.state()
         
        # Apply filters for state and measure type
        filtered_df = df[df["State Name"] == selected_state]

        ultra_filtered_df = filtered_df[
            filtered_df['State Name', 
                        'Year', 
                        'Total State Pre-K Spending (2023 Dollars)',
                        'Total State Pre-K Enrollment']]
        
        return ultra_filtered_df

    @reactive.calc
    def filtered_data_qs():
        # Filter data based on user input
        df = full_data()
        selected_measure = input.measure()
        selected_state = input.state()

        # Apply filters for state and measure type
        filtered_df = df[df["State Name"] == selected_state]
        
        ultra_filtered_df = filtered_df[
            filtered_df['State Name', 
                        'Year', 
                        'Total State Pre-K Spending (2023 Dollars)',
                        'percent_benchmarks']]
        
        return ultra_filtered_df

    @render.table()
    def filtered_table_enrollment():
        return filtered_data_enrollment()

    @render.table()
    def filtered_table_qs():
        return filtered_data_qs()
    
    @render_altair
    def scatter_plot_enrollment():
        e_x_s_chart = alt.Chart(filtered_data_enrollment).transform_calculate(
            SpendingInMillions='datum["Total State Pre-K Spending (2023 Dollars)"] / 1000000'
        ).mark_circle(size=60).encode(
            x=alt.X(
                'SpendingInMillions:Q',
                axis=alt.Axis(
                    format='$,.0f',  # Format with one decimal place
                    title='Total Pre-K Spending (Millions of Dollars)'
            ),
                scale=alt.Scale(
                    domain=[
                        filtered_data_enrollment['Total State Pre-K Spending (2023 Dollars)'].min() / 1000000,
                        filtered_data_enrollment['Total State Pre-K Spending (2023 Dollars)'].max() / 1000000
                    ]
                )
            ),
            y=alt.Y(
                'Total State Pre-K Enrollment:Q',
                axis=alt.Axis(title='Total  Pre-K Enrollment')
            ),
            tooltip=[
                'State Name',
                'Total State Pre-K Spending (2023 Dollars):Q',
                'Total State Pre-K Enrollment'
            ]
        ).properties(
            title=f'{input.state()} Spending vs Enrollment'
        )

        trend_line = alt.Chart(filtered_data_enrollment).transform_calculate(
            SpendingInMillions='datum["Total State Pre-K Spending (2023 Dollars)"] / 1000000'
        ).transform_regression(
            'SpendingInMillions', 'Total State Pre-K Enrollment'
        ).mark_line(color='red').encode(
            x='SpendingInMillions:Q',
            y='Total State Pre-K Enrollment:Q'
        )

        # Combine scatter plot and trend line
        enrollment_chart = (e_x_s_chart + trend_line).interactive()
       
        return enrollment_chart
    @render_altair
    def scatter_plot_qs():
        q_x_s_chart = alt.Chart(filtered_data_qs).transform_calculate(
            SpendingInMillions='datum["Total State Pre-K Spending (2023 Dollars)"] / 1000000'
        ).mark_circle(size=60).encode(
            x=alt.X(
                'SpendingInMillions:Q',
                axis=alt.Axis(
                    format='$,.0f',  # Format with one decimal place
                    title='Total Illinois Pre-K Spending (Millions of Dollars)'
                ),
                scale=alt.Scale(
                    domain=[
                        il_preschool_stats['Total State Pre-K Spending (2023 Dollars)'
                            ].min() / 1000000,
                        il_preschool_stats['Total State Pre-K Spending (2023 Dollars)'
                            ].max() / 1000000
                    ]
                )
        ),
            y=alt.Y(
                'percent_benchmarks:Q',
                axis=alt.Axis(title='Percentage of Pre-K Quality Standards Met')
                ),
            tooltip=[
                'State Name',
                'Total State Pre-K Spending (2023 Dollars):Q',
                'percent_benchmarks'
            ]
        ).properties(
            title=f'{input.state()} Spending vs Percentage of Pre-K Quality Standards Met'
        )

        trend_line = alt.Chart(filtered_data_qs).transform_calculate(
            SpendingInMillions='datum["Total State Pre-K Spending (2023 Dollars)"] / 1000000'
        ).transform_regression(
            'SpendingInMillions', 'percent_benchmarks'
        ).mark_line(color='red').encode(
            x='SpendingInMillions:Q',
            y='percent_benchmarks:Q'
        )

        # Combine scatter plot and trend line
        quality_chart = (il_q_x_s_chart + trend_line).interactive()

        return quality_chart
        
app = App(app_ui, server)
