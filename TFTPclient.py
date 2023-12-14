#!/usr/bin/python3
'''
$ tftp ip_address [-p port_mumber] <get|put> filename
'''
import sys
import socket
import argparse
from struct import pack

DEFAULT_PORT = 69
BLOCK_SIZE = 512
DEFAULT_TRANSFER_MODE = 'octet'

OPCODE = {'RRQ': 1, 'WRQ': 2, 'DATA': 3, 'ACK': 4, 'ERROR': 5}
MODE = {'netascii': 1, 'octet': 2, 'mail': 3}

ERROR_CODE = {
    0: "Not defined, see error message (if any).",
    1: "File not found.",
    2: "Access violation.",
    3: "Disk full or allocation exceeded.",
    4: "Illegal TFTP operation.",
    5: "Unknown transfer ID.",
    6: "File already exists.",
    7: "No such user."
}

def send_wrq(filename, mode):
    format = f'>h{len(filename)}sB{len(mode)}sB'
    wrq_message = pack(format, OPCODE['WRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(wrq_message, server_address)
    print(wrq_message)

def send_rrq(filename, mode):
    format = f'>h{len(filename)}sB{len(mode)}sB'
    rrq_message = pack(format, OPCODE['RRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(rrq_message, server_address)
    print(rrq_message)

def send_ack(seq_num, server):
    format = f'>hh'
    ack_message = pack(format, OPCODE['ACK'], seq_num)
    sock.sendto(ack_message, server)
    print(seq_num)
    print(ack_message)

def send_data(block_number, file_block, server_new_socket):
    sock.settimeout(5)
    try:
        format = f'>hh{len(file_block)}s'
        data_packet = pack(format, OPCODE['DATA'], block_number, file_block)
        sock.sendto(data_packet, server_new_socket)
        print(block_number)
    except socket.timeout:
        print("데이터 전송 중 타임아웃이 발생했습니다. 다시 시도 중...")

# Parse command line arguments
parser = argparse.ArgumentParser(description='TFTP client program')
parser.add_argument(dest="host", help="Server IP address", type=str)
parser.add_argument(dest="operation", help="get or put a file", type=str)
parser.add_argument(dest="filename", help="name of file to transfer", type=str)
parser.add_argument("-p", "--port", dest="port", type=int)
args = parser.parse_args()

'''
if validators.domain(args.host):
    serber_ip = gethostbyname(args.host) 
else
    server_ip = args.host

if args.port == None:
    server_port = DEFAULT_PORT
'''

# Create a UDP socket
server_ip = args.host
server_port = DEFAULT_PORT
server_address = (server_ip, server_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mode = DEFAULT_TRANSFER_MODE
operation = args.operation
filename = args.filename

if operation.lower() == 'put':
    sock.settimeout(5)
    send_wrq(filename, mode)
    file = open(filename, 'rb')
    blnum = 1
elif operation.lower() == 'get':
    send_rrq(filename, mode)
    file = open(filename, 'wb')
    expected_block_number = 1
else:
    print("Invalid operation. Please use 'put' or 'get'.")

while True:
    # Receive data from the server
    # Server uses a newly assigned port (not 69) to transfer data
    # So ACK should be sent to the new socket
    data, server_new_socket = sock.recvfrom(516)
    opcode = int.from_bytes(data[:2], 'big')

    # Check message type
    if opcode == OPCODE['DATA']:
        block_number = int.from_bytes(data[2:4], 'big')
        if block_number == expected_block_number:
            send_ack(block_number, server_new_socket)
            file_block = data[4:]
            file.write(file_block)
            expected_block_number += 1
            print(file_block.decode())
        else:
            send_ack(block_number, server_new_socket)

    elif opcode == OPCODE['ACK']:
        block_number = int.from_bytes(data[2:4], 'big')
        file_block = file.read(512)
        if block_number == 0 or block_number == blnum:
            send_data(blnum, file_block, server_new_socket)
            blnum += 1
            if not file_block:
                break
        else:
            send_data(blnum, file_block, server_new_socket)

    elif opcode == OPCODE['ERROR']:
        error_code = int.from_bytes(data[2:4], byteorder='big')
        if error_code == 1:  # File not found
            print(ERROR_CODE[error_code])
            sys.exit()
        else:
            print(ERROR_CODE[error_code])
            sys.exit()

    else:
        break

    if len(file_block) < BLOCK_SIZE:
        file.close()
        print(len(file_block))
        break
