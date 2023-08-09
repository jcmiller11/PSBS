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

## Whitespace

Control structures in PSBS templates preserve whitespace.

## Escaping

Occasionally you may want
