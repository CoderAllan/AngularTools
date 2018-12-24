import os
import os.path
import re
from html.parser import HTMLParser
from html.entities import name2codepoint
from tinycss2.parser import parse_stylesheet
from tinycss2.tokenizer import IdentToken, LiteralToken, WhitespaceToken

# TODO: Change the variable to the folder with your project
rootDir = r'C:\MyAngularProject'

def GetSelectorsFromRule(rule: list):
  selectorFound = False
  selector = ''
  selectors = set()
  for token in rule:
    #print(f"token: {token}")
    if token.type == 'literal' and token.value != ',' and selectorFound == True:
      #print(f"literal1: {token.value} - selector: {selector}")
      selector = selector + token.value
      #print(f"literal2: {token.value} - selector: {selector}")
    if token.type == 'ident':
      #print(f"ident1: {token.value} - selector: {selector}")
      selectorFound = True
      selector = selector + ' ' + token.value
      #print(f"ident2: {token.value} - selector: {selector}")
    if (token.type == "literal" and token.value == ",") or token.type == "whitespace":
      #print(f"whitespace: {token.value} - selector: {selector}")
      selectorFound = False
      if len(selector.strip()) > 0:
        selectors.add(selector.strip())
      selector = ""
  return selectors

def FindAllSelectors():
  stylesheetFilenames = [os.path.join(dp, f) for dp, dn, filenames in os.walk(rootDir) for f in filenames if f.endswith(".css")]
  selectors = set()
  for stylesheetFilename in stylesheetFilenames:
    if stylesheetFilename.find('node_modules') == -1:
      with open(stylesheetFilename) as f:
        content = f.read()
        rules = parse_stylesheet(content, True, True)
        if len(rules) > 0:
          for rule in rules:
            if rule.type == "qualified-rule":
              #print(f"rule: {rule.prelude}")
              selectorsFromRule = GetSelectorsFromRule(rule.prelude)
              #print(f"selectorsFromRule: {selectorsFromRule}")
              selectors = selectors | selectorsFromRule
  return selectors

class HTMLStarttagParser(HTMLParser):
  CssClasses = set()

  def handle_starttag(self, tag, attrs):
      for attr in attrs:
        if attr[0] == 'class':
          classesRaw = attr[1].strip()
          classes = re.split(r'\s|\.|,', classesRaw)
          self.CssClasses.update(classes)

def FindAllClassReferences():
  templateFilenames = [os.path.join(dp, f) for dp, dn, filenames in os.walk(rootDir) for f in filenames if f.endswith(".component.html")]
  parser = HTMLStarttagParser()
  for templateFilename in templateFilenames:
    with open(templateFilename) as f:
      content = f.read()
      parser.feed(content)
  #   print(f"Template: {templateFilename} - Count: {len(parser.CssClasses}"))
  # print(f"cssClasses: {parser.CssClasses}")
  return parser.CssClasses

def PrintSortedList(listToSort):
  sortedList = list(listToSort)
  sortedList.sort(key=lambda s: s.lower())
  print(*sortedList, sep='\n')

selectors = FindAllSelectors()
#print(f"Selectors: {selectors}")
cssClasses = FindAllClassReferences()
#PrintSortedList(cssClasses)
print(f"selectors: {len(selectors)} - cssClasses: {len(cssClasses)}")
unusedClasses = selectors - cssClasses
print(f"unusedClasses: {len(unusedClasses)}")
PrintSortedList(unusedClasses)
usedClasses = selectors & cssClasses
print(f"usedClasses: {len(usedClasses)}")
#PrintSortedList(usedClasses)
undefinedClasses = cssClasses - selectors
print(f"undefinedClasses: {len(undefinedClasses)}")
#PrintSortedList(undefinedClasses)

