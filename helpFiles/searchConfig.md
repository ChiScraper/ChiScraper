# 1. Configuration File Structure

The configuration file is a JSON file that contains several key-value pairs. Each key represents a specific search criterion or setting, and the values define the parameters for that criterion. Here is a breakdown of the keys you can include in your configuration file:

# 2. Required Keys
## 2.1 config_tag:
**Type**: String
**Description**: A unique identifier for the configuration. This tag is used to label the articles retrieved using this configuration.
## 2.2 list_authors:
**Type**: List of Strings
**Description**: A list of author names to include in the search. If left empty, the search will not filter by authors.
## 2.3 list_categories:
**Type**: List of Strings
**Description**: A list of arXiv categories to search within. Each category is represented by its arXiv identifier (e.g., "astro-ph.IM").
## 2.4 list_keywords_exclude:
**Type**: List of Lists of Strings
**Description**: Keywords or phrases to exclude from the search. Articles containing any of these keywords will be filtered out.
## 2.5 list_keywords_include:
**Type**: List of Lists of Strings
**Description**: Keywords or phrases to include in the search. The script uses set theory to match these keywords. Each sublist represents a set of keywords that must all be present in an article for it to be considered relevant.

# 3 Example Configuration Files
Here are two example configuration files:
## 3.1 Quantum Optics Configuration
{
    "config_tag": "QuantumOptics",
    "list_authors": [],
    "list_categories": ["astro-ph.IM", "physics.optics", "eess.SP"],
    "list_keywords_exclude": [],
    "list_keywords_include": [
        ["quantum"],
        ["qubit"],
        ["QKD"],
        ["quantum", "key", "distribution"],
        ["quantum", "communication"]
    ]
}
## 3.2 FSOC Configuration
{
    "config_tag": "FSOC",
    "list_authors": [],
    "list_categories": ["astro-ph.IM", "physics.optics", "eess.SP"],
    "list_keywords_exclude": [],
    "list_keywords_include": [
        ["adaptive", "optics"],
        [["atmosphere", "atmospheric"], "turbulence"],
        ["wavefront", "sensor"],
        ["free", "space"],
        ["optical", "communication"]
    ]
}

# 4 How to Use the Configuration
1. Create a JSON file: Write your configuration in a JSON file, following the structure and examples provided above.
Place the file in the correct directory: Ensure the JSON file is located in the directory specified by the CONFIG_DIRECTORY in your script.
Run the script: Execute the search_arxiv.py script. It will read the configuration file, perform the search based on the specified criteria, and output the results as configured.
By following these steps, you can customize the search behavior of the script to suit your specific research needs.
