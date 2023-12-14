# TFTPClient
이 프로젝트는 간단한 TFTP 클라이언트입니다. 이 클라이언트는 TFTP 서버에서 파일을 업로드(put)하거나 다운로드(get)할 수 있습니다.

# 사용법
    python TFTPcli.py ip_address [-p port_number] <get|put> filename

# 인수
* ip_address : TFTP 서버의 IP 주소입니다.
* <get|put> : 서버에서 파일을 가져오거나 업로드할지 지정합니다.
* filename : 전송할 파일 이름입니다.

# 기능
* 파일의 업로드(put)와 다운로드(get)을 지원합니다.
* UDP 통신을 사용합니다.
* 요청한 파일이 서버에 없을 경우 사용자에게 알리고 종료하는 파일 오류처리가 가능합니다.
* 
