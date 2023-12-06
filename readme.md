# IEEE Paper Data Crawling and Graph Relationship Analysis Project

## Project Overview

This project aims to crawl paper information from the IEEE (Institute of Electrical and Electronics Engineers) database and visually represent relationships between authors and citation relationships between papers. In the future, there are plans to integrate this data into a dedicated website platform for in-depth analysis of paper information. The project consists of two main modules: `essaycrawler.py` for paper data crawling and `graphdata.py` for data processing and graph visualization.

### `essaycrawler.py`

#### Overview

`essaycrawler.py` is the core component for crawling IEEE paper data, utilizing the IEEE API to obtain author information and citation relationships.

#### Dependencies

- Python 3.x
- Beautiful Soup (`bs4`)
- Requests (`requests`)
- Pandas (`pandas`)
- Logging (`logging`)
- JSON (`json`)
- Time (`time`)
- Random (`random`)
- OS (`os`)
- Argparse (`argparse`)

#### License

This module is licensed under the MIT license. Detailed license information can be found in the license statement within the source code.

#### Key Features

1. **`crawl_ieee_paper_authors`**: Get author information based on paper code.
2. **`crawl_ieee_reference`**: Get citation relationship information based on paper code.
3. **`get_essay_list`**: Obtain a list of IEEE papers based on search keywords.
4. **`make_request`**: Make HTTP requests and handle exceptions.
5. **`process_response`**: Process HTTP responses.
6. **`extract_authors`**: Extract authors from HTML responses.
7. **`extract_references`**: Extract citation relationship information from JSON responses.
8. **`extract_essay_list`**: Extract IEEE paper information from JSON responses.
9. **`main`**: Main function to execute the entire crawling process.

#### Usage

Pass search keywords, the maximum number of pages, and the output CSV file name as command-line parameters, for example:

```bash
python essaycrawler.py --search_keywords "social network" --max_pages 10 --file_name social_network_data
```

### `graphdata.py`

#### Overview

`graphdata.py` is responsible for processing the crawled data from `essaycrawler.py` and creating visual graphs using the NetworkX library. The generated graphs mainly represent relationships between authors and citation relationships between papers.

#### Dependencies

- Python 3.x
- Pandas (`pandas`)
- NetworkX (`networkx`)
- Logging (`logging`)
- OS (`os`)
- Argparse (`argparse`)

#### License

This module is licensed under the MIT license. Detailed license information can be found in the license statement within the source code.

#### Key Features

1. **`create_and_save_graph`**: Create graphs from a DataFrame and save them as GraphML files.
2. **`process_row`**: Process data rows and add edges to the graph.
3. **`create_output_directory`**: Create the output directory if it does not exist.
4. **`main`**: Main function to process social network paper data.

#### Usage

Pass the input CSV file path and the file paths for the output authors and references graphs as command-line parameters, for example:

```bash
python graphdata.py --input ./csvdata/social_network_essay_data_V2.csv --output_authors ./graphml/authors.graphml --output_references ./graphml/ref.graphml
```

## Future Plans

In the future, there are plans to develop a dedicated website platform for in-depth analysis of paper information. This platform will integrate the crawled data, providing a user-friendly interface and functionalities to meet users' needs for comprehensive exploration and visualization of paper information.

## Notes

1. Before using, ensure that all dependencies are installed. You can use the following command:

```bash
pip install beautifulsoup4 requests pandas networkx
```

2. Modify file paths and other configurations according to your project structure and requirements.

3. When executing the program, be mindful of the data crawling frequency to avoid unnecessary burden on the target website.

4. Adhere to the terms of use of the IEEE website to ensure legal and compliant use of the provided data.