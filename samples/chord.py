#!/usr/bin/env python3

from functools import partial
from pimidipy import *
pimidipy = PimidiPy()
from os import getenv

# Get the semitones from the environment variable or use the default value.
CHORD_SEMITONES = list(map(int, getenv('CHORD_SEMITONES', '0,4,7').split(',')))

# Eliminate duplicates, respecting the order.
CHORD_SEMITONES = list(dict.fromkeys(CHORD_SEMITONES))

input = pimidipy.open_input(0)
output = pimidipy.open_output(0)

print('Using input port {} and output port {}'.format(input.name, output.name))

def produce_chord(event, semitones: list[int]):
	if type(event) == NoteOnEvent:
		print(f'Producing chord for {event}')
		for semitone in semitones:
			n = event.note + semitone
			if n < 0 or n > 127:
				print(f'Note {n} out of range, discarding')
				continue
			output.write(NoteOnEvent(event.channel, n, event.velocity))
	elif type(event) == NoteOffEvent:
		print(f'Producing note offs for {event}')
		for semitone in semitones:
			n = event.note + semitone
			if n < 0 or n > 127:
				print(f'Note {n} out of range, discarding')
				continue
			output.write(NoteOffEvent(event.channel, n, event.velocity))
	else:
		print(f'Passing event {event}')
		output.write(event)

input.add_callback(partial(produce_chord, semitones=CHORD_SEMITONES))

pimidipy.run()
