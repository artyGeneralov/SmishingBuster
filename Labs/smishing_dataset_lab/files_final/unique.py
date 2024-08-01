import pandas as pd

def main():
    file1 = 'smishingDB.csv'
    file2 = 'spam.csv'
    output_file = 'unique.csv'
    find_unique_entries(file1, file2, output_file)

def find_unique_entries(file1, file2, output_file):
    # Load the two CSV files into dataframes
    df1 = open_file(file1)
    df2 = open_file(file2)
    
    # Extract 'TEXT' columns
    text_df1 = df1[['TEXT']]
    text_df2 = df2[['TEXT']]
    
    # Find the 'TEXT' entries that are in spam but not in smishingDB
    unique_to_spam = text_df2[~text_df2['TEXT'].isin(text_df1['TEXT'])]
    
    # Get the corresponding rows from the original spam dataframe
    unique_df = df2[df2['TEXT'].isin(unique_to_spam['TEXT'])]
    
    # Save the unique entries to a new CSV file
    unique_df.to_csv(output_file, index=False)
    print(f"Unique entries have been written to {output_file}")

def open_file(file_name):
    """Opens the CSV file and loads it into a DataFrame."""
    try:
        data = pd.read_csv(file_name)
        return data
    except UnicodeDecodeError:
        try:
            data = pd.read_csv(file_name, encoding="ISO-8859-1")
            return data
        except Exception as e:
            print(f"An error occurred when trying with ISO-8859-1 encoding: {e}")
        try:
            data = pd.read_csv(file_name, encoding="utf-8")
            return data
        except Exception as e:
            print(f"An error occurred when trying with utf-8 encoding: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__": 
    main()