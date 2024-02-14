from file_reader import FileReader

class Modbus:
    def __init__(self):
        file_reader = FileReader()
        self.jsonF = file_reader.load_json("./settings/modbus_messages.json")

    def to_word(self, decimal):
        msb = (decimal >> 8) & 0xff
        lsb = decimal & 0xff
        return [msb, lsb]

    def to_byte(self, decimal):
        return [decimal]

    def word_to_decimal(self, msb, lsb):
        return (msb << 8) + lsb

    def initiate_modbus_overheads(self):
        frame = []
        frame += self.to_word(self.jsonF["transaction id"])
        frame += self.to_word(self.jsonF["protocol id"])
        frame += self.to_word(self.jsonF["length"])
        frame += self.to_byte(self.jsonF["device address"])
        frame += self.to_byte(self.jsonF["function code"])
        frame += self.to_word(self.jsonF["register"])
        frame += self.to_word(self.jsonF["byte count"])
        return frame

    def create_modbus_frame(self, start, count, frame):
        start_register = self.to_word(start)
        register_count = self.to_word(count)
        frame[8] = start_register[0]
        frame[9] = start_register[1]
        frame[10] = register_count[0]
        frame[11] = register_count[1]
        return frame

    def check_frame_valid(self, raw_frame):
        if (raw_frame[7] == 83): 
            if (len(raw_frame) == 9):
                if (raw_frame[8] != 0):
                    return False
        return True
