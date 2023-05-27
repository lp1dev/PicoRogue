from os.path import join

class Loader:
    def __init__(self, rooms_dir):
        self.rooms_dir = rooms_dir
        return

    def load(self, floor, room_type):
        with open(join(self.rooms_dir, str(floor), '%s.room' %room_type)) as room_file:
            return room_file.readlines()