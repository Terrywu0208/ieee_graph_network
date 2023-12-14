"""
Copyright © 2023 Chia En Wu (GitHub: terrywu28)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import pandas as pd
import networkx as nx
import json
import logging
from itertools import combinations
import argparse
import time

# Set up logging configuration
log_file_path = 'error_log.txt'
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Add a StreamHandler to print logs to the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

# Constants
INPUT_FILE_PATH = './csvdata/social_network_essay_data_V2.csv'
OUTPUT_DIRECTORY = './graphml/'
OUTPUT_AUTHORS_GRAPHML = os.path.join(OUTPUT_DIRECTORY, 'authors.graphml')
OUTPUT_REFERENCES_GRAPHML = os.path.join(OUTPUT_DIRECTORY, 'ref.graphml')

def create_and_save_graph(data_frame, authors_col, references_col, output_file):
    """Create a graph from the given data and save it to a GraphML file.

    Args:
        data_frame (pd.DataFrame): The input DataFrame containing the essay data.
        authors_col (str): The column name containing authors' information.
        references_col (str): The column name containing references' information.
        output_file (str): The output GraphML file path.
    """
    try:
        graph = nx.Graph()

        data_frame.apply(lambda row: process_row(row, graph, authors_col, references_col), axis=1)

        nx.write_graphml(graph, output_file)

    except Exception as e:
        error_message = (f"Error creating and saving graph: {e}")
        logging.error(error_message)

def process_row(row, graph, authors_col, references_col):
    """Process a row of data and add edges to the graph.

    Args:
        row (pd.Series): The row of data from the DataFrame.
        graph (nx.Graph): The graph to which edges will be added.
        authors_col (str): The column name containing authors' information.
        references_col (str): The column name containing references' information.
    """
    try:
        items = row[authors_col].split(';') if authors_col in row else json.loads(row[references_col]).keys()
        for pair in combinations(items, 2):
            graph.add_edge(pair[1], row["title"])

    except Exception as e:
        error_message = (f"Error processing row: {e}")
        logging.error(error_message)

def create_output_directory(output_directory):
    """Create the output directory if it does not exist.

    Args:
        output_directory (str): The path to the output directory.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        error_message = (f"Output directory '{output_directory}' created.")
        logging.info(error_message)

def main():
    """Main function to process social network essay data."""
    try:
        parser = argparse.ArgumentParser(description="Process social network essay data.")
        parser.add_argument('--input', default=INPUT_FILE_PATH, help='Input CSV file path')
        parser.add_argument('--output_authors', default=OUTPUT_AUTHORS_GRAPHML, help='Output authors graphml file path')
        parser.add_argument('--output_references', default=OUTPUT_REFERENCES_GRAPHML, help='Output references graphml file path')
        args = parser.parse_args()

        output_directory = os.path.dirname(args.output_authors)
        create_output_directory(output_directory)

        logging.info(f"Reading data from: {args.input}")
        data_frame = pd.read_csv(args.input)

        logging.info("Creating and saving authors graphml...")
        create_and_save_graph(data_frame, 'author', None, args.output_authors)

        logging.info("Creating and saving references graphml...")
        create_and_save_graph(data_frame, None, 'reference', args.output_references)

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
