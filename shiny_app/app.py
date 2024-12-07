from shiny import App, render, ui, reactive
import pandas as pd
import altair as alt
from shinywidgets import render_altair, output_widget

enrollment_1 = ui.layout_columns(
                ui.card(
                    ui.card_header("Plot"),
                    ui.card_body(
                        output_widget('scatter_plot_enrollment')
                    ),
                ),
                ui.card(
                    ui.card_header("Table"),
                    ui.card_body(
                        ui.output_table("enrollment_table_page1")
                    ),
                )
            )
standards_1 = ui.layout_columns(
                ui.card(
                    ui.card_header("Plot"),
                    ui.card_body(
                        output_widget('scatter_plot_qs')
                    ),
                ),
                ui.card(
                    ui.card_header("Table"),
                    ui.card_body(
                        ui.output_table("qs_table_page1")
                    ),
                )
            )

enrollment_2 = ui.layout_columns(
                ui.card(
                    ui.card_header("Map of State Pre-K Enrollment Trends"),
                    ui.card_body(
                        output_widget('choropleth_enrollment')
                    ),
                ),
                ui.card(
                    ui.card_header("Table"),
                    ui.card_body(
                        ui.output_table("enrollment_table_page2")
                    ),
                )
            )

standards_2 = ui.layout_columns(
                ui.card(
                    ui.card_header("Map of State Pre-K Quality Standards Met Over Time"),
                    ui.card_body(
                        output_widget('choropleth_qs')
                    ),
                ),
                ui.card(
                    ui.card_header("Table"),
                    ui.card_body(
                        ui.output_table("qs_table_page2")
                    ),
                )
            )

spending_2 = ui.layout_columns(
                ui.card(
                    ui.card_header("Map of State Pre-K Spending Per Child Over Time"),
                    ui.card_body(
                        output_widget('choropleth_spending')
                    ),
                ),
                ui.card(
                    ui.card_header("Table"),
                    ui.card_body(
                        ui.output_table("spending_table_page2")
                    ),
                )
            )
# Page 1 UI
page1 = ui.page_fluid(
    ui.card(
        ui.card_header("Selection"
        ),
        ui.card_body(
            ui.input_select(
                id='state',
                label='Choose a state:',
                choices=[
                    "Alabama", "Alaska", "Arizona", "Arkansas", 
                    "California", "Colorado", "Connecticut", "Delaware", 
                    "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", 
                    "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", 
                    "Maine", "Maryland", "Massachusetts", "Michigan", 
                    "Minnesota", "Mississippi", "Missouri", "Montana", 
                    "Nebraska", "Nevada", "New Hampshire", "New Jersey", 
                    "New Mexico", "New York", "North Carolina", "North Dakota", 
                    "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", 
                    "South Carolina", "South Dakota", "Tennessee", "Texas", 
                    "Utah", "Vermont", "Virginia", "Washington", "West Virginia", 
                    "Wisconsin", "Wyoming"
                ]
            ),
            ui.input_radio_buttons(
                id='measure1',
                label='Choose a measure:',
                choices=["Enrollment", "Quality Standards"]
            )
        )
    ),
    ui.panel_conditional("input.measure1 === 'Enrollment'", enrollment_1),
    ui.panel_conditional("input.measure1 === 'Quality Standards'", standards_1)
)


# Page 2 UI
page2 = ui.page_fluid(
            ui.card(
            ui.card_header("Selection"
            ),
            ui.card_body(
                ui.input_select(
                    id = 'year', 
                    label = 'Choose a year:',
                    choices = ["2002", "2003", "2004", "2005", "2006", 
                        "2007", "2008", "2009", "2010", "2011", "2012", 
                        "2013", "2014","2015", "2016", "2017", "2018", 
                        "2019", "2020", "2021", "2022", "2023"]),
            ui.input_radio_buttons(
                id = 'measure2', 
                label = 'Choose a measure:', 
                           choices = ["Enrollment", "Quality Standards", "Spending"]
            )
        )
    ),
    ui.panel_conditional("input.measure2 === 'Enrollment'", enrollment_2),
    ui.panel_conditional("input.measure2 === 'Quality Standards'", standards_2),
    ui.panel_conditional("input.measure2 === 'Spending'", spending_2)
)

# Main UI
app_ui = ui.page_navbar(
    ui.nav_spacer(),
    ui.nav_panel("Page 1", page1),
    ui.nav_panel("Page 2", page2),
    title="State Pre-K Trends",
)

