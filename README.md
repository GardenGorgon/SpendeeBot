# SpendeeBot
This machine plays splendor

Controls:
---------
There are only two actions "Take" (t) and "buy" (b)
t takes up to 3 coins of any available colors with the format
Script format: t(color)(color)(color)
Script example: tgwg
This examples takes 1 green, 1 white, and another green chip.
Acceptable colors are b (blue) r (red) g (green) k (black) and w (white).

b buys a card if possible with the format
Script format: b(row)(column)
row is an integer from 1-3 refering to the level of the card. More expensive cards are higher levels
column is an interger from 1-4 refering to the position of the card on that row.
The leftmost card is 1 the rightmost card is 4.

Script example: b14
This example buys the 4th card card from the 1st tier. If the player cannot actually afford the card,
an error will be thrown.

Starting the game:
------------------
 Initiate by entering "python3 play.py" in the terminal. Afterwards, you will be asked to enter a number from 0 to 3 to choose an agent to play against. Enter a single number and the game should start.
 0: Basic Agent
 1: Cheap Agent
 2: NobleAgent
 3: Adversarial Agent



