#!/usr/bin/env python3

import utils
from pimidipy import *
pimidipy = PimidiPy()

INPUT_PORT = utils.get_input_port(0)
MAX_PORT = 8

print('Using input port {}'.format(INPUT_PORT))
input = pimidipy.open_input(INPUT_PORT)

outputs = []
for i in range(MAX_PORT):
	port_out = utils.get_output_port(i)
	print('Using output port {}'.format(port_out))
	outputs.append(pimidipy.open_output(port_out))

def output_to_all(event):
	print('Forwarding event {} to all outputs'.format(event))
	for output in outputs:
		output.write(event)

input.add_callback(output_to_all)

pimidipy.run()
