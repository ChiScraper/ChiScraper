import os
os.system("clear")


def printHeading(str):
  print(str)
  print("=" * len(str))


def allKeywordsInPhrase(phrase, list_search_terms):
  list_bools = []
  for term in list_search_terms:
    if type(term) is str:
      term_bool = (term in phrase)
      list_bools.append(term_bool)
    elif type(term) is list:
      list_bools.append(
        anyKeywordsInPhrase(phrase, term)
      )
  return all(list_bools)


def anyKeywordsInPhrase(phrase, list_search_terms):
  list_bools = []
  for term in list_search_terms:
    if type(term) is str:
      term_bool = (term in phrase)
      list_bools.append(term_bool)
      if term_bool: break
    elif type(term) is list:
      list_bools.append(
        allKeywordsInPhrase(phrase, term)
      )
  return any(list_bools)


def main():
  list_animals    = [ "fox", "lion", "hippo" ]
  list_actions    = [ "jumped", "climbed" ]
  list_objects    = [ "hill", "log", "turtle" ]
  list_phrases    = []
  for animal in list_animals:
    for action in list_actions:
      for object in list_objects:
        list_phrases.append(f"the {animal} {action} over the {object}")
  printHeading("List of phrases:")
  print("\n".join(list_phrases))
  print(" ")
  list_search_terms = [
    # "fox",
    # "turtle",
    # [ "lion", "turtle" ], # fox and turtle
    # [ "fox", ["jumped", "turtle"] ], # fox and (jumped or turtle)
    [ ["fox", "hippo"], "jumped", ["log", "turtle"] ],
  ]
  printHeading("List of phrases that met condition:")
  for phrase in list_phrases:
    if anyKeywordsInPhrase(phrase, list_search_terms):
      print(phrase)
      continue


if __name__ == "__main__":
  main()


## END OF DEMO PROGRAM