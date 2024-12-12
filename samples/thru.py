#!/usr/bin/env python3

from pimidipy import *
pimidipy = PimidiPy()

MAX_PORT = 8

input = pimidipy.open_input(0)
print('Using input port {}'.format(input.name))

outputs = []
for i in range(MAX_PORT):
	port_out = pimidipy.get_output_port(i)
	print('Using output port {}'.format(port_out))
	outputs.append(pimidipy.open_output(port_out))

def output_to_all(event):
	print('Forwarding event {} to all outputs'.format(event))
	for output in outputs:
		output.write(event)

input.add_callback(output_to_all)

pimidipy.run()
