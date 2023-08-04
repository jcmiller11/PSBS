# Functions

## cycler

## image

`image(filename, alpha=False, max_colors=10, left=0, top=0, width=None, height=None)`

Import an image file directly into your game as a PuzzleScript object!

?> The project directory is used as the root for the filename parameter, for example use src/image.png to import an image in your src directory.

- filename: (string) the image file to import
- alpha: (bool) whether to include an alpha channel in the output colors
- max_colors: (int) the maximum number of colors to include in the output image, useful for forks that support more than 10 colors
- left: (int) horizontal position in image to start importing from
- top: (int) vertical position in image to start importing from
- width: (int) width of the object to import, if None set to the width of the image file
- height: (int) height of the object to import, if None set to the height of the image file
```psbs
Target
(( image("images/target.png") ))
```

Using the parameters here you can also load objects from a single image as a spritesheet.
```psbs
(% set directions = ["down","left","up","right"] %)
(# Variable could be set in your main template instead #)
(% for dir in directions %)
Player_(( dir ))
(( image("images/player.png",left=loop.index0*5,width=5,height=5) ))
(% endfor %)
```

## range

## tiled
