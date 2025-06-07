import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import io
import warnings

warnings.filterwarnings('ignore')
pd.set_option('display.max_rows', 100)

@st.cache_data
def load_all_data():
    covid_19_confirmed_dataset_path = "data/covid_19_confirmed_v1_lyst1747728690432.csv"
    covid_19_deaths_dataset_path = "data/covid_19_deaths_v1_lyst1747728711771.csv"
    covid_19_recovered_dataset_path = "data/covid_19_recovered_v1_lyst1747728719904.csv"

    confirmed = pd.read_csv(covid_19_confirmed_dataset_path)
    deaths_raw = pd.read_csv(covid_19_deaths_dataset_path)
    recovered_raw = pd.read_csv(covid_19_recovered_dataset_path)

    deaths = deaths_raw.copy()
    deaths.columns = [column for column in deaths.iloc[0]]
    deaths = deaths[1:].reset_index(drop=True)
    recovered = recovered_raw.copy()
    recovered.columns = [column for column in recovered.iloc[0]]
    recovered = recovered[1:].reset_index(drop=True)

    for df in [confirmed, deaths, recovered]:
        for col in df.columns[4:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    deaths_processed = deaths.copy()
    for cols in deaths_processed.columns[4:]:
        deaths_processed[cols] = deaths_processed[cols].astype('Int64')
    for col in ['Lat', 'Long']:
        deaths_processed[col] = pd.to_numeric(deaths_processed[col], errors='coerce')
    deaths = deaths_processed
    
    recovered_processed = recovered.copy()
    for col in recovered_processed.columns[4:]:
        recovered_processed[col] = recovered_processed[col].astype('Int64')
    for cols in ('Lat', 'Long'):
        recovered_processed[cols] = pd.to_numeric(recovered_processed[cols], errors='coerce')
    recovered = recovered_processed

    for df in [confirmed, deaths, recovered]:
        df[['Lat', 'Long']] = df[['Lat', 'Long']].ffill()
        df[df.columns[4:]] = df[df.columns[4:]].ffill(axis=1)
        df['Province/State'] = df['Province/State'].fillna('All Provinces')

    confirmed_long = pd.melt(frame=confirmed, id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'], var_name='Date', value_name='confirmed')
    deaths_long = pd.melt(frame=deaths, id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'], var_name='Date', value_name='deaths')
    recovered_long = pd.melt(frame=recovered, id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'], var_name='Date', value_name='recovered')
    for df in [confirmed_long, deaths_long, recovered_long]:
        df['Date'] = pd.to_datetime(df['Date'])
    
    merged_confirm_deaths = pd.merge(left=confirmed_long.drop(['Lat', 'Long'], axis=1), right=deaths_long.drop(['Lat', 'Long'], axis=1), on=['Country/Region', 'Province/State', 'Date'], how='outer')
    merged_confirm_deaths_recovered = pd.merge(left=merged_confirm_deaths, right=recovered_long.drop(['Lat', 'Long'], axis=1), on=['Country/Region', 'Province/State', 'Date'], how='outer')
    for col in ['confirmed', 'deaths', 'recovered']:
        merged_confirm_deaths_recovered[col] = merged_confirm_deaths_recovered[col].fillna(0).astype('Int64')
    
    grouped_merged_data = merged_confirm_deaths_recovered.groupby(['Country/Region', 'Date'])[['confirmed', 'deaths', 'recovered']].sum().reset_index()
    grouped_merged_data = grouped_merged_data.sort_values(by=['Country/Region', 'Date'])
    grouped_merged_data['daily_confirmed'] = grouped_merged_data.groupby(['Country/Region'])['confirmed'].diff().fillna(grouped_merged_data['confirmed'])
    grouped_merged_data['daily_deaths'] = grouped_merged_data.groupby(['Country/Region'])['deaths'].diff().fillna(grouped_merged_data['deaths'])
    grouped_merged_data['daily_recovered'] = grouped_merged_data.groupby(['Country/Region'])['recovered'].diff().fillna(grouped_merged_data['recovered'])
    for col in ['daily_confirmed', 'daily_deaths', 'daily_recovered']:
        grouped_merged_data[col] = grouped_merged_data[col].astype('Int64')
    grouped_merged_data['Month-Year'] = grouped_merged_data['Date'].dt.to_period('M')

    return confirmed, deaths, recovered, grouped_merged_data

def millions_formatter(x, pos):
    return f'{x / 1e6:.0f}M'

def readable_formatter(x, pos):
    if x >= 1e6:
        return f'{x / 1e6:.1f}M'
    elif x >= 1e3:
        return f'{x / 1e3:.0f}K'
    else:
        return f'{x:,.0f}'

st.set_page_config(layout="wide")
st.title("COVID-19 Case Study Interactive Dashboard")

confirmed, deaths, recovered, grouped_merged_data = load_all_data()

st.sidebar.title("Case Study Questions")
question_choice = st.sidebar.selectbox(
    "Select a Question to View:",
    [
        "Q1.1: Data Loading",
        "Q2.1: Data Structure",
        "Q2.2: Top Countries Plot",
        "Q2.3: China Plot",
        "Q3.1 & Q4.1: Data Cleaning",
        "Q5.1: Peak Daily Cases",
        "Q5.2: Recovery Rate Comparison",
        "Q5.3: Canada Death Rate Distribution",
        "Q6.1-Q6.4: Data Transformation",
        "Q7.1-Q7.3: Data Merging & Monthly Analysis",
        "Q8.1: 2020 Death Rate Analysis",
        "Q8.2: South Africa Recoveries vs. Deaths",
        "Q8.3: US Monthly Recovery Ratio"
    ]
)

st.sidebar.header("Plotting Options")
dark_mode = st.sidebar.checkbox("Use Dark Mode for Plots", value=True)

st.header(f"Analysis for {question_choice.split(':')[0]}")
st.subheader(f"_{question_choice.split(':')[1].strip()}_")
st.markdown("---")

if question_choice == "Q1.1: Data Loading":
    st.markdown("The three datasets (`confirmed`, `deaths`, `recovered`) were loaded into pandas DataFrames.")
    st.write("First 5 rows of **Confirmed** dataset:")
    st.dataframe(confirmed.head())
    st.write("First 5 rows of **Deaths** dataset (after header correction):")
    st.dataframe(deaths.head())
    st.write("First 5 rows of **Recovered** dataset (after header correction):")
    st.dataframe(recovered.head())

elif question_choice == "Q2.1: Data Structure":
    st.markdown("The structure of each dataset was explored using `.info()` to check rows, columns, and data types.")
    for name, df in [('Confirmed', confirmed), ('Deaths', deaths), ('Recovered', recovered)]:
        st.write(f"**{name} DataFrame Info:**")
        buffer = io.StringIO()
        df.info(buf=buffer)
        info_string = buffer.getvalue()
        st.text(info_string)

elif question_choice == "Q2.2: Top Countries Plot":
    st.markdown("Cumulative confirmed cases are plotted over time for the top N countries. Use the slider to change the number of countries shown.")
    top_n = st.slider("Select number of top countries:", 3, 20, 5)
    
    top_n_countries = confirmed.drop(['Lat','Long', 'Province/State'], axis=1, errors='ignore').groupby('Country/Region').sum().sort_values(by='5/29/21', ascending=False).T
    top_n_countries.index = pd.to_datetime(top_n_countries.index)

    if dark_mode:
        plt.style.use('dark_background')
        text_color = 'white'
    else:
        plt.style.use('fivethirtyeight')
        text_color = '#333333'

    fig, ax = plt.subplots(figsize=(12, 8))
    top_n_countries.iloc[:, :top_n].plot(kind='line', ax=ax, linewidth=2.5)

    ax.set_title(f'Pandemic Trajectory for Top {top_n} Countries', loc='left', fontsize=18, fontweight='bold', color=text_color)
    ax.text(x=ax.get_xlim()[0], y=ax.get_ylim()[1]*1.07, s='Cumulative Confirmed COVID-19 Cases', fontsize=14, va='bottom', color=text_color)
    
    ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    ax.set_xlabel('Date')
    ax.set_ylabel('Cumulative Cases (in Millions)')
    ax.text(x=ax.get_xlim()[1], y=ax.get_ylim()[0] - ax.get_ylim()[1]*0.18, s='Source: JHU CSSE COVID-19 Data', ha='right', style='italic', color='grey')
    
    legend = ax.legend(title='Country/Region')
    if dark_mode:
        legend.get_frame().set_facecolor('black')
        for text in legend.get_texts():
            text.set_color(text_color)
        legend.get_title().set_color(text_color)

    plt.tight_layout()
    st.pyplot(fig)

elif question_choice == "Q2.3: China Plot":
    st.markdown("A specific plot showing the evolution of cumulative confirmed cases over time for China.")
    top_n_countries = confirmed.drop(['Lat','Long', 'Province/State'], axis=1, errors='ignore').groupby('Country/Region').sum().sort_values(by='5/29/21', ascending=False).T
    top_n_countries.index = pd.to_datetime(top_n_countries.index)
    
    if dark_mode:
        plt.style.use('dark_background')
        text_color = 'white'
        arrow_color = 'white'
    else:
        plt.style.use('fivethirtyeight')
        text_color = 'black'
        arrow_color = 'black'

    fig, ax = plt.subplots(figsize=(12, 8))
    top_n_countries['China'].plot(kind='line', color='#d62728', ax=ax, legend=False)

    ax.set_title("China's Data Shows a Rapid Flattening of the Curve", loc='left', fontsize=18, fontweight='bold', color=text_color)
    ax.yaxis.set_major_formatter(FuncFormatter(readable_formatter))
    ax.set_xlabel('Date')
    ax.set_ylabel('Cumulative Confirmed Cases')


    plt.tight_layout()
    st.pyplot(fig)

elif question_choice == "Q3.1 & Q4.1: Data Cleaning":
    st.markdown("Missing values were handled using forward-fill (`ffill`), and blank provinces were replaced with 'All Provinces'.")
    st.write("After cleaning, all missing values in the datasets have been addressed.")
    st.write("**Sample of the 'Confirmed' dataframe after filling missing values:**")
    st.dataframe(confirmed.head())
    st.write("**Final NaN check:**")
    st.text(f"Confirmed NaNs: {confirmed.isna().sum().sum()}")
    st.text(f"Deaths NaNs: {deaths.isna().sum().sum()}")
    st.text(f"Recovered NaNs: {recovered.isna().sum().sum()}")

elif question_choice == "Q5.1: Peak Daily Cases":
    st.markdown("Analysis of the peak number of *daily new cases* in Germany, France, and Italy.")
    selected_countries = ['Germany', 'France', 'Italy']
    country_df = confirmed.groupby(['Country/Region']).sum().drop(['Lat', 'Long', 'Province/State'], axis=1, errors='ignore')
    daily_new_cases_df = country_df.diff(axis=1)
    daily_new_cases_df.iloc[:, 0] = country_df.iloc[:, 0]
    daily_new_cases_df[daily_new_cases_df.columns[0]] = daily_new_cases_df[daily_new_cases_df.columns[0]].astype('Int64')
    peak_daily_cases_df = daily_new_cases_df.max(axis=1)

    result_string = f"The country with the highest single-day surge is **{peak_daily_cases_df[selected_countries].idxmax()}** with **{peak_daily_cases_df[selected_countries].max():,}** cases on **{daily_new_cases_df.loc[peak_daily_cases_df[selected_countries].idxmax(), :].idxmax()}**."
    st.success(result_string)
    st.write("**Peak daily new cases for each country (sorted descending):**")
    st.dataframe(peak_daily_cases_df.loc[selected_countries].sort_values(ascending=False).to_frame(name="Peak Daily Cases"))
    
    if dark_mode:
        plt.style.use('dark_background')
        text_color = 'white'
    else:
        plt.style.use('fivethirtyeight')
        text_color = '#333333'
    
    fig_q5_1, ax_q5_1 = plt.subplots(figsize=(10, 6))
    plot_data = peak_daily_cases_df.loc[selected_countries].sort_values(ascending=True)

    bars = ax_q5_1.barh(plot_data.index, plot_data.values, color='#007acc', height=0.7)
    
    ax_q5_1.set_title('Which Country Had the Highest Single-Day Surge?', loc='left', fontsize=16, fontweight='bold', color=text_color)
    ax_q5_1.set_xlabel('Peak Number of Daily New Cases')
    ax_q5_1.set_ylabel('')
    
    ax_q5_1.bar_label(bars, fmt='{:,.0f}', padding=5, fontsize=12, fontweight='bold', color=text_color)
    
    ax_q5_1.xaxis.set_major_formatter(FuncFormatter(readable_formatter))
    ax_q5_1.set_xlim(right=plot_data.max() * 1.25)
    
    plt.tight_layout()
    st.pyplot(fig_q5_1)
    
elif question_choice == "Q5.2: Recovery Rate Comparison":
    st.markdown("Comparison of recovery rates (`recoveries / confirmed`) between Canada and Australia as of December 31, 2020.")
    
    date_to_compare = '12/31/20'
    country_df = confirmed.groupby(['Country/Region']).sum()
    country_df_recovered = recovered.drop(['Lat','Long','Province/State'], axis=1).groupby('Country/Region').sum()
    
    recovery_rate_df = country_df_recovered.div(country_df)
    
    result_series = recovery_rate_df.loc[['Canada', 'Australia'], [date_to_compare]]
    st.dataframe(result_series.style.format('{:.2%}'))
    
    winner = result_series.idxmax().iloc[0]
    rate = result_series.max().iloc[0]
    st.success(f"**{winner}** showed better management according to this metric, with a recovery rate of **{rate:.2%}** on {date_to_compare}.")
    
    if dark_mode:
        plt.style.use('dark_background')
        text_color = 'white'
    else:
        plt.style.use('fivethirtyeight')
        text_color = '#333333'
        
    fig_q5_2, ax_q5_2 = plt.subplots(figsize=(7, 5))
    bars = result_series[date_to_compare].plot(kind='bar', ax=ax_q5_2, color=['#007acc', '#2ca02c'])
    
    ax_q5_2.set_title(f'Recovery Rate on {date_to_compare}', loc='left', fontsize=16, fontweight='bold', color=text_color)
    ax_q5_2.set_ylabel('Recovery Rate (Recoveries / Confirmed)')
    ax_q5_2.set_xlabel('Country')
    
    ax_q5_2.bar_label(ax_q5_2.containers[0], fmt='{:.1%}', padding=3, color=text_color)
    ax_q5_2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: '{:.0%}'.format(x)))
    ax_q5_2.set_ylim(top=result_series[date_to_compare].max() * 1.2)
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig_q5_2)
    
elif question_choice == "Q5.3: Canada Death Rate Distribution":
    st.markdown("Distribution of death rates (`deaths / confirmed`) among provinces in Canada as of the latest data point.")
    confirmed_Canada = confirmed[confirmed['Country/Region'] == 'Canada'].drop(['Country/Region', 'Lat', 'Long'], axis=1, errors='ignore').set_index('Province/State')
    deaths_Canada = deaths[deaths['Country/Region'] == 'Canada'].drop(['Country/Region', 'Lat', 'Long'], axis=1, errors='ignore').set_index('Province/State')
    death_rate_canada_df = deaths_Canada.div(confirmed_Canada)
    latest_date_col = death_rate_canada_df.columns[-1]
    latest_rates = death_rate_canada_df[latest_date_col].replace(np.inf, np.nan).dropna()
    
    st.write(f"Death rates by province as of {latest_date_col}:")
    
    if dark_mode:
        plt.style.use('dark_background')
        text_color = 'white'
    else:
        plt.style.use('fivethirtyeight')
        text_color = '#333333'
        
    fig, ax = plt.subplots(figsize=(10, 8))
    latest_rates_pct = (latest_rates * 100).sort_values(ascending=True)

    highest_province = latest_rates.drop(['Grand Princess', 'Diamond Princess', 'Repatriated Travellers'], errors='ignore').idxmax()
    lowest_province = latest_rates.drop(['Grand Princess', 'Diamond Princess', 'Repatriated Travellers'], errors='ignore').idxmin()
    colors = ['#d62728' if x == highest_province else '#2ca02c' if x == lowest_province else 'grey' for x in latest_rates_pct.index]
    
    bars = ax.barh(latest_rates_pct.index, latest_rates_pct.values, color=colors)
    
    ax.set_title(f"Death Rate by Province in Canada as of {latest_date_col}", loc='left', fontsize=16, color=text_color)
    ax.set_xlabel("Death Rate (Deaths / Confirmed)")
    ax.set_ylabel("")
    
    ax.bar_label(bars, fmt='%.2f%%', padding=3, fontsize=10, color=text_color)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    ax.set_xlim(right=latest_rates_pct.max() * 1.15)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.info("Note: 'Grand Princess' and 'Diamond Princess' are cruise ships included in the data.")
    st.success(f"Among geopolitical provinces, **{highest_province}** had the highest death rate, and **{lowest_province}** had the lowest.")

elif question_choice == "Q6.1-Q6.4: Data Transformation":
    st.markdown("This section covers analyses performed on transformed (long-format) data.")
    st.subheader("Q6.1 & Q6.2: Data Transformation and Total Deaths")
    st.markdown("The `deaths` dataset is transformed from wide to long format using `pd.melt`. From this, we can easily find the total cumulative deaths per country as of the latest date.")
    
    deaths_long_q6 = pd.melt(frame=deaths, id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'], var_name='Date', value_name='Counts')
    deaths_long_q6['Date'] = pd.to_datetime(deaths_long_q6['Date'])
    
    total_deaths_sorted = deaths_long_q6[deaths_long_q6['Date'] == deaths_long_q6['Date'].max()].groupby('Country/Region')['Counts'].sum().sort_values(ascending=False)
    st.write("Top 10 countries by total cumulative deaths:")
    st.dataframe(total_deaths_sorted.head(10).to_frame(name="Total Cumulative Deaths"))

    if dark_mode:
        plt.style.use('dark_background')
        text_color = 'white'
    else:
        plt.style.use('fivethirtyeight')
        text_color = 'black'
    
    fig_q6_2, ax_q6_2 = plt.subplots(figsize=(12, 8))
    plot_data = total_deaths_sorted.head(10).sort_values()
    bars = ax_q6_2.barh(plot_data.index, plot_data.values, color='#d62728')
    ax_q6_2.bar_label(bars, fmt=lambda x: f'{x:,.0f}', padding=3, color=text_color)
    ax_q6_2.set_title('Top 10 Countries by Total Cumulative Deaths', loc='left', fontsize=16, color=text_color)
    ax_q6_2.set_xlabel('Total Cumulative Deaths')
    ax_q6_2.set_ylabel('Country/Region')
    ax_q6_2.xaxis.set_major_formatter(FuncFormatter(readable_formatter))
    ax_q6_2.set_xlim(right=plot_data.max() * 1.15)
    plt.tight_layout()
    st.pyplot(fig_q6_2)

    st.subheader("Q6.3: Top 5 Countries by Average Daily Deaths")
    st.markdown("Here, we calculate the average of the *new* deaths reported each day for every country.")

    daily_deaths_long = deaths_long_q6[['Country/Region', 'Date', 'Counts']].copy()

    with st.spinner("Calculating average daily deaths..."):
        daily_deaths_long_sorted = daily_deaths_long.sort_values(by=['Country/Region', 'Date'])

        daily_deaths_long_sorted['daily_deaths'] = daily_deaths_long_sorted.groupby('Country/Region')['Counts'].diff()
        daily_deaths_long_sorted['daily_deaths'] = daily_deaths_long_sorted['daily_deaths'].fillna(daily_deaths_long_sorted['Counts'])

        avg_daily_deaths = daily_deaths_long_sorted.groupby('Country/Region')['daily_deaths'].mean().sort_values(ascending=False)

    st.write("Top 5 countries by average daily new deaths:")
    st.dataframe(avg_daily_deaths.head(5).to_frame(name="Average Daily Deaths"))
    if dark_mode:
        plt.style.use('dark_background')
        
        rc_params = {
            'text.color': 'white', 'axes.labelcolor': 'white',
            'xtick.color': 'white', 'ytick.color': 'white',
            'axes.titlecolor': 'white'
        }
        plt.rcParams.update(rc_params)
    else:
        plt.style.use('fivethirtyeight')
        plt.rcdefaults()
    fig_q6_3, ax_q6_3 = plt.subplots(figsize=(10, 6))
    avg_daily_deaths.head(5).sort_values().plot(kind='barh', ax=ax_q6_3)
    ax_q6_3.set_title('Top 5 Countries by Average Daily New Deaths')
    ax_q6_3.set_xlabel('Average Daily New Deaths')
    ax_q6_3.set_ylabel('Country/Region')
    plt.tight_layout()
    st.pyplot(fig_q6_3)
    st.subheader("Q6.4: Evolution of Deaths in the US")
    st.markdown("This plot shows the trend of *cumulative* total deaths over time for the United States.")
    
    us_deaths_cumulative = grouped_merged_data[grouped_merged_data['Country/Region'] == 'US']
    if dark_mode:
        plt.style.use('dark_background')
        
        rc_params = {
            'text.color': 'white', 'axes.labelcolor': 'white',
            'xtick.color': 'white', 'ytick.color': 'white',
            'axes.titlecolor': 'white'
        }
        plt.rcParams.update(rc_params)
    else:
        plt.style.use('fivethirtyeight')
        plt.rcdefaults()    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(us_deaths_cumulative['Date'], us_deaths_cumulative['deaths'])
    ax.set_title('Total Cumulative Deaths in the United States Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Deaths (Cumulative)')
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)

elif question_choice == "Q7.1-Q7.3: Data Merging & Monthly Analysis":
    st.markdown("This section analyzes the fully merged dataset to understand monthly pandemic progression.")
    st.subheader("Q7.1: Merged Dataset Sample")
    st.write("A sample of the final merged DataFrame at the country-daily level:")
    st.dataframe(grouped_merged_data.head())
    
    st.subheader("Q7.2 & Q7.3: Monthly Progression for Selected Countries")
    monthly_merged_df = grouped_merged_data.groupby(['Country/Region', 'Month-Year'])[['daily_confirmed', 'daily_deaths', 'daily_recovered']].sum().reset_index()
    
    country_list = sorted(grouped_merged_data['Country/Region'].unique())
    default_countries = ['US', 'Italy', 'Brazil', 'India']
    selected_countries = st.multiselect("Select countries to plot monthly data:", country_list, default=default_countries)
    
    for country in selected_countries:
        if dark_mode:
            plt.style.use('dark_background')
            text_color = 'white'
            arrow_color = 'white'
        else:
            plt.style.use('fivethirtyeight')
            text_color = 'black'
            arrow_color = 'black'

        fig, ax = plt.subplots(figsize=(12, 8))
        country_data = monthly_merged_df[monthly_merged_df['Country/Region'] == country]
        x_axis_labels = country_data['Month-Year'].astype(str)

        ax.plot(x_axis_labels, country_data['daily_confirmed'], label='Confirmed', color='#007acc', marker='o', zorder=3)
        ax.plot(x_axis_labels, country_data['daily_deaths'], label='Deaths', color='#d62728', marker='o', zorder=3)

        if country == 'US':
            us_good_recovery = country_data[country_data['Month-Year'] < '2020-12']
            us_bad_recovery = country_data[country_data['Month-Year'] >= '2020-11']
            ax.plot(us_good_recovery['Month-Year'].astype(str), us_good_recovery['daily_recovered'], label='Recovered', color='#2ca02c', marker='o')
            ax.plot(us_bad_recovery['Month-Year'].astype(str), us_bad_recovery['daily_recovered'], color='#2ca02c', linestyle='--', label='Recovered (Unreliable Data)')
        else:
            ax.plot(x_axis_labels, country_data['daily_recovered'], label='Recovered', color='#2ca02c', marker='o')

        peak_idx = country_data['daily_confirmed'].idxmax()
        peak_value = country_data.loc[peak_idx, 'daily_confirmed']
        if peak_value > 0:
            peak_date_str = str(country_data.loc[peak_idx, 'Month-Year'])
            ax.annotate('Peak Wave', xy=(peak_date_str, peak_value), xytext=(peak_date_str, peak_value + ax.get_ylim()[1] * 0.1), ha='center', arrowprops=dict(arrowstyle="->", color=arrow_color), bbox=dict(boxstyle="round,pad=0.3", fc='yellow', alpha=0.7), color='black')

        ax.set_title(f'Monthly Pandemic Waves in {country}', loc='left', fontsize=18, color=text_color)
        ax.set_xlabel('Month-Year')
        ax.set_ylabel('Number of Monthly Events')
        ax.yaxis.set_major_formatter(FuncFormatter(readable_formatter))
        
        legend = ax.legend(loc='upper left')
        if dark_mode:
            legend.get_frame().set_facecolor('black')
            for text in legend.get_texts():
                text.set_color('white')
        
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)
        if country == 'US':
            st.warning("Data Quality Alert: The recovery data for the US becomes unreliable from December 2020 onwards, shown as a dashed line.")

