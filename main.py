from woocommerce import API
import PySimpleGUI as sg
import serial
import time
import subprocess
import requests

orders_dict = {}
send_list = []

'''
Orders are stored in the orders_dict dictionary, current structure:
Key         |   Value
            |   Key       |   Value
------------|-----------------------------------------
OrderNo     |   name      |   'John Doe'
            |   products  |   [product name, quantity]
            |   total_num |   8
'''


def connect_printer(port):
    global arduino
    arduino = serial.Serial(port=port, baudrate=9600, timeout=3)
    time.sleep(3)
    print_data("Marco")
    if read_data() == 'Polo':
        return True
    else:
        return False


def print_data(data):
    arduino.write(bytes(data, 'utf-8'))
    time.sleep(2)


def read_data():
    return arduino.readline().decode('utf-8').strip()


def auto_connect(all_ports):
    for port in all_ports:
        if connect_printer(port) == True:
            return True
    return False


def generate_orders():
    wcapi = API(
        url="https://example.com",
        consumer_key="*********",
        consumer_secret="********",
        timeout=100,
        wp_api=True,
        version="wc/v3"
    )

    # results = wcapi.get("orders", params={'status': 'processing'}).json() #Show only orders in status processing
    results = wcapi.get("orders", params={'per_page': '5'}).json()  # Show latest n orders, regardless of their status
    if len(results) == 0:
        message_screen('No orders found', 1)

    for res in results:
        orderno = res['id']
        name = f"{res['billing']['first_name']} {res['billing']['last_name']}"
        products = res['line_items']
        orders_dict[orderno] = {'name': name}
        orders_dict[orderno]['products'] = []
        orders_dict[orderno]['total_num'] = len(products)
        for product in products:
            product_name = product['name']
            product_number = product['quantity']
            orders_dict[orderno]['products'].append([product_name, product_number])


def print_all_orders():
    for key in orders_dict:
        send_list = []
        send_list.append(f"Name: [{key}]{orders_dict[key]['name']}")
        send_list.append("Products:")
        for value in orders_dict[key]['products']:
            send_list.append(f"{value[0]} x {value[1]}")
        print(f"List generated: {send_list}")
        for line in send_list:
            print(f"Printing: {line}")
            print_data(line)
        print_data('-------')
        print("--List done--")


def print_order(orderid):
    send_list = []
    send_list.append(f"[{orderid}]{orders_dict[orderid]['name']}:")
    for entry in orders_dict[orderid]['products']:
        send_list.append(f"{entry[0]} x {entry[1]}")
    print(f"Send list: {send_list}")
    for line in send_list:
        print_data(line)
    print_data('-------')
    print_data('-------')


def generate_window_layout():
    layout_l = []
    layout_r = [[sg.Output(s=(90, 25))]]
    for key in orders_dict:
        layout_l.append([sg.Button(key), sg.Text(orders_dict[key]['name']), sg.Text(len(orders_dict[key]['products']))])
        layout_l.append([sg.HSep()])
    layout_full = [[sg.Col(layout_l), sg.VSep(), sg.Col(layout_r)],
                   [sg.HSep()],
                   [sg.Button('Refresh'), sg.Button('Exit')]]
    return layout_full


def generate_portwindow_layout(all_ports):
    layout = []
    for value in all_ports:
        layout.append([sg.Radio(value, 'port')])
    layout.append([sg.Button('Select'), sg.Button('AutoConnect')])
    return layout


def port_selection_sreen():
    ports = list(subprocess.run("ls /dev/cu.*", shell=True, capture_output=True).stdout.decode("utf-8").split('\n'))
    ports.remove("")
    if len(ports) == 0:
        message_screen('No ports found, make sure that the printer is connected.', 1)
    layout = generate_portwindow_layout(ports)
    window = sg.Window('Ports', layout=layout)
    while True:
        event, value = window.read()
        if event == 'Select':
            if return_value(value):
                if connect_printer(ports[return_value(value)]) == True:
                    break
            else:
                message_screen('Please select port', 0)
        elif event == 'AutoConnect':
            if auto_connect(ports) == True:
                break
            else:
                message_screen("No compatible ports found", 0)
        elif event == sg.WIN_CLOSED:
            exit()


def return_value(res_dict):
    for res in res_dict:
        if res_dict[res] == True:
            return res


def order_selection_screen():
    layout = generate_window_layout()
    window = sg.Window('Orders', layout)
    while True:
        value, event = window.read()
        if event == sg.WIN_CLOSED:
            break
        if value != 'Refresh' and int(value) in list(orders_dict.keys()):
            print(f'The current order id was selected: {value}')
            print_order(int(value))
        elif value == 'Refresh':
            window.refresh()
            print('Orders refreshed')
        elif value == 'Exit':
            break


def message_screen(text, severity):
    '''
    Severity chart:
    Number  Name        Action
    0       Warnings    Only displays the message
    1       Errors      Displays the message and exits the code
    '''
    layout = [[sg.Text(text, s=(40, 10))], [sg.Button('Exit')]]
    window = sg.Window('Error', layout)
    while True:
        value, event = window.read()
        if value == 'Exit' or event == sg.WIN_CLOSED:
            if severity == 0:
                window.close()
                break
            elif severity == 1:
                exit()


def website_connection_check():
    try:
        requests.get('https://example.com')
    except:
        message_screen('Connection to Example failed to establish, check your internet.', 1)


if __name__ == '__main__':
    website_connection_check()
    port_selection_sreen()
    generate_orders()
    order_selection_screen()
