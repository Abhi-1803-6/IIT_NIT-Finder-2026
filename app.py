import streamlit as st
import pandas as pd

st.set_page_config(page_title="College Predictor 2026", layout="wide")

# 1. Load the unified data
# Remove the @st.cache_data decorator temporarily if you are still making changes to the CSV
#@st.cache_data
def load_data():
    return pd.read_csv('cleaned_all_colleges_2026.csv')

try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file not found. Please ensure 'cleaned_all_colleges_2026.csv' is in the same folder.")
    st.stop()

# 2. Main Title
st.title("🎓 College Predictor 2026")
st.write("Find eligible colleges based on the 2026 OR-CR data.")

# 3. Sidebar toggle for College Type
st.sidebar.header("Select College Type")
# Use a radio button to toggle between IIT (Advanced) and NIT (Mains OBC)
college_type = st.sidebar.radio("Target Institution:", options=["IIT", "NIT"])

# Filter the main dataframe based on the toggle selection immediately
df_filtered_by_type = df[df['Type'] == college_type].copy()

# 4. Dynamic Sidebar Inputs based on toggle
st.sidebar.header("Your Details")

# Change the input label to make it clear which rank is needed
if college_type == "IIT":
    rank_label = "Enter your JEE Advanced Rank (CRL):"
else:
    rank_label = "Enter your JEE Mains Rank (OBC-NCL):"

user_rank = st.sidebar.number_input(rank_label, min_value=1, value=1500, step=1)

# Dynamically populate branches ONLY for the selected college type
available_branches = df_filtered_by_type['Branch'].unique().tolist()

selected_branches = st.sidebar.multiselect(
    f"Select Preferred {college_type} Branches (in order):",
    options=available_branches,
    help="The order in which you select branches will dictate the sorting order."
)

# 5. Filtering and Sorting Logic
def filter_and_sort_data(data, rank, branches):
    # Filter by closing rank
    filtered = data[data['Closing_Rank'] >= rank]
    
    if branches:
        # Filter by selected branches
        filtered = filtered[filtered['Branch'].isin(branches)].copy()
        
        # Sort by user's branch priority
        branch_category = pd.CategoricalDtype(categories=branches, ordered=True)
        filtered['Branch'] = filtered['Branch'].astype(branch_category)
        filtered.sort_values(by=['Branch', 'Closing_Rank'], inplace=True)
    else:
        # Sort by Closing Rank if no branches selected
        filtered.sort_values(by=['Closing_Rank'], inplace=True)
        
    return filtered.reset_index(drop=True)

# 6. Display Data Separately for Male and Female using Tabs
st.subheader(f"Eligible {college_type}s for Rank: {user_rank}")
tab_male, tab_female = st.tabs(["Male Candidates", "Female Candidates"])

with tab_male:
    male_data = df_filtered_by_type[df_filtered_by_type['Gender'] == 'Male']
    result_male = filter_and_sort_data(male_data, user_rank, selected_branches)
    
    if result_male.empty:
        st.warning("No colleges found for this rank and branch combination.")
    else:
        st.dataframe(result_male[['Institute', 'Branch', 'Opening_Rank', 'Closing_Rank']], use_container_width=True)

with tab_female:
    female_data = df_filtered_by_type[df_filtered_by_type['Gender'] == 'Female']
    result_female = filter_and_sort_data(female_data, user_rank, selected_branches)
    
    if result_female.empty:
        st.warning("No colleges found for this rank and branch combination.")
    else:
        st.dataframe(result_female[['Institute', 'Branch', 'Opening_Rank', 'Closing_Rank']], use_container_width=True)