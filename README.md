# TFTPClient
이 프로젝트는 간단한 TFTP 클라이언트입니다. 이 클라이언트는 TFTP 서버에서 파일을 업로드(put)하거나 다운로드(get)할 수 있습니다.

# 사용법
    python TFTPcli.py ip_address [-p port_number] <get|put> filename

# 인수
* 'ip_address' : TFTP 서버의 IP 주소입니다.
* '<get|put>' : 서버에서 파일을 가져오거나 업로드할지 지정합니다.
* 'filename' : 전송할 파일 이름입니다.

# 기능
* 파일의 업로드(put)와 다운로드(get)을 지원합니다.
* UDP 통신을 사용합니다.
* 요청한 파일이 서버에 없을 경우 사용자에게 알리고 종료하는 파일 오류처리가 가능합니다.
* 데이터블록을 전송할 때 타임아웃을 처리합니다.

# 실행 예시
    $ python TFTPcli.py 203.250.133.88 put tftp.conf
    $ python TFTPcli.py 203.250.133.88 get tftp.txt

# 코드 구조
*  'send_wrq' : 서버에 WRQ 패킷을 전송하는 함수입니다. put을 할 시에 사용됩니다.
*  'send_rrq' : 서버에 RRQ 패킷을 전송하는 함수입니다. get을 할 시에 사용됩니다.
*  'send_ack' : 서버에 ACK을 전송하는 함수입니다. get을 할 시에 사용됩니다.
*  'send_data' : 서버에 데이터 패킷을 전송하는 함수입니다. put을 할 시에 사용됩니다.
*  클라이언트 동작에 따라 'send_wrq' 또는 'send_rrq'를 호출하고 작업을 시작합니다.
*  서버로부터 데이터를 수신하고, 데이터 형식을 확인하여 ACK 또는 데이터패킷을 전송합니다.
