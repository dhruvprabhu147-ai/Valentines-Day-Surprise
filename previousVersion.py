import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import time
import json
import random

st.set_page_config(page_title="For My Valentine", page_icon="❤️")

# --- GHOSTING FIX: DETECT ROLE CHANGE & FORCE RELOAD ---
# This ensures that if you switch from 'Aditi' to 'Me', the previous screen is wiped instantly.
if 'last_role' not in st.session_state:
    st.session_state.last_role = "Aditi"

# --- 1. Background & Helper Functions ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    if not os.path.exists(png_file):
        return
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/jpg;base64,%s");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .block-container {
        background-color: rgba(0, 0, 0, 0.6);
        border-radius: 15px;
        padding: 60px 30px 30px 30px; 
        backdrop-filter: blur(5px);
    }
    h1, h2, h3, h4, h5, h6, p, li, .stMarkdown {
        color: white !important;
        text-align: center;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background('background.jpg')

# --- DB FUNCTIONS (THE SHARED BRAIN) ---
DB_FILE = "love_box.json"

def load_db():
    # This reads the shared file that connects both users
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list): return data
            return []
    except:
        return []

def send_to_db(sender, text):
    # This writes to the shared file
    messages = load_db()
    messages.append({
        "sender": sender,
        "message": text,
        "id": int(time.time() * 1000), # Unique ID
        "top": random.randint(10, 80), # Random Position Y
        "left": random.randint(10, 80) # Random Position X
    })
    with open(DB_FILE, "w") as f:
        json.dump(messages, f)

def clear_my_messages(user_id):
    # Clears messages from the shared file
    messages = load_db()
    new_messages = [m for m in messages if m['sender'] == user_id]
    with open(DB_FILE, "w") as f:
        json.dump(new_messages, f)

def read_file_as_b64(path):
    if not os.path.exists(path): return None
    try:
        with open(path, 'rb') as f: return base64.b64encode(f.read()).decode()
    except: return None

# --- COMPONENT FUNCTIONS ---

def scratch_card(img_b64, caption_text, glitter_b64, key):
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; background: transparent; font-family: sans-serif; overflow: hidden; user-select: none; }}
        .card-container {{ position: relative; width: 300px; height: 300px; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.3); background: #000; }}
        .hidden-image {{ width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0; z-index: 1; }}
        .hidden-caption {{ position: absolute; bottom: 10px; left: 0; width: 100%; text-align: center; color: white; font-size: 14px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.9); z-index: 2; pointer-events: none; }}
        .grid-container {{ position: absolute; top: 0; left: 0; width: 300px; height: 300px; z-index: 3; }}
        .scratch-tile {{ position: absolute; width: 45px; height: 45px; background-image: url("data:image/gif;base64,{glitter_b64}"); background-size: 300px 300px; transition: transform 0.1s, opacity 0.1s; mask-image: url("data:image/svg+xml;utf8,<svg viewBox='0 0 32 29.6' xmlns='http://www.w3.org/2000/svg'><path d='M23.6,0c-3.4,0-6.3,2.7-7.6,5.6C14.7,2.7,11.8,0,8.4,0C3.8,0,0,3.8,0,8.4c0,9.4,9.5,11.9,16,21.2 c6.1-9.3,16-11.3,16-21.2C32,3.8,28.2,0,23.6,0z'/></svg>"); -webkit-mask-image: url("data:image/svg+xml;utf8,<svg viewBox='0 0 32 29.6' xmlns='http://www.w3.org/2000/svg'><path d='M23.6,0c-3.4,0-6.3,2.7-7.6,5.6C14.7,2.7,11.8,0,8.4,0C3.8,0,0,3.8,0,8.4c0,9.4,9.5,11.9,16,21.2 c6.1-9.3,16-11.3,16-21.2C32,3.8,28.2,0,23.6,0z'/></svg>"); mask-size: contain; -webkit-mask-size: contain; mask-repeat: no-repeat; -webkit-mask-repeat: no-repeat; mask-position: center; -webkit-mask-position: center; }}
    </style>
    </head>
    <body>
    <div class="card-container">
        <img src="data:image/jpeg;base64,{img_b64}" class="hidden-image">
        <div class="hidden-caption">{caption_text}</div>
        <div class="grid-container" id="grid-{key}"></div>
    </div>
    <script>
        const grid = document.getElementById('grid-{key}');
        const containerSize = 300;
        const heartSize = 45;
        const densityStep = 20; 
        const brushRadius = 30; 
        let tiles = [];
        for (let y = -15; y < 300; y += 20) {{
            for (let x = -15; x < 300; x += 20) {{
                const tile = document.createElement('div');
                tile.className = 'scratch-tile';
                tile.style.width = '45px'; tile.style.height = '45px';
                tile.style.left = x + 'px'; tile.style.top = y + 'px';
                tile.style.backgroundPosition = `-${{x}}px -${{y}}px`;
                tile.style.transform = `rotate(${{Math.random() * 30 - 15}}deg)`;
                tile.centerX = x + 22.5; tile.centerY = y + 22.5;
                tile.isRevealed = false;
                grid.appendChild(tile);
                tiles.push(tile);
            }}
        }}
        function erase(mx, my) {{
            for (let i = 0; i < tiles.length; i++) {{
                const tile = tiles[i];
                if (tile.isRevealed) continue;
                const dx = mx - tile.centerX; const dy = my - tile.centerY;
                if ((dx * dx + dy * dy) < (brushRadius * brushRadius)) {{
                    tile.style.transform = `scale(0.8)`; tile.style.opacity = '0';
                    tile.isRevealed = true;
                    setTimeout(() => tile.style.visibility = 'hidden', 150);
                }}
            }}
        }}
        let isThrottled = false;
        function onMove(x, y) {{
            if (isThrottled) return;
            isThrottled = true;
            const rect = grid.getBoundingClientRect();
            erase(x - rect.left, y - rect.top);
            setTimeout(() => {{ isThrottled = false; }}, 20); 
        }}
        grid.addEventListener('mousemove', (e) => {{ onMove(e.clientX, e.clientY); }});
        grid.addEventListener('touchmove', (e) => {{ e.preventDefault(); const touch = e.touches[0]; onMove(touch.clientX, touch.clientY); }}, {{passive: false}});
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=320)

