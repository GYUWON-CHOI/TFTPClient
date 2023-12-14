# TFTPClient
이 프로젝트는 간단한 TFTP 클라이언트입니다. 이 클라이언트는 TFTP 서버에서 파일을 업로드(put)하거나 다운로드(get)할 수 있습니다.

# 사용법
    python tftpcli.py ip_address [-p port_number] <get|put> filename

> # 인수
> ip_address : TFTP 서버의 IP 주소
> -p : 포트번호
> <get|put> : 서버에서 파일을 가져오거나 업로드할지 지정
> filename : 전송할 파일 이름