elif question_choice == "Q8.1: 2020 Death Rate Analysis":
    st.markdown("Identifying the three countries with the highest overall death rates throughout 2020.")
    st.markdown("This rate is calculated as `(Total New Deaths in 2020) / (Total New Confirmed Cases in 2020)`.")
    grouped_merged_data_2020 = grouped_merged_data[grouped_merged_data['Date'].dt.year == 2020].copy()
    annual_grouped_merged_data_2020 = (grouped_merged_data_2020.groupby('Country/Region')['daily_deaths'].sum() / grouped_merged_data_2020.groupby('Country/Region')['daily_confirmed'].sum().replace(0, np.nan)).dropna().sort_values(ascending=False)
    st.dataframe(annual_grouped_merged_data_2020.head(3).to_frame(name="Overall 2020 Death Rate").style.format('{:.2%}'))
    
    if dark_mode:
        plt.style.use('dark_background')
        text_color = 'white'
    else:
        plt.style.use('fivethirtyeight')
        text_color = 'black'
        
    fig_q8_1, ax_q8_1 = plt.subplots(figsize=(10, 6))
    plot_data = (annual_grouped_merged_data_2020.head(10) * 100).sort_values()
    bars = ax_q8_1.barh(plot_data.index, plot_data.values, color='maroon')
    ax_q8_1.bar_label(bars, fmt='%.2f%%', padding=3, color=text_color)
    ax_q8_1.set_title('Top 10 Countries by Overall 2020 Death Rate', loc='left', fontsize=16, color=text_color)
    ax_q8_1.set_xlabel('Overall 2020 Death Rate (Deaths / Confirmed)')
    ax_q8_1.set_ylabel('Country/Region')
    ax_q8_1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))
    plt.tight_layout()
    st.pyplot(fig_q8_1)
    
