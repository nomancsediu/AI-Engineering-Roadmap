import os, re, json, base64, wave, time, shutil, subprocess, sys, tempfile
import urllib.request, urllib.error
from PIL import Image, ImageDraw, ImageFont

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
TTS_MODEL = "gemini-3.8-flash-tts"
VOICE = "Puck"
STYLE = "Clear, cheerful, friendly teaching voice."
PER_RUN = 1
START_TOPIC = int(os.environ.get("START_TOPIC", "1"))   # 1 = progress.json er prothom topic
REPO = os.environ.get("GITHUB_REPOSITORY", "")
PROGRESS_FILE = "progress.json"
W, H = 1280, 720
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

BG = (15, 23, 42)
ACCENT = (56, 189, 248)
TEXT = (226, 232, 240)
MUTED = (148, 163, 184)


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def wrap(draw, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def make_slide(path, topic, n, total, title, bullets):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 16, H], fill=ACCENT)
    d.text((80, 50), topic.upper(), font=font("DejaVuSans.ttf", 26), fill=MUTED)
    y = 110
    for line in wrap(d, title, font("DejaVuSans-Bold.ttf", 60), 1100):
        d.text((80, y), line, font=font("DejaVuSans-Bold.ttf", 60), fill=TEXT)
        y += 76
    y += 10
    d.rectangle([80, y, 280, y + 6], fill=ACCENT)
    y += 50
    bf = font("DejaVuSans.ttf", 38)
    for b in bullets[:4]:
        lines = wrap(d, b, bf, 1050)
        d.rectangle([80, y + 14, 96, y + 30], fill=ACCENT)
        for line in lines:
            d.text((120, y), line, font=bf, fill=TEXT)
            y += 52
        y += 22
    d.text((W - 220, H - 60), f"Scene {n} / {total}", font=font("DejaVuSans.ttf", 24), fill=MUTED)
    d.rectangle([0, H - 10, int(W * n / total), H], fill=ACCENT)
    img.save(path)


def parse_script(path):
    txt = open(path, encoding="utf-8").read().replace("\u2011", "-")
    scenes = []
    for block in re.split(r"^## Scene \d+: ", txt, flags=re.M)[1:]:
        title, _, rest = block.partition("\n")
        m = re.search(r"On-screen:\s*(.*?)\s*Narration:\s*(.*)", rest, re.S)
        if not m:
            continue
        bullets = [re.sub(r"^- ", "", l).strip() for l in m.group(1).splitlines() if l.strip()]
        narration = " ".join(m.group(2).split())
        scenes.append((title.strip(), bullets, narration))
    return scenes


def tts(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TTS_MODEL}:generateContent"
    payload = {
        # 3.8 reads text verbatim, so style goes in speech_metadata, not in the text
        "contents": [{"parts": [{
            "text": text,
            "speech_metadata": {"style": STYLE},
        }]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
        },
    }
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_KEY}
    for attempt in range(5):
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            part = r["candidates"][0]["content"]["parts"][0]
            return base64.b64decode(part["inlineData"]["data"])
        except urllib.error.HTTPError as e:
            print("TTS HTTP ERROR", e.code, e.read().decode()[:300])
            if e.code in (429, 500, 502, 503):
                time.sleep(20 * (attempt + 1))
                continue
            raise
        except (KeyError, IndexError) as e:
            print("TTS bad response, retrying...", e)
            time.sleep(5)
    raise RuntimeError("Gemini TTS failed")


def write_wav(path, audio):
    if audio[:4] == b"RIFF":          # 3.8 returns a ready WAV with header
        with open(path, "wb") as f:
            f.write(audio)
        return
    with wave.open(path, "wb") as w:  # fallback: raw PCM
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(audio)


def run(cmd):
    subprocess.run(cmd, check=True)


def build_video(p, out_mp4):
    script = os.path.join(p["path"], "video", "script.md")
    scenes = parse_script(script)
    if not scenes:
        raise RuntimeError("No scenes found in " + script)
    tmp = tempfile.mkdtemp()
    clips = []
    for n, (title, bullets, narration) in enumerate(scenes, 1):
        png = f"{tmp}/s{n}.png"
        wav = f"{tmp}/s{n}.wav"
        mp4 = f"{tmp}/s{n}.mp4"
        make_slide(png, p["topic"], n, len(scenes), title, bullets)
        write_wav(wav, tts(narration))
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "25",
             "-i", png, "-i", wav, "-c:v", "libx264", "-tune", "stillimage",
             "-pix_fmt", "yuv420p", "-r", "25", "-c:a", "aac",
             "-af", "apad=pad_dur=0.7",          # 0.7s silence after each scene
             "-ar", "44100", "-ac", "2", "-b:a", "128k", "-shortest", mp4])
        clips.append(mp4)
        print("Scene", n, "done")
        time.sleep(8)
    lst = f"{tmp}/list.txt"
    open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", out_mp4])
    shutil.rmtree(tmp, ignore_errors=True)


def upload(p, mp4):
    tag = f"video-{p['key']}"
    exists = subprocess.run(["gh", "release", "view", tag], capture_output=True).returncode == 0
    if exists:
        run(["gh", "release", "upload", tag, mp4, "--clobber"])
    else:
        run(["gh", "release", "create", tag, mp4,
             "--title", f"Video: {p['topic']}",
             "--notes", f"Narrated video for {p['topic']}"])
    return f"https://github.com/{REPO}/releases/tag/{tag}"


def update_readme(p, url):
    path = os.path.join(p["path"], "README.md")
    txt = open(path, encoding="utf-8").read()
    txt = txt.replace("**Watch:** coming soon.", f"**Watch:** [Open video]({url})")
    open(path, "w", encoding="utf-8").write(txt)


def main():
    if not GEMINI_KEY:
        print("GEMINI_API_KEY not set, skipping video.")
        return
    progress = json.load(open(PROGRESS_FILE, encoding="utf-8"))
    todo = [
        p for i, p in enumerate(progress, 1)
        if i >= START_TOPIC and not p.get("video_url")
    ][:PER_RUN]
    if not todo:
        print("No topics need a video.")
        return
    for p in todo:
        print("Video for:", p["topic"])
        out = os.path.join(tempfile.gettempdir(), f"{p['key']}.mp4")
        build_video(p, out)
        url = upload(p, out)
        update_readme(p, url)
        p["video_url"] = url
        json.dump(progress, open(PROGRESS_FILE, "w", encoding="utf-8"), indent=2)
        print("Video ready:", url)


main()
