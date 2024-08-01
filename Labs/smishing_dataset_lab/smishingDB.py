# INSTRUCTIONS:
''' THIS CLASS IS USED TO INTERACT WITH THE SMISHING DATABASE.
    Functions:
    1. open_file: Opens the CSV file and loads it into a DataFrame.
    2. get_data_object: Returns the data object
    3. get_column_names: Returns the names of all columns in the DataFrame.
    4. get_messages_by_attribute: Returns rows where the specified column matches the given value.
    5. count_by_attribute: Counts and returns the number of occurrences of a value in a specified column.
    6. unique_values: Returns all unique values in the specified column.
    7. replace_value_in_column: Replaces all occurrences of old_value with new_value in the specified column.
    8. replace_full_column: Replaces the entire column with the new values provided.
    9. filter_by_attribute_and_get_results: Returns a list of values from 'result_column' where 'filter_column' matches 'filter_value'.
    10. save_data_to_file: Saves the DataFrame to a file in the specified format.
    11. get_full_column: Returns the full column of the specified column name.
    '''

import pandas as pd

class SmishingDB:
    def __init__(self, file_name):
        self.file_name = file_name
        self.data = None

    def open_file(self):
        """Opens the CSV file and loads it into a DataFrame."""
        try:
            self.data = pd.read_csv(self.file_name)
        except UnicodeDecodeError:
            try:
                self.data = pd.read_csv(self.file_name, encoding="ISO-8859-1")
            except Exception as e:
                print(f"An error occurred when trying with ISO-8859-1 encoding: {e}")
                try:
                    self.data = pd.read_csv(self.file_name, encoding="utf-8")
                except Exception as e:
                    print(f"An error occurred when trying with utf-8 encoding: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_data_object(self):
            """
            Returns:
                The data object if it has been loaded successfully, otherwise None.
            """
            if self.data is not None:
                return self.data
            else:
                print("Data not loaded. Please run open_file() first.")
                return None
        
    def get_column_names(self):
        """Returns the names of all columns in the DataFrame."""
        if self.data is not None:
            return self.data.columns.tolist()
        else:
            print("Data not loaded. Please run open_file() first.")
            return None
    
    def get_messages_by_attribute(self, column, value):
        """Returns rows where the specified column matches the given value."""
        if self.data is not None:
            if column in self.data.columns:
                return self.data[self.data[column] == value]
            else:
                print(f"Column '{column}' does not exist in the data.")
                return None
        else:
            print("Data not loaded. Please run open_file() first.")
            return None
    
    def count_by_attribute(self, column, value):
        """Counts and returns the number of occurrences of a value in a specified column."""
        if self.data is not None:
            if column in self.data.columns:
                return self.data[column].value_counts().get(value, 0)
            else:
                print(f"Column '{column}' does not exist in the data.")
                return None
        else:
            print("Data not loaded. Please run open_file() first.")
            return None
    
    def unique_values(self, column):
        """Returns all unique values in the specified column."""
        if self.data is not None:
            if column in self.data.columns:
                return self.data[column].unique()
            else:
                print(f"Column '{column}' does not exist in the data.")
                return None
        else:
            print("Data not loaded. Please run open_file() first.")
            return None

    def replace_value_in_column(self, column, old_value, new_value):
        """Replaces all occurrences of old_value with new_value in the specified column."""
        if self.data is not None:
            if column in self.data.columns:
                self.data[column] = self.data[column].replace(old_value, new_value)
            else:
                print(f"Column '{column}' does not exist in the data.")
        else:
            print("Data not loaded. Please run open_file() first.")
    
    def filter_by_attribute_and_get_results(self, filter_column, result_column, filter_value):
        """Returns a list of values from 'result_column' where 'filter_column' matches 'filter_value'."""
        if self.data is not None:
            if filter_column in self.data.columns and result_column in self.data.columns:
                filtered_data = self.data[self.data[filter_column] == filter_value][result_column]
                return filtered_data.tolist()
            else:
                print(f"One or both specified columns ('{filter_column}' or '{result_column}') do not exist in the data.")
                return None
        else:
            print("Data not loaded. Please run open_file() first.")
            return None
        
    def replace_full_column(self, column, new_values):
        """Replaces the entire column with the new values provided."""
        if self.data is not None:
            if column in self.data.columns:
                self.data[column] = new_values
            else:
                print(f"Column '{column}' does not exist in the data.")
        else:
            print("Data not loaded. Please run open_file() first.")
    
    def save_data_to_file(self, file_name, file_format='csv', index=False):
        """Saves the DataFrame to a file in the specified format."""
        if self.data is not None:
            try:
                if file_format.lower() == 'csv':
                    self.data.to_csv(file_name, index=index)
                elif file_format.lower() == 'excel':
                    self.data.to_excel(file_name, index=index)
                elif file_format.lower() == 'json':
                    self.data.to_json(file_name, orient='records')
                elif file_format.lower() == 'html':
                    self.data.to_html(file_name, index=index)
                else:
                    print(f"Unsupported file format: {file_format}")
            except Exception as e:
                print(f"An error occurred while saving the file: {e}")
        else:
            print("Data not loaded. Please run open_file() first.")

    def get_full_column(self, columnName):
        return self.data[columnName]
    
    def inflate_data_with_dataframe(self, df):
        self.data = pd.concat([self.data, df], ignore_index=True)
