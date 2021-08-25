import os
import spell_cards
from colored import fg, bg, attr

def clear():
  
  # for windows
  if os.name == 'nt':
      _ = os.system('cls')

  # for mac and linux(here, os.name is 'posix')
  else:
      _ = os.system('clear')

class terminal_selection_menu:
  def __init__(self, intro, options):
    self.intro = intro 
    self.options = options

  def run(self):
    clear()
    print(self.intro, end="\n\n")
    for i in range(len(self.options)):
      print(str(i).rjust(2," "), end=": ")
      print(self.options[i])
    
    while(True):
      x = input(">>> ")
      if x.isnumeric() and int(x) < len(self.options):
        return int(x) 
      else:
        print("PLEASE INPUT AN INTEGER IN RANGE")

def main():
  with open("All_Spells.csv", "r") as infile:
    lines = infile.readlines()

  pos = 0
  titles = lines[0]
  spells = lines[1:]
  header_to_index = {}
  for title in titles.split(","):
    header_to_index[title.strip()] = pos
    pos += 1

  print(spells[0])
  spell_dict = {}
  for header in header_to_index:
    print(header, end=":")
    print(spells[0].split(",")[header_to_index[header]].strip())
    spell_dict[header] = spells[0].split(",")[header_to_index[header]].strip()
  c = "C" if spell_dict["CONCENTRATION"] == "yes" else ""
  r = "R" if spell_dict["RITUAL"] == "yes" else ""
  spell_dict["C/R"] = c+r

  scribe = spell_cards.SigilWriter(2)
  scribe.draw_spell_from_dict(spell_dict)
  scribe.export_image(spell_dict["NAME"] + ".png")

def print_palette(dir):
  for filename in os.scandir(dir):
    if filename.is_file() and filename.name.endswith(".spl"):
      with open(filename.path, "r") as infile:
        lines = infile.readlines()

      print(filename.name, end=": ")
      for line in lines:
        if "PALETTE" in line:
          colors=line.split(":")[1].split("#")
          for color in colors:
            if color:
              print(bg("#"+color) + "  ", end=attr("reset"))
      print("\n")

class spell_db_interface:
  def __init__(self, csv_in, csv_out):
    self.csv_in = csv_in 
    self.csv_out = csv_out 
    self.load_db() 

  def load_db(self):
    with open(self.csv_in, "r") as db:
      lines = db.readlines()

    self.header_to_index = {}
    header_titles = lines[0].split(",")
    for i in range(len(header_titles)):
      self.header_to_index[header_titles[i].strip()] = i
    self.index_to_header = list(self.header_to_index.keys())

    self.spells = {}
    for spell_line in lines[1:]:
      spell_dict = {}
      for header in self.header_to_index:
        spell_dict[header] = spell_line.split(",")[self.header_to_index[header]].strip()
      c = "C" if spell_dict["CONCENTRATION"] == "yes" else ""
      r = "R" if spell_dict["RITUAL"] == "yes" else ""
      spell_dict["C/R"] = c+r
      self.spells[spell_dict["NAME"]] = spell_dict 

  def select_function(self):
    functions = ["Print Spell Card",
                 "Quit"]
    intro = "Please select what you'd like to do"

    menu = terminal_selection_menu(intro, functions)
    selection = menu.run() 
    if functions[selection] == "Print Spell Card":
      self.print_spell_card() 
    else:
      pass

  def edit_spell(self, name, intro):
    spell = self.spells[name]
    options = [x + ":" + spell[x] for x in self.header_to_index]
    menu = terminal_selection_menu(intro, options)
    header = self.index_to_header[menu.run()]
    print()
    prompt = "Current Value: " + self.spells[name][header] + "\n"
    prompt += "Please Enter New Value for " + header + " :"
    self.spells[name][header] = input(prompt).strip()

  def correct_malformed_spell(self, name):
    intro = "Spell \"" + name + "\" is missing information\n\
Mandatory fields are NAME, SCHOOL, SAVE, and PALETTE \n\
Please select field to update"
    self.edit_spell(name, intro)

  def display_message(self, message):
    input(message+"\n\nPress ENTER to continue")

  def draw_spell_card_with_valid_name(self, name):
    try:
      scribe = spell_cards.SigilWriter(2)
      scribe.draw_spell_from_dict(self.spells[name])
      scribe.export_image(name + ".png")
      self.display_message("Saved as " + name + ".png")
    except Exception:
      self.correct_malformed_spell(name)
      self.draw_spell_card_with_valid_name(name)
      
  def get_valid_spellname(self, action):
    clear() 
    name = input("Please enter the name of the spell you wish to " + action + "\n>>> ")
    if name in self.spells:
      return name
    else:
      possible_list = []
      for spellname in self.spells:
        if name.upper() in spellname.upper():
          possible_list.append(spellname)
      if(possible_list):
        possible_list.append("None of these")
        intro = "Spell Not Found\nDid you mean?\n"
        spell_menu = terminal_selection_menu(intro, possible_list)
        corrected_spell = possible_list[spell_menu.run()]
        if corrected_spell != "None of these":
          return corrected_spell
      else:
        self.display_message("No spell found with that name")
    return None

  def print_spell_card(self):
    clear() 
    name = self.get_valid_spellname("print")
    if name in self.spells:
      self.draw_spell_card_with_valid_name(name)
    self.select_function()
          


if __name__ == "__main__":
  options = ["Draw Acid Splash",
             "Print Color Palletes",
             "Test"]
  init_menu = terminal_selection_menu("test", options)
  x = init_menu.run()
  if(x == 0):
    clear()
    main()
  elif(x == 1):
    clear()
    print_palette("src")
  elif(x == 2):
    db = spell_db_interface("All_Spells.csv", "")
    db.select_function()