# Page 1 Server
def server(input, output, session):
    @reactive.calc
    def full_data1():
        return pd.read_csv("data/preschool_stats.csv")

    @reactive.calc
    def enrollment_data_1():
        # Filter data based on user input
        df = full_data1()
        print("Columns in Data:", df.columns)
        print(df.head())
        selected_measure = input.measure1()
        selected_state = input.state()
         
        # Apply filters for state and measure type
        filtered_df = df[df["State Name"] == selected_state]

        ultra_filtered_df = filtered_df[
            ['State Name', 
            'Year', 
            'Total State Pre-K Spending (2023 Dollars)',
            'Total State Pre-K Enrollment']]
        
        return ultra_filtered_df

    @reactive.calc
    def qs_data_1():
        # Filter data based on user input
        df = full_data1()
        selected_measure = input.measure1()
        selected_state = input.state()

        # Apply filters for state and measure type
        filtered_df = df[df["State Name"] == selected_state]
        
        ultra_filtered_df = filtered_df[
            ['State Name', 
            'Year', 
            'Total State Pre-K Spending (2023 Dollars)',
            'percentage']]
        
        return ultra_filtered_df

    @render.table()
    def enrollment_table_page1():
        return enrollment_data_1()

    @render.table()
    def qs_table_page1():
        return qs_data_1()
    
    @render_altair
    def scatter_plot_enrollment():
        e_x_s_chart = alt.Chart(enrollment_data_1()).transform_calculate(
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
                        enrollment_data_1()['Total State Pre-K Spending (2023 Dollars)'].min() / 1000000,
                        enrollment_data_1()['Total State Pre-K Spending (2023 Dollars)'].max() / 1000000
                    ]
                )
            ),
            y=alt.Y(
                'Total State Pre-K Enrollment:Q',
                axis=alt.Axis(title='Total Pre-K Enrollment')
            ),
            tooltip=[
                'State Name',
                'Total State Pre-K Spending (2023 Dollars):Q',
                'Total State Pre-K Enrollment'
            ]
        ).properties(
            title=f'{input.state()} Spending vs Enrollment'
        )

        trend_line = alt.Chart(enrollment_data_1()).transform_calculate(
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
        q_x_s_chart = alt.Chart(qs_data_1()).transform_calculate(
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
                        qs_data_1()['Total State Pre-K Spending (2023 Dollars)'
                            ].min() / 1000000,
                        qs_data_1()['Total State Pre-K Spending (2023 Dollars)'
                            ].max() / 1000000
                    ]
                )
        ),
            y=alt.Y(
                'percentage:Q',
                axis=alt.Axis(title='Percentage of Pre-K Quality Standards Met')
                ),
            tooltip=[
                'State Name',
                'Total State Pre-K Spending (2023 Dollars):Q',
                'percentage'
            ]
        ).properties(
            title=f'{input.state()} Spending vs Percentage of Pre-K Quality Standards Met'
        )

        trend_line = alt.Chart(qs_data_1()).transform_calculate(
            SpendingInMillions='datum["Total State Pre-K Spending (2023 Dollars)"] / 1000000'
        ).transform_regression(
            'SpendingInMillions', 'percentage'
        ).mark_line(color='red').encode(
            x='SpendingInMillions:Q',
            y='percentage:Q'
        )

        # Combine scatter plot and trend line
        quality_chart = (q_x_s_chart + trend_line).interactive()

        return quality_chart

# Page 2 Reactive Data
    @reactive.calc
    def full_data2():
        return pd.read_csv("data/preschool_geometry.csv")

    @reactive.calc
    def enrollment_data_2():
        # Filter data based on user input
        df = full_data2()
        selected_measure = input.measure2()
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
    def qs_data_2():
        # Filter data based on user input
        df = full_data2()
        selected_measure = input.measure2()
        selected_year = input.year()

        # Apply filters for state and measure type
        filtered_df = df[df["Year"] == selected_year]
        
        ultra_filtered_df = filtered_df[['State Name', 'Year', 'percentage','id']]
        
        return ultra_filtered_df

    @reactive.calc
    def spending_data_2():
        # Filter data based on user input
        df = full_data2()
        selected_measure = input.measure2()
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
    def enrollment_table_page2():
        return enrollment_data_2()

    @render.table()
    def qs_table_page2():
        return qs_data_2()
    
    @render.table()
    def spending_table_page2():
        return spending_data_2()

    @render_altair
    def choropleth_spending(): 
        from vega_datasets import data

        states = alt.topo_feature(data.us_10m.url, 'states')

        spending_chart = alt.Chart(states).mark_geoshape().encode(
            color=alt.Color('State Spending per Child (2023 Dollars):Q')
        ).transform_lookup(
            lookup='id',
            from_=alt.LookupData(spending_data_2(), 'id', ['State Spending per Child (2023 Dollars)', 'State Name'])
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
            from_=alt.LookupData(enrollment_data_2(), 'id', list(enrollment_data_2().columns))
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
            from_=alt.LookupData(qs_data_2(), 'id', list(qs_data_2().columns))
        ).properties(
            width=500,
            height=300
        ).project(
            type='albersUsa'
        )
        return qs_chart

app = App(app_ui, server)

