## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, unittest

from src.headers import WWLists


## ###############################################################
## UNIT TESTS
## ###############################################################
class TestHelperFuncs(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.list_phrases = []
    for animal in ["fox", "turtle", "cow"]:
      for action in ["jumped", "leaped"]:
        for object in ["moon", "log", "river"]:
          cls.list_phrases.append(f"the {animal} {action} over the {object}")

  def _testCondition(self, search_condition, expected_phrases):
    matching_phrases = {
      phrase
      for phrase in self.list_phrases
      if WWLists.meetsSearchCriteria(phrase, search_condition)
    }
    self.assertEqual(matching_phrases, expected_phrases)

  def test_singleWord(self):
    search_condition = [ "turtle" ]
    expected_phrases = {
      "the turtle jumped over the moon",
      "the turtle jumped over the log",
      "the turtle jumped over the river",
      "the turtle leaped over the moon",
      "the turtle leaped over the log",
      "the turtle leaped over the river"
    }
    self._testCondition(search_condition, expected_phrases)

  def test_AND_opperator(self):
    ## "fox" AND "leaped" AND "river"
    search_condition = [
      [ "fox", "leaped", "river" ]
    ]
    expected_phrases = {
      "the fox leaped over the river"
    }
    self._testCondition(search_condition, expected_phrases)

  def test_OR_opperator(self):
    ## "fox" OR "moon"
    search_condition = [
      [[ "fox", "moon" ]]
    ]
    expected_phrases = {
      "the fox jumped over the moon",
      "the fox jumped over the log",
      "the fox jumped over the river",
      "the fox leaped over the moon",
      "the fox leaped over the log",
      "the fox leaped over the river",
      "the turtle jumped over the moon",
      "the turtle leaped over the moon",
      "the cow jumped over the moon",
      "the cow leaped over the moon"
      }
    self._testCondition(search_condition, expected_phrases)

  def test_mix_opperators(self):
    ## ('cow' OR ('leaped' AND 'moon'))
    ## OR
    ## ('fox' AND 'jumped' AND 'river')
    search_condition = [
      [[ "cow", [ "leaped", "moon" ] ]],
      [ "fox", "jumped", "river" ]
    ]
    expected_phrases = {
      "the fox jumped over the river",
      "the fox leaped over the moon",
      "the turtle leaped over the moon",
      "the cow jumped over the moon",
      "the cow jumped over the log",
      "the cow jumped over the river",
      "the cow leaped over the moon",
      "the cow leaped over the log",
      "the cow leaped over the river"
    }
    self._testCondition(search_condition, expected_phrases)

  def test_case_insensitive(self):
    search_condition = [ "FOX" ]
    expected_phrases = {
      "the fox jumped over the moon",
      "the fox jumped over the log",
      "the fox jumped over the river",
      "the fox leaped over the moon",
      "the fox leaped over the log",
      "the fox leaped over the river"
    }
    self._testCondition(search_condition, expected_phrases)


## ###############################################################
## TEST ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  unittest.main()
  sys.exit(0)


## END OF TEST PROGRAM