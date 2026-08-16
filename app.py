import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="IIT College Predictor", layout="wide")

# 2. Load the cleaned data
# @st.cache_data ensures the CSV is only loaded once into memory, making the app fast
# @st.cache_data
def load_data():
    return pd.read_csv('cleaned_iit_cutoffs_2026.csv')

try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file not found. Please ensure 'cleaned_iit_cutoffs_2026.csv' is in the same folder.")
    st.stop()

# 3. Sidebar for User Inputs
st.sidebar.header("Your Details")
user_rank = st.sidebar.number_input("Enter your Rank:", min_value=1, value=1500, step=1)

# Get unique branches for the dropdown dynamically from the dataset
available_branches = df['Branch'].unique().tolist()

# Multiselect allows users to pick multiple branches in a specific order
selected_branches = st.sidebar.multiselect(
    "Select Preferred Branches (in order of priority):",
    options=available_branches,
    help="The order in which you select branches will dictate the sorting order."
)

st.title("🎓 IIT College Predictor")
st.write("Find eligible colleges based on the 2026 OR-CR data.")

# 4. Filtering Logic
def filter_and_sort_data(data, rank, branches):
    # Filter to only show colleges where the closing rank is >= the user's rank
    filtered_df = data[data['Closing_Rank'] >= rank]
    
    if branches:
        # Filter to only include the specific branches the user selected
        filtered_df = filtered_df[filtered_df['Branch'].isin(branches)].copy()
        
        # Sort by the exact priority order selected by the user
        branch_category = pd.CategoricalDtype(categories=branches, ordered=True)
        filtered_df['Branch'] = filtered_df['Branch'].astype(branch_category)
        
        # Sort primarily by Branch priority, then by Closing Rank
        filtered_df.sort_values(by=['Branch', 'Closing_Rank'], inplace=True)
    else:
        # If no branches are selected, just show everything sorted by Closing Rank
        filtered_df.sort_values(by=['Closing_Rank'], inplace=True)
        
    return filtered_df.reset_index(drop=True)

# 5. Displaying Data Separately for Male and Female using Tabs
tab_male, tab_female = st.tabs(["Male Candidates", "Female Candidates"])

with tab_male:
    st.subheader("Eligible Colleges for Male Candidates")
    male_data = df[df['Gender'] == 'Male']
    result_male = filter_and_sort_data(male_data, user_rank, selected_branches)
    
    if result_male.empty:
        st.warning("No colleges found for this rank and branch combination.")
    else:
        st.dataframe(result_male[['Institute', 'Branch', 'Opening_Rank', 'Closing_Rank']], use_container_width=True)

with tab_female:
    st.subheader("Eligible Colleges for Female Candidates")
    female_data = df[df['Gender'] == 'Female']
    result_female = filter_and_sort_data(female_data, user_rank, selected_branches)
    
    if result_female.empty:
        st.warning("No colleges found for this rank and branch combination.")
    else:
        st.dataframe(result_female[['Institute', 'Branch', 'Opening_Rank', 'Closing_Rank']], use_container_width=True)