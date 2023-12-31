from abc import ABCMeta, abstractmethod
import json
import logging
import os
import socket
import struct


class TCPConnection(metaclass=ABCMeta):
    HEADER_FORMAT = '16s1s47s'
    HEADER_SIZE = 64
    REQUEST_SIZE = 16
    MEDIA_TYPE_SIZE = 1
    PAYLOAD_SIZE = 47

    BUFFER_SIZE = 1400
    TIMEOUT = 60

    DEST_DIR = './dest'

    def __init__(self, host: str, port: int, logger: logging.Logger):
        self.logger = logger
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    @abstractmethod
    def run(self):
        raise NotImplementedError

    def send_header(self, sock: socket.socket, media_type: str, request: dict, file_path: str):
        request_size = len(bytes(json.dumps(request), 'utf-8'))
        media_type_size = len(bytes(media_type, 'utf-8')) if media_type else 0
        payload_size = os.path.getsize(file_path) if file_path else 0
        self.logger.info(
            f'request_size: {request_size}, media_type_size: {media_type_size}, payload_size: {payload_size}')
        packed_header = struct.pack(TCPConnection.HEADER_FORMAT,
                                    int.to_bytes(request_size, TCPConnection.REQUEST_SIZE, 'big'),
                                    int.to_bytes(media_type_size, TCPConnection.MEDIA_TYPE_SIZE, 'big'),
                                    int.to_bytes(payload_size, TCPConnection.PAYLOAD_SIZE, 'big'))
        sock.send(packed_header)

    def send_body(self, sock: socket.socket, media_type: str, request: dict, file_path: str):
        # jsonを送信する
        json_data = json.dumps(request)
        sock.send(bytes(json_data, 'utf-8'))
        # media_typeを送信する
        sock.send(bytes(media_type, 'utf-8'))
        # ファイルを読み込んで送信する
        if not os.path.exists(file_path):
            self.logger.info(f'File: {file_path} does not exist!')
            return
        with open(file_path, 'rb') as f:
            try:
                # self.buffer_size分ずつファイルを読み込んで送信する
                while True:
                    data = f.read(TCPConnection.BUFFER_SIZE)
                    if data:
                        sock.send(data)
                    else:
                        self.logger.info('File has been sent!')
                        break
            # socketが例外を発生させたら接続を切る
            except socket.error:
                sock.close()

    def receive_header(self, sock: socket.socket) -> tuple[int, int, int]:
        self.logger.info('Waiting for header...')
        header = sock.recv(TCPConnection.HEADER_SIZE)
        request_size_bytes, media_type_size_bytes, payload_size_bytes = struct.unpack(TCPConnection.HEADER_FORMAT,
                                                                                      header)
        request_size = int.from_bytes(request_size_bytes, 'big')
        media_type_size = int.from_bytes(media_type_size_bytes, 'big')
        payload_size = int.from_bytes(payload_size_bytes, 'big')
        return request_size, media_type_size, payload_size

    def receive_body(self, sock: socket.socket, request_size: int, media_type_size: int, payload_size: int) -> tuple[
            dict, str,]:
        # jsonを受信する
        request_bytes = sock.recv(request_size)
        request_string = request_bytes.decode('utf-8')
        # dictに変換する
        request = json.loads(request_string)

        # メディアタイプを受信する
        media_type_bytes = sock.recv(media_type_size)
        media_type = media_type_bytes.decode('utf-8')

        # ファイルを受信する
        address, port = sock.getsockname()
        file_name = f'{address}_{port}.' + media_type
        if not os.path.exists(TCPConnection.DEST_DIR):
            os.makedirs(TCPConnection.DEST_DIR)
        file_path = os.path.join(TCPConnection.DEST_DIR, file_name)
        self.logger.info(f'Saving file to {file_path}')
        with open(file_path, 'wb') as f:
            while payload_size > 0:
                data = sock.recv(TCPConnection.BUFFER_SIZE)
                f.write(data)
                payload_size -= len(data)
            self.logger.info('File has been received!')
        return request, file_name
