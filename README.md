# Ignores all non alpha-numeric characters except newline

### To Use on Repl.it
 - Type what you want to translate in `input.txt`
   - The rune translator will match the placement of what you type so insert your own newlines as desired

- Press Run **|>**
- Your text will be translated to `output.png`

### To Use Locally
 - Type what you want to translate in `input.txt`
 - run `python3 main.py`
 - Your text will be translated to `output.png`

The only dependencies for local users are python3, the python math library (should be included standard) and the pycairo library which can be installed with `pip3 install pycairo`.

## Spellcard definition
put a spell card named `name.spl` in the `src` dir to have it processed. Each spell card should include:

```
LEVEL:

SAVE:

DAMAGE:
DAMAGEDICE:

RANGE:

DURATION:

CAST:

TARGET:
TARGETSHAPE:

C/R: 

SCHOOL:

COMPONENTS:
```


### Example of Curser
> This is mostly just a reminder for myself
The curser is positioned at the `+` below relative to the space given each character


```
 ----+---- -
 |       | H
 |       | e
 |       | i 
 |       | g
 |       | h
 |       | t 
 --------- - 
 |-Width-|
```

