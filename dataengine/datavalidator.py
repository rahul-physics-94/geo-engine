import pandas as pd
import numpy as np
from typing import Literal
import re

geo_pattern: dict[str, str] = {
    "city": r"^[^\W\d_][\w\s.'’()-]*$",
    "postcode": r"^[A-Za-z0-9][A-Za-z0-9\s-]{1,11}$",
    "latitude": r"^[+-]?(?:90(?:\.0+)?|[0-8]?\d(?:\.\d+)?)$",
    "longitude": r"^[+-]?(?:180(?:\.0+)?|1[0-7]\d(?:\.\d+)?|[0-9]?\d(?:\.\d+)?)$",
    "state": r"^[^\W\d_][\w\s.'’()-]*$",
    "country": r"^[^\W\d_][\w\s.'’()-]*$",
    "region": r"^[^\W\d_][\w\s.'’()-]*$",
    "district": r"^[^\W\d_][\w\s.'’()-]*$",
    "province": r"^[^\W\d_][\w\s.'’()-]*$",
    "municipality": r"^[^\W\d_][\w\s.'’()-]*$",
    "borough": r"^[^\W\d_][\w\s.'’()-]*$",
    "ward": r"^[^\W\d_][\w\s.'’()-]*$",
    "census_tract": r"^\d{1,6}(?:\.\d{1,6})?$",
    "census_block": r"^\d{1,10}$",
    "zip_code": r"^[A-Za-z0-9][A-Za-z0-9\s-]{1,11}$",
    "fips_code": r"^\d{5}$",
}

geo_codes = list(geo_pattern)

