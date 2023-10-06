# Templates

PSBS uses Jinja2, a fast, expressive, extensible templating engine, to build your PuzzleScript project.

This document contains a subset of Jinja2 features most useful for building PuzzleScript projects as well as documentation of the additional features PSBS extends the templates with. To learn more about all of the features available to you check out the Jinja2 [Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/).

To avoid conflicting with valid PuzzleScript code, the Jinja2 Tags have been changed to use parenthesis.  There are three kinds of tags available in your templates.
```psbs
(% statements %)
```
Statements contain code that will be run when the template is compiled.  Mainly control structures and setting of variables happen here.
```psbs
(( expressions ))
```
Expressions contain code that will be printed when the template is compiled.
```psbs
(# comments #)
```
Comments allow you to put comments in your template or comment out sections of your template for debugging.  Unlike PuzzleScript comments these comments will not be present in the final PuzzleScript code output by PSBS.

## Variables

Variables can be assigned with the set expression and used throughout your template.

If the set expression does not contain an assignment it is assumed to be a block assignment and any content before an (% endset %) tag will be assigned to the variable as a string.

```psbs
(% set hat_color = "red" %)
(% set character_sprite %)
.000.
.111.
22222
.333.
.3.3.
(% endset %)

Player1
(( hat_color )) orange white blue
(( character_sprite ))

Player2
(( hat_color )) orange black grey
(( character_sprite ))
```

## For

Loop over each item in a sequence.  For example to create four identical sprites called Player1, Player2, Player3, and Player4:

```psbs
(% for playernum in range(4) %)
Player(( playernum+1 ))
black orange white blue
.000.
.111.
22222
.333.
.3.3.
(% endfor %)
```

Within a loop block some special variables are accessible

- loop.index
  - The current iteration of the loop. (1 indexed) |
- loop.index0
  - The current iteration of the loop. (0 indexed)
- loop.revindex
  - The number of iterations from the end of the loop (1 indexed)
- loop.revindex0
  - The number of iterations from the end of the loop (0 indexed)
- loop.first
  - True if first iteration.
- loop.last
  - True if last iteration.
- loop.length
  - The number of items in the sequence.
- loop.cycle
  - A helper function to cycle between a list of sequences. See the explanation below.
- loop.depth
  - Indicates how deep in a recursive loop the rendering currently is. Starts at level 1
- loop.depth0
  - Indicates how deep in a recursive loop the rendering currently is. Starts at level 0
- loop.previtem
  - The item from the previous iteration of the loop. Undefined during the first iteration.
- loop.nextitem
  - The item from the following iteration of the loop. Undefined during the last iteration.
- loop.changed(*val)
  - True if previously called with a different value (or not called at all).

## If

A standard if statement that tests if a statement is True or False and only runs the contents of its block if True.

```psbs
Player(( playernum ))
(% if playernum == 1 %)
red
(% elif playernum == 2 %)
blue
(% else %)
green
(% endif %)
```

## Macros

Macros are similar to functions in regular programming languages, they can be used to put often used idioms into reusable blocks.

```psbs
(% macro push(pusher, pushee) %)
[ > (( pusher )) | (( pushee )) ] -> [ > (( pusher )) | > (( pushee )) ]
(% endmacro %)

(( push("Player", "Crate") ))
(# [ > Player | Crate ] -> [ > Player | > Crate ] #)
```

## Include

Inserts another source file into your template.  Included source files inherit the scope of the parent file but not the other way around.

```psbs
(% set playername = "Fred" %)
(% include "objects.pss" %)
(# playername variable is accessible within objects.pss #)
```
