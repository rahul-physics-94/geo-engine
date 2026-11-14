from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from typing import Any, Dict, Union
import yaml
from pathlib import Path
import pandas as pd


class column_definition(BaseModel):
    """
    column_definition is a class that defines the structure and types of columns in the dataset.
    It uses Pydantic's BaseModel to ensure data integrity and validation.
    """
    dtype: Literal["int", "float", "str", "bool", "datetime"]
    required: bool = True
    min_value: float | None = None
    max_value: float | None = None      
    allowed_values: List[Any] | None = None

class dataset_definition(BaseModel):
    """
    dataset_definition is a class that defines the structure of the dataset.
    It uses Pydantic's BaseModel to ensure data integrity and validation.
    """
    name: str
    version: str
    description: str | None = None
    columns: Dict[str, column_definition]

class schema_definition(BaseModel):
    """
    schema_definition is a class that defines the structure of the schema.
    It uses Pydantic's BaseModel to ensure data integrity and validation.
    """
    datasets: dict[str, dataset_definition]


def load_schema(schema_path: Union[str, Path]) -> schema_definition:
    """
    Load and validate a schema from a YAML file.

    Args:
        schema_path (Union[str, Path]): The path to the YAML schema file.
        """
    # Load the YAML file
    with open(schema_path, 'r') as file:
        schema_dict = yaml.safe_load(file)

    # Validate and create a schema_definition instance
    validated_schema = schema_definition(**schema_dict)
    return validated_schema


    
def data_validator(
        df:pd.DataFrame,
        schema: schema_definition,
        dataset_type: str   
):
    """
    Validate a DataFrame against a given schema.

    Args:
        df (pd.DataFrame): The DataFrame to validate.
        schema (schema_definition): The schema to validate against.
        dataset_type (str): The type of dataset to validate (e.g., "geo_dataset", "time_series_dataset").

    Returns:
        bool: True if the DataFrame is valid, False otherwise.
    """
    datetime_columns = ['date', 'week', 'month', 'quarter', 'year']
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    for column_name, column_def in schema.datasets[dataset_type].columns.items():
        if column_name not in df.columns:
            if column_def.required:
                raise ValueError(f"Missing required column: {column_name}")
            else:
                continue  # Skip optional columns

        # Validate data type
        if column_def.dtype == "int":
            if not pd.api.types.is_integer_dtype(df[column_name]):
                raise TypeError(f"Column {column_name} must be of type int")
        elif column_def.dtype == "float":
            if not pd.api.types.is_float_dtype(df[column_name]):
                raise TypeError(f"Column {column_name} must be of type float")
        elif column_def.dtype == "str":
            if not pd.api.types.is_string_dtype(df[column_name]):
                raise TypeError(f"Column {column_name} must be of type str")
        elif column_def.dtype == "bool":
            if not pd.api.types.is_bool_dtype(df[column_name]):
                raise TypeError(f"Column {column_name} must be of type bool")
        elif column_def.dtype == "datetime":
            if not pd.api.types.is_datetime64_any_dtype(df[column_name]):
                raise TypeError(f"Column {column_name} must be of type datetime")

        # Validate min and max values for numeric columns
        if column_def.min_value is not None:
            if (df[column_name] < column_def.min_value).any():
                raise ValueError(f"Column {column_name} has values below the minimum of {column_def.min_value}")
        if column_def.max_value is not None:
            if (df[column_name] > column_def.max_value).any():
                raise ValueError(f"Column {column_name} has values above the maximum of {column_def.max_value}")

        # Validate allowed values for categorical columns
        if column_def.allowed_values is not None:
            if not df[column_name].isin(column_def.allowed_values).all():
                raise ValueError(f"Column {column_name} contains values outside the allowed set: {column_def.allowed_values}")

    return True
