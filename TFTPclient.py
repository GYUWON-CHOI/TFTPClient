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

def send_wrq(filename, mode): # WRQ 패킷 전송
    format = f'>h{len(filename)}sB{len(mode)}sB' # 포맷 지정
    wrq_message = pack(format, OPCODE['WRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0) # WRQ 패킷 생성
    sock.sendto(wrq_message, server_address) # 서버에 전송
    print(wrq_message)

def send_rrq(filename, mode): # RRQ 패킷 전송
    format = f'>h{len(filename)}sB{len(mode)}sB'
    rrq_message = pack(format, OPCODE['RRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(rrq_message, server_address)
    print(rrq_message)

def send_ack(seq_num, server): # ACK 패킷 전송
    format = f'>hh'
    ack_message = pack(format, OPCODE['ACK'], seq_num)
    sock.sendto(ack_message, server)
    print(seq_num)
    print(ack_message)

def send_data(block_number, file_block, server_new_socket): # 데이터 패킷 전송
    sock.settimeout(5) # 소켓 타임아웃 설정
    max_retries = 3  # 최대 재시도 횟수
    retries = 0

    while retries < max_retries:
        try:
            format = f'>hh{len(file_block)}s'
            data_packet = pack(format, OPCODE['DATA'], block_number, file_block)
            sock.sendto(data_packet, server_new_socket)
            return
        except socket.timeout:
            retries += 1
            print(f'Timeout({retries}/{max_retries})')

    sys.exit()


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
    send_wrq(filename, mode)
    file = open(filename, 'rb')
    blnum = 1
elif operation.lower() == 'get':
    send_rrq(filename, mode)
    file = open(filename, 'wb')
    expected_block_number = 1
else:
    print("Please use 'put' or 'get'.")

while True:
    # Receive data from the server
    # Server uses a newly assigned port (not 69) to transfer data
    # So ACK should be sent to the new socket
    data, server_new_socket = sock.recvfrom(516)
    opcode = int.from_bytes(data[:2], 'big')

    # Check message type
    if opcode == OPCODE['DATA']: # 데이터 패킷을 수신했을 
        block_number = int.from_bytes(data[2:4], 'big') # 블록 번호 추출
        if block_number == expected_block_number: # 예상 블록 번호와 일치하는 경우
            send_ack(block_number, server_new_socket) # ACK 전송
            file_block = data[4:] # 데이터 블록 추출
            file.write(file_block) # 쓰기
            expected_block_number += 1 # 예상 번호 증가
            print(file_block.decode())
        else:
            send_ack(block_number, server_new_socket)

    elif opcode == OPCODE['ACK']: # ACK을 수신했을 때
        block_number = int.from_bytes(data[2:4], 'big') # 블록 번호 추출
        file_block = file.read(512) # 데이터 블록 읽기
        if block_number == 0 or block_number == blnum: # 블록 번호가 0이거나 예상 블록 번화와 일치하는 경
            send_data(blnum, file_block, server_new_socket) # 데이터 전
            blnum += 1 # 예상 번호 증가
            if not file_block: # 파일 끝에 도달할 경우
                break # 루프 종료
        else:
            send_data(blnum, file_block, server_new_socket)

    elif opcode == OPCODE['ERROR']: # 오류 패킷을 수신했을 때
        error_code = int.from_bytes(data[2:4], byteorder='big')
        if error_code == 1:  # File not found
            print(ERROR_CODE[error_code]) # 오류 메시지 출력
            sys.exit() # 프로그램 종료
        else:
            print(ERROR_CODE[error_code]) # 오류 메시지 출력
            sys.exit() # 프로그램 종료

    else:
        break

    if len(file_block) < BLOCK_SIZE:
        file.close()
        print(len(file_block))
        break
