class Airport:

    def __init__(self, name, center, corners, image_filepath):
        self.name = name
        self.center = center
        self.corners = corners
        self.image_filepath = image_filepath

    def __repr__(self):
        return "<Airport: %s>" % self.name
