class BoundingRect(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def set_size(self, width, height, halign, valign):
        self.target_width = width
        self.target_height = height
        self.calculate_proportional_dimensions()
        self.calculate_crops(halign, valign)

    def calculate_proportional_dimensions(self):
        if not self.target_width:
            self.target_width = self.target_height * self.width / self.height

        if not self.target_height:
            self.target_height = self.target_width * self.height / self.width

    def calculate_crops(self, halign, valign):
        
        if isinstance(valign, basestring):
            self.top = ((self.height - self.target_height) / 2) / self.height
            if self.top < 0:
                self.top = 0
            self.bottom = 1 - self.top
            if valign == "top":
                self.bottom = 1 - (2 * self.top)
                self.top = 0
            elif valign == "bottom":
                self.top = 2 * self.top
                self.bottom = 1
        else:
            crop_height = self.height - self.target_height
            self.top = (crop_height * valign) / self.height
            self.bottom = (self.height - (crop_height * (1 - valign))) / self.height

        if isinstance(halign, basestring):
            self.left = ((self.width - self.target_width) / 2) / self.width
            if self.left < 0:
                self.left = 0
            self.right = 1 - self.left
            if halign == "left":
                self.right = 1 - (2 * self.left)
                self.left = 0
            elif halign == "right":
                self.left = 2 * self.left
                self.right = 1
        else:
            crop_width = self.width - self.target_width
            self.left = (crop_width * halign) / self.width
            self.right = (self.width - (crop_width * (1 - halign))) / self.width
