from flask import Flask, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# ================= PLATFORM DETECTION =================
def detect_platform(url):
    url = url.lower()

    if "youtube.com" in url or "youtu.be" in url:
        return "YouTube ✅ Supported"
    elif "instagram.com" in url:
        return "Instagram ⚠️ Limited Support"
    elif "facebook.com" in url:
        return "Facebook ✅ Supported"
    elif "twitter.com" in url or "x.com" in url:
        return "Twitter/X ✅ Supported"
    else:
        return "Unknown ❌ Not Supported"


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

/* NAVBAR */
.navbar{
background:#020617;
padding:15px 30px;
display:flex;
justify-content:space-between;
align-items:center;
}

.logo{
font-size:22px;
font-weight:bold;
color:#38bdf8;
}

.tagline{
font-size:14px;
opacity:0.7;
}

/* HEADER */
.header{
padding:20px;
text-align:center;
font-size:28px;
font-weight:bold;
}

/* NAV */
.nav{
display:flex;
justify-content:center;
gap:20px;
margin-bottom:20px;
}

.nav button{
padding:10px 20px;
border:none;
border-radius:6px;
cursor:pointer;
background:#334155;
color:white;
}

.nav button:hover{
background:#38bdf8;
}

/* BOX */
.section{
display:none;
background:#1e293b;
width:420px;
margin:20px auto;
padding:30px;
border-radius:12px;
}

.active{
display:block;
}

/* INPUT */
input{
width:100%;
padding:12px;
margin-top:10px;
border:none;
border-radius:6px;
}

/* BUTTON */
.download-btn{
margin-top:10px;
padding:12px;
width:100%;
background:#38bdf8;
border:none;
border-radius:6px;
cursor:pointer;
font-weight:bold;
}

.download-btn:hover{
background:#0ea5e9;
}

/* SELECT */
select{
width:100%;
padding:10px;
margin-top:10px;
border-radius:6px;
}

/* FOOTER */
.footer{
position:fixed;
bottom:0;
width:100%;
background:#020617;
padding:10px;
text-align:center;
font-size:14px;
opacity:0.8;
}
</style>

<script>
function showTab(id){
document.getElementById("video").classList.remove("active");
document.getElementById("mp3").classList.remove("active");
document.getElementById("playlist").classList.remove("active");
document.getElementById(id).classList.add("active");
}

function checkLink(){
let url = document.getElementById("url").value;

fetch("/check", {
method: "POST",
headers: {"Content-Type": "application/x-www-form-urlencoded"},
body: "url=" + encodeURIComponent(url)
})
.then(res => res.text())
.then(data => {
alert(data);
});
}
</script>

</head>

<body>

<div class="navbar">
<div class="logo">🚀 DownloadIt</div>
<div class="tagline">Fast • Free • Smart Downloader</div>
</div>

<div class="header">
Download Videos Easily ⚡
</div>

<div class="nav">
<button onclick="showTab('video')">Video</button>
<button onclick="showTab('mp3')">MP3</button>
<button onclick="showTab('playlist')">Playlist</button>
</div>

<!-- VIDEO -->
<div id="video" class="section active">
<h3>Download Video</h3>

<form action="/download_video" method="post">
<input id="url" name="url" placeholder="Paste video link">

<button type="button" onclick="checkLink()" class="download-btn">
Check Link
</button>

<select name="quality">
<option value="best">Best</option>
<option value="720">720p</option>
<option value="1080">1080p</option>
<option value="4k">4K</option>
</select>

<button class="download-btn">Download Video</button>
</form>
</div>

<!-- MP3 -->
<div id="mp3" class="section">
<h3>Convert to MP3</h3>

<form action="/download_mp3" method="post">
<input name="url" placeholder="Paste video link">
<button class="download-btn">Download MP3</button>
</form>
</div>

<!-- PLAYLIST -->
<div id="playlist" class="section">
<h3>Download Playlist</h3>

<form action="/download_playlist" method="post">
<input name="url" placeholder="Paste playlist link">
<button class="download-btn">Download Playlist</button>
</form>
</div>

<div class="footer">
Made by Sagar ⚡ | DownloadIt © 2026
</div>

</body>
</html>
'''


# ================= CHECK =================
@app.route("/check", methods=["POST"])
def check():
    url = request.form["url"]
    return detect_platform(url)


# ================= VIDEO DOWNLOAD (FIXED) =================
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

    filename = "video.mp4"

    ydl_opts = {
        'format': fmt,
        'outtmpl': filename
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return send_file(filename, as_attachment=True)


# ================= MP3 =================
@app.route("/download_mp3", methods=["POST"])
def mp3():
    url = request.form["url"]

    filename = "audio.mp3"

    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return send_file(filename, as_attachment=True)


# ================= PLAYLIST =================
@app.route("/download_playlist", methods=["POST"])
def playlist():
    url = request.form["url"]

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return "Playlist download started (check server)"


# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
