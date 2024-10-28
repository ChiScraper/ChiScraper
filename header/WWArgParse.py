import sys, argparse


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
  

## END OF HEADER FILE