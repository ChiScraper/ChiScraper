## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, re, argparse

from headers import Directories
from headers import WWFnFs

## ###############################################################
## FORMAT HELPFUL DETAILS ABOUT USER INPUT
## ###############################################################
class MyParser(argparse.ArgumentParser):
  def __init__(self, description):
    super(MyParser, self).__init__(
      description     = description,
      formatter_class = lambda prog: MyHelpFormatter(prog, max_help_position=50),
    )

  def error(self, message):
    sys.stderr.write("Error: {}\n\n".format(message))
    self.print_help()
    sys.exit(2)

class MyHelpFormatter(argparse.RawDescriptionHelpFormatter):
  def _format_action(self, action):
    parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
    if action.nargs == argparse.PARSER:
      parts = "\n".join(parts.split("\n")[1:])
    return parts


## ###############################################################
## GROUP DIFFERENT TYPES OF USER INPUTS
## ###############################################################
class GetUserInputs:
  def __init__(self):
    self.parser = MyParser(description="arXiv-Scraper: program to search for relevant arXiv papers.")
    self._addMainProgramArguments()
    self._addSearchArguments()
    self._addFetchArgument()
    ## parse all arguments and store them
    self.args = vars(self.parser.parse_args())

  def _addMainProgramArguments(self):
    """Sets up main program flag arguments."""
    dict_args = {
      "default": False,
      "required": False,
      "action": "store_true",
      "help": "Type: bool, default: %(default)s"
    }
    parse_flags = self.parser.add_argument_group(description="Main program flags:")
    parse_flags.add_argument("-s", "--search",   **dict_args)
    parse_flags.add_argument("-f", "--fetch",    **dict_args)
    parse_flags.add_argument("-s", "--score",     **dict_args)
    parse_flags.add_argument("-p", "--print",    **dict_args)
    parse_flags.add_argument("-d", "--download", **dict_args)
    parse_flags.add_argument("-w", "--webapp",   **dict_args)

  def _addSearchArguments(self):
    """Sets up search-specific arguments."""
    search_args = self.parser.add_argument_group(description="Search arguments (relevant when main program is run with `-s`):")
    search_args.add_argument("-c",  "--config_name",   type=str, required=False, metavar="", help="Name of the config-file that defines search parameters.")
    search_args.add_argument("-lb", "--lookback_days", type=int, required=False, metavar="", help="Lookback period (in days) to start search.")

  def _addFetchArgument(self):
    """Sets up fetch-specific arguments."""
    fetch_args = self.parser.add_argument_group(description="Fetch argument (relevant when running with `-f`):")
    fetch_args.add_argument("-id", type=str, required=False, metavar="", help="arXiv ID in the format `2310.17036`.")

  def getMainProgramInputs(self):
    """Returns only the main program flag."""
    ## check at least one program flag has been passed
    list_required_program_flags = [
      "search", "fetch", "score", "download", "webapp"
    ]
    str_error_message = "Error: At least one of the following program flags must be provided: " + ", ".join([
      f"--{key}"
      for key in list_required_program_flags
    ])
    if not any([
        self.args.get(key)
        for key in list_required_program_flags
      ]): self.parser.error(str_error_message)
    ## collect relevant main-program arguments
    dict_main_flags = {
      key: self.args.get(key)
      for key in [
        "search", "fetch", "score", "print", "download", "webapp"
      ]
    }
    return dict_main_flags

  def getSearchInputs(self):
    """Returns only the search-specific arguments and prompts for any missing parameters if required."""
    ## collect relevant search-related arguments
    dict_search_args = {
      key: self.args.get(key)
      for key in [
        "config_name", "lookback_days"
      ]
    }
    ## prompt for missing values
    if not dict_search_args["config_name"]: dict_search_args["config_name"] = input("Please provide --config_name: ")
    config_name = dict_search_args["config_name"]
    if not WWFnFs.fileExists(f"{Directories.directory_config}/{config_name}.json"):
      raise Exception(f"Error: Config file `{config_name}.json` does not exist under: {Directories.directory_config}")
    if dict_search_args["lookback_days"] is None: dict_search_args["lookback_days"] = int(input("Please provide --lookback_days: "))
    return dict_search_args

  def getFetchInputs(self):
    """Returns only the fetch-specific arguments, prompting if the arXiv ID is not passed, and validates the ID-format."""
    arxiv_id = self.args.get("id")
    ## prompt for missing value
    if arxiv_id is None:
      print("Which article do you want to fetch from the arXiv?")
      arxiv_id = input("Enter an arXiv ID (e.g., `2310.17036`): ")
    print(" ")
    ## check the arXiv ID follows the right format
    re_pattern = r"^\d{4}\.\d{4,5}$"
    if not re.match(re_pattern, arxiv_id): raise Exception(f"The ID you entered `{arxiv_id}` was invalid. Please enter it in the format `2310.17036`.")
    return arxiv_id


## END OF HEADER FILE