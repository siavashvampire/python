# import json
#
# from pyModbusTCP import utils
# from pyModbusTCP.client import ModbusClient
# import math
#
# __debug = 0
#
#
# def single_register_read(_input_or_holding, _address, _data_type, _big_endian=False):
#     if (_data_type == "32bit_float"):
#         if (_input_or_holding == "input"):
#             data = client.read_input_registers(_address, 2)
#         if (_input_or_holding == "holding"):
#             data = client.read_holding_registers(_address, 2)
#         if data:
#             list_32_bits = utils.word_list_to_long(data, big_endian=_big_endian)
#             float_32bit_val = round(utils.decode_ieee(list_32_bits[0]), 2)
#             if (__debug):
#                 print("{:.2f}".format(float_32bit_val))
#             return float_32bit_val
#
#     if (_data_type == "16bit_uint"):
#         if (_input_or_holding == "input"):
#             data = client.read_input_registers(_address, 1)
#         if (_input_or_holding == "holding"):
#             data = client.read_holding_registers(_address, 1)
#
#         if data:
#             uint_16bit_val = data[0]
#             if (__debug):
#                 print(uint_16bit_val)
#             return uint_16bit_val
#
#
# def multiple_register_read(_input_or_holding, _address, _length, _data_type, _big_endian=False):
#     if (_data_type == "FLOAT32"):
#         list_float_32bit = []
#         if (_input_or_holding == "input"):
#             data = client.read_input_registers(_address, 2 * _length)
#         if (_input_or_holding == "holding"):
#             data = client.read_holding_registers(_address, 2 * _length)
#         if data:
#             list_32_bits = utils.word_list_to_long(data, big_endian=_big_endian)
#             for val in list_32_bits:
#                 list_float_32bit.append(round(utils.decode_ieee(val), 2))
#             if (__debug):
#                 print(list_float_32bit)
#
#             return list_float_32bit
#
#     if (_data_type == "INT16"):
#         if (_input_or_holding == "input"):
#             data = client.read_input_registers(_address, _length)
#         if (_input_or_holding == "holding"):
#             data = client.read_holding_registers(_address, _length)
#         if data:
#             list_uint_16bit = data
#             if (__debug):
#                 print(list_uint_16bit)
#
#             return list_uint_16bit
#
#     if (_data_type == "4Q_FP_PF"):
#         list_4Q_FP_PF = []
#         if (_input_or_holding == "input"):
#             data = client.read_input_registers(_address, _length * 2)
#         if (_input_or_holding == "holding"):
#             data = client.read_holding_registers(_address, _length * 2)
#         if data:
#             list_32_bits = utils.word_list_to_long(data, big_endian=_big_endian)
#             for val in list_32_bits:
#                 list_4Q_FP_PF.append(round(utils.decode_ieee(val), 2))
#             if (__debug):
#                 print(list_4Q_FP_PF)
#
#             return list_4Q_FP_PF
#
#     if (_data_type == "INT64"):
#         list_INT64 = []
#         if (_input_or_holding == "input"):
#             data = client.read_input_registers(_address, _length * 4)
#         if (_input_or_holding == "holding"):
#             data = client.read_holding_registers(_address, _length * 4)
#         if data:
#             while (len(data) >= 4):
#                 this_INT64 = (data[0:4][3] << 16 * 3) + (data[0:4][2] << 16 * 2) + (data[0:4][1] << 16 * 1) + data[0:4][
#                     0]
#                 list_INT64.append(this_INT64)
#                 del data[0:4]
#             if (__debug):
#                 print(list_INT64)
#
#             return list_INT64
#
#
# def Read_PM2100(client_obj, RS485_address):
#     client_obj.unit_id(RS485_address)
#     incoming_data = []
#
#     incoming_data_part1 = multiple_register_read("holding", 3000, 17, "FLOAT32")
#     print("incoming_data_part1 : ", incoming_data_part1)
#     num = incoming_data_part1[0]
#     print(num != num)
#     print(float("nan"))
#     incoming_data_part2 = multiple_register_read("holding", 3036, 21, "FLOAT32")
#     print("incoming_data_part2 : ", incoming_data_part2)
#     incoming_data_part3 = multiple_register_read("holding", 3078, 8, "4Q_FP_PF")
#     print("incoming_data_part3 : ", incoming_data_part3)
#     incoming_data_part4 = multiple_register_read("holding", 3110, 1, "FLOAT32")
#     print("incoming_data_part4 : ", incoming_data_part4)
#     incoming_data_part5 = multiple_register_read("holding", 3194, 1, "FLOAT32")
#     print("incoming_data_part5 : ", incoming_data_part5)
#     incoming_data_part6 = multiple_register_read("holding", 3204, 12, "INT64")
#     print("incoming_data_part6 : ", incoming_data_part6)
#     incoming_data_part7 = multiple_register_read("holding", 3272, 4, "INT64")
#     print("incoming_data_part7 : ", incoming_data_part7)
#     incoming_data_part8 = multiple_register_read("holding", 3304, 12, "INT64")
#     print("incoming_data_part8 : ", incoming_data_part8)
#     incoming_data_part9 = multiple_register_read("holding", 3518, 9, "INT64")
#     print("incoming_data_part9 : ", incoming_data_part9)
#
#     try:
#         incoming_data = incoming_data_part1 + \
#                         incoming_data_part2 + \
#                         incoming_data_part3 + \
#                         incoming_data_part4 + \
#                         incoming_data_part5 + \
#                         incoming_data_part6 + \
#                         incoming_data_part7 + \
#                         incoming_data_part8 + \
#                         incoming_data_part9
#
#         for a in incoming_data:
#             print(incoming_data.index(a) + 1, " | ", a)
#
#         print("------------------")
#         print("Size : ", len(incoming_data))
#
#         dict_data_out = {
#             "Current_A": incoming_data[0],
#             "Current_B": incoming_data[1],
#             "Current_C": incoming_data[2],
#             "Current_N": incoming_data[3],
#             "Current_G": incoming_data[4],
#             "Current_Avg": incoming_data[5],
#
#             "Current_Unbalance_A": incoming_data[6],
#             "Current_Unbalance_B": incoming_data[7],
#             "Current_Unbalance_C": incoming_data[8],
#             "Current_Unbalance_Worst": incoming_data[9],
#
#             "Voltage_A_B": incoming_data[10],
#             "Voltage_B_C": incoming_data[11],
#             "Voltage_C_A": incoming_data[12],
#             "Voltage_L_L_Avg": incoming_data[13],
#             "Voltage_A_N": incoming_data[14],
#             "Voltage_B_N": incoming_data[15],
#             "Voltage_C_N": incoming_data[16],
#             "Voltage_L_N_Avg": incoming_data[17],
#
#             "Voltage_Unbalance_A_B": incoming_data[18],
#             "Voltage_Unbalance_B_C": incoming_data[19],
#             "Voltage_Unbalance_C_A": incoming_data[20],
#             "Voltage_Unbalance_L_L_Worst": incoming_data[21],
#             "Voltage_Unbalance_A_N": incoming_data[22],
#             "Voltage_Unbalance_B_N": incoming_data[23],
#             "Voltage_Unbalance_C_N": incoming_data[24],
#             "Voltage_Unbalance_L_N_Worst": incoming_data[25],
#
#             "Active_Power_A": incoming_data[26],
#             "Active_Power_B": incoming_data[27],
#             "Active_Power_C": incoming_data[28],
#             "Active_Power_Total": incoming_data[29],
#             "Reactive_Power_A": incoming_data[30],
#             "Reactive_Power_B": incoming_data[31],
#             "Reactive_Power_C": incoming_data[32],
#             "Reactive_Power_Total": incoming_data[33],
#             "Apparent_Power_A": incoming_data[34],
#             "Apparent_Power_B": incoming_data[35],
#             "Apparent_Power_C": incoming_data[36],
#             "Apparent_Power_Total": incoming_data[37],
#
#             "Power_Factor_A": incoming_data[38],
#             "Power_Factor_B": incoming_data[39],
#             "Power_Factor_C": incoming_data[40],
#             "Power_Factor_Total": incoming_data[41],
#             "Displacement_Power_Factor_A": incoming_data[42],
#             "Displacement_Power_Factor_B": incoming_data[43],
#             "Displacement_Power_Factor_C": incoming_data[44],
#             "Displacement_Power_Factor_Total": incoming_data[45],
#
#             "Frequency": incoming_data[46],
#
#             "Power_Factor_Total_IEEE": incoming_data[47],
#
#             "Active_Energy_Delivered_Into_Load": incoming_data[48],
#             "Active_Energy_Received_Out_of_Load": incoming_data[49],
#             "Active_Energy_Delivered_Pos_Received": incoming_data[50],
#             "Active_Energy_Delivered_Neg_Received": incoming_data[51],
#             "Reactive_Energy_Delivered": incoming_data[52],
#             "Reactive_Energy_Received": incoming_data[53],
#             "Reactive_Energy_Delivered_Pos_Received": incoming_data[54],
#             "Reactive_Energy_Delivered_Neg_Received": incoming_data[55],
#             "Apparent_Energy_Delivered": incoming_data[56],
#             "Apparent_Energy_Received": incoming_data[57],
#             "Apparent_Energy_Delivered_Pos_Received": incoming_data[58],
#             "Apparent_Energy_Delivered_Neg_Received": incoming_data[59],
#
#             "Reactive_Energy_in_Quadrant_I": incoming_data[60],
#             "Reactive_Energy_in_Quadrant_II": incoming_data[61],
#             "Reactive_Energy_in_Quadrant_III": incoming_data[62],
#             "Reactive_Energy_in_Quadrant_IV": incoming_data[63],
#
#             "Active_Energy_Delivered_Into_Load_Permanent": incoming_data[64],
#             "Active_Energy_Received_Out_of_Load_Permanent": incoming_data[65],
#             "Active_Energy_Delivered_Pos_Received_Permanent": incoming_data[66],
#             "Active_Energy_Delivered_Neg_Received_Permanent": incoming_data[67],
#             "Reactive_Energy_Delivered_Permanent": incoming_data[68],
#             "Reactive_Energy_Received_Permanent": incoming_data[69],
#             "Reactive_Energy_Delivered_Pos_Received_Permanent": incoming_data[70],
#             "Reactive_Energy_Delivered_Neg_Received_Permanent": incoming_data[71],
#             "Apparent_Energy_Delivered_Permanent": incoming_data[72],
#             "Apparent_Energy_Received_Permanent": incoming_data[73],
#             "Apparent_Energy_Delivered_Pos_Received_Permanent": incoming_data[74],
#             "Apparent_Energy_Delivered_Neg_Received_Permanent": incoming_data[75],
#
#             "Active_Energy_Delivered_Phase_A": incoming_data[76],
#             "Active_Energy_Delivered_Phase_B": incoming_data[77],
#             "Active_Energy_Delivered_Phase_C": incoming_data[78],
#             "Reactive_Energy_Delivered_Phase_A": incoming_data[79],
#             "Reactive_Energy_Delivered_Phase_B": incoming_data[80],
#             "Reactive_Energy_Delivered_Phase_C": incoming_data[81],
#             "Apparent_Energy_Delivered_Phase_A": incoming_data[82],
#             "Apparent_Energy_Delivered_Phase_B": incoming_data[83],
#             "Apparent_Energy_Delivered_Phase_C": incoming_data[84]
#         }
#
#         json_data_out = json.dumps(dict_data_out, indent=2)
#
#         return json_data_out
#
#     except:
#         print("Error")
#
#
# def read_on_timer():
#     client.unit_id(13)
#     a = multiple_register_read("input", 1, 1, "INT64")
#     if (a):
#         sec = a[0] / 1000
#         min = sec / 60
#         hour = min / 60
#
#         print("sec = ", round(sec, 1), " | ", "min = ", round(min, 1), " | ", "hour = ", round(hour, 1))
#
#
# def read_onBoard_sensors():
#     client.unit_id(13)
#     a = multiple_register_read("input", 41, 1, "INT16")
#     if (a):
#         if (a[0]):
#             print(a[0])
#
#
# def read_num_of_data_in_queue():
#     client.unit_id(13)
#     a = multiple_register_read("input", 61, 1, "INT16")
#     if (a):
#         if (a[0]):
#             print(a[0])
#
#
# def read_temperature():
#     client.unit_id(13)
#     a = multiple_register_read("input", 5, 1, "FLOAT32")
#     if (a):
#         print(a[0])
#
#
# def enable_sensor_edge():
#     client.unit_id(13)
#     client.write_single_coil(1, 1)
#
#
# def disable_sensor_edge():
#     client.unit_id(13)
#     client.write_single_coil(1, 0)
#
#
# def enable_sensor_time():
#     client.unit_id(13)
#     client.write_single_coil(2, 1)
#
#
# def disable_sensor_time():
#     client.unit_id(13)
#     client.write_single_coil(2, 0)
#
#
# def read_input_status():
#     client.unit_id(13)
#     state = client.read_coils(11, 4)
#
#     if (state):
#         return state
#
#
# client = ModbusClient(host="192.168.1.239", port=502, auto_open=True, auto_close=True, timeout=2.2, debug=False)
# # client.unit_id(13)
#
# q = Read_PM2100(client, 5)
# print(q)
#
# q = Read_PM2100(client, 4)
# print(q)
#
# # while(1):
# # print(read_input_status())
# # read_on_timer()
# # read_temperature()
# # read_onBoard_sensors()
# # read_num_of_data_in_queue()
# # sleep(0.5)