elif question_choice == "Q8.2: South Africa Recoveries vs. Deaths":
    st.markdown("Comparison of total cumulative recoveries to total cumulative deaths in South Africa as of the latest date in the dataset.")
    sa_data = grouped_merged_data[grouped_merged_data['Country/Region'] == 'South Africa'].copy()
    latest_sa_data = sa_data[sa_data['Date'] == sa_data['Date'].max()]
    
    if not latest_sa_data.empty:
        total_recovered_sa = latest_sa_data['recovered'].iloc[0]
        total_deaths_sa = latest_sa_data['deaths'].iloc[0]
        st.metric("Total Recoveries in South Africa", f"{total_recovered_sa:,}")
        st.metric("Total Deaths in South Africa", f"{total_deaths_sa:,}")
        if total_deaths_sa > 0:
            recovery_to_death_ratio = total_recovered_sa / total_deaths_sa
            st.metric("Recoveries per Death", f"{recovery_to_death_ratio:.2f}")
            
        if dark_mode:
            plt.style.use('dark_background')
            text_color = 'white'
        else:
            plt.style.use('fivethirtyeight')
            text_color = 'black'
            
        metrics_sa = pd.Series({'Total Recoveries': total_recovered_sa, 'Total Deaths': total_deaths_sa})
        fig_q8_2, ax_q8_2 = plt.subplots(figsize=(7, 5))
        bars = metrics_sa.plot(kind='bar', ax=ax_q8_2, color=['#2ca02c', '#d62728'])
        ax_q8_2.bar_label(ax_q8_2.containers[0], fmt=lambda x: f'{x:,.0f}', padding=3, color=text_color)
        ax_q8_2.set_title('South Africa: Recoveries vs. Deaths', loc='left', fontsize=16, color=text_color)
        ax_q8_2.set_ylabel('Total Count (Cumulative)')
        ax_q8_2.set_ylim(top=metrics_sa.max() * 1.2)
        plt.xticks(rotation=0)
        plt.tight_layout()
        st.pyplot(fig_q8_2)
    else:
        st.error("Data for South Africa could not be found.")

