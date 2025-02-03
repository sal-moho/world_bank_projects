import streamlit as st
import pandas as pd
import country_converter as coco
import plotly.express as px

cc = coco.CountryConverter()

@st.cache_data
def fetch_project_data():
    projects_df = pd.read_excel("https://search.worldbank.org/api/v3/projects/all.xlsx", header=2)
    total_projects = projects_df.shape[0]
    return total_projects, projects_df

@st.cache_data
def find_unique_countries(projects_df):
    country_list = projects_df["countryshortname"].unique()
    return country_list

def select_country(country, df):
    country_df = df[df["countryshortname"] == country]
    return country_df


st.title("World Bank Projects explorer :globe_with_meridians:")
st.markdown("""World Bank Projects & Operations provides access to basic information 
            on all of the World Bank's lending projects from 1947 to the present through their
            [data catalogue](https://datacatalog.worldbank.org/search/dataset/0037800). This app provides a global overview of these and
            details on individual country's projects.  
            *This app was created as a personal project for learning Streamlit and is not affiliated
            with the World Bank.*
            """)

total_projects, projects_df = fetch_project_data()
st.markdown(f"""**Total number of World Bank projects: {total_projects}**""")

countries_col1, countries_col2 = st.columns([2,4])

project_count = projects_df.groupby("countryshortname").size().reset_index(name='counts')
with countries_col1:
    st.dataframe(project_count.sort_values("counts", ascending=False), hide_index = True,
                 column_config = {"countryshortname" : "Country/region", "counts": "No. projects"})

projects_df["country_code"] = cc.pandas_convert(series = projects_df["countryshortname"], to = "ISO3")
countries_df = projects_df[projects_df["country_code"] != "not found"]
countries_project_count = countries_df.groupby("country_code").size().reset_index(name='counts')
countries_project_count["Country"] = cc.pandas_convert(series = countries_project_count["country_code"], to = "name_short")
fig = px.choropleth(countries_project_count, locations="country_code",
                    color="counts",
                    hover_name="Country",
                    labels = {"counts":"No. projects"},
                    color_continuous_scale=px.colors.sequential.Plotly3_r)

with countries_col2:
    st.plotly_chart(fig)

st.header("Country fact sheet")
country_list = sorted(list(find_unique_countries(countries_df)))
selected_country = st.selectbox("Select country", country_list)
country_df = select_country(selected_country, projects_df)

country_total_projects = country_df.shape[0]
country_total_commitment = country_df["curr_total_commitment"].sum()
selected_country_code_iso2 = cc.convert(names = [list(country_df["country_code"])[0]], to = "ISO2")
flag_emoji = (f":flag-{selected_country_code_iso2}:").lower()

st.write(f"""{flag_emoji} Total projects: {country_total_projects}  
{flag_emoji} Total commitment value (US $): {country_total_commitment}""")


country_df_datecount = country_df.groupby("boardapprovaldate").size().cumsum().reset_index().rename(columns = {0:"count"})
country_project_count_fig = px.line(country_df_datecount, x = "boardapprovaldate", y = "count")
country_project_count_fig.update_layout(xaxis_title='Time (board approval date)', yaxis_title='Project count')
st.plotly_chart(country_project_count_fig)

country_column_config = {
    "id" : "Project ID",
    "status" : "Status",
    "last_stage_reached_name" : "Last stage reached",
    "project_name" : "Project name",
    "pdo" : "Development objective",
    "impagency" : "Implementing agency",
    "public_disclosure_date" : "Public disclosure_date",
    "boardapprovaldate" : "Board approval date",
    "loan_effective_date" : "Loan effective date",
    "closingdate" : "Closing date",
    "curr_total_commitment" : "Current total commitment (US $)",
    "borrower" : "Borrower",
    "regionname" : None,
    "countryshortname" : None,
    "curr_project_cost" : None,
    "curr_ibrd_commitment" : None,
    "idacommamt" : None,
    "grantamt" : None,
    "lendinginstr" : None,
    "envassesmentcategorycode" : None,
    "esrc_ovrl_risk_rate" : None,
    "supplementprojectflg" : None,
    "cons_serv_reqd_ind" : None,
    "projectfinancialtype" : None,
    "country_code" : None,
}

st.dataframe(country_df.sort_values("boardapprovaldate", ascending = False), hide_index = True, column_config = country_column_config)