import csv
import spell_cards
from colored import fg, bg, attr

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

if __name__ == "__main__":
  main()