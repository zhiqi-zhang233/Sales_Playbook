import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px

st.set_page_config(page_title="📊 SymTrain Dashboard", layout="wide")

@st.cache_data
def load_deals():
    return pd.read_csv("data/deals.csv")

@st.cache_data
def load_tickets():
    return pd.read_csv("data/tickets.csv")

@st.cache_data
def load_companies():
    return pd.read_csv("data/companies.csv")

# Sidebar dataset selector
dataset = st.sidebar.selectbox("Select Dataset", ["Deals", "Tickets", "Companies"])

# ===================================
# ========== DEALS DASHBOARD ==========
# ===================================
if dataset == "Deals":
    df = load_deals()
    st.title("💼  Deals")

    tab1, tab2 = st.tabs(["📋 Overview", "📊 Visual Insights"])

    with tab1:
        st.subheader("Dataset Overview")
        st.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
        st.dataframe(df.head())

    with tab2:
        st.title("Dashboard")

        # ----- Main-Body Filter Panel -----
        with st.expander("Filter Deals Data", expanded=False):
            st.markdown("### Numeric Filters")
            # Use columns to better organize sliders side-by-side if desired
            col_num1, col_num2 = st.columns(2)
            
            with col_num1:
                score_min, score_max = float(df["Deal Score"].min()), float(df["Deal Score"].max())
                score_range = st.slider("Deal Score Range", min_value=score_min, 
                                        max_value=score_max, value=(score_min, score_max))
                prob_min, prob_max = float(df["Deal probability"].min()), float(df["Deal probability"].max())
                prob_range = st.slider("Deal Probability Range", min_value=prob_min, 
                                    max_value=prob_max, value=(prob_min, prob_max))
                days_min, days_max = int(df["Days to close"].min()), int(df["Days to close"].max())
                days_range = st.slider("Days to Close Range", min_value=days_min, 
                                    max_value=days_max, value=(days_min, days_max))
            with col_num2:
                amount_min, amount_max = float(df["Amount"].min()), float(df["Amount"].max())
                amount_range = st.slider("Amount Range", min_value=amount_min, 
                                        max_value=amount_max, value=(amount_min, amount_max))
                wamount_min, wamount_max = float(df["Weighted amount"].min()), float(df["Weighted amount"].max())
                wamount_range = st.slider("Weighted Amount Range", min_value=wamount_min, 
                                        max_value=wamount_max, value=(wamount_min, wamount_max))

            st.markdown("### Categorical Filters")

            deal_stage_options = df["Deal Stage"].dropna().unique().tolist()
            selected_deal_stage = st.multiselect("Deal Stage", options=deal_stage_options, default=deal_stage_options)

            forecast_columns = [
                "Forecast category_Closed won", 
                "Forecast category_Commit", 
                "Forecast category_Not forecasted", 
                "Forecast category_Pipeline"
            ]
            selected_forecast = st.multiselect("Forecast Categories", 
                                                options=forecast_columns, default=forecast_columns)

            deal_type_columns = ["Deal Type_New", "Deal Type_PS", "Deal Type_Renewal"]
            selected_deal_types = st.multiselect("Deal Type", 
                                                options=deal_type_columns, default=deal_type_columns)

        # ----- Filter the DataFrame -----
        filtered_df = df[
            (df["Deal Score"] >= score_range[0]) & (df["Deal Score"] <= score_range[1]) &
            (df["Deal probability"] >= prob_range[0]) & (df["Deal probability"] <= prob_range[1]) &
            (df["Amount"] >= amount_range[0]) & (df["Amount"] <= amount_range[1]) &
            (df["Weighted amount"] >= wamount_range[0]) & (df["Weighted amount"] <= wamount_range[1]) &
            (df["Days to close"] >= days_range[0]) & (df["Days to close"] <= days_range[1]) &
            (df["Deal Stage"].isin(selected_deal_stage))
        ]

        # For forecast and deal type filters: assuming these columns are binary (0/1 or True/False)
        if selected_forecast:
            forecast_filter = filtered_df[selected_forecast].any(axis=1)
            filtered_df = filtered_df[forecast_filter]

        if selected_deal_types:
            deal_type_filter = filtered_df[selected_deal_types].any(axis=1)
            filtered_df = filtered_df[deal_type_filter]

        st.markdown("---")
        st.subheader("Key Sales Metrics Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            total_revenue = filtered_df["Amount"].sum()
            st.metric("Total Revenue", f"${total_revenue:,.0f}")
        with col2:
            avg_deal_score = filtered_df["Deal Score"].mean()
            st.metric("Avg Deal Score", f"{avg_deal_score:.2f}")
        with col3:
            avg_days_close = filtered_df["Days to close"].mean()
            st.metric("Avg Days to Close", f"{avg_days_close:.1f}")

        st.markdown("---")
        # ----- Revenue by Deal Stage -----
        st.subheader("Revenue by Deal Stage")
        revenue_by_stage = filtered_df.groupby("Deal Stage")["Amount"].sum().reset_index()
        bar_chart = alt.Chart(revenue_by_stage).mark_bar().encode(
            x=alt.X("Deal Stage:N", sort='-y'),
            y=alt.Y("Amount:Q", title="Total Revenue"),
            tooltip=["Deal Stage", "Amount"]
        ).properties(width=600, height=400)
        st.altair_chart(bar_chart, use_container_width=True)

        # ----- Deal Score vs. Deal Probability (Bubble Chart) -----
        st.subheader("Deal Score vs. Deal Probability")
        bubble_chart = px.scatter(
            filtered_df,
            x="Deal Score",
            y="Deal probability",
            size="Amount",
            hover_data=["Record ID", "Days to close"],
            title="Deal Score vs. Deal Probability (Bubble Size = Amount)"
        )
        st.plotly_chart(bubble_chart, use_container_width=True)

        # ----- Distribution of Days to Close -----
        st.subheader("Distribution of Days to Close")
        hist_chart = alt.Chart(filtered_df).mark_bar().encode(
            x=alt.X("Days to close:Q", bin=alt.Bin(maxbins=30)),
            y=alt.Y("count()", title="Count of Deals"),
            tooltip=["count()"]
        ).properties(width=600, height=400)
        st.altair_chart(hist_chart, use_container_width=True)

        # ----- Deal Recommendations & Action Plans -----
        st.subheader("Deal Recommendations and Action Plans")
        record_ids = filtered_df["Record ID"].unique().tolist()
        if record_ids:
            selected_record = st.selectbox("Select a Deal (Record ID)", record_ids)
            selected_deal = filtered_df[filtered_df["Record ID"] == selected_record].iloc[0]

            st.markdown("### Deal Details")
            st.write(selected_deal)

            recommendation = ""
            action_plan = ""
            if selected_deal["Deal Score"] < 50:
                recommendation = "The deal score is low; consider additional qualification."
                action_plan = "Schedule a follow-up call to better understand client needs."
            elif selected_deal["Days to close"] > 60:
                recommendation = "The sales cycle is lengthy; analyze possible bottlenecks."
                action_plan = "Review internal processes and offer targeted incentives."
            else:
                recommendation = "The deal appears to be on track."
                action_plan = "Maintain regular engagement and monitor progress."
            
            st.markdown("#### Recommendations")
            st.write(f"**Recommendation:** {recommendation}")
            st.write(f"**Action Plan:** {action_plan}")

            st.markdown("#### Templated Messaging")
            if selected_deal.get("Deal Type_New", 0) == 1:
                message = ("Thank you for your interest in our new offerings. "
                        "We are excited to work with you and support your needs.")
            elif selected_deal.get("Deal Type_Renewal", 0) == 1:
                message = ("We appreciate your loyalty and are committed to providing continued value. "
                        "Let's discuss your renewal options.")
            else:
                message = ("Please let us know if you have any questions or need further assistance. "
                        "We are here to support you.")
            st.write(message)
        else:
            st.info("No deals match the selected filter criteria.")

# ===================================
# ========== TICKETS DASHBOARD ==========
# ===================================
elif dataset == "Tickets":
    df = load_tickets()
    st.title("🎫  Tickets")

    tab1, tab2 = st.tabs(["📋 Overview", "📊 Visual Insights"])

    with tab1:
        st.subheader("Dataset Overview")
        st.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
        st.dataframe(df.head())

    with tab2:
        st.title("Dashboard")

        # ----- Main-Body Filter Panel -----
        with st.expander("Filter Tickets Data", expanded=False):
            st.markdown("### Numeric Filters")
            col_num1, col_num2, col_num3 = st.columns(3)
            
            with col_num1:
                resp_min, resp_max = float(df["Response time hours"].min()), float(df["Response time hours"].max())
                resp_range = st.slider("Response Time (hours)", min_value=resp_min, 
                                    max_value=resp_max, value=(resp_min, resp_max))
                
            with col_num2:
                impl_min, impl_max = float(df["Implementation Duration Days"].min()), float(df["Implementation Duration Days"].max())
                impl_range = st.slider("Implementation Duration (days)", min_value=impl_min, 
                                    max_value=impl_max, value=(impl_min, impl_max))
                
            with col_num3:
                training_min, training_max = int(df["Training Completion Count"].min()), int(df["Training Completion Count"].max())
                training_range = st.slider("Training Completion Count", min_value=training_min, 
                                        max_value=training_max, value=(training_min, training_max))
            
            st.markdown("### Categorical Filters")
            col_cat1, col_cat2, col_cat3 = st.columns(3)
            with col_cat1:
                status_options = df["Ticket status"].dropna().unique().tolist()
                selected_status = st.multiselect("Ticket Status", options=status_options, default=status_options)
            with col_cat2:
                year_options = sorted(df["Create date_Year"].dropna().unique().tolist())
                selected_year = st.multiselect("Creation Year", options=year_options, default=year_options)
            with col_cat3:
                month_options = sorted(df["Create date_Month"].dropna().unique().tolist())
                selected_month = st.multiselect("Creation Month", options=month_options, default=month_options)
            
            # For the trial requirements, we can use checkboxes (or multiselect if needed)
            st.markdown("### Trial Requirements Filters")
            col_req1, col_req2, col_req3 = st.columns(3)
            with col_req1:
                req_onboarding = st.checkbox("Has Onboarding Requirement", value=False)
            with col_req2:
                req_coaching = st.checkbox("Has Coaching Requirement", value=False)
            with col_req3:
                req_assessment = st.checkbox("Has Assessment Requirement", value=False)

        # ----- Filter the DataFrame -----
        filtered_df = df[
            (df["Response time hours"] >= resp_range[0]) & (df["Response time hours"] <= resp_range[1]) &
            (df["Implementation Duration Days"] >= impl_range[0]) & (df["Implementation Duration Days"] <= impl_range[1]) &
            (df["Training Completion Count"] >= training_range[0]) & (df["Training Completion Count"] <= training_range[1]) &
            (df["Ticket status"].isin(selected_status)) &
            (df["Create date_Year"].isin(selected_year)) &
            (df["Create date_Month"].isin(selected_month))
        ]

        # Filter by trial requirements if selected
        if req_onboarding:
            filtered_df = filtered_df[filtered_df["Requirements for the Trial_Onboarding"] == 1]
        if req_coaching:
            filtered_df = filtered_df[filtered_df["Requirements for the Trial_Coaching"] == 1]
        if req_assessment:
            filtered_df = filtered_df[filtered_df["Requirements for the Trial_Assessment"] == 1]

        st.markdown("---")

        # ----- KPI Metrics -----
        st.subheader("Key Ticket Metrics Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            total_tickets = filtered_df["Ticket ID"].nunique()
            st.metric("Total Tickets", total_tickets)
        with col2:
            avg_response = filtered_df["Response time hours"].mean()
            st.metric("Avg Response Time (hrs)", f"{avg_response:.2f}")
        with col3:
            avg_impl = filtered_df["Implementation Duration Days"].mean()
            st.metric("Avg Implementation Duration (days)", f"{avg_impl:.1f}")

        st.markdown("---")

        # ----- Ticket Status Distribution -----
        st.subheader("Ticket Status Distribution")
        status_counts = filtered_df["Ticket status"].value_counts().reset_index()
        status_counts.columns = ["Ticket status", "Count"]
        bar_chart = alt.Chart(status_counts).mark_bar().encode(
            x=alt.X("Ticket status:N", sort='-y'),
            y=alt.Y("Count:Q", title="Number of Tickets"),
            tooltip=["Ticket status", "Count"]
        ).properties(width=600, height=400)
        st.altair_chart(bar_chart, use_container_width=True)

        # ----- Ticket Creation Trends -----
        st.subheader("Ticket Creation Trends")
        # Trend over time using Year and Month for a simple aggregation
        trend_df = filtered_df.groupby(["Create date_Year", "Create date_Month"])["Ticket ID"].count().reset_index()
        trend_df.columns = ["Year", "Month", "Tickets Count"]
        trend_chart = alt.Chart(trend_df).mark_line(point=True).encode(
            x=alt.X("Month:N", title="Month"),
            y=alt.Y("Tickets Count:Q", title="Tickets Created"),
            color="Year:N",
            tooltip=["Year", "Month", "Tickets Count"]
        ).properties(width=600, height=400)
        st.altair_chart(trend_chart, use_container_width=True)

        # ----- Response vs. Implementation Scatter Plot -----
        st.subheader("Response Time vs. Implementation Duration")
        scatter_chart = px.scatter(
            filtered_df,
            x="Response time hours",
            y="Implementation Duration Days",
            size="Training Completion Count",
            hover_data=["Ticket ID", "Ticket status"],
            title="Response Time vs. Implementation Duration (Bubble size = Training Completion Count)"
        )
        st.plotly_chart(scatter_chart, use_container_width=True)

        # ----- Ticket Recommendations & Action Plans -----
        st.subheader("Ticket Recommendations and Action Plans")
        ticket_ids = filtered_df["Ticket ID"].unique().tolist()
        if ticket_ids:
            selected_ticket = st.selectbox("Select a Ticket (Ticket ID)", ticket_ids)
            ticket_details = filtered_df[filtered_df["Ticket ID"] == selected_ticket].iloc[0]
            
            st.markdown("### Ticket Details")
            st.write(ticket_details)
            
            recommendation = ""
            action_plan = ""
            # Example recommendation logic:
            if ticket_details["Response time hours"] > 48:
                recommendation = "High response time; review support communication processes."
                action_plan = "Consider follow-up training for the support team or a review of ticket handling procedures."
            elif ticket_details["Implementation Duration Days"] > 30:
                recommendation = "Long implementation duration; investigate underlying causes."
                action_plan = "Initiate a process review to identify bottlenecks and streamline implementation steps."
            else:
                recommendation = "Ticket metrics are within acceptable ranges."
                action_plan = "Maintain current practices and monitor for any changes."
                
            st.markdown("#### Recommendations")
            st.write(f"**Recommendation:** {recommendation}")
            st.write(f"**Action Plan:** {action_plan}")
        else:
            st.info("No tickets match the selected filter criteria.")

elif dataset == "Companies":
    df = load_companies()
    st.title("🏢  Companies")
    
    # Create two tabs: Overview and Visual Insights
    tab1, tab2 = st.tabs(["📋 Overview", "📊 Visual Insights"])
    
    with tab1:
        st.subheader("Dataset Overview")
        st.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
        st.dataframe(df.iloc[:, :100].head())
    
    with tab2:
        st.title("Dashboard")

        # ----- Create Lists of Column Groups for Filters -----
        # Company Type filter (e.g., Type_Analyst, Type_BPO, etc.)
        type_columns = [col for col in df.columns if col.startswith("Type_")]

        # Primary Industry filter columns (e.g., Primary Industry_Agriculture, Primary Industry_Business Services, etc.)
        primary_industry_columns = [col for col in df.columns if col.startswith("Primary Industry_")]

        # Country/Region filter columns (e.g., Country/Region_United States, Country/Region_Canada, etc.)
        country_columns = [col for col in df.columns if col.startswith("Country/Region_")]

        # Web Technologies columns (to later count technologies used by each company)
        web_tech_columns = [col for col in df.columns if col.startswith("Web Technologies_")]

        # ----- Main-Body Filter Panel -----
        with st.expander("Filter Companies Data", expanded=False):
            st.markdown("### Time Filters")
            year_options = sorted(df["Create Date_Year"].dropna().unique().tolist())
            selected_years = st.multiselect("Creation Year", options=year_options, default=year_options)
            
            st.markdown("### Company Type Filters")
            selected_types = st.multiselect("Company Type", options=type_columns, default=type_columns)
            
            st.markdown("### Primary Industry Filters")
            selected_primary = st.multiselect("Primary Industry", options=primary_industry_columns, default=primary_industry_columns)
            
            st.markdown("### Country/Region Filters")
            selected_countries = st.multiselect("Country/Region", options=country_columns, default=country_columns)
            
            st.markdown("### Additional Filters")
            form_submission_filter = st.checkbox("Only show companies with Form Submission YN = Yes", value=False)
            close_filter = st.checkbox("Only show companies with Close YN = Yes", value=False)

        # ----- Filter the DataFrame -----
        filtered_df = df[df["Create Date_Year"].isin(selected_years)]

        # Filter by Company Type: Keep rows that have a 1 in at least one of the selected type columns
        if selected_types:
            type_mask = filtered_df[selected_types].eq(1).any(axis=1)
            filtered_df = filtered_df[type_mask]

        # Filter by Primary Industry: Keep rows that have a 1 in at least one of the selected primary industry columns
        if selected_primary:
            primary_mask = filtered_df[selected_primary].eq(1).any(axis=1)
            filtered_df = filtered_df[primary_mask]

        # Filter by Country/Region: Keep rows that have a 1 in at least one of the selected country columns
        if selected_countries:
            country_mask = filtered_df[selected_countries].eq(1).any(axis=1)
            filtered_df = filtered_df[country_mask]

        # Additional filters for binary flags
        if form_submission_filter:
            # Assuming a value of 1 (or "Yes") indicates a form submission; adjust if necessary.
            filtered_df = filtered_df[filtered_df["Form Submission YN"] == 1]
        if close_filter:
            filtered_df = filtered_df[filtered_df["Close YN"] == 1]

        # ----- Compute Additional Metrics -----
        # Create a "Tech Count" column that counts the number of web technologies (assumed binary indicators)
        if web_tech_columns:
            filtered_df["Tech Count"] = filtered_df[web_tech_columns].sum(axis=1)
        else:
            filtered_df["Tech Count"] = 0

        # ----- KPI Metrics -----
        st.markdown("---")
        st.subheader("Key Company Metrics Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            total_companies = filtered_df.shape[0]
            st.metric("Total Companies", total_companies)
        with col2:
            # Count companies with form submission (if available)
            form_count = filtered_df[filtered_df["Form Submission YN"] == 1].shape[0]
            st.metric("Companies with Form Submission", form_count)
        with col3:
            close_count = filtered_df[filtered_df["Close YN"] == 1].shape[0]
            st.metric("Companies with Close", close_count)

        # ----- Visualization 1: Company Type Distribution -----
        st.markdown("---")
        st.subheader("Company Type Distribution")
        # Count how many companies fall under each Type (sum binary flags)
        type_data = pd.DataFrame({
            "Type": selected_types,
            "Count": [filtered_df[col].sum() for col in selected_types]
        })
        bar_chart = alt.Chart(type_data).mark_bar().encode(
            x=alt.X("Type:N", sort='-y'),
            y=alt.Y("Count:Q", title="Number of Companies"),
            tooltip=["Type", "Count"]
        ).properties(width=600, height=400)
        st.altair_chart(bar_chart, use_container_width=True)

        # ----- Visualization 2: Top Primary Industries -----
        st.markdown("---")
        st.subheader("Top Primary Industries")
        # Sum across primary industry columns and display top 10 industries.
        primary_counts = {col: filtered_df[col].sum() for col in selected_primary}
        primary_df = pd.DataFrame(list(primary_counts.items()), columns=["Primary Industry", "Count"])
        primary_df = primary_df.sort_values("Count", ascending=False).head(10)
        bar_chart_primary = alt.Chart(primary_df).mark_bar().encode(
            x=alt.X("Primary Industry:N", sort='-y'),
            y=alt.Y("Count:Q", title="Number of Companies"),
            tooltip=["Primary Industry", "Count"]
        ).properties(width=600, height=400)
        st.altair_chart(bar_chart_primary, use_container_width=True)

        # ----- Visualization 3: Companies by Creation Year -----
        st.markdown("---")
        st.subheader("Companies by Creation Year")
        year_counts = filtered_df["Create Date_Year"].value_counts().reset_index()
        year_counts.columns = ["Year", "Count"]
        bar_chart_year = alt.Chart(year_counts).mark_bar().encode(
            x=alt.X("Year:O", title="Creation Year"),
            y=alt.Y("Count:Q", title="Number of Companies"),
            tooltip=["Year", "Count"]
        ).properties(width=600, height=400)
        st.altair_chart(bar_chart_year, use_container_width=True)

        # ----- Visualization 4: Distribution of Web Technology Usage -----
        st.markdown("---")
        st.subheader("Distribution of Web Technology Usage")
        hist_chart = alt.Chart(filtered_df).mark_bar().encode(
            x=alt.X("Tech Count:Q", bin=alt.Bin(maxbins=20), title="Number of Web Technologies Used"),
            y=alt.Y("count()", title="Number of Companies"),
            tooltip=["count()"]
        ).properties(width=600, height=400)
        st.altair_chart(hist_chart, use_container_width=True)

        # ----- Company Details & Recommendations -----
        st.markdown("---")
        st.subheader("Company Details and Recommendations")
        # Use the DataFrame index as an identifier for selection
        if not filtered_df.empty:
            selected_company = st.selectbox("Select a Company (by row index)", filtered_df.index.tolist())
            company_details = filtered_df.loc[selected_company]
            st.markdown("### Company Details")
            st.write(company_details)
            
            # Simple recommendation logic based on the count of web technologies
            tech_count = company_details["Tech Count"]
            recommendation = ""
            action_plan = ""
            if tech_count < 10:
                recommendation = "The company appears to use a limited set of web technologies."
                action_plan = "Consider engaging to understand if additional technologies could enhance operations."
            elif tech_count < 20:
                recommendation = "The company has a moderate technology stack."
                action_plan = "Evaluate opportunities for streamlined integration of additional tools."
            else:
                recommendation = "The company leverages a robust array of web technologies."
                action_plan = "Explore advanced solutions that may further optimize their tech stack."
            
            st.markdown("#### Recommendations")
            st.write(f"**Recommendation:** {recommendation}")
            st.write(f"**Action Plan:** {action_plan}")
        else:
            st.info("No companies match the selected filter criteria.")
