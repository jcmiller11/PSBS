# Filters

PSBS gives you access to all of Jinja's [builtin filters](https://jinja.palletsprojects.com/en/3.1.x/templates/#list-of-builtin-filters) but also offers some extras to help with PuzzleScript development

Filters can be applied to values using pipe notation `(( myVar|reverse ))` or applied to an entire block of code, for example
```psbs
(# [OBJECT1] -> [OBJECT2] #)
(% filter upper %)
[object1] -> [object2]
(% endfilter %)
```

## add_prefix

`add_prefix(prefix)`

Accepts a string as a parameter and adds it to every line of the string passed to this filter.

```psbs
(# Late rules #)
(% filter add_prefix("LATE") %)
[object1] -> [object2]
(% endfilter %)
```

## combine_levels

`combine_levels(columns = 0)`

A powerful filter for combining levels into one larger level.

If a flat list of levels or a string containing levels is passed it will combine these levels horizontally into one long row unless the optional columns parameter is passed, which will break it into rows of the input levels that number of columns wide.

For more fine grained control can also be passed a 2D list explicitly showing the format you would like your levels to be in.

```psbs
(% set levels %)
###
#..
#.#

###
..#
#.#

#.#
#..
###

#.#
..#
###
(% endset %)
(( levels|combine_levels(2) ))

(# Output:
######
#....#
#.##.#
#.##.#
#....#
######
#)
```

## levels_to_list

`levels_to_list()`

Accepts a string containing puzzlescript levels and outputs a list where each item contains one level.

```psbs
(% set levels %)
###
..#
###

###
#..
###
(% endset %)
(( levels|levels_to_list|reverse|combine_levels ))

(# Output:
######
#....#
######
#)
```

## wrap

`wrap(width=5)`

Accepts a string and adds a newline every width number of characters, useful for programmatically generating sprites and levels.

```psbs
(% for number in range(0,26) %)
RemainingChalk((number))
white
(( (("0"*number)+("."*(25-number))) | wrap ))
(% endfor %)
```