class DataChecker:
    """
    A class for validating datasets against a given schema.
    """

    def __init__(self, df: pd.DataFrame, schema: dict, dataset_type: str) -> None:
        """
        Initialize the DataValidator with a DataFrame and a schema.

        Args:
            df (pd.DataFrame): The DataFrame to validate.
            schema (dict): The schema to validate against.
            dataset_type (str): The type of dataset (e.g., "geo", "population", "confounders").
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError('df must be a pandas dataframe')
        
        self.df = df
        self.schema = schema
        self.dataset_type = dataset_type
    @staticmethod
    def _result(success: bool, message:str, **details:any) -> dict:
        return {
            "success": success,
            "message": message,
            **details,
        }


    def GeoChecker(self, df: pd.DataFrame) -> dict:
        """
        Check for valid geographic coordinates in the DataFrame.

        Returns:
            bool: True if all coordinates are valid, False otherwise.
        """
        cols = set(df.columns)
        try:
            if 'latitude' in cols and 'longitude' in cols:
                invalid_lat = df[(df['latitude'] < -90) | (df['latitude'] > 90)]
                invalid_lon = df[(df['longitude'] < -180) | (df['longitude'] > 180)]
                if not invalid_lat.empty or not invalid_lon.empty:
                    print("Invalid geographic coordinates found.")
                    return False
            elif any(code in cols for code in geo_codes):
                try:
                    x = geo_codes.index(next(code for code in geo_codes if code in cols))
                    temp_df = df[geo_codes[x]].value_counts().reset_index()
                    temp_df.columns = [geo_codes[x], 'count']
                    for i in range(len(temp_df)):
                        if temp_df['count'][i] - temp_df['count'][i+1] > 0 or temp_df['count'][i] - temp_df['count'][i+1] < 0:
                            print(f"{geo_codes[x].replace('_', ' ').title()} {temp_df[geo_codes[x]][i]} has inconsistent counts.")
                            return False
                        elif " " in temp_df[geo_codes[x]][i]:
                            print(f"{geo_codes[x].replace('_', ' ').title()} {temp_df[geo_codes[x]][i]} contains whitespace.")
                            return False
                        elif temp_df['count'][i] == 0:
                            print(f"{geo_codes[x].replace('_', ' ').title()} {temp_df[geo_codes[x]][i]} has zero count.")
                            return False
                        elif df.duplicated(subset=[geo_codes[x],df.select_dtypes['datetime64[ns]', 'datetime64[ns, UTC]'].columns].sum()).any():
                            print(f"There are duplicated dates for {temp_df[geo_codes[x]][i]}. Please remove the duplicated date and try again")
                        else:
                            return True
                    
                except Exception as e:
                    print(f"Error in GeoChecker: {e}")
                    return False
            elif 'latitude' not in cols and 'longitude' not in cols and not any(code in cols for code in geo_codes):
                print("No geographic columns found for validation.")
                return False
            else:
                print("No geographic columns found for validation.")
                return True

        except Exception as e:
            print(f"Error in GeoChecker: {e}")
            return False

        try:
            x = [col for col in geo_codes if col in cols]
            for col in x:
                if col in geo_codes:
                    pattern = geo_pattern[col]
                    invalid_entries = df[~df[col].astype(str).str.fullmatch(pattern, na = False)]
                    if not invalid_entries.empty:
                        print(f"Invalid entries found in column '{col}':")
                        print(invalid_entries)
                        return False
            return True
        except Exception as e:
            print(f"Error in GeoChecker: {e}")
            return False
        
        return True

    def DatTimeChecker(self, df: pd.DataFrame) -> bool:
        """
        Check for valid datetime columns in the DataFrame.

        Returns:
            bool: True if all datetime columns are valid, False otherwise.
        """
        datetime_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
        try:
            for col in datetime_cols:
                if not pd.api.types.is_datetime64_any_dtype(df[col]):
                    print(f"Column '{col}' is not a valid datetime column.")
                    return False
                elif df[col].isnull().all():
                    print(f"Column '{col}' contains only NaN values.")
                    return False
                elif df[col].nunique() <= 1:
                    print(f"Column '{col}' has insufficient unique values for datetime validation.")
                    return False
                elif df[col].frequency().nunique() < 2:
                    print(f"Column '{col}' has insufficient frequency variation for datetime validation.")
                    return False
                elif df[col].is_monotonic_increasing or df[col].is_monotonic_decreasing:
                    print(f"Column '{col}' is monotonic and may not be suitable for datetime validation.")
                    return False
                else:
                    print(f"Column '{col}' passed all datetime validations.")
                dates = pd.to_datetime(df[col]).drop_duplicates().sort_values()
                diffs = dates.diff().dt.days
                most_common_diff = diffs.mode()[0]
                if (diffs != most_common_diff).any():
                    print(f"Column '{col}' has inconsistent time intervals.")
                    return False
                elif most_common_diff <= 0:
                    print(f"Column '{col}' has non-positive time intervals. The date time requires further sorting and cleaning.")
                    return False
                else:
                    print(f"Column '{col}' has consistent time intervals.")
        except Exception as e:
            print(f'Error in DateTimeChecker:{e}')
        

        return True

    def NumericalIntegrity(self, df: pd.DataFrame):
        """
        Check for valid numerical columns in the DataFrame.

        Returns:
            bool: True if all numerical columns are valid, False otherwise.
        """
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        result = {
            "success" : False,
            "message": None,
            "errors":[],
            "missing_values":{},
            "invalid_columns":[],
            "validated_columns":[]
        }
        try:
            for col in numerical_cols:
                if df[col].isnull().all():
                    result['errors'].append(
                        f"Column '{col}' contains only NaN values."
                        )
                    result['invalid_columns'].append(col)
                
                elif df[col].nunique() <= 1:
                    result['errors'].append(
                        f"Column '{col}' has insufficient unique values for numerical validation."
                        )
                    result['invalid_columns'].append(col)
                elif (df[col] < 0).any():
                    result['errors'].append(
                        f"Column '{col}' contains negative values."
                        )
                    result['invalid_columns'].append(col)
                else:
                    result['validated_columns'].append(col)

        except Exception as e:
            result['message'].append("Numerical Validation Failed")
            result['errors'].append(
                str(e)
                )
        else:
            result['missing_values'] = (
                df[numerical_cols].isnull.sum().to_dict()
            )
            if result['invalid_columns']:
                result['message'] = "Numerical Validation Failed for some columns"
            else:
                result['success'] = True
                result['message'] = 'All Numerical Validation Checks passed'
        finally:
            result['execution_complete'] = True        


        return result