def memory_slideshow():
    memories = [
        ("Pencils in my Hair", "Remember when you used to poke pens and pencils into my hair? You managed to put 11 one day!"),
        ("In the Physics Lab", "Remember when a wire had gone through your finger? You told me to pull it out and I was surprised at how brave you were. I was happy I managed to pull it out without hurting you."),
        ("The Armwrestling", "Remember when you used to challenge me to armwrestling matches in class? You are really strong!"),
        ("Bhangra Night", "Remember when we danced together in a circle at the bhangra night? It was the day I had thought of confessing to you but I wanted to get to know your beautiful soul more before I did."),
        ("When you used to call me 'Gadheda'", "Remember when you used to call me 'Gadheda' near the back exit of HFS and I actually turned around XD."),
        ("The day I Confessed", "Remember the gift I gave you? I had over-designed it because I really wanted to tell how that you were the most special girl in the world to me. I was scared it could ruin our friendship but I am so glad that you wanted to still be friends."),
        ("The Late Night Study Sessions", "Remember all the night we solved doubts and gave mocks together? It was really fun and your maturity inspired me to do better."),
        ("Our First Date", "Remember when we went on our first date? When our heads touched I really felt close to you. It was a dream come true since I love you with all my heart."),
        ("When I played the Flute", "Remember when I played the flute for you at the park? I was rusty but I was so happy to see you smile as I played 'A Thousand Years' for you. I will practice more and play for you again soon!"),
        ("Our Late Night Calls", "All the calls that we have had until now, and all the ones we will have in the future, are so special to me. I love hearing your sweet voice and seeing your adorable face. It makes my day always."),
    ]
    cards_html = ""
    for i, (front, back) in enumerate(memories):
        initial_class = "active" if i == 0 else ""
        cards_html += f"""<div class="card-wrapper {initial_class}" id="card-{i}"><div class="card"><div class="card-front"><div class="content"><h3>#{i+1}</h3><h2>{front}</h2><p style="font-size: 12px; margin-top: 15px; opacity: 0.7;">(Click to reveal)</p></div></div><div class="card-back"><div class="content"><p>{back}</p><p style="font-size: 12px; margin-top: 15px; opacity: 0.7;">(Click for next)</p></div></div></div></div>"""
    
    html_code = f"""<!DOCTYPE html><html><head><link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:ital@0;1&display=swap" rel="stylesheet"><style>body {{ margin: 0; padding: 0; background: transparent; display: flex; justify-content: center; align-items: center; height: 400px; overflow: hidden; font-family: 'Playfair Display', serif; user-select: none; -webkit-tap-highlight-color: transparent; }}.slideshow-container {{ position: relative; width: 300px; height: 250px; perspective: 1000px; cursor: pointer; }}.card-wrapper {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; transform: scale(0.8); transition: opacity 0.6s ease, transform 0.6s ease; pointer-events: none; }}.card-wrapper.active {{ opacity: 1; transform: scale(1); pointer-events: auto; }}.card {{ width: 100%; height: 100%; position: relative; transform-style: preserve-3d; transition: transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1); box-shadow: 0 10px 30px rgba(0,0,0,0.3); border-radius: 15px; }}.card-wrapper.flipped .card {{ transform: rotateY(180deg); }}.card-front, .card-back {{ position: absolute; width: 100%; height: 100%; -webkit-backface-visibility: hidden; backface-visibility: hidden; border-radius: 15px; display: flex; align-items: center; justify-content: center; text-align: center; padding: 20px; box-sizing: border-box; border: 2px solid #d4af37; }}.card-front {{ background: linear-gradient(135deg, #fff0f0, #ffd1d1); color: #4a4a4a; }}.card-back {{ background: linear-gradient(135deg, #d4af37, #f7e7ce); color: #2c2c2c; transform: rotateY(180deg); }}h2 {{ font-family: 'Great Vibes', cursive; font-size: 32px; margin: 0; color: #d44; }}h3 {{ font-size: 14px; color: #888; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; }}p {{ font-size: 18px; line-height: 1.4; margin: 0; }}</style></head><body><div class="slideshow-container" onclick="handleClick()">{cards_html}</div><script>const totalCards = {len(memories)}; let current = 0; let isFlipped = false; document.getElementById('card-0').classList.add('active'); function handleClick() {{ const cardWrapper = document.getElementById('card-' + current); if (!isFlipped) {{ cardWrapper.classList.add('flipped'); isFlipped = true; }} else {{ cardWrapper.classList.remove('active'); setTimeout(() => {{ cardWrapper.classList.remove('flipped'); }}, 600); current++; if (current >= totalCards) current = 0; const nextCard = document.getElementById('card-' + current); nextCard.classList.add('active'); isFlipped = false; }} }}</script></body></html>"""
    components.html(html_code, height=420)

