from typing import Optional

from pyModbusTCP.client import ModbusClient

from pyModbusTCP import utils


class MersadModbusClient(ModbusClient):
    register_for_counter: int

    def __init__(self, host=None, port=None, unit_id=None, timeout=None,
                 debug=None, auto_open=None, auto_close=None,
                 register_for_counter: int = 0,
                 register_for_data: int = 0,
                 register_for_start_read: int = 0,
                 register_for_end_read: int = 0,
                 register_for_test: int = 0):
        super().__init__(host, port, unit_id, timeout, debug, auto_open, auto_close)
        self.register_for_counter = register_for_counter
        self.register_for_data = register_for_data
        self.register_for_start_read = register_for_start_read
        self.register_for_end_read = register_for_end_read
        self.register_for_test = register_for_test

    def counter(self) -> int:
        if self.register_for_counter:
            data = int(self.read_holding_registers(self.register_for_counter, 1)[0])
            if data > 32767:
                data = data - 65536
        else:
            return 0
        return data

    def single_register_read(self, _input_or_holding: str, _address: int, _data_type: str, _big_endian: bool = False):
        data = 0
        if _data_type == "32bit_float":
            if _input_or_holding == "input":
                data = self.read_input_registers(_address, 2)
            if _input_or_holding == "holding":
                data = self.read_holding_registers(_address, 2)
            if data:
                list_32_bits = utils.word_list_to_long(data, big_endian=_big_endian)
                float_32bit_val = round(utils.decode_ieee(list_32_bits[0]), 2)

                return float_32bit_val

        if _data_type == "16bit_uint":
            if _input_or_holding == "input":
                data = self.read_input_registers(_address, 1)
            if _input_or_holding == "holding":
                data = self.read_holding_registers(_address, 1)

            if data:
                uint_16bit_val = data[0]

                return uint_16bit_val

    def multiple_register_read(self, _input_or_holding: str, _address: int, _length: int, _data_type: str,
                               _big_endian: bool = False):
        _length = self.get_correct_length_by_data_type(_data_type, _length)

        if _input_or_holding == "input":
            data = self.read_input_registers(_address, _length)
        elif _input_or_holding == "holding":
            data = self.read_holding_registers(_address, _length)
        else:
            data = self.read_holding_registers(_address, _length)

        if data:
            return self.render_data(_data_type, data, _big_endian)

    def read_on_timer(self):
        self.unit_id(13)
        a = self.multiple_register_read("input", 1, 1, "INT64")
        if a:
            if a[0]:
                sec = a[0] / 1000
                minute = sec / 60
                hour = minute / 60

                print("sec = ", round(sec, 1), " | ", "min = ", round(minute, 1), " | ", "hour = ", round(hour, 1))
                return sec, minute, hour

        return -1, -1, -1

    def read_on_board_sensors(self):
        self.unit_id(13)
        a = self.multiple_register_read("input", 1000, 1, "INT16")
        if a:
            if a[0]:
                return a[0]

        return -1

    def read_temperature(self):
        self.unit_id(13)
        a = self.multiple_register_read("input", 5, 1, "FLOAT32")
        if a:
            if a[0]:
                return a[0]
        return -1

    @staticmethod
    def get_correct_length_by_data_type(_data_type, _length) -> int:
        if _data_type == "FLOAT32" or _data_type == "4Q_FP_PF":
            return _length * 2
        elif _data_type == "INT16":
            return _length
        elif _data_type == "INT64":
            return _length * 4
        else:
            return _length

    @staticmethod
    def render_data(_data_type: str, data: list[int], _big_endian: bool) -> list[float]:
        list_float = []
        if _data_type == "FLOAT32" or _data_type == "4Q_FP_PF":
            list_32_bits = utils.word_list_to_long(data, big_endian=_big_endian)
            for val in list_32_bits:
                list_float.append(round(utils.decode_ieee(val), 2))

            return list_float
        elif _data_type == "INT16":
            return data
        elif _data_type == "INT64":
            while len(data) >= 4:
                this_int_64 = (data[0:4][3] << 16 * 3) + (data[0:4][2] << 16 * 2) + (data[0:4][1] << 16 * 1) + \
                              data[0:4][0]
                list_float.append(this_int_64)
                del data[0:4]

            return list_float
        else:
            return data

    def safe_read_data(self) -> Optional[int]:
        self.write_single_coil(self.register_for_start_read, True)
        data = self.read_holding_registers(self.register_for_data, 1)
        self.write_single_coil(self.register_for_end_read, True)
        if data is not None:
            return int(data[0])
        return None

    def test(self, status: bool = False) -> None:
        self.write_single_coil(self.register_for_test, status)
