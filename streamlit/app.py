import streamlit as st
import requests
import pandas as pd
import plotly.express as px  # For interactive graphs

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
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Current Cases"

# Sidebar for Navigation with Custom Title
st.sidebar.markdown('<h1 class="sidebar-title">Covid-19 Dashboard</h1>', unsafe_allow_html=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("Current Cases"):
    st.session_state.page = "Current Cases"

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("Predictions"):
    st.session_state.page = "Predictions"

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("Vaccination Info"):
    st.session_state.page = "Vaccination Info"

# Determine the current page
page = st.session_state.page

# **1. Current Cases Page**
if page == "Current Cases":
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
            st.write("Graph of Current Cases")
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

            # Add a date input for user to query cases on a specific date
            st.write("### Check Cases on a Specific Date")
            selected_date = st.date_input("Select a date to check the cases:")
            if selected_date:
                # Filter data for the selected date
                selected_date = pd.Timestamp(selected_date)  # Convert to Timestamp
                filtered_data = df[df['date'] == selected_date]

                if not filtered_data.empty:
                    st.write(f"Cases on {selected_date.date()}: {filtered_data['cases'].iloc[0]}")
                else:
                    st.write(f"No data available for {selected_date.date()}.")
        else:
            st.write("No data available.")
    else:
        st.error("Failed to fetch current cases.")


# **2. Predictions Page**
elif page == "Predictions":
    st.title("Predicted COVID-19 Cases")

    # Fetch predicted cases data from Django
    response = requests.get(f"{BASE_URL}predict/")
    if response.status_code == 200:
        predictions = response.json().get('predictions', [])

        # Convert predictions into DataFrame
        if predictions:
            prediction_dates = pd.date_range(start="2024-11-01", periods=len(predictions))
            df = pd.DataFrame({"date": prediction_dates, "predicted_cases": predictions})

            st.write("Graph of Predicted Cases")

            # Plot using Plotly
            fig = px.line(df, x="date", y="predicted_cases", title="Predicted COVID-19 Cases")
            st.plotly_chart(fig)
        else:
            st.write("No predictions available.")
    else:
        st.error("Failed to fetch predictions.")

    # Allow user to input a date for prediction
    st.write("Want to see specific predictions?")
    date_input = st.date_input("Select a date to predict cases:")
    if st.button("Get Prediction for Date"):
        if len(predictions) > 0:
            # Convert date_input to a pd.Timestamp
            date_input = pd.Timestamp(date_input)

            index = (date_input - pd.Timestamp(prediction_dates[0])).days
            if 0 <= index < len(predictions):
                st.write(f"Predicted cases for {date_input}: {predictions[index]}")
            else:
                st.warning("Selected date is out of the 21-day prediction range.") #dy pergi dekat sini, tolong tengok nntitttt
        else:
            st.warning("Predictions not available.")


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
    st.subheader("For more information, visit:")
    st.markdown("- [WHO COVID-19 Vaccines](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/covid-19-vaccines)")
    st.markdown("- [Malaysia MoH](https://covid-19.moh.gov.my/)")
    st.markdown("- [NPRA Vaccine Information](https://npra.gov.my/)")
