# Templates

PSBS uses Jinja2, a fast, expressive, extensible templating engine, to build your PuzzleScript project.  To learn more about all of the features available to you check out the Jinja2 [Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/).

To avoid conflicting with valid PuzzleScript code, the Jinja2 Tags have been changed as follows:

(% blocks %) (( variables )) (# comments #)

## Images

A helper function has been added to the template environment `Image(filename)` that will import an image file directly into your game as a PuzzleScript object!

    Target
    ((image("images/target.png")))

Additionally, this helper function contains the following optional parameters (alpha=False, max_colors=10, left=0, top=0, width=None, height=None)

- left: (int) horizontal position in image to start importing from
- top: (int) vertical position in image to start importing from
- width: (int) width of the object to import, if None set to the width of the image file
- height: (int) height of the object to import, if None set to the height of the image file

By using the last four parameters listed one can load objects from a single image as a spritesheet.

    (% set directions = ["down","left","up","right"] %) (# Can be placed in your main template #)
    (% for dir in directions %)
    Player_((dir))
    ((image("images/player.png",left=loop.index0*5,width=5,height=5)))
    (% endfor %)
 
