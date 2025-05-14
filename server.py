import os
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import unquote

# Load configuration
CONFIG_PATH = 'config.json'

def load_config():
    if not os.path.exists(CONFIG_PATH):
        default_config = {'port': 8000, 'upload_dir': 'uploads'}
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=4)
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

config = load_config()
PORT = config.get('port', 8000)
UPLOAD_DIR = os.path.abspath(config.get('upload_dir', 'uploads'))

os.makedirs(UPLOAD_DIR, exist_ok=True)

class FileServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"Handling GET request for path: {self.path}")  # 调试信息

        if self.path in ['/', '/index.html']:
            template_dir = os.path.abspath(os.path.dirname(__file__))
            index_path = os.path.join(template_dir, 'templates', 'index.html')
            print(f"Trying to load template from: {index_path}")  # 调试信息

            if not os.path.exists(index_path):
                self.send_error(404, f"Template file not found: {index_path}")
                return

            # 读取模板文件内容并返回
            with open(index_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
            return

        if self.path.startswith('/list'):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            files = os.listdir(UPLOAD_DIR)
            self.wfile.write(json.dumps(files).encode())
            return

        elif os.path.isfile(os.path.join(UPLOAD_DIR, self.path.strip("/"))):
            file_path = os.path.join(UPLOAD_DIR, self.path.strip("/"))
            with open(file_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
            return

        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b'File not found')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        filename = self.headers.get('Filename', 'uploaded_file')
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, 'wb') as f:
            f.write(self.rfile.read(content_length))

        self.send_response(200)
        self.end_headers()
        self.wfile.write(f'File {filename} uploaded successfully'.encode())

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, FileServer)
    print(f'Serving on port {PORT}, upload dir: {UPLOAD_DIR}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()