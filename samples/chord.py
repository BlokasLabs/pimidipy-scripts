#!/usr/bin/env python3

from functools import partial
import utils
from pimidipy import *
pimidipy = PimidiPy()
from os import getenv

# Get the semitones from the environment variable or use the default value.
semitones = getenv('SEMITONES', '0,4,7')
SEMITONES = list(map(int, semitones.split(',')))

# Eliminate duplicates, respecting the order.
SEMITONES = list(dict.fromkeys(SEMITONES))

port_in = utils.get_input_port(0)
port_out = utils.get_output_port(0)

print('Using input port {} and output port {}'.format(port_in, port_out))

input = pimidipy.open_input(port_in)
output = pimidipy.open_output(port_out)

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

input.add_callback(partial(produce_chord, semitones=SEMITONES))

pimidipy.run()
