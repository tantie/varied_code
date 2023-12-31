"""
простой принт сервер с обработкой ошибок и выводом данных. код в процессе разработки и отладки

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


stop process:
sudo fuser -k 5000/tcp

"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from datetime import datetime
import subprocess
import time

log_file_path = "/home/pi/print_log.txt"
printer_name = "canon" #название принтера
pause_duration = 8 #ждем принтер

if not os.path.exists(log_file_path):
    with open(log_file_path, "w") as log_file:
        log_file.write("0,10,10\n")

def read_log(): #пишем статистику печати допишу позже
    try:
        with open(log_file_path, "r") as log_file:
            last_line = log_file.readlines()[-1]
            total_printed, prints_left, total_prints = map(int, last_line.split(','))
            return total_printed, prints_left, total_prints
    except Exception as e:
        print(f"Error reading log: {e}")
        return 0, 10, 10

def is_printer_enabled(printer_name): #проверяем состояние принтера
    result = subprocess.run(['lpstat', '-p', printer_name], stdout=subprocess.PIPE)
    output = result.stdout.decode().strip()
    return "is idle." in output or "is printing." in output or "is busy." in output

def enable_printer(printer_name): #активируем принтер если он не желает печатать из-за придуманных причин
    subprocess.run(['sudo', 'cupsenable', printer_name])

def get_print_status(job_id): #проверяем в лоб ошибки для отладки
    try:
        time.sleep(pause_duration)
        result = subprocess.run(['lpstat', '-l', '-W', 'all', '-o'], stdout=subprocess.PIPE)
        lpstat_output = result.stdout.decode()

        if job_id in lpstat_output:
            start = lpstat_output.find(job_id)
            end = lpstat_output.find("Alerts", start)
            job_info = lpstat_output[start:end].strip()

            status_start = job_info.find("Status:")
            status_end = job_info.find("\n", status_start)
            status = job_info[status_start:status_end].strip() if status_start != -1 else "Status not found"

            return status
        return "Job status not found"
    except Exception as e:
        return f"Error checking print status: {e}"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global prints_left, total_prints, total_printed
        content_length = int(self.headers['Content-Length'])

        image_data = self.rfile.read(content_length)
        if image_data:
            filename = f"image_{int(datetime.now().timestamp())}.png"
            image_path = f"/home/pi/img/{filename}"

            with open(image_path, 'wb') as image_file:
                image_file.write(image_data)

            try:
                if not is_printer_enabled(printer_name):
                    enable_printer(printer_name)
                    time.sleep(3) # активируем и ожидаем пока оно очухается

                command = ["lp", "-d", printer_name, image_path]
                result = subprocess.run(command, check=True, stdout=subprocess.PIPE)
                lp_output = result.stdout.decode().strip()
                job_id_parts = lp_output.split(' ')
                job_id = job_id_parts[3] if len(job_id_parts) > 3 else ""
                os.remove(image_path)

                job_status = get_print_status(job_id)

                if "printing" in job_status.lower():
                    prints_left -= 1
                    total_printed += 1
                    with open(log_file_path, "a") as log_file:
                        log_file.write(f"{total_printed},{prints_left},{total_prints}\n")
                    response_message = f"Image received and printing initiated. Prints left: {prints_left}/{total_prints}\n\nStatus: {job_status}"
                else:
                    response_message = f"Image received, but printing status is uncertain. \n\n{job_status}" #из-за тормозов принтера будем постоянно ловить потом поправлю
                
                self.send_response(200)
                self.end_headers()
                self.wfile.write(response_message.encode())
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
