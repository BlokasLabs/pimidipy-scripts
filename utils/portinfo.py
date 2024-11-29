from os import getenv

def get_port(id: int, input: bool) -> str:
	"""Get the port string id for the given numeric id.

	The port string id is read from the environment variable PORT_{IN/OUT}_{id} if it exists, otherwise it is
	constructed from the id. The port is returned in the format 'pimidi{device}:{port}'.

	You may set the PORT_{IN/OUT}_{id} variables in /etc/pimidipy.conf to avoid hardcoding the port ids in your
	code:

	PORT_IN_0=pimidi0:0
	PORT_OUT_0=pimidi3:1

	Default port ids are 'pimidi{device}:{port}' where device is id // 2 and port is id % 2.
	For example: 0 => 'pimidi0:0', 1 => 'pimidi0:1', 2 => 'pimidi1:0', 3 => 'pimidi1:1', etc...

	:param id: The id of the port.
	:type id: int
	:param input: Whether the port is an input port.
	:type input: bool
	:return: The port string id for the given id.
	:rtype: str
	"""

	if id < 0:
		raise ValueError("Port id must be 0 or greater.")

	dir = 'IN' if input else 'OUT'
	port = getenv(f'PORT_{dir}_{id}', None)
	if port is not None:
		return port

	if id >= 8:
		raise ValueError("Port id must be between 0 and 7. Or set the PORT_{IN/OUT}_{id} environment variable in /etc/pimidipy.conf.")

	return 'pimidi{}:{}'.format(id // 2, id % 2)

def get_input_port(id: int) -> str:
	"""Get the port string id for the given numeric id.

	The port string id is read from the environment variable PORT_IN_{id} if it exists, otherwise it is constructed
	from the id. The port is returned in the format 'pimidi{device}:{port}'.

	You may set the PORT_IN_{id} variables in /etc/pimidipy.conf to avoid hardcoding the port ids in your code:

	PORT_IN_0=pimidi0:0
	PORT_IN_1=pimidi3:1

	Default port ids are 'pimidi{device}:{port}' where device is id // 2 and port is id % 2.
	For example: 0 => 'pimidi0:0', 1 => 'pimidi0:1', 2 => 'pimidi1:0', 3 => 'pimidi1:1', etc...

	:param id: The id of the port.
	:type id: int
	:return: The port string id for the given id.
	:rtype: str
	"""
	return get_port(id, True)

def get_output_port(id: int) -> str:
	"""Get the port string id for the given numeric id.

	The port string id is read from the environment variable PORT_OUT_{id} if it exists, otherwise it is constructed
	from the id. The port is returned in the format 'pimidi{device}:{port}'.

	You may set the PORT_OUT_{id} variables in /etc/pimidipy.conf to avoid hardcoding the port ids in your code:

	PORT_OUT_0=pimidi0:0
	PORT_OUT_1=pimidi3:1

	Default port ids are 'pimidi{device}:{port}' where device is id // 2 and port is id % 2.
	For example: 0 => 'pimidi0:0', 1 => 'pimidi0:1', 2 => 'pimidi1:0', 3 => 'pimidi1:1', etc...

	:param id: The id of the port.
	:type id: int
	:return: The port string id for the given id.
	:rtype: str
	"""
	return get_port(id, False)
