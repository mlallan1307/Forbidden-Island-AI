Forbidden Island
================

Forbidden Island game for CSU CS440 FALL 2014 project
Created by Mike Allan and James Doles

usage: forbidden_island.py [-h] [--baseValues BASEVALUES] [--save SAVE SAVE]
                           [--load LOAD [LOAD ...]] [--rerun RERUN]
                           {a,ar,h} {2,3,4} {0,1,2,3}

The Forbidden Island game

positional arguments:
  {a,ar,h}              For ai game enter 'a', for human game enter 'h'
  {2,3,4}               Number of players between 2 and 4 inclusive
  {0,1,2,3}             Difficulty number between 0 and 3 inclusive from
                        easiest to hardest

optional arguments:
  -h, --help            show this help message and exit
  --baseValues BASEVALUES
                        The base values for the ai to determine the action
                        weights
  --save SAVE SAVE      Save game state to <file> <Num Runs>
  --load LOAD [LOAD ...]
                        Load game state from: <file> <line number>
  --rerun RERUN         Rerun this many times

