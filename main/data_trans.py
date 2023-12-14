import pandas as pd
import csv
import module.co_occurrence_Matrix

def process_author_column(input_csv_path, output_csv_path):
    def replace_by_comma(text):
        return text.replace(";", ",")

    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv_path)

    # Apply the replace_by_comma function to the "author" column
    df["author"] = df["author"].apply(replace_by_comma)

    # Split the "author" column by commas
    processed_data = [row.split(',') if row else [] for row in df["author"]]

    # Write the processed data to a new CSV file with utf-8 encoding
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as output_file:
        csv_writer = csv.writer(output_file)

        # Write each processed row to the CSV file
        csv_writer.writerows(processed_data)

    print(f'Data has been written to {output_csv_path}')

# Example usage
input_path = "../csvdata/social_network_essay_data_V2.csv"
output_path = 'output_data/author_tmp.csv'
process_author_column(input_path, output_path)
