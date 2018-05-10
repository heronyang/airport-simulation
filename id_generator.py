"""Provides functions for retrieving a new ID for the simulation."""


class LastAssignedId:
    """Static class that stores the latest assigned IDs."""
    link_id = 0
    node_id = 0


def get_new_link_id():
    """Retrieve a new link ID."""
    i = LastAssignedId.link_id
    LastAssignedId.link_id += 1
    return i


def get_new_node_id():
    """Retrieve a new node ID."""
    i = LastAssignedId.node_id
    LastAssignedId.node_id += 1
    return i
