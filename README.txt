Hello and Welcome to the Deck Factory 2.7! (NOW WITH RUDIMENTARY GUI)
This is a set of scripts that take MtG deck lists and turn them into "Print sheets" for Tabletop Simulator, making it really easy to import your own custom decks and play some magic as Richard Garfield intended!
You'll need Python 3 (I used 3.7) and the dependencies listed at the bottom of this file. 

To import a custom deck, put your decklist in the DeckLists folder or somewhere you can find it.
 Then run deckFactory.py or deckFactory.exe. On the open window hit Select Decklists and navigate to your deck list files (multiple selection does work).
Finished print sheets will be in the PrintSheets folder.


All of these images are obtained from publicly available sources and no profit is made from them in any way.
a couple of notes.
1. Custom deck lists (not generated in Xmage) should be .csv files or .json files, Xmage generates .dck files. The old txt format is still supported, but does not handle multiple piles or copies, thus the new CSV format is used by the deck editor.
2. Xmage has terrible practice with set codes and the promos have been butchered beyond usability. Don't use Promo card art in xmage decks that you want to import that way.
3. You no longer need to go get your own tokens or backs of cards. The tool gets them for you, along with planeswalker emblems.

Also there is a custom deck editor! just use it to make the most effective format more easily.
Use the deck editor, it will produce the smoothest experience by far.


Dependencies for this project:
Python 3.6+ (currently using 3.7, but 3.6 and up should work)
And the following Packages
numpy
pillow (this one doesn't just come along with Anaconda Navigator, make sure to install it)
sys
re
os
glob
urllib3
json
tkinter
time
shutil
logging
imgurpython

Thanks!
Ben


NOTE 
Any and all card/token/emblem images retrieved by this tool are solely property of Wizards of the Coast and I make no claim to them.
These images are not archived and are promptly scoured from this tool's directories for the purposes of maintaining the integrity of the IP of Wizards of the Coast.
Any liablity of archiving these images falls upon the user.


P.S. Here is a link to a good table for playing magic in the workshop:
https://steamcommunity.com/sharedfiles/filedetails/?id=887148653

