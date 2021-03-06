# coding: utf-8

from smbus2 import SMBus


class SO1602A():
    def __init__(self, bus_address=1, sa0=0, cursor=False, blink=False):
        self.bus = SMBus(bus_address)
        # Select I2C slave address by sa0 status
        if sa0 == 0:
            self.address = 0x3c
        else:
            self.address = 0x3d

        # Initialize LCD
        self.clear_display()
        self.return_home()
        self.display_on(cursor, blink)
        self.clear_display()

    def display_off(self):
        self.bus.write_byte_data(self.address, 0x00, 0x08)
        
    def return_home(self):
        self.bus.write_byte_data(self.address, 0x00, 0x02)

    def clear_display(self):
        self.bus.write_byte_data(self.address, 0x00, 0x01)

    def display_on(self, cursor, blink):
        command = 0x0c
        if cursor:
            command += 0x02

        if blink:
            command += 0x01
        
        self.bus.write_byte_data(self.address, 0x00, command)

    def shift_display(self, direction='right', number=1):
        for i in range(number):
            if direction == 'right':
                self.bus.write_byte_data(self.address, 0x00, 0x1c)
            elif direction == 'left':
                self.bus.write_byte_data(self.address, 0x00, 0x18)

    def set_cursor(self, coordinate=[0, 0]):  # coordinate = [row, columm]
        # If columm number is grater than 16, the number is adjusted under 16
        if coordinate[1] >= 16:
            coordinate[1] -= 16

        if coordinate[0] == 0:
            self.bus.write_byte_data(self.address, 0x00, (0x80 + coordinate[1]))
        elif coordinate[0] == 1:
            self.bus.write_byte_data(self.address, 0x00, (0xa0 + coordinate[1]))

    def print_str(self, str=''):
        if len(str) < 17:
            for i in range(len(str)):
                self.bus.write_byte_data(self.address, 0x40, ord(str[i]))

    def print_char(self, char_code):
        # type: (int) -> None
        self.bus.write_byte_data(self.address, 0x40, char_code)


if __name__ == '__main__':
    pass
