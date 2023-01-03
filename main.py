import time
from pymodbus.client import ModbusTcpClient as ModbusClient
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian


def init_firestore():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
        db_object = firestore.client()
        print('Firestore connected')
        return db_object
    except Exception as e:
        print("Init Firestore Exception: " + str(e))


def get_values():
    print("Get Values start")
    global value
    global name
    global db_o
    global my_Dict
    global temp_dict
    dict_my = {}

    db_o = init_firestore()

    try:
        for i in range(105):
            read2 = client.read_input_registers(address=i , count=2, slave=1)
            if i in float_list:
                real_decoder = BinaryPayloadDecoder.fromRegisters(read2.registers,byteorder = Endian.Big, wordorder=Endian.Little)
                val=real_decoder.decode_32bit_float()
                name = dict_trans_id_name[i]
                temp_dict = {name:round(val,2)}
            elif i in const_list:
                name = dict_trans_id_name[i]
                temp_dict = {name:read2.registers[0]}
            if dict_name_value[name] != temp_dict[name]:
                    dict_name_value[name] = temp_dict[name]
                    print("Value Change for " + name + "=" + str(dict_name_value[name]))
            if dict_my != dict_name_value:
                dict_my = dict_name_value
                print("Pushing Data : "+str(dict_my))
                db_o.collection(u'CP Factory').document('Lathe Machine').set(
                dict_name_value, merge=True)
           
       
    except Exception as e:
        if str(e).startswith("Modbus Error: [Connection] Failed to connect"):
            print("Machine is off")
            db_o.collection(u'CP Factory').document('Lathe Machine').set(
                {"power_on": 0}, merge=True)
            print("Connecting with PLC")
            client.connect()
        else:
            print(e)
            db_o.collection(u'CP Factory').document('Lathe Machine').set(
                {"error": str(e)}, merge=True)
            

def main():
    case = 1
    while 1:
        if case == 1:
            try:
                print("Connecting with PLC")
                client.connect()
                print("Connected with PLC")
                case = 2
            except Exception as e:
                print("Case 1 Exception" + str(e))
                case = 1
        elif case == 2:
            print("In Case 2")
            try:
                #time.sleep(1)
                get_values()
                print("**************************")
            except Exception as except_name:
                print("Case 2 Exception: " + str(except_name))


if __name__ == '__main__':
    const_list = [7, 6, 0, 8, 12, 94, 90, 92, 1, 5, 2, 10]
    float_list = [15, 17, 24, 26, 28, 40, 42, 44, 80, 82, 78]
    trans_id = 0
    value = 0
    power_on = 0
    PLC_IP = "10.213.120.118"
    PLC_PORT = 502
    client = ModbusClient(PLC_IP, port=PLC_PORT)
    UNIT = 1
    my_Dict = {}
    temp_dict = {}
    dict_trans_id_name = {7: 'model', 6: 'cycle_time', 0: 'power_on', 8: 'presence_of_allen_key', 
                           12: 'spindle_rpm', 94: 'performance', 90: 'availability', 92: 'quality', 1: 'cumm_ok_product',
                           5: 'cumm_not_ok_product', 2: 'ok_product',10: 'not_ok_product',
                            15: 'feed_rate',17: 'depth', 24: 'v1', 26: 'v2', 28: 'v3', 40: 'i1',
                            42: 'i2', 44: 'i3',80: 'frequency', 82: 'kwh', 78: 'average_pf'
                          }

                    

    dict_name_value = {'model': 0, 'cycle_time': 0, 'power_on': 0, 'presence_of_allen_key': 0, 'feed_rate': 0,
                       'spindle_rpm': 0,
                       'depth': 0, 'performance': 0, 'availability': 0, 'quality': 0, 'cumm_ok_product': 0,
                       'cumm_not_ok_product': 0, 'ok_product': 0,
                       'not_ok_product': 0, 'v1': 0, 'v2': 0, 'v3': 0, 'i1': 0, 'i2': 0, 'i3': 0, 'frequency': 0,
                       'kwh': 0, 'average_pf': 0, 'error': ""}

    main()