elif question_choice == "Q8.3: US Monthly Recovery Ratio":
    st.markdown("Analysis of the ratio of `New Recoveries / New Confirmed Cases` for the United States on a monthly basis from March 2020 to May 2021.")
    us_data = grouped_merged_data[(grouped_merged_data['Country/Region'] == 'US') & (grouped_merged_data['Month-Year'] >= '2020-03') & (grouped_merged_data['Month-Year'] <= '2021-05')].copy()
    us_monthly_totals = us_data.groupby('Month-Year')[['daily_confirmed', 'daily_recovered']].sum()
    us_monthly_totals['recovery_rate'] = us_monthly_totals['daily_recovered'] / us_monthly_totals['daily_confirmed'].replace(0, np.nan)
    st.dataframe(us_monthly_totals.sort_values(by='recovery_rate', ascending=False).style.format({'recovery_rate': '{:.2%}', 'daily_confirmed': '{:,}', 'daily_recovered': '{:,}'}))
    us_monthly_totals['cumu_recovery_rate'] = us_data.groupby('Month-Year')['recovered'].sum() / us_data.groupby('Month-Year')['confirmed'].sum().replace(0, np.nan)
    highest_rate_month_info = us_monthly_totals.dropna(subset=['recovery_rate']).sort_values(by='recovery_rate', ascending=False).head(1)
    
    if not highest_rate_month_info.empty:
        highest_month = highest_rate_month_info.index[0]
        highest_rate_value = highest_rate_month_info['recovery_rate'].iloc[0]
        st.success(f"**Peak Month:** The highest recovery ratio of **{highest_rate_value:.2%}** occurred in **{highest_month}**.")
    plot_data_q8_3 = us_monthly_totals.copy()
    plot_data_q8_3.index = plot_data_q8_3.index.astype(str)
    if dark_mode:
        plt.style.use('dark_background')
        text_color = 'white'
        arrow_color = 'white'
    else:
        plt.style.use('fivethirtyeight')
        text_color = '#333333'
        arrow_color = 'black'

    fig_q8_3, ax_q8_3 = plt.subplots(figsize=(12, 8))
    ax_q8_3.plot(plot_data_q8_3.index, plot_data_q8_3['recovery_rate'], marker='o', linestyle='-')
    ax_q8_3.set_title('US Monthly Recovery Ratio (New Recoveries / New Confirmed)')
    ax_q8_3.set_xlabel('Month-Year')
    ax_q8_3.set_ylabel('Daily Recovery Ratio')
    ax_q8_3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: '{:.2%}'.format(x)))
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    us_monthly_totals.reset_index(inplace=True)
    us_monthly_totals['Month-Year'] = us_monthly_totals['Month-Year'].astype(str)
    peak_daily_recovery_idx = us_monthly_totals['recovery_rate'].idxmax()
    peak_rec_value = us_monthly_totals.loc[peak_daily_recovery_idx, 'recovery_rate']
    if peak_rec_value > 0:
        peak_date_str = str(us_monthly_totals.loc[peak_daily_recovery_idx, 'Month-Year'])
        ax_q8_3.annotate('Peak Recovery', xy=(peak_date_str, peak_rec_value), xytext=(peak_date_str, peak_rec_value + ax_q8_3.get_ylim()[1] * 0.1), ha='center', arrowprops=dict(arrowstyle="->", color=arrow_color), bbox=dict(boxstyle="round,pad=0.3", fc='yellow', alpha=0.7), color='black')    

    plt.tight_layout()
    st.pyplot(fig_q8_3)

    fig_q8_3_2, ax_q8_3_2 = plt.subplots(figsize=(12, 6))
    ax_q8_3_2.plot(plot_data_q8_3.index, plot_data_q8_3['cumu_recovery_rate'], marker='o', linestyle='-')
    ax_q8_3_2.set_title('US Monthly Recovery Ratio (Recoveries / Confirmed)')
    ax_q8_3_2.set_xlabel('Month-Year')
    ax_q8_3_2.set_ylabel('Recovery Ratio')
    ax_q8_3_2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: '{:.2%}'.format(x)))
    peak_daily_recovery_idx = us_monthly_totals['cumu_recovery_rate'].idxmax()
    peak_rec_value = us_monthly_totals.loc[peak_daily_recovery_idx, 'cumu_recovery_rate']
    if peak_rec_value > 0:
        peak_date_str = str(us_monthly_totals.loc[peak_daily_recovery_idx, 'Month-Year'])
        ax_q8_3_2.annotate('Peak Total Recovery', xy=(peak_date_str, peak_rec_value), xytext=(peak_date_str, peak_rec_value + ax_q8_3.get_ylim()[1] * 0.1), ha='center', arrowprops=dict(arrowstyle="->", color=arrow_color), bbox=dict(boxstyle="round,pad=0.3", fc='yellow', alpha=0.7), color='black')    

    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(fig_q8_3_2)
    st.warning("Data Quality Alert: US recovery data is unreliable from Dec 2020, affecting this ratio analysis.")