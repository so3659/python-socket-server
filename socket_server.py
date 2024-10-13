import os
import socket
from datetime import datetime

class SocketServer:
    def __init__(self):
        self.bufsize = 1024  # 버퍼 크기 설정
        with open('./response.bin', 'rb') as file:
            self.RESPONSE = file.read()  # 응답 파일 읽기
        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        """디렉토리 생성"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def run(self, ip, port):
        """서버 실행"""
        # 소켓 생성
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server!\r\n")
        try:
            while True:
                # 클라이언트의 요청 대기
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)  # 타임아웃 설정(5초)
                print("Request message...\r\n")
                response = b""
                try:
                    while True:
                        data = clnt_sock.recv(self.bufsize)
                        if not data:
                            break
                        response += data
                except socket.timeout:
                    print("Connection timed out")

                now = datetime.now()
                filename = self.DIR_PATH + now.strftime('/%Y-%m-%d-%H-%M-%S.bin')
                with open(filename, 'wb') as file:
                    file.write(response)
                print(f"Request saved to {filename}")

                try:
                    headers_end = response.find(b'\r\n\r\n') + 4
                    headers = response[:headers_end].decode('iso-8859-1')
                    body = response[headers_end:]

                    boundary = ''
                    for line in headers.split('\r\n'):
                        if line.lower().startswith('content-type:'):
                            if 'boundary=' in line:
                                boundary = line.split('boundary=')[1].strip()
                                if boundary.startswith('"') and boundary.endswith('"'):
                                    boundary = boundary[1:-1]
                                break

                    if boundary:
                        boundary_bytes = ('--' + boundary).encode('utf-8')
                        parts = body.split(boundary_bytes)
                        for part in parts:
                            part = part.strip(b'\r\n')
                            if not part or part == b'--':
                                continue
                            part_headers_end = part.find(b'\r\n\r\n') + 4
                            part_headers = part[:part_headers_end].decode('iso-8859-1')
                            part_body = part[part_headers_end:]

                            filename = 'image.png'

                            if filename:
                                with open(filename, 'wb') as img_file:
                                    img_file.write(part_body)
                                print(f"Image saved to {filename}")
                    else:
                        print("No multipart boundary found.")
                except Exception as e:
                    print(f"Error parsing multipart data: {e}")

                print("Received data:")
                print(response.decode('utf-8', errors='replace'))
                # 응답 전송
                clnt_sock.sendall(self.RESPONSE)
                # 클라이언트 소켓 닫기
                clnt_sock.close()
        except KeyboardInterrupt:
            print("\r\nStop the server...")
            # 서버 소켓 닫기
            self.sock.close()

if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)
