class LastAssignedId:
    link_id = 0
    node_id = 0

def get_new_link_id():
    i = LastAssignedId.link_id
    LastAssignedId.link_id += 1
    return i

def get_new_node_id():
    i = LastAssignedId.node_id
    LastAssignedId.node_id += 1
    return i
