"""
Data validation utilities for ETL pipelines.
"""
import logging
from typing import List, Dict, Any, Callable, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class DataValidator:
    """Data validation utilities for ETL pipelines."""
    
    @staticmethod
    def validate_dataframe(
        df: pd.DataFrame, 
        required_columns: List[str],
        validation_rules: Optional[Dict[str, Callable]] = None
    ) -> Dict[str, Any]:
        """
        Validate a pandas DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame to validate
            required_columns (List[str]): List of required column names
            validation_rules (Dict[str, Callable]): Column name to validation function mapping
            
        Returns:
            Dict[str, Any]: Validation results
        """
        validation_results = {
            "is_valid": True,
            "missing_columns": [],
            "validation_errors": [],
            "row_count": len(df)
        }
        
        # Check for missing columns
        for col in required_columns:
            if col not in df.columns:
                validation_results["missing_columns"].append(col)
                validation_results["is_valid"] = False
        
        # Apply validation rules if any
        if validation_rules and not validation_results["missing_columns"]:
            for col, validation_func in validation_rules.items():
                if col in df.columns:
                    try:
                        is_valid = validation_func(df[col])
                        if not is_valid:
                            validation_results["validation_errors"].append(
                                f"Validation failed for column: {col}"
                            )
                            validation_results["is_valid"] = False
                    except Exception as e:
                        validation_results["validation_errors"].append(
                            f"Error validating column {col}: {str(e)}"
                        )
                        validation_results["is_valid"] = False
        
        return validation_results
    
    @staticmethod
    def check_for_duplicates(df: pd.DataFrame, key_columns: List[str]) -> Dict[str, Any]:
        """
        Check for duplicate records in a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame to check
            key_columns (List[str]): Columns that should be unique together
            
        Returns:
            Dict[str, Any]: Results with duplicate count and examples
        """
        duplicate_rows = df[df.duplicated(subset=key_columns, keep=False)]
        duplicate_count = len(duplicate_rows)
        
        results = {
            "has_duplicates": duplicate_count > 0,
            "duplicate_count": duplicate_count,
            "duplicate_examples": []
        }
        
        if duplicate_count > 0:
            # Get example duplicates (limit to 5)
            example_keys = []
            for _, row in duplicate_rows.iterrows():
                key_values = tuple(row[key_columns].values)
                if key_values not in example_keys:
                    example_keys.append(key_values)
                    if len(example_keys) >= 5:
                        break
            
            results["duplicate_examples"] = [dict(zip(key_columns, key)) for key in example_keys]
            
        return results
    
    @staticmethod
    def check_null_values(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Check for null values in a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame to check
            
        Returns:
            Dict[str, Any]: Results with null counts by column
        """
        null_counts = df.isnull().sum().to_dict()
        has_nulls = any(count > 0 for count in null_counts.values())
        
        return {
            "has_nulls": has_nulls,
            "null_counts": null_counts,
            "total_nulls": sum(null_counts.values())
        }
