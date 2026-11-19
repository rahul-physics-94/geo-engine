import pandas as pd


import streamlit as st
from dataengine.schemavalidator import LoadSchema, ValidateDataFrame


st.set_page_config(
    page_title="Data Validation and Visualization",
    layout="wide"
)

st.title("Data Validation")

try:
    with st.container(border = True):
        st.subheader("Upload Dataset")
        uploaded_file = st.file_uploader("Upload your dataset (CSV format)", type=["csv", "xlsx"])

        dataset_type = st.selectbox("Select the dataset type", 
                                    ["geo", "population", "confounders"])

        if uploaded_file is None:
            st.warning("Please upload a dataset to proceed.")
            st.stop()

        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a CSV or Excel file.")
                st.stop()

        schema = LoadSchema(f"dataengine/config_schema.yaml")

        try:
            is_valid = ValidateDataFrame(df, schema, dataset_type)
            if is_valid:
                st.success("Dataset is valid according to the schema.")
        except Exception as e:
            st.error(f"Dataset validation failed: {e}")
            st.stop()
    with st.container(border = True):
        st.subheader("Dataset Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Rows", df.shape[0])

        with col2:
            st.metric("Columns", df.shape[1])

        with col3:
            st.metric("Missing Values", int(df.isna().sum().sum()))

        st.subheader("Dataset preview:")
        st.dataframe(df.head())

        st.subheader("Dataset summary statistics:")
        st.dataframe(df.select_dtypes(include=['datetime64[ns]']).describe().loc[['count', 'min', 'max']].transpose())


        st.subheader("Column Information")

        column_info = pd.DataFrame({
            "Data Type": df.dtypes.astype(str),
            "Non-null Count": df.notna().sum(),
            "Missing Count": df.isna().sum(),
            "Missing (%)": (df.isna().mean() * 100).round(2)
        })

        st.dataframe(column_info, width=True)
except Exception as e:
    st.error(f"An error occurred: {e}")