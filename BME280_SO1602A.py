# coding: utf-8
from driver_module import SO1602A
from driver_module import BME280
from decimal import Decimal, ROUND_HALF_UP


def main():
    lcd = SO1602A.SO1602A(sa0=0)
    bme = BME280.BME280(SDO=0)
    bme.mode = 0b01

    bme.read_data()
    temperature = bme.temperature
    humidity = bme.humidity
    pressure = bme.pressure

    temperature_str = 'TEMP:{}'.format(Decimal(temperature).quantize(Decimal('0'), rounding=ROUND_HALF_UP))
    humidity_str = 'RH:{}%'.format(Decimal(humidity).quantize(Decimal('0'), rounding=ROUND_HALF_UP))
    pressure_str = 'PRESSURE:{}hPa'.format(Decimal(pressure / 100).quantize(Decimal('0'), rounding=ROUND_HALF_UP))
    
    print(temperature_str)
    print(humidity_str)
    print(pressure_str)

    lcd.print_str(str=temperature_str)
    lcd.print_char(char_code=0xdf)  # print ℃
    lcd.print_char(char_code=ord('C'))
    lcd.print_str(str=' ' + humidity_str)
    lcd.set_cursor(coordinate=[1, 0])
    lcd.print_str(str=pressure_str)


if __name__ == "__main__":
    main()
