# coding: utf-8
from smbus2 import SMBus


class BME280():
    # Set various parameter
    osrs_t = 0b001  # Temperature oversampling rate
    osrs_p = 0b001  # Humidity oversampling rate
    osrs_h = 0b001  # Pressure oversampling rate
    mode = 0b11  # Set nomal mode
    t_sb = 0b101  # Set standby time for 1000 ms
    filter_mode = 0b000  # Set filter to disable
    spi3w_en = 0b0  # Disabe 3-wire SPI interface

    # Store calibration data
    digT = []
    digP = []
    digH = []
    
    # Variable for calculation
    t_fine = 0.0

    # Store calculated data
    temperature = 0.0
    pressure = 0.0
    humidity = 0.0

    def __init__(self, bus_address=1, SDO=0):
        self.bus = SMBus(bus_address)
        # Select I2C slave address by SDO status
        if SDO == 0:
            self.address = 0x76
        else:
            self.address = 0x77

        self.setup()
        self.get_calibration_parameter()

    def setup(self):
        # Making setup data
        ctrl_meas_register = (self.osrs_t << 5) | (self.osrs_p << 2) | self.mode
        config_register = (self.t_sb << 5) | (self.filter_mode << 2) | self.spi3w_en
        ctrl_hum_register = self.osrs_h

        self.bus.write_byte_data(self.address, 0xf4, ctrl_meas_register)
        self.bus.write_byte_data(self.address, 0xf5, config_register)
        self.bus.write_byte_data(self.address, 0xf2, ctrl_hum_register)

    def get_calibration_parameter(self):
        calib = []
        for i in range(0x88, 0x88 + 24):
            calib.append(self.bus.read_byte_data(self.address, i))
        calib.append(self.bus.read_byte_data(self.address, 0xa1))
        for i in range(0xe1, 0xe1 + 7):
            calib.append(self.bus.read_byte_data(self.address, i))

        self.digT.append((calib[1] << 8) | calib[0])
        self.digT.append((calib[3] << 8) | calib[2])
        self.digT.append((calib[5] << 8) | calib[4])

        self.digP.append((calib[7] << 8) | calib[6])
        self.digP.append((calib[9] << 8) | calib[8])
        self.digP.append((calib[11] << 8) | calib[10])
        self.digP.append((calib[13] << 8) | calib[12])
        self.digP.append((calib[15] << 8) | calib[14])
        self.digP.append((calib[17] << 8) | calib[16])
        self.digP.append((calib[19] << 8) | calib[18])
        self.digP.append((calib[21] << 8) | calib[20])
        self.digP.append((calib[23] << 8) | calib[22])

        self.digH.append(calib[24])
        self.digH.append((calib[26] << 8) | calib[25])
        self.digH.append(calib[27])
        self.digH.append((calib[28] << 4) | (0x0F & calib[29]))
        self.digH.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
        self.digH.append(calib[31])

        for i in range(1, 2):
            if self.digT[i] & 0x8000:
                self.digT[i] = (-self.digT[i] ^ 0xFFFF) + 1
        
        for i in range(1, 8):
            if self.digP[i] & 0x8000:
                self.digP[i] = (-self.digP[i] ^ 0xFFFF) + 1

        for i in range(0, 6):
            if self.digH[i] & 0x8000:
                self.digH[i] = (-self.digH[i] ^ 0xFFFF) + 1

    def read_data(self):
        data = []
        for i in range(0xf7, 0xf7 + 8):
            data.append(self.bus.read_byte_data(self.address, i))

        pressure_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temperature_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        humidity_raw = (data[6] << 8) | data[7]

        self.compensate_temperature(temperature_raw)
        self.compensate_pressure(pressure_raw)
        self.compensate_humidity(humidity_raw)

    def compensate_temperature(self, temperature_raw):
        v1 = (temperature_raw / 16384.0 - self.digT[0] / 1024.0) * self.digT[1]
        v2 = ((temperature_raw / 131072.0 - self.digT[0] / 8192.0) ** 2) * self.digT[2]
        self.t_fine = v1 + v2
        self.temperature = self.t_fine / 5120.0

    def compensate_pressure(self, pressure_raw):
        v1 = (self.t_fine / 2.0) - 64000.0
        v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * self.digP[5]
        v2 = v2 + ((v1 * self.digP[4]) * 2.0)
        v2 = (v2 / 4.0) + (self.digP[3] * 65536.0)
        v1 = (((self.digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8) + ((self.digP[1] * v1) / 2.0)) / 262144
        v1 = ((32768 + v1) * self.digP[0]) / 32768

        if v1 == 0:
            return 0
        self.pressure = ((1048576 - pressure_raw) - (v2 / 4096)) * 3125
        if self.pressure < 0x80000000:
            self.pressure = (self.pressure * 2.0) / v1
        else:
            self.pressure = (self.pressure / v1) * 2
        v1 = (self.digP[8] * (((self.pressure / 8.0) * (self.pressure / 8.0)) / 8192.0)) / 4096
        v2 = ((self.pressure / 4.0) * self.digP[7]) / 8192.0
        self.pressure = self.pressure + ((v1 + v2 + self.digP[6]) / 16.0)

    def compensate_humidity(self, humidity_raw):
        # Valiable for caluculation
        a = 0.0
        b = 0.0

        var_h = self.t_fine - 76800.0
        if var_h != 0:
            a = (humidity_raw - (self.digH[3] * 64.0 + self.digH[4] / 16384.0 * var_h))
            b = (self.digH[1] / 65536.0 * (1.0 + self.digH[5] / 67108864.0 * var_h * (1.0 + self.digH[2] / 67108864.0 * var_h)))
            var_h = a * b
        else:
            return 0
        
        var_h = var_h * (1.0 - self.digH[0] * var_h / 524288.0)
        if var_h > 100.0:
            var_h = 100.0
        elif var_h < 0.0:
            var_h = 0.0

        self.humidity = var_h


if __name__ == "__main__":
    pass
