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
    
    # Rounding data
    temperature_dec = Decimal(temperature).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
    humidity_dec = Decimal(humidity).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
    pressure_dec = Decimal(pressure / 100).quantize(Decimal('0'), rounding=ROUND_HALF_UP)

    # Create string
    if temperature_dec < 10:
        temperature_str = 'TEMP: {}'.format(temperature_dec)
    else:
        temperature_str = 'TEMP:{}'.format(temperature_dec)

    if humidity_dec < 10:
        humidity_str = 'RH: {}%'.format(humidity_dec)
    elif humidity_dec > 99:
        humidity_dec = 99
        humidity_str = 'RH:{}%'.format(humidity_dec)
    else:
        humidity_str = 'RH:{}%'.format(humidity_dec)

    if pressure_dec < 1000:
        pressure_str = 'PRESSURE: {}hPa'.format(pressure_dec)
    else:
        pressure_str = 'PRESSURE:{}hPa'.format(pressure_dec)

    # Display
    lcd.print_str(str=temperature_str)
    lcd.print_char(char_code=0xdf)  # print ℃
    lcd.print_char(char_code=ord('C'))
    lcd.print_str(str=' ' + humidity_str)
    lcd.set_cursor(coordinate=[1, 0])
    lcd.print_str(str=pressure_str)


if __name__ == "__main__":
    main()
