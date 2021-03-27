# glow
A point light system for Piqueserver

## How does it work?
Glow interprets user-placed blocks with an R, G or B value of 255 as a "light block". Said blocks dynamically apply its color to surrounding blocks in a point-light fashion.

## How do I run it?
Glow shares some file architecture with imger, so folders at the root of your piqueserver installation need to be created (for the DISABLED_USERS_GLOW.txt file). Said file is located in "img/userdata/DISABLED_USERS_GLOW.txt".

The script is also disabled by default on non-glow maps. That can be changed in the script by changing "ALWAYS_GLOW" in the user inputs to "True".

## How do I make a "glow map"?
If ALWAYS_GLOW is turned OFF, these extensions will need to be added to the map's .txt file:

```
extensions = {
    'glow_enabled': True,
    'glow_stored_colors': {}
}
```

A good candidate for a glow map is a map with no RGB values of 255 all across. If your map doesn't meet that requirement, it can be easily edited with the use of "glowpp.py" (glow pre-process). This script will edit map colors on a server boot so that every block's color values get clamped. Also useful if you wish to grade the whole map at once (turn it to night, for example). It is then simply a matter of saving the map to a new .vxl file, and use that one instead. (Make sure you don't run your server with glowpp running at all time; this will make map loading between matches horribly long (and break glow functionality if there are glow blocks on the map).

## What if I want glow blocks on my map (like Royal Parade Night)?
Once your map is pre-processed and ready to be worked on, type "/glowrecord" as an administrator before starting work on the map. This will dump STORED_COLORS to a .txt file on your server once piqueserver shuts down. (Be sure to save the map before shutting down!) This will be a fairly big file containing block coordinates; these are the original colors of blocks being glown upon (and the values of light blocks on the map). This text must then be added to the map's .txt file, as the "glow_stored_colors" extension.

## My players are complaining that glow is ruining the game and that Yusuf is a big fat loser, what do I do?
Tell your players that it's possible to deactivate glow client-side using the command "/glow". This should prevent their username from receiving block updates from the plugin from now on.
