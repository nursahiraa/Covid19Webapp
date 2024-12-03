import streamlit as st
import requests
import pandas as pd
import plotly.express as px  # For interactive graphs
from streamlit_option_menu import option_menu
import json

# Configure the Streamlit page
st.set_page_config(
    page_title="COVID Forecast Hub",  # Title displayed in the browser tab
    page_icon="🌟",                 # Favicon (can be an emoji or image URL)
    layout="wide",
    initial_sidebar_state="auto"# Layout style ('centered' or 'wide')
)

# Base URL of your Django backend
BASE_URL = "http://127.0.0.1:8000/"  # Update with your Django server URL

# Inject custom CSS for styling
st.markdown(
    """
    <style>
    /* Adjust the sidebar width */
    [data-testid="stSidebar"] {
        min-width: 300px;
        max-width: 300px;
    }

    /* Adjust the font size and color of the custom sidebar title */
    h1.sidebar-title {
        font-size: 28px !important; /* Adjust size as needed */
        font-weight: bold !important;
        color: #FF5733 !important; /* Change to desired color */
        margin-bottom: 20px;
    }

    /* Adjust the general sidebar content styles */
    [data-testid="stSidebar"] .sidebar-content {
        font-size: 14px;
        padding: 10px;
    }
        /* Transparent buttons */
    .transparent-button {
        background-color: transparent !important;
        color: #333 !important; /* Text color */
        border: 2px solid #333 !important; /* Border color */
        border-radius: 5px; /* Rounded corners */
        font-size: 16px !important; /* Font size */
        padding: 10px 20px !important; /* Padding */
        margin: 10px 0 !important; /* Spacing between buttons */
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    /* Hover effect for buttons */
    .transparent-button:hover {
        background-color: #007bff !important; /* Highlight color on hover */
        color: white !important;
        border-color: #007bff !important;
    }
    .metric-container {
        font-size: 1.5em !important; /* Adjust the font size */
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


# Load COVID-19 data directly from the API
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/refs/heads/main/epidemic/cases_state.csv"
    covid_data = pd.read_csv(url)
    covid_data['date'] = pd.to_datetime(covid_data['date'])
    return covid_data

# Load death cases data directly from the API
@st.cache_data
def load_death():
    url = "https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/refs/heads/main/epidemic/deaths_malaysia.csv"
    death_data = pd.read_csv(url)
    death_data['date'] = pd.to_datetime(death_data['date'])
    return death_data

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Sidebar for Navigation with Custom Title
st.sidebar.markdown('<h1 class="sidebar-title">COVID Forecast Hub</h1>', unsafe_allow_html=True)

with st.sidebar:
    selected = option_menu (
        menu_title="Main Menu",
        options=["Home", "Current Cases", "Predictions", "Vaccination Info"],
    )

if selected == "Home":
    st.session_state.page = "Home"
if selected == "Current Cases":
    st.session_state.page = "Current Cases"
if selected == "Predictions":
    st.session_state.page = "Predictions"
if selected == "Vaccination Info":
    st.session_state.page = "Vaccination Info"


# Determine the current page
page = st.session_state.page


if page == "Home":
    st.title("🌟 Welcome to COVID Forecast Hub")
    st.write("")

    st.subheader("Your One-Stop Solution for COVID-19 Data Insights and Predictions")
    st.write("""
    This application provides up-to-date information on COVID-19 cases, future predictions, and vaccination data. 
    Use the sidebar to navigate through the sections for a detailed analysis and insights.
    """)
    # fetch data
    covid_data = load_data();
    death_data = load_death();
    # Aggregate totals
    total_cases = covid_data['cases_new'].sum()
    total_recovered = covid_data['cases_recovered'].sum()
    total_death = death_data['deaths_new'].sum()

    # Example (Replace with actual data fetched from the backend)
    st.markdown('<h2 style="color:#FF5733;">Malaysia COVID-19 Summary</h2>', unsafe_allow_html=True)
    st.write("")
    col1, col2, col3 = st.columns(3)
    # Wrap metrics in a container with the custom class
    col1.markdown('<div class="metric-container">Total Cases</div>', unsafe_allow_html=True)
    col1.metric("", f"{total_cases:,}")

    col2.markdown('<div class="metric-container">Total Deaths</div>', unsafe_allow_html=True)
    col2.metric("", f"{total_death:,}")

    col3.markdown('<div class="metric-container">Total Recovered</div>', unsafe_allow_html=True)
    col3.metric("", f"{total_recovered:,}")
    st.write("")

    # Load the GeoJSON file
    with open("/Users/nursahirazhamri/Desktop/Covid19/streamlit/malaysia_state.geojson", "r") as f:
        geojson_data = json.load(f)

    geojson_states = [feature["properties"]["name"] for feature in geojson_data["features"]]
    print("GeoJSON States:", geojson_states)

    latest_date = covid_data['date'].max()
    latest_data = covid_data[covid_data['date'] == latest_date]
    map_data = latest_data[['state', 'cases_new']].rename(columns={"cases_new": "cases"})

    api_states = map_data['state'].unique()
    print("API States:", api_states)
    # Check mismatches
    mismatched_states = set(api_states) - set(geojson_states)
    print("Mismatched States:", mismatched_states)

    # Map state names if necessary (example for WP states)
    state_mapping = {
        "W.P. Kuala Lumpur": "Kuala Lumpur",
        "W.P. Labuan": "Labuan",
        "W.P. Putrajaya": "Putrajaya",
        "Johor": "Johor",
        "Kedah": "Kedah",
        "Kelantan": "Kelantan",
        "Melaka": "Melaka",
        "Negeri Sembilan": "Negeri Sembilan",
        "Pahang": "Pahang",
        "Sabah": "Sabah",
        "Sarawak": "Sarawak",
        "Selangor": "Selangor",
        "Terengganu": "Terengganu",
        "Pulau Pinang": "Pulau Pinang",
        "Perak": "Perak",
        "Perlis": "Perlis",
    }
    map_data['state'] = map_data['state'].replace(state_mapping)
    formatted_date = latest_date.strftime("%d-%m-%Y")  # Format date as DD-MM-YYYY


    # Create a choropleth map
    fig = px.choropleth(
        map_data,
        geojson=geojson_data,
        locations="state",  # Match this column with GeoJSON properties.name
        featureidkey="properties.name",  # GeoJSON key for state names
        color="cases",  # Column for coloring
        color_continuous_scale=["green", "yellow", "red"],  # Color gradient
    )
    # Adjust the map layout for a bigger size
    fig.update_layout(
        title={
        "text": (
            "<b>COVID-19 Cases by State in Malaysia</b>"
            "<br><span style='font-size:16px; color:gray;'>Latest Data: "
            f"{formatted_date}</span>"
        ),
        "font": {"size": 35,"family": "Arial", "color": "#FF5733"},  # Adjust the font size (e.g., 24 for larger text)
        "x": 0.1, # Center-aligned
        "y": 0.9,  # Adjust vertical alignment (closer to the top edge)
        },
        height=700,  # Increase map height (default ~450)
        width=1000,  # Increase map width (default ~700)
        plot_bgcolor="blue",  # Background color of the plot
        shapes=[
            # Rectangle frame
            dict(
                type="rect",  # Shape type
                xref="paper", yref="paper",  # Use paper coordinates (relative to plot area)
                x0=0, y0=0.172,  # Bottom-left corner of the rectangle
                x1=1, y1=0.828,  # Top-right corner of the rectangle
                line=dict(color="black", width=2)  # Border color and thickness
            )
        ],
        margin={"r": 0, "t": 30, "l": 0, "b": 0},  # Adjust map margins
        coloraxis_colorbar=dict(
            len=0.7,  # Adjust the height of the color bar (0.7 = 70% of map height)
            y=0.5,  # Center the color bar vertically
            yanchor="middle",  # Align the color bar relative to the center
        )
    )
    # Adjust map appearance
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="#F0F8FF")
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": True,  # Show the mode bar
            "modeBarButtonsToRemove": [
                "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d",
                "zoomOut2d", "autoScale2d", "toggleSpikelines", "hoverClosestCartesian",
                "hoverCompareCartesian", "toggleFullscreen", "toImage"
            ],  # Remove all buttons except reset
            "displaylogo": False  # Remove Plotly logo
        }
    )
    # # Show additional data (optional)
    # st.subheader(f"COVID-19 Cases on {latest_date.date()}")
    # st.dataframe(map_data)


# **1. Current Cases Page**
elif page == "Current Cases":
    st.title("Current COVID-19 Cases")

    # Fetch all current cases data from Django
    response = requests.get(f"{BASE_URL}current_cases/")
    if response.status_code == 200:
        current_data = response.json().get('current_cases', [])
        if current_data:
            # Convert data to DataFrame
            df = pd.DataFrame(current_data)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Ensure proper datetime format

            # Plot the graph using Plotly
            # st.write("Graph of Current Cases")
            if len(df) < 2:
                # Add dummy data point if only one row exists
                st.warning("Not enough data to generate a meaningful graph. Adding a dummy data point.")
                last_date = df['date'].iloc[0]
                dummy_date = last_date - pd.Timedelta(days=1)
                dummy_cases = df['cases'].iloc[0]  # Use the same case count for simplicity
                df = pd.concat([df, pd.DataFrame({'date': [dummy_date], 'cases': [dummy_cases]})])

            fig = px.line(
                df,
                x="date",
                y="cases",
                title="Current COVID-19 Cases",
                width=800,  # Adjust width of the graph
                height=500  # Adjust height of the graph
            )
            st.plotly_chart(fig)
            st.markdown("---")
            # Add a date input for user to query cases on a specific date
            st.markdown('<h2 style="color:#FF5733;">📅 Cases on a Specific Date</h2>', unsafe_allow_html=True)
            st.write("")
            selected_date = st.date_input("Select a date to check the cases:")

            # Button to fetch prediction for the selected date
            if st.button("Submit"):
                if selected_date:
                    # Filter data for the selected date
                    selected_date = pd.Timestamp(selected_date)  # Convert to Timestamp
                    filtered_data = df[df['date'] == selected_date]

                    if not filtered_data.empty:
                        st.write(f"Cases on {selected_date.date()}: {filtered_data['cases'].iloc[0]}")
                    else:
                        st.write(f"No data available.")

        else:
            st.write("No data available.")
    else:
        st.error("Failed to fetch current cases.")

# nnti cuba buat dekat homapage dekt total cases tu,, kat sini maybe tambah kotak je kot untuk output
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style='background-color: #f4f4f4; padding: 20px; border-radius: 10px;'>
                <h3 style='color: #0073e6;'>📊 Total Cases</h3>
                <p style='font-size: 18px; color: #333;'>{}</p>
            </div>
            """.format(111),
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div style='background-color: #ffe6e6; padding: 20px; border-radius: 10px;'>
                <h3 style='color: #ff4d4d;'>💀 Total Deaths</h3>
                <p style='font-size: 18px; color: #333;'>{}</p>
            </div>
            """.format(2222),
            unsafe_allow_html=True
        )



# **2. Predictions Page**
elif page == "Predictions":
    st.title("Predicted COVID-19 Cases")

    # Fetch predicted cases data from Django
    response = requests.get(f"{BASE_URL}predict/")
    if response.status_code == 200:
        raw_predictions = response.json().get('predictions', [])

        if raw_predictions:
            # Convert raw predictions to DataFrame
            df = pd.DataFrame(raw_predictions)
            df['date'] = pd.to_datetime(df['date'])  # Ensure dates are in datetime format

            # Handle missing dates by reindexing to a full date range
            start_date = df['date'].min()
            end_date = df['date'].max()
            full_date_range = pd.date_range(start=start_date, end=end_date)
            df = df.set_index('date').reindex(full_date_range, fill_value=0).reset_index()
            df.columns = ['date', 'predicted_cases']  # Rename columns

            # Add dummy data point if there’s only one row
            if len(df) < 2:
                last_date = df['date'].iloc[0]
                dummy_date = last_date - pd.Timedelta(days=1)
                dummy_cases = df['predicted_cases'].iloc[0]  # Use the same case count for simplicity
                df = pd.concat([df, pd.DataFrame({'date': [dummy_date], 'predicted_cases': [dummy_cases]})])

            # Plot the graph using Plotly
            # st.write("Graph of Predicted Cases")
            fig = px.line(
                df,
                x="date",
                y="predicted_cases",
                title="Predicted COVID-19 Cases",
                width=800,  # Adjust width of the graph
                height=500  # Adjust height of the graph
            )
            st.plotly_chart(fig)

            # Allow user to input a date for prediction
            st.markdown("---")
            st.markdown('<h2 style="color:#FF5733;">📅 Cases on a Specific Date</h2>', unsafe_allow_html=True)
            st.write("")
            # Input date box for selecting a specific date
            selected_date = st.date_input("Select a date to predict cases:")

            # Button to fetch prediction for the selected date
            if st.button("Submit"):
                if selected_date:
                    # Filter data for the selected date
                    selected_date = pd.Timestamp(selected_date)  # Convert to Timestamp
                    filtered_data = df[df['date'] == selected_date]

                    if not filtered_data.empty:
                        st.write(f"Predicted cases on {selected_date.date()}: {filtered_data['predicted_cases'].iloc[0]}")
                        st.markdown('<h5 style="color:#FF5733;">For more information, visit:</h5>',unsafe_allow_html=True)
                    else:
                        st.write(f"No prediction available.")

        else:
            st.write("No predictions available.")
    else:
        st.error("Failed to fetch predictions.")


# **3. Vaccination Info Page**
elif page == "Vaccination Info":
    st.title("Vaccination Information")
    st.markdown("---")
    # What is a Vaccine?
    st.header("What is a Vaccine?")
    st.write(
        """
        A vaccine is a biological preparation that strengthens the immune system to recognize and fight specific pathogens, 
        such as viruses or bacteria. COVID-19 vaccines introduce components of the SARS-CoV-2 virus—like its spike protein—or 
        use mRNA technology to instruct cells to produce this protein. This process triggers the immune system to create antibodies, 
        equipping the body to defend itself if exposed to the virus.

        COVID-19 vaccines have proven essential in reducing severe cases, hospitalizations, and deaths. They underwent rigorous 
        clinical trials to ensure safety and effectiveness and continue to be monitored during distribution. Booster doses are often 
        recommended to maintain immunity over time, especially against emerging variants.
        """
    )
    st.markdown("---")
    # Why Vaccination Matters
    st.header("Why Vaccination Matters")
    st.write(
        """
        Vaccination is one of the most powerful tools to combat COVID-19 by significantly reducing the risks of severe illness, 
        hospitalization, and death. It trains the immune system to recognize and fight the virus effectively, providing vital protection 
        for individuals and especially vulnerable populations, such as the elderly and those with underlying health conditions. High 
        vaccination coverage not only protects individuals but also slows virus transmission, creating community-level protection.

        During the COVID-19 pandemic, vaccines have been instrumental in controlling the spread of the virus in Malaysia and globally. 
        They have eased pressure on healthcare systems, allowed societies to recover socially and economically, and mitigated the 
        impact of new variants by reducing severe outcomes. Staying up to date with booster doses ensures continued protection, as 
        immunity can wane over time.
        """
    )
    st.markdown(
        "[Learn more from WHO](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/covid-19-vaccines)"
    )
    st.markdown("---")
    # COVID-19 Vaccination in Malaysia
    st.header("COVID-19 Vaccination in Malaysia")
    st.write(
        """
        Malaysia's National COVID-19 Immunization Program, launched in 2021, has been vital in controlling the pandemic. 
        Initial phases prioritized healthcare workers, the elderly, and high-risk groups, later extending to include adolescents 
        and children aged five and above. 

        The program has significantly reduced severe cases, hospitalizations, and deaths. Vaccination coverage remains high, 
        with booster doses being administered to sustain immunity, particularly against new variants. Vaccines approved and used 
        in Malaysia include Pfizer-BioNTech (Comirnaty), Sinovac (CoronaVac), AstraZeneca, and others, ensuring a range of safe 
        and effective options for the population.
        """
    )
    st.markdown("---")
    # Types of COVID-19 Vaccines
    st.header("Types of COVID-19 Vaccines")
    st.write(
        """
        Several COVID-19 vaccines have been approved for use in Malaysia, each developed using different technologies. 
        These include:

        - **mRNA Vaccines**: These vaccines use messenger RNA to instruct cells to produce a harmless viral protein, 
          triggering an immune response. Examples: Pfizer-BioNTech (Comirnaty) and Moderna.
        - **Viral Vector Vaccines**: These vaccines use a harmless virus as a delivery system to introduce genetic 
          material of the SARS-CoV-2 virus. Example: AstraZeneca.
        - **Inactivated Vaccines**: These vaccines use killed virus particles to elicit an immune response without causing 
          infection. Examples: Sinovac (CoronaVac), Sinopharm.
        - **Protein Subunit Vaccines**: These vaccines include harmless fragments of the virus (such as proteins) 
          to stimulate immunity. Example: Novavax.

        In Malaysia, the vaccines primarily used include Pfizer-BioNTech (Comirnaty), Sinovac (CoronaVac), and AstraZeneca, 
        among others. Booster doses are also being administered to strengthen immunity over time, particularly for high-risk 
        groups and against newer variants.
        """
    )
    st.markdown("[More details from Malaysia MoH](https://covid-19.moh.gov.my/)")
    st.markdown("---")
    # Vaccine Safety and Effectiveness
    st.header("Vaccine Safety and Effectiveness")
    st.write(
        """
        All COVID-19 vaccines approved for use in Malaysia by the National Pharmaceutical Regulatory Agency (NPRA) 
        have undergone rigorous clinical trials to ensure their safety and effectiveness. These trials involve multiple 
        phases, testing the vaccines in diverse populations to confirm they provide significant protection against severe 
        illness, hospitalization, and death.

        The vaccines in use have demonstrated a high safety profile, with most side effects being mild and temporary, 
        such as soreness at the injection site, fatigue, or a mild fever. Serious adverse events are extremely rare, and 
        comprehensive monitoring systems are in place to ensure ongoing safety.

        Effectiveness studies have shown that vaccination significantly reduces the risk of severe outcomes from COVID-19, 
        even with the emergence of new variants. Booster doses are recommended to maintain high levels of immunity over time. 
        By choosing to vaccinate, individuals not only protect themselves but also contribute to the broader goal of community 
        protection, reducing the overall burden on healthcare systems.
        """
    )
    st.markdown("[Learn more about vaccine safety from NPRA](https://npra.gov.my/)")
    st.markdown("---")
    # Frequently Asked Questions
    st.header("Frequently Asked Questions (FAQs)")

    with st.expander("Question 1: Are COVID-19 vaccines safe for children?"):
        st.write(
            """
            Yes, COVID-19 vaccines approved for children in Malaysia are safe and effective for those aged 5 and above. 
            These vaccines have undergone rigorous testing in clinical trials to ensure their safety and efficacy in younger age groups.
            """
        )

    with st.expander("Question 2: Can I still get COVID-19 after being vaccinated?"):
        st.write(
            """
            Yes, but the vaccines significantly reduce the risk of severe illness, hospitalization, and death. 
            Breakthrough infections are generally mild due to the protection provided by the vaccine.
            """
        )

    with st.expander("Question 3: What are the common side effects of COVID-19 vaccines?"):
        st.write(
            """
            Common side effects include pain or swelling at the injection site, fatigue, mild fever, headache, and muscle aches. 
            These symptoms usually resolve within a few days and indicate that the body is building immunity.
            """
        )

    with st.expander("Question 4: Do I need a booster dose?"):
        st.write(
            """
            Yes, booster doses are recommended to sustain immunity over time, especially for high-risk groups and to strengthen protection against new variants.
            """
        )

    with st.expander("Question 5: Is it safe to get vaccinated if I’m pregnant or breastfeeding?"):
        st.write(
            """
            Yes, COVID-19 vaccines are safe and recommended for pregnant and breastfeeding individuals. Vaccination helps 
            protect both the mother and the baby from severe illness.
            """
        )

    with st.expander("Question 6: How long does immunity last after vaccination?"):
        st.write(
            """
            Immunity may wane over time, particularly against new variants. Booster doses are recommended to ensure 
            continued protection and enhance immunity.
            """
        )

    with st.expander("Question 7: Do close contacts of COVID-19 cases need to undergo quarantine?"):
        st.write(
            """
            The requirement for quarantine depends on the current public health guidelines in Malaysia. Close contacts 
            should monitor their symptoms and follow the latest advice from health authorities.
            """
        )

    with st.expander("Question 8: What should I do if I still have symptoms after completing the isolation period?"):
        st.write(
            """
            If symptoms persist after the isolation period, you should consult a healthcare professional for further 
            evaluation and guidance.
            """
        )

    with st.expander("Question 9: Can I choose which vaccine to receive?"):
        st.write(
            """
            Vaccine availability may vary based on supply and logistics. In Malaysia, individuals are typically 
            offered vaccines based on availability, but in some cases, specific options may be available for medical reasons 
            or personal preferences.


            """
        )

    with st.expander("Question 10: Do I need a vaccine if I’ve already had COVID-19?"):
        st.write(
            """
            Yes, vaccination is recommended even if you’ve recovered from COVID-19. 
            Natural immunity may not last as long as vaccine-induced immunity, and vaccination offers added protection 
            against reinfection.
            """
        )
    st.write("")

    st.write("You can visit the official website of the Malaysia Ministry of Health (MoH) for more FAQs on COVID-19.")
    st.markdown("[Visit Malaysia MoH for more FAQs](https://covid-19.moh.gov.my/faqsop/faq-covid-19-kkm)")

    st.markdown("---")
    # Provide a summary with links to credible sources
    st.markdown('<h3 style="color:#FF5733;">For more information, visit:</h3>', unsafe_allow_html=True)
    st.markdown("- [WHO COVID-19 Vaccines](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/covid-19-vaccines)")
    st.markdown("- [Malaysia MoH](https://covid-19.moh.gov.my/)")
    st.markdown("- [NPRA Vaccine Information](https://npra.gov.my/)")

