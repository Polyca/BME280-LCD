# coding: utf-8

from smbus2 import SMBus
import time


class SO1602():
    def __init__(self, Bus_address=1, sa0=0, cursor=False, blink=False):
        self.bus = SMBus(Bus_address)

        if sa0 == 0:
            self.Address = 0x3c
        else:
            self.Address = 0x3d

        self.clear_display()
        self.return_home()
        self.display_on(cursor, blink)
        self.clear_display()

    def writeline(self, str='', line=0, align='left'):
        while len(str) < 16:
            if align == 'right':
                str = ' ' + str
            else:
                str = str + ' '
            
        if line == 1:
            self.bus.write_byte_data(self.Address, 0x00, (0x00 + 0x20))
        else:
            self.bus.write_byte_data(self.Address, 0x00, 0x80)

        for i in range(len(str)):
            self.bus.write_byte_data(self.Address, 0x40, ord(str[i]))

    def clear_display(self):
        self.bus.write_byte_data(self.Address, 0x00, 0x01)

    def return_home(self):
        self.bus.write_byte_data(self.Address, 0x00, 0x02)

    def display_on(self, cursor=False, blink=False):
        cmd = 0x0c
        if cursor:
            cmd += 0x02
        
        if blink:
            cmd += 0x01

        self.bus.write_byte_data(self.Address, 0x00, cmd)
    
    def display_off(self):
        self.bus.write_byte_data(self.Address, 0x00, 0x08)


def main():
    oled = SO1602(sa0=0)

    oled.writeline(str='Hello World!', line=0)
    time.sleep(0.5)
    oled.writeline(str='Polyca', line=1)
    time.sleep(5)
    oled.clear_display


if __name__ == '__main__':
    main()
