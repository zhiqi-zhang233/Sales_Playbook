# Sales Success Playbook Project

## Overview
This project, developed for the DS 5640 Machine Learning course at Vanderbilt University, focuses on improving sales strategy using data-driven insights. The team built a predictive and interactive system that allows sales teams to:

- Segment customers using clustering algorithms and RFM analysis
- Predict deal success using machine learning models
- Visualize insights through a custom Streamlit dashboard
- Deploy the solution using Docker for consistency and scalability

We used three datasets (companies, deals, tickets) to understand customer behavior, forecast outcomes, and generate actionable recommendations across the sales lifecycle.

## Key Features
- **Customer Segmentation**: Applied K-Means clustering after dimensionality reduction to identify high-value customer groups.
- **Deal Prediction**: Trained and evaluated Logistic Regression, Random Forest, and XGBoost—achieving best performance with XGBoost (AUC = 0.919).
- **Interactive Dashboard**: Built with Streamlit to support data exploration, personalized recommendations, and filtering by account, deal, or ticket.
- **Deployment**: Packaged the dashboard in Docker for reproducible deployment across systems.

## Technologies Used
- Python, Pandas, Scikit-learn, XGBoost
- Streamlit for dashboarding
- Docker for deployment
- Git/GitHub for version control

## Repository Structure
📦Sales_Playbook
┣ 📂.ipynb_checkpoints
┣ 📂data
┣ 📂streamlit_app
┣ 📄EDA of tickets.ipynb
┣ 📄Final_code.ipynb
┣ 📄Model.ipynb
┣ 📄Dockerfile
┣ 📄app.py
┣ 📄docker.ipynb
┣ 📄sales-pipeline-processing.ipynb
┣ 📄mappings.json
┗ 📄README.md

## Authors
- **Zhiqi (Camille) Zhang** – zhiqi.zhang@vanderbilt.edu  
- **Ashley Stevens** – ashley.m.stevens@vanderbilt.edu  
- **Brooke Stevens**

## Future Work
We plan to:
- Integrate SHAP explainability into model predictions
- Expand time-series forecasting for deal progression
- Add simulation tools for scenario planning within the dashboard
