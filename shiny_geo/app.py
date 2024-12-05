from shiny import App, render, ui

from shiny import App, render, ui, reactive
import pandas as pd
import anywidget
from shinywidgets import render_altair, output_widget 
import altair as alt
import json
import geopandas as gpd

app_ui = ui.page_fluid(
    ui.input_select(id = 'year', 
                    label = 'Choose a year:',
                    choices = ["2002", "2003", "2004", "2005", "2006", 
                        "2007", "2008", "2009", "2010", "2011", "2012", 
                        "2013", "2014","2015", "2016", "2017", "2018", 
                        "2019", "2020", "2021", "2022", "2023"]),
    ui.input_radio_buttons(id = 'measure', 
                           label = 'Choose a measure:', 
                           choices = ["Enrollment", "Quality Standards", "Spending"]),
    ui.panel_conditional(
                    "input.measure === 'Enrollment'",
                    output_widget('choropleth_enrollment'),
                    ui.output_table("filtered_table_enrollment"),
    ),
    ui.panel_conditional(
                    "input.measure === 'Quality Standards'",
                    output_widget('choropleth_qs'),
                    ui.output_table("filtered_table_qs"),
    ),
    ui.panel_conditional(
                    "input.measure === 'Spending'",
                    output_widget('choropleth_spending'),
                    ui.output_table("filtered_table_spending"),
    ),
)

def server(input, output, session):
    @reactive.calc
    def full_data():
        return pd.read_csv(".venv/preschool_geometry.csv")

    @reactive.calc
    def filtered_data_enrollment():
        # Filter data based on user input
        df = full_data()
        selected_measure = input.measure()
        selected_year = input.year()
        
        df['Year'] = df['Year'].astype(str)
        
        print("Selected Year:", selected_year)
        print(type(input.year()), input.year())
        print(df.head())

        # Apply filters for year
        filtered_df = df[df["Year"] == selected_year]

        print("Filtered Data:", filtered_df.head())

        ultra_filtered_df = filtered_df[
            ['State Name', 
            'Year', 
            'Percentage of 4-year-olds Enrolled in State Pre-K',
            'id']]
        
        return ultra_filtered_df

    @reactive.calc
    def filtered_data_qs():
        # Filter data based on user input
        df = full_data()
        selected_measure = input.measure()
        selected_year = input.year()

        # Apply filters for state and measure type
        filtered_df = df[df["Year"] == selected_year]
        
        ultra_filtered_df = filtered_df[['State Name', 'Year', 'percentage','id']]
        
        return ultra_filtered_df

    @reactive.calc
    def filtered_data_spending():
        # Filter data based on user input
        df = full_data()
        selected_measure = input.measure()
        selected_year = input.year()
        
        df['Year'] = df['Year'].astype(str)
        
        # Apply filters for state and measure type
        filtered_df = df[df["Year"] == selected_year]
        
        ultra_filtered_df = filtered_df[
            ['State Name', 
            'Year', 
            'State Spending per Child (2023 Dollars)',
            'id']]
        ultra_filtered_df['State Spending per Child (2023 Dollars)'] = ultra_filtered_df['State Spending per Child (2023 Dollars)'].astype(int)
        return ultra_filtered_df

    @render.table()
    def filtered_table_enrollment():
        return filtered_data_enrollment()

    @render.table()
    def filtered_table_qs():
        return filtered_data_qs()
    
    @render.table()
    def filtered_table_spending():
        return filtered_data_spending()

    @render_altair
    def choropleth_spending(): 
        from vega_datasets import data

        states = alt.topo_feature(data.us_10m.url, 'states')

        spending_chart = alt.Chart(states).mark_geoshape().encode(
            color=alt.Color('State Spending per Child (2023 Dollars):Q')
        ).transform_lookup(
            lookup='id',
            from_=alt.LookupData(filtered_data_spending(), 'id', ['State Spending per Child (2023 Dollars)', 'State Name'])
        ).properties(
            width=500,
            height=300
        ).project(
            type='albersUsa'
        )
        return spending_chart

    @render_altair
    def choropleth_enrollment(): 
        from vega_datasets import data

        states = alt.topo_feature(data.us_10m.url, 'states')

        enrollment_chart = alt.Chart(states).mark_geoshape().encode(
            color='Percentage of 4-year-olds Enrolled in State Pre-K:Q'
        ).transform_lookup(
            lookup='id',
            from_=alt.LookupData(filtered_data_enrollment(), 'id', list(filtered_data_enrollment().columns))
        ).properties(
            width=500,
            height=300
        ).project(
            type='albersUsa'
        )
        return enrollment_chart

    @render_altair
    def choropleth_qs(): 
        from vega_datasets import data

        states = alt.topo_feature(data.us_10m.url, 'states')

        qs_chart = alt.Chart(states).mark_geoshape().encode(
            color='percentage:Q'
        ).transform_lookup(
            lookup='id',
            from_=alt.LookupData(filtered_data_qs(), 'id', list(filtered_data_qs().columns))
        ).properties(
            width=500,
            height=300
        ).project(
            type='albersUsa'
        )
        return qs_chart

app = App(app_ui, server)