def love_hacker():
    secret_message = """Creating connection...
    
    TO: The Love of My Life
    SUBJECT: In the Depths of My Heart
    
    Aditi,
    
    In the noise of life,
    Your voice is like candy.

    Your smile melts my soul,
    You make me whole.

    With you, everything feels right,
    With you every endevour feels light.

    I wonder what I did,
    to deserve an angel straight from heaven.

    You entered my life at the perfect time,
    and I am so grateful that I can say you are mine.

    Thank you for giving this boy a chance,
    To show you how much he loves you,
    And it does not matter that we are far apart,
    wherever you are, I will always love you from
                 
                The Depths of My Heart.

    System.exit(I love you Aditi <3);
    """
    
    safe_message = secret_message.replace("\n", "\\n").replace("'", "\\'")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; padding: 0; background: transparent; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; }}
        
        .terminal-window {{
            width: 100%; max-width: 600px; height: 300px; background-color: #1e1e1e; border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid #333; display: flex; flex-direction: column; overflow: hidden;
            position: relative; 
        }}
        
        .terminal-header {{ background-color: #2d2d2d; padding: 10px; display: flex; align-items: center; border-bottom: 1px solid #333; }}
        .dot {{ height: 12px; width: 12px; background-color: #bbb; border-radius: 50%; margin-right: 8px; }}
        .red {{ background-color: #ff5f56; }} .yellow {{ background-color: #ffbd2e; }} .green {{ background-color: #27c93f; }}
        
        .terminal-body {{
            padding: 20px; flex-grow: 1; overflow-y: auto; color: #ff69b4; font-size: 16px; line-height: 1.5;
            text-shadow: 0 0 5px rgba(255, 105, 180, 0.5); cursor: text; white-space: pre-wrap;
        }}
        
        .cursor {{ display: inline-block; width: 10px; height: 18px; background-color: #ff69b4; animation: blink 1s step-end infinite; vertical-align: text-bottom; }}
        @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
        
        #hack-input {{ 
            position: absolute; top: 0; left: 0; width: 1px; height: 1px; opacity: 0; padding: 0; border: none; z-index: -1; 
        }}
        
        .hint {{ position: absolute; bottom: 10px; right: 20px; color: rgba(255,255,255,0.2); font-size: 12px; pointer-events: none; }}
    </style>
    </head>
    <body>
        <div class="terminal-window" onclick="focusInput()">
            <div class="terminal-header">
                <div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div>
                <span style="margin-left: 10px; color: #aaa; font-size: 12px;">love_kernel.exe</span>
            </div>
            <div class="terminal-body" id="screen">
                <span id="typed-text"></span><span class="cursor"></span>
            </div>
            <input type="text" id="hack-input" autocomplete="off">
            <div class="hint">Tap & Start Typing...</div>
        </div>
        <script>
            const fullText = `{safe_message}`;
            let currentIndex = 0;
            let commandMode = false;
            let promptText = "\\n\\nroot@love:~# ";
            
            const display = document.getElementById('typed-text');
            const input = document.getElementById('hack-input');
            const screen = document.getElementById('screen');
            
            function focusInput() {{ input.focus(); }}
            
            function handleType() {{
                if (!commandMode) {{
                    // HACKER MODE
                    if (currentIndex < fullText.length) {{
                        display.textContent += fullText.charAt(currentIndex);
                        currentIndex++;
                        input.value = ""; 
                        screen.scrollTop = screen.scrollHeight;
                    }}
                    // Transition to Command Mode
                    if (currentIndex >= fullText.length) {{
                        commandMode = true;
                        display.textContent += promptText;
                        input.value = "";
                        screen.scrollTop = screen.scrollHeight;
                    }}
                }} else {{
                    // COMMAND MODE: Mirror typing
                    let currentText = display.textContent;
                    // Find the last prompt occurrence
                    let lastPromptIndex = currentText.lastIndexOf("root@love:~# ");
                    // Keep everything before the prompt + prompt itself
                    let baseText = currentText.substring(0, lastPromptIndex + 13); 
                    display.textContent = baseText + input.value;
                    screen.scrollTop = screen.scrollHeight;
                }}
            }}
            
            document.addEventListener('keydown', (e) => {{
                if (!commandMode) {{
                    // In hacker mode, keys trigger text generation
                    if (e.key.length === 1 || e.key === 'Enter') {{ handleType(); }}
                }} else {{
                    // In command mode, handle Enter to check code
                    if (e.key === 'Enter') {{
                        let command = input.value.trim();
                        if (command === "run yourEternalLover()") {{
                            // RESET
                            currentIndex = 0;
                            commandMode = false;
                            display.textContent = "";
                            input.value = "";
                        }} else {{
                            // Invalid command
                            display.textContent += "\\nCommand not found. Try: run yourEternalLover()";
                            display.textContent += promptText;
                            input.value = "";
                            screen.scrollTop = screen.scrollHeight;
                        }}
                    }}
                }}
            }});
            
            input.addEventListener('input', (e) => {{
                handleType(); 
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=350)

def heart_jukebox():
    def get_audio_b64(path):
        try:
            with open(path, "rb") as f: return f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"
        except: return ""
    songs_data = {
        "s1": {
            "title": "A Thousand Years",
            "audio": get_audio_b64("AThousandYears.mp3"),
            "lyrics": [
                {"time": 0, "text": "🎵 Enjoy, my love"},
                {"time": 21, "text": "Heart beats fast 💗"},
                {"time": 25, "text": "Colors and promises"},
                {"time": 29.5, "text": "How to be brave? 🥺"},
                {"time": 32.7, "text": "How can I love when I'm afraid to fall"},
                {"time": 40, "text": "But watching you stand alone"},
                {"time": 45.5, "text": "All of my doubt suddenly goes away somehow 🥹"},
                {"time": 54.5, "text": "One step closer"},
                {"time": 62, "text": "I have died every day waiting for you"},
                {"time": 67, "text": "Darling, don't be afraid 😇"},
                {"time": 70, "text": "I have loved you for a thousand years 💞"},
                {"time": 76, "text": "I'll love you for a thousand more 🥰"},
                {"time": 87.5, "text": "Time stands still ⏱️"},
                {"time": 91.5, "text": "Beauty in all she is 😍"},
                {"time": 97, "text": "I will be brave 😤"},
                {"time": 99, "text": "I will not let anything take away ❌"},
                {"time": 106, "text": "What's standing in front of me 🥹"},
                {"time": 112, "text": "Every breath, every hour has come to this 😮‍💨"},
                {"time": 121, "text": "One step closer"},
                {"time": 128.5, "text": "I have died every day waiting for you"},
                {"time": 134.5, "text": "Darling, don't be afraid 😇"},
                {"time": 137, "text": "I have loved you for a thousand years 💞"},
                {"time": 142.5, "text": "I'll love you for a thousand more 🥰"},
                {"time": 150, "text": "And all along I believed I would find you"},
                {"time": 155, "text": "Time has brought your heart to me 🥹"},
                {"time": 158, "text": "I have loved you for a thousand years 💞"},
                {"time": 163, "text": "I'll love you for a thousand more 🥰"},
                {"time": 193, "text": "One step closer..."},
                {"time": 204, "text": "One step closer..."},
                {"time": 212, "text": "I have died every day waiting for you"},
                {"time": 220, "text": "Darling, don't be afraid 😇"},
                {"time": 222, "text": "I have loved you for a thousand years 💞"},
                {"time": 227.5, "text": "I'll love you for a thousand more 🥰"},
                {"time": 235, "text": "And all along I believed I would find you"},
                {"time": 240, "text": "Time has brought your heart to me 🥹"},
                {"time": 243, "text": "I have loved you for a thousand years 💞"},
                {"time": 248.5, "text": "I'll love you for a thousand more 🥰"}
            ]
        },
        "s2": {
            "title": "Khoobsurat",
            "audio": get_audio_b64("Khoobsurat.mp3"),
            "lyrics": [
                {"time": 0, "text": "🎵 Enjoy, my love"},
                {"time": 14, "text": "Jo dekhe ek baar ko 👀"},
                {"time": 17, "text": "Palat ke baar baar woh 🙂‍↕️"},
                {"time": 21, "text": "Khuda jaane kyun tujhe 😉"},
                {"time": 24, "text": "Dekhne lagta hai"},
                {"time": 27, "text": "Sach boloon imaan se 😌"},
                {"time": 30, "text": "Khabar hai aasmaan se 💭"},
                {"time": 34, "text": "Hairat mein chaand bhi 🌔"},
                {"time": 38, "text": "Tujh ko takta hai... 🥰"},
                {"time": 41, "text": "Ki koi itna khoobsurat... 😳"},
                {"time": 44, "text": "Koi itna khoobsurat... 😍"},
                {"time": 48, "text": "Koi itna khoobsurat 😩"},
                {"time": 51, "text": "Kaise ho sakta hai? 🥰"},
                {"time": 55, "text": "Ke koi itna khoobsurat... 😳"},
                {"time": 58, "text": "Koi itna khoobsurat... 😍"},
                {"time": 61, "text": "Koi itna khoobsurat 😩"},
                {"time": 64, "text": "Kaise ho sakta hai? 🥰"},
                {"time": 68, "text": "Khoobsurti par teri ✨"},
                {"time": 72, "text": "Khud ko maine qurbaan kiya 😇"},
                {"time": 75, "text": "Muskura ke dekha tu ne 😁"},
                {"time": 78, "text": "Deewane par ehsaan kiya 🧎🏻‍♂️"},
                {"time": 82, "text": "Khoobsurti par teri ✨"},
                {"time": 85, "text": "Khud ko maine qurbaan kiya 😇"},
                {"time": 88, "text": "Muskura ke dekha tu ne 😁"},
                {"time": 92, "text": "Deewane par ehsaan kiya 🧎🏻‍♂️"},
                {"time": 95, "text": "🎵 (Music Interlude)"},
                {"time": 108, "text": "Ke koi itna khoobsurat... 😳"},
                {"time": 111, "text": "Koi itna khoobsurat... 😍"},
                {"time": 114, "text": "Koi itna khoobsurat 😩"},
                {"time": 118, "text": "Kaise ho sakta hai? 🥰"},
                {"time": 122, "text": "Dhoop bhi tere roop ke ☀️"},
                {"time": 125, "text": "Sone pe qurbaan hui hai 💛"},
                {"time": 129, "text": "Teri rangat pe khud"},
                {"time": 131, "text": "Holi ki rut hairaan hui hai 🌈"},
                {"time": 136, "text": "Tujhko chalte dekha "},
                {"time": 141, "text": "Tujhko chalte dekha 😍"},
                {"time": 144, "text": "Tab hirno ne seekha chalna 🙂‍↕️"},
                {"time": 149, "text": "Tujhe hi sun ke koyal ko 🕊️"},
                {"time": 152, "text": "Sur ki pehchaan hui hai 🎶"},
                {"time": 158, "text": "Tujh se dil lagaye jo 💗"},
                {"time": 161, "text": "Urdu na bhi aaye to 😮‍💨"},
                {"time": 164, "text": "Shaks woh shaayari 🙂‍↕️"},
                {"time": 168, "text": "Karne lagta hai..."},
                {"time": 171, "text": "Ke koi itna khoobsurat... 😳"},
                {"time": 174, "text": "Koi itna khoobsurat... 😍"},
                {"time": 177, "text": "Koi itna khoobsurat 😩"},
                {"time": 181, "text": "Kaise ho sakta hai? 🥰"},
                {"time": 184, "text": "Koi itna khoobsurat... 😳"},
                {"time": 187, "text": "Koi itna khoobsurat... 😍"},
                {"time": 190, "text": "Koi itna khoobsurat 😩"},
                {"time": 194, "text": "Kaise ho sakta hai? 🥰"},
                {"time": 198, "text": "Khoobsurti par teri ✨"},
                {"time": 202, "text": "Khud ko maine qurbaan kiya 😇"},
                {"time": 205, "text": "Muskura ke dekha tu ne 😁"},
                {"time": 208, "text": "Deewane par ehsaan kiya 🧎🏻‍♂️"},
                {"time": 212, "text": "Khoobsurti par teri ✨"},
                {"time": 215, "text": "Khud ko maine qurbaan kiya 😇"},
                {"time": 218, "text": "Muskura ke dekha tu ne 😁"},
                {"time": 222, "text": "Deewane par ehsaan kiya 🧎🏻‍♂️"},
                {"time": 225, "text": "Koi itna... 😮‍💨"},
                {"time": 227, "text": "Koi itna... 😮‍💨"},
                {"time": 229, "text": "Koi itna... 😮"},
                {"time": 231, "text": "Koi itna... 😍"},
                {"time": 233, "text": "Koi itna khoobsurat 🥰"},
                {"time": 235, "text": "Kaise ho sakta hai? 😩"}
            ]
        },
        "s3": {
            "title": "Dandelions",
            "audio": get_audio_b64("Dandelions.mp3"),
            "lyrics": [

                {"time": 0, "text": "🎵 Enjoy, my love"},
                {"time": 12, "text": "Maybe it's the way you say my name 🤔"},
                {"time": 18, "text": "Maybe it's the way you play your game 😏"},
                {"time": 23, "text": "But it's so good... 😍"},
                {"time": 25, "text": "I've never known anybody like you 💞"},
                {"time": 29, "text": "But it's so good... 😍"},
                {"time": 31, "text": "I've never dreamed of nobody like you ✨"},
                {"time": 35.5, "text": "And I've heard of a love that comes 💛"},
                {"time": 39, "text": "Once in a lifetime 🥹"},
                {"time": 42.5, "text": "And I'm pretty sure that you are that love of mine ✅"},
                {"time": 47.5, "text": "'Cause I'm in a field of dandelions 🌼"},
                {"time": 52, "text": "Wishing on every one that you'd be mine 🥰"},
                {"time": 58, "text": "Mine..."},
                {"time": 60, "text": "And I see forever in your eyes 👀✨"},
                {"time": 64, "text": "I feel okay when I see you smile 😃"},
                {"time": 70, "text": "Smile..."},
                {"time": 73, "text": "Wishing on dandelions all of the time 🌼"},
                {"time": 76, "text": "Praying to God that one day you'll be mine 🙏"},
                {"time": 78, "text": "Wishing on dandelions all of the time 🌼"},
                {"time": 82, "text": "All of the time... ⏳"},
                {"time": 86, "text": "I think that you are the one for me 💞"},
                {"time": 91, "text": "'Cause it gets so hard to breathe 😩"},
                {"time": 97, "text": "When you're looking at me 🥹"},
                {"time": 99, "text": "I've never felt so alive and free 😇"},
                {"time": 102.5, "text": "When you're looking at me 😍"},
                {"time": 105, "text": "I've never felt so happy... 😄"},
                {"time": 109, "text": "And I've heard of a love that comes 💛"},
                {"time": 112.5, "text": "Once in a lifetime 🥹"},
                {"time": 117, "text": "And I'm pretty sure that you are that love of mine ✅"},
                {"time": 122, "text": "'Cause I'm in a field of dandelions 🌼"},
                {"time": 126, "text": "Wishing on every one that you'd be mine 🥰"},
                {"time": 132.5, "text": "Mine..."},
                {"time": 134, "text": "And I see forever in your eyes 👀✨"},
                {"time": 138, "text": "I feel okay when I see you smile 😃"},
                {"time": 144, "text": "Smile..."},
                {"time": 147, "text": "Wishing on dandelions all of the time 🌼"},
                {"time": 149, "text": "Praying to God that one day you'll be mine 🙏"},
                {"time": 153, "text": "Wishing on dandelions all of the time 🌼"},
                {"time": 156, "text": "All of the time... ⏳"},
                {"time": 160, "text": "Dandelion into the wind you go 🌬️"},
                {"time": 164, "text": "Won't you let my darling know? 🥺"},
                {"time": 166, "text": "Dandelion into the wind you go 🌬️"},
                {"time": 169, "text": "Won't you let my darling know that... 🥺"},
                {"time": 173, "text": "I'm in a field of dandelions 🌼"},
                {"time": 177, "text": "Wishing on every one that you'd be mine 🥰"},
                {"time": 183, "text": "Mine..."},
                {"time": 184, "text": "And I see forever in your eyes 👀✨"},
                {"time": 189, "text": "I feel okay when I see you smile 😃"},
                {"time": 195, "text": "Smile..."},
                {"time": 197, "text": "Wishing on dandelions all of the time 🌼"},
                {"time": 200, "text": "Praying to God that one day you'll be mine 🙏"},
                {"time": 203, "text": "Wishing on dandelions all of the time 🌼"},
                {"time": 207, "text": "All of the time... ⏳"},
                {"time": 211, "text": "I'm in a field of dandelions 🌼"},
                {"time": 213, "text": "Wishing on every one that you'd be mine 🥰"},
                {"time": 219, "text": "Mine... 💞"},

                
            ]
                
        }
    }
    json_data = json.dumps(songs_data)
    html_code = f"""<!DOCTYPE html><html><head><style>body {{ margin:0; padding:0; background:transparent; font-family: 'Arial', sans-serif; display: flex; flex-direction: column; align-items: center; }}#heart-menu {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 40px; margin-top: 20px; transition: opacity 0.5s ease; width: 100%; }} #lyrics-display {{ display: none; background-color: rgba(255, 240, 245, 0.95); border: 2px solid #ffcccc; border-radius: 15px; padding: 30px; width: 90%; max-width: 500px; height: 300px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-family: 'Courier New', Courier, monospace; margin-top: 10px; overflow-y: auto; scroll-behavior: smooth; position: relative; }} #lyrics-display::-webkit-scrollbar {{ display: none; }} #lyrics-display {{ -ms-overflow-style: none; scrollbar-width: none; }} .lyric-line {{ font-size: 16px; color: #888; margin: 15px 0; transition: all 0.3s ease; opacity: 0.5; min-height: 20px; }} .lyric-line.active {{ font-size: 22px; color: #d6334d; font-weight: bold; opacity: 1; transform: scale(1.05); }} .stop-btn-container {{ margin-top: 15px; text-align: center; width: 100%; }} .stop-btn {{ background-color: #ff4d4d; color: white; border: none; padding: 10px 25px; border-radius: 25px; font-size: 16px; cursor: pointer; transition: background 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }} .stop-btn:hover {{ background-color: #cc0000; }} .heart {{ background-color: #ffcccc; width: 80px; height: 80px; position: relative; transform: rotate(-45deg); cursor: pointer; margin: 20px; display: flex; align-items: center; justify-content: center; box-shadow: 0 5px 15px rgba(0,0,0,0.2); transition: transform 0.2s; }} .heart:hover {{ transform: rotate(-45deg) scale(1.1); }} .heart::before, .heart::after {{ content: ""; width: 80px; height: 80px; background-color: #ffcccc; border-radius: 50%; position: absolute; }} .heart::before {{ top: -40px; left: 0; }} .heart::after {{ top: 0; left: 40px; }} .song-name {{ transform: rotate(45deg); z-index: 2; color: #d6334d; font-weight: bold; font-size: 12px; text-align: center; pointer-events: none; width: 80px; }}</style></head><body><div id="heart-menu"><div class="heart" onclick="playMusic('s1')"><span class="song-name">{songs_data['s1']['title']}</span></div><div class="heart" onclick="playMusic('s2')"><span class="song-name">{songs_data['s2']['title']}</span></div><div class="heart" onclick="playMusic('s3')"><span class="song-name">{songs_data['s3']['title']}</span></div></div><div id="lyrics-display"><div id="lyrics-content"></div><br><br><br> </div><div class="stop-btn-container" id="controls" style="display:none;"><button class="stop-btn" onclick="stopMusic()">Stop & Go Back ⏹️</button></div><audio id="audio-player"></audio><script>var songDB = {json_data}; var player = document.getElementById("audio-player"); var menu = document.getElementById("heart-menu"); var display = document.getElementById("lyrics-display"); var content = document.getElementById("lyrics-content"); var controls = document.getElementById("controls"); var currentLyrics = []; function playMusic(id) {{ var song = songDB[id]; if(song.audio === "") {{ alert("Audio not found!"); return; }} player.src = song.audio; player.play(); currentLyrics = song.lyrics; content.innerHTML = ""; song.lyrics.forEach((line, index) => {{ var div = document.createElement("div"); div.className = "lyric-line"; div.id = "line-" + index; div.innerText = line.text; div.dataset.time = line.time; content.appendChild(div); }}); menu.style.display = "none"; display.style.display = "block"; controls.style.display = "block"; }} player.addEventListener("timeupdate", function() {{ var currentTime = player.currentTime; var activeIndex = -1; for(var i = 0; i < currentLyrics.length; i++) {{ if(currentTime >= currentLyrics[i].time) {{ activeIndex = i; }} else {{ break; }} }} var allLines = document.getElementsByClassName("lyric-line"); for(var i = 0; i < allLines.length; i++) {{ allLines[i].classList.remove("active"); }} if(activeIndex !== -1) {{ var activeLine = document.getElementById("line-" + activeIndex); activeLine.classList.add("active"); var containerHeight = display.clientHeight; var lineTop = activeLine.offsetTop; var lineHeight = activeLine.clientHeight; var scrollPos = lineTop - (containerHeight / 2) + (lineHeight / 2); display.scrollTo({{ top: scrollPos, behavior: 'smooth' }}); }} }}); player.addEventListener("ended", function() {{ stopMusic(); }}); function stopMusic() {{ player.pause(); player.currentTime = 0; display.style.display = "none"; controls.style.display = "none"; menu.style.display = "flex"; }}</script></body></html>"""
    components.html(html_code, height=600)

def love_box_feature(user_id, key_suffix):
    st.markdown("---")
    st.header("🎁 The Love Box")
    col1, col2 = st.columns([2, 1])
    all_messages = load_db()
    my_incoming_messages = [m for m in all_messages if m['sender'] != user_id]
    
    hearts_html = ""
    for msg in my_incoming_messages:
        if 'id' not in msg or 'top' not in msg or 'left' not in msg: continue
        hearts_html += f"""<div class="heart-msg" id="msg-{msg['id']}" style="top: {msg['top']}%; left: {msg['left']}%;" onclick="burstMessage('msg-{msg['id']}', '{msg['message']}')">🎁</div>"""

    with col1:
        st.write(f"### {user_id}'s Box")
        box_html = f"""<!DOCTYPE html><html><head><style>.box-container {{ width: 100%; height: 350px; background: linear-gradient(135deg, #2c3e50, #000); border: 2px dashed #ff4b4b; border-radius: 15px; position: relative; overflow: hidden; }} .heart-msg {{ position: absolute; font-size: 30px; cursor: pointer; animation: float 3s infinite ease-in-out; transition: transform 0.2s; z-index: 10; }} .heart-msg:hover {{ transform: scale(1.3); }} @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }} .burst-text {{ position: absolute; color: #ff4b4b; font-weight: bold; font-family: 'Courier New', monospace; font-size: 20px; text-align: center; width: 80%; padding: 15px; background: rgba(0,0,0,0.85); border-radius: 10px; z-index: 100; pointer-events: none; transform: translate(-50%, -50%) scale(0.5); opacity: 0; transition: all 1.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); box-shadow: 0 0 15px rgba(255, 75, 75, 0.5); }} .burst-text.centered {{ top: 50% !important; left: 50% !important; transform: translate(-50%, -50%) scale(1); opacity: 1; }} .burst-text.fading {{ opacity: 0; transform: translate(-50%, -50%) scale(1.1); }} .empty-text {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #555; font-size: 14px; pointer-events: none; }}</style></head><body><div class="box-container" id="box">{hearts_html if hearts_html else '<div class="empty-text">Box is empty... waiting for love.</div>'}</div><script>(function() {{ var hearts = document.querySelectorAll('.heart-msg'); hearts.forEach(function(h) {{ if (localStorage.getItem(h.id) === 'read') {{ h.style.display = 'none'; }} }}); }})(); function burstMessage(id, text) {{ var el = document.getElementById(id); var box = document.getElementById("box"); localStorage.setItem(id, 'read'); var span = document.createElement("div"); span.className = "burst-text"; span.innerText = text; span.style.top = el.style.top; span.style.left = el.style.left; box.appendChild(span); el.style.display = "none"; void span.offsetWidth; setTimeout(() => {{ span.classList.add("centered"); }}, 10); setTimeout(() => {{ span.classList.add("fading"); }}, 3000); setTimeout(() => {{ span.remove(); }}, 4500); }}</script></body></html>"""
        components.html(box_html, height=370)
        if st.button("Clear My Box 🗑️", key=f"clear_{key_suffix}"):
            clear_my_messages(user_id)
            st.rerun()

    with col2:
        st.write("### Send Love")
        with st.form(f"send_form_{key_suffix}"):
            txt = st.text_area("Message:", height=100)
            if st.form_submit_button("Send"):
                send_to_db(user_id, txt)
                st.success("Sent!")
                time.sleep(0.5)
                st.rerun()
    return st.checkbox("Live Connection", value=True, key=f"live_{key_suffix}")

def date_time_quiz():
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:ital@1&display=swap" rel="stylesheet">
    <style>
        body { margin: 0; padding: 0; background: transparent; display: flex; justify-content: center; align-items: center; height: 450px; font-family: 'Playfair Display', serif; overflow: hidden; }
        .quiz-container { position: relative; z-index: 10; border: 3px solid #d4af37; border-radius: 15px; padding: 30px; background: rgba(0, 0, 0, 0.85); box-shadow: 0 0 20px rgba(212, 175, 55, 0.3); text-align: center; color: white; width: 300px; }
        .shake { animation: shake 0.5s; }
        @keyframes shake { 0% { transform: translate(1px, 1px) rotate(0deg); } 10% { transform: translate(-1px, -2px) rotate(-1deg); } 20% { transform: translate(-3px, 0px) rotate(1deg); } 30% { transform: translate(3px, 2px) rotate(0deg); } 40% { transform: translate(1px, -1px) rotate(1deg); } 50% { transform: translate(-1px, 2px) rotate(-1deg); } 60% { transform: translate(-3px, 1px) rotate(0deg); } 100% { transform: translate(0, 0); } }
        h2 { font-family: 'Great Vibes', cursive; font-size: 32px; color: #ffcccb; margin: 0 0 20px 0; }
        label { display: block; margin-top: 10px; font-size: 14px; color: #d4af37; }
        input { width: 80%; padding: 8px; margin-top: 5px; border-radius: 5px; border: 1px solid #555; background: #222; color: white; font-family: sans-serif; font-size: 16px; text-align: center; color-scheme: dark; }
        button { margin-top: 25px; padding: 10px 30px; font-size: 18px; border: none; border-radius: 25px; background: linear-gradient(45deg, #d4af37, #f7e7ce); color: #333; cursor: pointer; font-weight: bold; transition: transform 0.2s; }
        button:hover { transform: scale(1.05); }
        .success-msg { display: none; font-size: 28px; color: #d4af37; margin-top: 0px; transform: translateY(-5px); animation: fadeIn 1s; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .heart { position: absolute; font-size: 20px; pointer-events: none; z-index: 100; }
    </style>
    </head>
    <body>
    <div class="quiz-container" id="quizBox">
        <div id="quiz-content">
            <h2>When did our story officially begin?</h2>
            <label>The Date</label><input type="date" id="dateInput">
            <label>The Time</label><input type="time" id="timeInput">
            <button onclick="checkAnswer()">Check Memory</button>
        </div>
        <div id="success-content" class="success-msg">Correct! <br><span style="font-size: 20px; color: white;">It was perfect.</span></div>
    </div>
    <script>
        function checkAnswer() {
            const dateVal = document.getElementById('dateInput').value;
            const timeVal = document.getElementById('timeInput').value;
            const quizBox = document.getElementById('quizBox');
            if (dateVal === '2025-06-27' && timeVal === '16:54') {
                document.getElementById('quiz-content').style.display = 'none';
                document.getElementById('success-content').style.display = 'block';
                explodeHearts();
            } else {
                quizBox.classList.remove('shake');
                void quizBox.offsetWidth; quizBox.classList.add('shake');
            }
        }
        function explodeHearts() {
            const container = document.body;
            for (let i = 0; i < 60; i++) {
                const heart = document.createElement('div');
                heart.classList.add('heart'); heart.innerHTML = '❤️';
                heart.style.left = '50%'; heart.style.top = '50%';
                heart.style.fontSize = (Math.random() * 20 + 10) + 'px';
                container.appendChild(heart);
                const angle = Math.random() * Math.PI * 2;
                const velocity = 200 + Math.random() * 200;
                const duration = 1000 + Math.random() * 1000;
                heart.animate([{ transform: 'translate(-50%, -50%) scale(0.5)', opacity: 1 }, { transform: `translate(calc(-50% + ${Math.cos(angle) * velocity}px), calc(-50% + ${Math.sin(angle) * velocity}px)) scale(1.5)`, opacity: 0 }], { duration: duration, easing: 'cubic-bezier(0, .9, .57, 1)', fill: 'forwards' });
            }
        }
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=450)


def runaway_buttons():
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px; background: transparent; color: white; text-align: center; overflow: hidden; }
        .btn-container { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
        button { padding: 15px 40px; font-size: 20px; border: none; border-radius: 50px; cursor: pointer; font-weight: bold; outline: none; position: absolute; z-index: 10; }
        #yesBtn { background-color: #28a745; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.2); transition: transform 0.2s; left: 50%; top: 50%; transform: translate(-160%, -50%); }
        #yesBtn:hover { transform: translate(-160%, -50%) scale(1.1); box-shadow: 0 0 15px rgba(40, 167, 69, 0.6); }
        #noBtn { background-color: #dc3545; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.2); left: 50%; top: 50%; transform: translate(60%, -50%); transition: left 0.4s cubic-bezier(0.25, 0.8, 0.25, 1), top 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); }
        #success-msg { display: none; font-size: 40px; color: #ff4b4b; z-index: 20; animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        @keyframes popIn { 0% { opacity: 0; transform: scale(0.5); } 100% { opacity: 1; transform: scale(1); } }
    </style>
    </head>
    <body>
    <div class="btn-container" id="btnArea">
        <button id="yesBtn" onclick="celebrate()">YES</button>
        <button id="noBtn">NO</button>
        <div id="success-msg">💖 YAY! I LOVE YOU! 💖 <br><span style="font-size:20px; color:white;">(I knew you'd say yes! Hehehehe XD)</span></div>
    </div>
    <script>
        const noBtn = document.getElementById('noBtn'); const yesBtn = document.getElementById('yesBtn'); const successMsg = document.getElementById('success-msg');
        const detectionRadius = 120; const moveDistance = 150;
        document.addEventListener('mousemove', function(e) {
            const rect = noBtn.getBoundingClientRect();
            const btnX = rect.left + rect.width / 2; const btnY = rect.top + rect.height / 2;
            const deltaX = e.clientX - btnX; const deltaY = e.clientY - btnY;
            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
            if (distance < detectionRadius) {
                const angle = Math.atan2(deltaY, deltaX);
                const jitter = (Math.random() - 0.5) * 1.0; 
                const moveX = Math.cos(angle + jitter) * moveDistance;
                const moveY = Math.sin(angle + jitter) * moveDistance;
                const currentLeft = noBtn.offsetLeft; const currentTop = noBtn.offsetTop;
                let newLeft = currentLeft - moveX; let newTop = currentTop - moveY;
                const margin = 50; const maxWidth = window.innerWidth; const maxHeight = 400;
                if (newLeft < margin || newLeft > maxWidth - margin || newTop < margin || newTop > maxHeight - margin) {
                    newLeft = maxWidth / 2 + (Math.random() * 200 - 100); newTop = maxHeight / 2 + (Math.random() * 200 - 100);
                }
                noBtn.style.left = `${newLeft}px`; noBtn.style.top = `${newTop}px`;
                noBtn.style.transform = "translate(-50%, -50%)"; 
            }
        });
        function celebrate() { yesBtn.style.display = 'none'; noBtn.style.display = 'none'; successMsg.style.display = 'block'; createConfetti(); }
        function createConfetti() {
            const colors = ['#ff4b4b', '#ffeb3b', '#28a745', '#007bff'];
            for (let i = 0; i < 50; i++) {
                const conf = document.createElement('div');
                conf.style.position = 'absolute'; conf.style.width = '10px'; conf.style.height = '10px'; conf.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                conf.style.left = '50%'; conf.style.top = '50%'; conf.style.transition = 'all 1s ease-out';
                document.body.appendChild(conf);
                setTimeout(() => {
                    const x = (Math.random() * 400) - 200; const y = (Math.random() * 400) - 200;
                    conf.style.transform = `translate(${x}px, ${y}px) rotate(${Math.random()*360}deg)`; conf.style.opacity = 0;
                }, 10);
            }
        }
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=450)

def photo_showcase(img_path, caption):
    if not os.path.exists(img_path):
        st.error(f"Could not find image: {img_path}")
        return
    with open(img_path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode()
    html_code = f"""<!DOCTYPE html><html><head><link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:ital@1&display=swap" rel="stylesheet"><style>body {{ margin: 0; padding: 0; background: transparent; display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'Playfair Display', serif; }}.photo-container {{ position: relative; width: 100%; max-width: 300px; max-height: 550px; display: flex; justify-content: center; align-items: center; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 4px solid rgba(255, 255, 255, 0.2); background: rgba(0,0,0,0.2); }}img {{ width: auto; height: auto; max-width: 100%; max-height: 550px; display: block; }}.caption {{ font-family: 'Great Vibes', cursive; font-size: 42px; color: #ffcccb; text-align: center; margin-top: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); display: block; }}</style></head><body><div class="photo-container"><img src="data:image/jpeg;base64,{img_b64}"></div><div class="caption">{caption}</div></body></html>"""
    components.html(html_code, height=500)

def read_file_as_b64(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

# ==========================
#     MAIN EXECUTION
# ==========================

st.sidebar.title("Login")
user_role = st.sidebar.radio("Select User", ["Aditi", "Me"])

# --- GHOSTING FIX LOGIC ---
# If the user toggles the radio button, we detect it here and force a rerun.
# This clears all previous elements before the 'if' blocks below run.
if st.session_state.last_role != user_role:
    st.session_state.last_role = user_role
    st.rerun()

should_refresh = False

if user_role == "Aditi":
    # --- RENDER FULL APP FOR HER ---
    st.title("❤️ Happy Valentine's Day! ❤️")
    st.write("I wanted to make something special for you.")

    st.divider()

    st.header("💌 5 Reasons Why I Love You")
    reasons = [
        "I love your strength and resilience.",
        "You are so mature and understanding.",
        "You look beautiful and your smile melts my heart.",
        "You and I have so much in common that it feels you were made for me.",
        "I see my future in your eyes."
    ]
    for r in reasons:
        st.write(f"💖 {r}")

    st.divider()

    st.title("❤️ Our Memories")
    st.write("Drag your cursor over the cards to see some of our memories!")

    # Load resources for scratch card
    glitter_data = read_file_as_b64("glitter.gif")
    photos_with_captions = [
        ("hehe.jpg", "The first time we held hands 💞"), 
        ("mylove.jpg", "Our first date! 🌹"), 
        ("angel.jpg", "In the garden (you look like an angel) 😍"),
    ]
    cols = st.columns(len(photos_with_captions))
    for i, (filename, caption) in enumerate(photos_with_captions):
        with cols[i]:
            img_data = read_file_as_b64(filename)
            if img_data and glitter_data:
                scratch_card(img_data, caption, glitter_data, key=i)
            elif img_data and not glitter_data:
                st.error("Missing 'glitter.gif' file!")
            elif not img_data:
                st.error(f"Missing image: {filename}")

    st.divider()

    st.title("✨ Fun Moments We Shared")
    memory_slideshow()

    st.divider()

    st.subheader("⌨️ A Message for You")
    love_hacker()

    st.divider()

    photo_showcase("goddess.jpg", "I fall in love with you more everyday 😍")

    st.divider()

    st.title("🎶 Songs for You")
    heart_jukebox()

    # Love Box for Aditi
    should_refresh = love_box_feature("Aditi", key_suffix="aditi_view")

    st.divider()

    date_time_quiz()

    st.header("🎁 One Last Thing...")
    st.write("Will you be my Valentine?")
    runaway_buttons()

elif user_role == "Me":
    # --- RENDER LIMITED APP FOR ME ---
    password = st.sidebar.text_input("Enter Password", type="password")
    
    if password == "mcboi123":
        st.success("Access Granted: Welcome back, my love!")
        # Love Box for Me
        should_refresh = love_box_feature("Me", key_suffix="me_view")
    elif password:
        st.error("Incorrect Password")

# REFRESH LOGIC (AT THE END)
if should_refresh:
    time.sleep(2)
    st.rerun()