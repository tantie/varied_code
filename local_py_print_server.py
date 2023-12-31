"""
настройка службы печати если нужна поддержка сублимационных фото принтеров:

обновляемся
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*
sudo apt-get update

устанавливаем cups
sudo apt-get install cups

устанавливаем gutenprint
sudo apt-get install printer-driver-gutenprint 

устанавливаем selphy_print тк в нем недостающие библиотеки для новых либо совсем старых принтеров
git clone https://git.shaftnet.org/gitea/slp/selphy_print.git
cd selphy_print
make
sudo make install

создаем img папку с правами 
mkdir -p /home/pi/img/ 
chmod 755 /home/pi/img/


stop process если остался в памяти:
sudo fuser -k 5000/tcp

"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from datetime import datetime
import subprocess

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        print(f"Received request with content length: {content_length} bytes")

        image_data = self.rfile.read(content_length)
        if image_data:
            filename = f"image_{int(datetime.now().timestamp())}.png"
            image_path = f"/home/pi/img/{filename}"

            with open(image_path, 'wb') as image_file:
                image_file.write(image_data)

            # Печать изображения
            try:
                printer_name = "canon"  # имя вашего принтера
                command = ["lp", "-d", printer_name, image_path]
                subprocess.run(command, check=True)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Image received and sent to the printer.")
            except subprocess.CalledProcessError as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Failed to print the image.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No data received in the request.")

httpd = HTTPServer(('0.0.0.0', 5000), SimpleHTTPRequestHandler)
print("Server started on port 5000...")
httpd.serve_forever()
