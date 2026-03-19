from flask import Flask, request, send_file
import yt_dlp
import os
import uuid
import re

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ================= CLEAN TITLE =================
def clean_title(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)


# ================= COOKIE SYSTEM =================
def get_cookie_file():
    if os.path.exists("cookies.txt"):
        return "cookies.txt"
    return None


def get_ydl_opts(format_string, output_path):
    opts = {
        'format': format_string,
        'outtmpl': output_path,
        'restrictfilenames': True
    }

    cookie_file = get_cookie_file()

    if cookie_file:
        opts['cookiefile'] = cookie_file

    return opts


def download_with_fallback(url, ydl_opts):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return info, filename
    except:
        # Retry without cookies
        ydl_opts.pop('cookiefile', None)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return info, filename


# ================= PLATFORM DETECTION =================
def detect_platform(url):
    url = url.lower()

    if "youtube.com" in url or "youtu.be" in url:
        return "YouTube ✅ Supported"
    elif "instagram.com" in url:
        return "Instagram 🔐 Cookies Used"
    elif "facebook.com" in url:
        return "Facebook 🔐 Cookies Used"
    elif "twitter.com" in url or "x.com" in url:
        return "Twitter/X 🔐 Cookies Used"
    else:
        return "Unknown ❌"


# ================= WEBSITE =================
@app.route("/")
def home():
    return '''
<html>
<head>
<title>DownloadIt 🚀</title>

<style>
body{
margin:0;
font-family:Arial;
background: linear-gradient(135deg,#0f172a,#1e293b);
color:white;
}

.navbar{
background:#020617;
padding:15px 30px;
display:flex;
justify-content:space-between;
}

.logo{
font-size:22px;
font-weight:bold;
color:#38bdf8;
}

.header{
text-align:center;
padding:20px;
font-size:28px;
}

.section{
background:#1e293b;
width:400px;
margin:20px auto;
padding:30px;
border-radius:12px;
}

input, select{
width:100%;
padding:10px;
margin-top:10px;
border-radius:6px;
border:none;
}

button{
margin-top:10px;
padding:12px;
width:100%;
background:#38bdf8;
border:none;
border-radius:6px;
cursor:pointer;
}
</style>

<script>
function checkLink(){
let url = document.getElementById("url").value;

fetch("/check", {
method: "POST",
headers: {"Content-Type": "application/x-www-form-urlencoded"},
body: "url=" + encodeURIComponent(url)
})
.then(res => res.text())
.then(data => alert(data));
}
</script>

</head>

<body>

<div class="navbar">
<div class="logo">🚀 DownloadIt</div>
</div>

<div class="header">Download Videos Easily ⚡</div>

<div class="section">
<form action="/download_video" method="post">

<input id="url" name="url" placeholder="Paste video link">

<button type="button" onclick="checkLink()">Check Link</button>

<select name="quality">
<option value="best">Best</option>
<option value="720">720p</option>
<option value="1080">1080p</option>
<option value="4k">4K</option>
</select>

<button>Download Video</button>

</form>
</div>

<div class="section">
<form action="/download_mp3" method="post">
<input name="url" placeholder="Paste video link">
<button>Download MP3</button>
</form>
</div>

</body>
</html>
'''


# ================= CHECK =================
@app.route("/check", methods=["POST"])
def check():
    url = request.form["url"]
    return detect_platform(url)


# ================= VIDEO =================
@app.route("/download_video", methods=["POST"])
def video():
    url = request.form["url"]
    quality = request.form["quality"]

    if quality == "720":
        fmt = "bestvideo[height<=720]+bestaudio/best"
    elif quality == "1080":
        fmt = "bestvideo[height<=1080]+bestaudio/best"
    elif quality == "4k":
        fmt = "bestvideo[height<=2160]+bestaudio/best"
    else:
        fmt = "bestvideo+bestaudio/best"

    unique_id = str(uuid.uuid4())
    filepath = f"{DOWNLOAD_FOLDER}/{unique_id}_%(title)s.%(ext)s"

    ydl_opts = get_ydl_opts(fmt, filepath)

    info, filename = download_with_fallback(url, ydl_opts)

    title = clean_title(info.get("title", "video"))
    ext = filename.split(".")[-1]
    final_name = f"{title}.{ext}"

    response = send_file(filename, as_attachment=True, download_name=final_name)

    try:
        os.remove(filename)
    except:
        pass

    return response


# ================= MP3 =================
@app.route("/download_mp3", methods=["POST"])
def mp3():
    url = request.form["url"]

    unique_id = str(uuid.uuid4())
    filepath = f"{DOWNLOAD_FOLDER}/{unique_id}_%(title)s.%(ext)s"

    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': filepath,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }],
        'restrictfilenames': True
    }

    cookie_file = get_cookie_file()
    if cookie_file:
        ydl_opts['cookiefile'] = cookie_file

    info, filename = download_with_fallback(url, ydl_opts)
    filename = filename.rsplit(".",1)[0] + ".mp3"

    title = clean_title(info.get("title", "audio"))
    final_name = f"{title}.mp3"

    response = send_file(filename, as_attachment=True, download_name=final_name)

    try:
        os.remove(filename)
    except:
        pass

    return response


# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
