import re
import json
import html
import time
import streamlit as st
import streamlit.components.v1 as components
import groq
from groq import Groq

# ---------- Setup ----------
client = Groq()  # reads GROQ_API_KEY from environment
MODELS = ['openai/gpt-oss-120b', 'openai/gpt-oss-20b']

st.set_page_config(page_title="Language Coach", page_icon="🗣️", layout="centered", initial_sidebar_state="expanded")

FLAGS = {
    "English": "🇬🇧", "Spanish": "🇪🇸", "French": "🇫🇷", "German": "🇩🇪",
    "Italian": "🇮🇹", "Portuguese": "🇵🇹", "Dutch": "🇳🇱", "Swedish": "🇸🇪",
    "Norwegian": "🇳🇴", "Danish": "🇩🇰", "Finnish": "🇫🇮", "Polish": "🇵🇱",
    "Czech": "🇨🇿", "Hungarian": "🇭🇺", "Romanian": "🇷🇴", "Greek": "🇬🇷",
    "Ukrainian": "🇺🇦", "Russian": "🇷🇺", "Turkish": "🇹🇷", "Hebrew": "🇮🇱",
    "Arabic": "🇸🇦", "Persian": "🇮🇷", "Hindi": "🇮🇳", "Bengali": "🇧🇩",
    "Urdu": "🇵🇰", "Punjabi": "🇮🇳", "Gujarati": "🇮🇳", "Marathi": "🇮🇳",
    "Tamil": "🇮🇳", "Telugu": "🇮🇳", "Kannada": "🇮🇳", "Malayalam": "🇮🇳",
    "Nepali": "🇳🇵", "Sinhala": "🇱🇰", "Chinese (Mandarin)": "🇨🇳",
    "Japanese": "🇯🇵", "Korean": "🇰🇷", "Thai": "🇹🇭", "Vietnamese": "🇻🇳",
    "Indonesian": "🇮🇩", "Malay": "🇲🇾", "Filipino (Tagalog)": "🇵🇭",
    "Swahili": "🇰🇪", "Afrikaans": "🇿🇦",
}
OTHER = "🌐 Other (type any language)"

LANG_CODES = {
    "English": "en-US", "Spanish": "es-ES", "French": "fr-FR", "German": "de-DE",
    "Italian": "it-IT", "Portuguese": "pt-PT", "Dutch": "nl-NL", "Swedish": "sv-SE",
    "Norwegian": "nb-NO", "Danish": "da-DK", "Finnish": "fi-FI", "Polish": "pl-PL",
    "Czech": "cs-CZ", "Hungarian": "hu-HU", "Romanian": "ro-RO", "Greek": "el-GR",
    "Ukrainian": "uk-UA", "Russian": "ru-RU", "Turkish": "tr-TR", "Hebrew": "he-IL",
    "Arabic": "ar-SA", "Persian": "fa-IR", "Hindi": "hi-IN", "Bengali": "bn-IN",
    "Urdu": "ur-PK", "Punjabi": "pa-IN", "Gujarati": "gu-IN", "Marathi": "mr-IN",
    "Tamil": "ta-IN", "Telugu": "te-IN", "Kannada": "kn-IN", "Malayalam": "ml-IN",
    "Nepali": "ne-NP", "Sinhala": "si-LK", "Chinese (Mandarin)": "zh-CN",
    "Japanese": "ja-JP", "Korean": "ko-KR", "Thai": "th-TH", "Vietnamese": "vi-VN",
    "Indonesian": "id-ID", "Malay": "ms-MY", "Filipino (Tagalog)": "fil-PH",
    "Swahili": "sw-KE", "Afrikaans": "af-ZA",
}

# ---------- Styling ----------
st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
.block-container {padding-top: 1.4rem; max-width: 800px;}

.hero {
    background: linear-gradient(135deg, #0F766E 0%, #115E59 45%, #1E3A5F 100%);
    padding: 28px 30px; border-radius: 22px; color: white;
    box-shadow: 0 10px 28px rgba(15, 118, 110, 0.28);
    border-bottom: 5px solid #F59E0B; margin-bottom: 14px;
}
.hero h1 {margin: 0; font-size: 2.1rem; color: white; letter-spacing: -0.5px;}
.hero p {margin: 8px 0 0 0; opacity: 0.92; font-size: 1.02rem;}

.pills {display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px;}
.pill {
    background: white; color: #0F766E; border: 1.5px solid #B7E0DA;
    padding: 6px 15px; border-radius: 999px; font-size: 0.85rem; font-weight: 700;
}
.pill.accent {background: #FEF3C7; color: #92400E; border-color: #FCD34D;}

[data-testid="stChatMessage"] {
    background: white; border-radius: 18px; padding: 14px 18px;
    box-shadow: 0 2px 12px rgba(31, 41, 55, 0.07);
    border-left: 5px solid #0F766E; margin-bottom: 12px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #FFFBEB; border-left: 5px solid #F59E0B;
}

.box {border-radius: 14px; padding: 12px 16px; margin-top: 10px; font-size: 0.95rem;}
.box-title {font-weight: 800; margin-bottom: 6px; font-size: 0.9rem; letter-spacing: 0.3px;}
.box.fix {background: #FEF3C7; border: 1.5px solid #FCD34D; color: #78350F;}
.box.words {background: #E6F4F1; border: 1.5px solid #B7E0DA; color: #134E4A;}
.chip {
    display: inline-block; background: white; border: 1px solid #B7E0DA;
    border-radius: 999px; padding: 4px 12px; margin: 3px 4px 3px 0; font-size: 0.88rem;
}
.chip b {color: #0F766E;}
.chip i {color: #6B7280; font-style: normal;}

[data-testid="stSidebar"] {background: linear-gradient(180deg, #E6F4F1 0%, #FAF7F2 100%);}
[data-testid="stSidebar"] .stButton button {
    width: 100%; border-radius: 12px; border: none; font-weight: 700;
    background: #0F766E; color: white; padding: 0.55rem 0;
}
[data-testid="stSidebar"] .stButton button:hover {background: #115E59; color: white;}
[data-testid="stMetric"] {
    background: white; border-radius: 14px; padding: 10px 14px;
    border: 1.5px solid #B7E0DA;
}
[data-testid="stChatInput"] {border-radius: 16px;}
</style>
""", unsafe_allow_html=True)


# ---------- Sidebar ----------
st.sidebar.markdown("## ⚙️ Your settings")
choice = st.sidebar.selectbox(
    "Language to practice (type to search)",
    list(FLAGS.keys()) + [OTHER],
    format_func=lambda l: l if l == OTHER else f"{FLAGS[l]}  {l}",
)
if choice == OTHER:
    language = st.sidebar.text_input(
        "Type the language", placeholder="e.g. Sanskrit, Welsh, Amharic"
    ).strip()
else:
    language = choice

level = st.sidebar.selectbox("Your level", ["Beginner", "Intermediate", "Advanced"])
scenario = st.sidebar.selectbox(
    "Scenario",
    ["Casual small talk", "Ordering at a café", "Travel and directions",
     "Job interview", "Shopping at a market", "At the airport",
     "Visiting a doctor", "Making new friends"],
)
explain_lang = st.sidebar.selectbox("Explanations in", ["English", "Hindi"])

if not language:
    st.markdown("""
    <div class="hero"><h1>🗣️ Language Coach</h1>
    <p>Type a language in the sidebar to begin.</p></div>
    """, unsafe_allow_html=True)
    st.stop()

flag = FLAGS.get(language, "🌐")

# ---------- State (auto-reset when settings change) ----------
for key, default in [("messages", []), ("summary", None), ("hint", None), ("think", True), ("quiz", None), ("quiz_checked", False), ("quiz_id", 0), ("last_audio", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

signature = (language, level, scenario, explain_lang)
if st.session_state.get("signature") != signature:
    st.session_state.signature = signature
    st.session_state.messages = []
    st.session_state.summary = None
    st.session_state.quiz = None
    st.session_state.quiz_checked = False
    st.session_state.hint = None


def reset_chat():
    st.session_state.messages = []
    st.session_state.summary = None
    st.session_state.quiz = None
    st.session_state.quiz_checked = False
    st.session_state.hint = None


# ---------- AI ----------
def build_system_prompt():
    return f"""You are a friendly, patient {language} conversation coach.
Learner level: {level}. Scenario: {scenario}. Explanations language: {explain_lang}.

Rules:
1. Play the character that fits the scenario and reply in {language},
   using vocabulary and grammar suited to a {level} learner.
2. Keep replies short (2-3 sentences) and end with a question so the
   conversation continues.
3. If the learner's last message has mistakes, add after your reply:
   Correction: <corrected sentence>
   Why: <one-line explanation in {explain_lang}>
   If there are no mistakes, praise them briefly instead.
4. If the learner writes in a language other than {language}, gently encourage
   them to try in {language} and give a helpful phrase.
5. For new or difficult words in your reply, add at the end:
   New words:
   word = meaning in {explain_lang}
   (one per line, maximum 4 words)
6. Always be encouraging, never harsh.
7. Keep the labels "Correction:", "Why:" and "New words:" in English."""


class _Null:
    def markdown(self, *a, **k):
        pass


def stream_ai(system_prompt, messages, placeholder, max_tokens=700):
    """Streams the reply into `placeholder` and returns the full text."""
    chat = [{"role": "system", "content": system_prompt}]
    for m in messages[-10:]:
        chat.append({"role": m["role"], "content": m["content"]})
    if chat[1]["role"] != "user":
        chat.insert(1, {"role": "user", "content": "Let's continue."})
    last_error = None
    for model in MODELS:
        for attempt in range(2):
            text = ""
            try:
                stream = client.chat.completions.create(
                    model=model, messages=chat, max_tokens=max_tokens,
                    temperature=0.7, stream=True,
                )
                for chunk in stream:
                    piece = chunk.choices[0].delta.content if chunk.choices else None
                    if piece:
                        text += piece
                        placeholder.markdown(text + " ▌")
                if text:
                    return text
            except groq.RateLimitError as e:
                last_error = e
                break  # try the next model
            except (groq.APIConnectionError, groq.InternalServerError) as e:
                last_error = e
                if text:
                    return text
                time.sleep(1)
            except groq.APIStatusError as e:
                last_error = e
                if e.status_code in (400, 404):
                    break  # bad or missing model: try the next one
                raise
    st.error("The AI service is busy right now. Please wait a minute and try again.")
    st.caption(str(last_error))
    st.stop()


def ask_ai(system_prompt, messages, max_tokens=900):
    return stream_ai(system_prompt, messages, _Null(), max_tokens)


# ---------- Reply rendering ----------
MARKER = re.compile(r"\*{0,2}(Correction|New words)(?:\*{0,2}\s*:|\s*:\*{0,2})", re.I)


def split_sections(text):
    matches = list(MARKER.finditer(text))
    if not matches:
        return text.strip(), {}
    main = text[:matches[0].start()].strip()
    sections = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[m.group(1).lower()] = text[m.end():end].strip()
    return main, sections


def fmt(t):
    t = html.escape(t.strip())
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t.replace("\n", "<br>")


def word_chips(block):
    chips = []
    for line in block.splitlines():
        line = line.strip().lstrip("*-• ").replace("**", "").strip()
        if not line:
            continue
        parts = re.split(r"\s*(?:=|–|—| - |:)\s*", line, maxsplit=1)
        word = html.escape(parts[0])
        meaning = html.escape(parts[1]) if len(parts) > 1 else ""
        chips.append(f'<span class="chip"><b>{word}</b> <i>{meaning}</i></span>')
    return "".join(chips)


def _render_reply_core(text):
    main, sec = split_sections(text)
    if main:
        st.markdown(main.replace("\n", "  \n"))
    if sec.get("correction"):
        st.markdown(
            f'<div class="box fix"><div class="box-title">✏️ CORRECTION</div>'
            f'{fmt(sec["correction"])}</div>',
            unsafe_allow_html=True,
        )
    if sec.get("new words"):
        chips = word_chips(sec["new words"])
        if chips:
            st.markdown(
                f'<div class="box words"><div class="box-title">📚 NEW WORDS</div>'
                f'{chips}</div>',
                unsafe_allow_html=True,
            )


def speak_button(text):
    clean = re.sub(r"[*_`#]", "", text).strip()
    if not clean:
        return
    payload = json.dumps({"t": clean, "l": LANG_CODES.get(language, "")}).replace("</", "<\\/")
    components.html(f"""
    <button id="b" style="background:#0F766E;color:white;border:none;border-radius:999px;
      padding:6px 16px;font-weight:700;cursor:pointer;font-family:sans-serif;font-size:13px;">
      🔊 Listen</button>
    <script>
    const d = {payload};
    document.getElementById('b').onclick = () => {{
      const u = new SpeechSynthesisUtterance(d.t);
      if (d.l) {{
        u.lang = d.l;
        const pre = d.l.split('-')[0].toLowerCase();
        const v = speechSynthesis.getVoices().find(
          x => x.lang.toLowerCase().replace('_', '-').startsWith(pre));
        if (v) u.voice = v;
      }}
      u.rate = 0.85;
      speechSynthesis.cancel();
      speechSynthesis.speak(u);
    }};
    </script>""", height=42)


def render_reply(text):
    main, _ = split_sections(text)
    _render_reply_core(text)
    speak_button(main)


def parse_quiz(raw):
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except Exception:
        return None
    out = []
    for q in data.get("questions", []):
        try:
            opts = [str(o) for o in q["options"]][:4]
            ans = int(q["answer"])
            if len(opts) >= 2 and 0 <= ans < len(opts):
                out.append({"q": str(q["q"]), "options": opts, "answer": ans,
                            "why": str(q.get("why", ""))})
        except Exception:
            continue
    return out or None


def transcribe(audio_bytes):
    code = LANG_CODES.get(language, "").split("-")[0]
    code = {"fil": "tl", "nb": "no"}.get(code, code)
    err = None
    for model in ["whisper-large-v3-turbo", "whisper-large-v3"]:
        for lang in ([code, ""] if code else [""]):
            try:
                kwargs = dict(file=("speech.wav", audio_bytes), model=model,
                              response_format="text")
                if lang:
                    kwargs["language"] = lang
                r = client.audio.transcriptions.create(**kwargs)
                text = r if isinstance(r, str) else getattr(r, "text", "")
                return text.strip()
            except Exception as e:
                err = e
    st.session_state.mic_err = str(err)[:200]
    return ""


# ---------- Header (shows instantly) ----------
st.markdown(f"""
<div class="hero">
  <h1>🗣️ Language Coach</h1>
  <p>Practice real conversations with your personal AI tutor</p>
</div>
<div class="pills">
  <span class="pill">{flag} {html.escape(language)}</span>
  <span class="pill">📶 {level}</span>
  <span class="pill accent">🎭 {scenario}</span>
</div>
""", unsafe_allow_html=True)

# ---------- Coach opens the conversation (streamed) ----------
if not st.session_state.messages:
    box = st.empty()
    with box.container():
        with st.chat_message("assistant", avatar="🎓"):
            ph = st.empty()
            opener = stream_ai(
                build_system_prompt(),
                [{"role": "user",
                  "content": "Please start the conversation with a short greeting "
                             "in character and ask me a first question."}],
                ph,
            )
    box.empty()
    st.session_state.messages.append({"role": "assistant", "content": opener})

# ---------- Chat history ----------
for m in st.session_state.messages:
    avatar = "🎓" if m["role"] == "assistant" else "🧑‍💻"
    with st.chat_message(m["role"], avatar=avatar):
        if m["role"] == "assistant":
            render_reply(m["content"])
        else:
            st.markdown(m["content"])

if st.session_state.hint:
    st.info("💡 **Hint:** " + st.session_state.hint)

quiz = st.session_state.quiz
if quiz:
    qid = st.session_state.quiz_id
    st.markdown("### 🧩 Quick quiz")
    for i, q in enumerate(quiz):
        st.markdown(f"**{i + 1}. {q['q']}**")
        st.radio("Choose one:", q["options"], index=None, key=f"quiz_{qid}_{i}",
                 label_visibility="collapsed", disabled=st.session_state.quiz_checked)
        if st.session_state.quiz_checked:
            picked = st.session_state.get(f"quiz_{qid}_{i}")
            right = q["options"][q["answer"]]
            if picked == right:
                st.success(f"✅ Correct! {q['why']}")
            else:
                st.error(f"❌ Correct answer: {right}. {q['why']}")
    if not st.session_state.quiz_checked:
        if st.button("✅ Check my answers"):
            st.session_state.quiz_checked = True
            st.rerun()
    else:
        score = sum(1 for i, q in enumerate(quiz)
                    if st.session_state.get(f"quiz_{qid}_{i}") == q["options"][q["answer"]])
        st.markdown(f"### 🏆 Your score: {score} / {len(quiz)}")
        if st.button("Close quiz"):
            st.session_state.quiz = None
            st.session_state.quiz_checked = False
            st.rerun()

# ---------- User input ----------
chat_value = st.chat_input(
    f"Type or record in {language}...", accept_audio=True
)
user_input = None
if chat_value:
    user_input = (chat_value.text or "").strip()
    if not user_input and chat_value.audio is not None:
        with st.spinner("🎧 Listening..."):
            user_input = transcribe(chat_value.audio.getvalue())
        if not user_input:
            st.warning("I couldn't hear that clearly. Please record again.")
            if st.session_state.get("mic_err"):
                st.caption(st.session_state.mic_err)
if user_input:
    st.session_state.hint = None
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🎓"):
        ph = st.empty()
        reply = stream_ai(build_system_prompt(), st.session_state.messages, ph)
        ph.empty()
        render_reply(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})


# ---------- Sidebar: tools ----------
def transcript_text():
    return "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages)


sent = sum(1 for m in st.session_state.messages if m["role"] == "user")
st.sidebar.divider()
st.sidebar.metric("💬 Messages you sent", sent)

if st.sidebar.button("💡 Give me a hint"):
    with st.spinner("Thinking of a hint..."):
        st.session_state.hint = ask_ai(
            "You are a helpful language coach.",
            [{"role": "user", "content":
              f"Here is a {language} practice conversation ({level} level):\n\n"
              f"{transcript_text()}\n\nSuggest ONE simple reply the learner could "
              f"send next, written in {language}, followed by its meaning in "
              f"{explain_lang}. Keep it to 2 lines."}],
            max_tokens=300,
        )
    st.rerun()

if st.sidebar.button("📝 Session summary"):
    if sent < 2:
        st.sidebar.warning("Chat a little first!")
    else:
        with st.spinner("Preparing summary..."):
            st.session_state.summary = ask_ai(
                "You are a helpful language coach.",
                [{"role": "user", "content":
                  f"Here is a {language} practice conversation:\n\n"
                  f"{transcript_text()}\n\nWrite a short summary for the learner "
                  f"with: (1) their most common mistakes, (2) 5 useful new words "
                  f"with meanings, (3) one tip for next time. Write in "
                  f"{explain_lang}, be encouraging."}],
            )

if st.sidebar.button("🧩 Quiz me"):
    with st.spinner("Writing your quiz..."):
        convo = transcript_text() if sent >= 1 else "(no conversation yet)"
        prompt = (
            f"Create 5 multiple-choice questions to test a {level} learner of {language}. "
            f"Base them on words and grammar from this conversation if there is one, "
            f"otherwise on the scenario '{scenario}'.\n\nConversation:\n{convo}\n\n"
            "Write the questions and options in " + language + " where sensible. "
            'Return ONLY JSON in exactly this shape: {"questions": [{"q": "question text", '
            '"options": ["A", "B", "C", "D"], "answer": 0, "why": "one-line explanation in '
            + explain_lang + '"}]} where answer is the 0-based index of the correct option.'
        )
        raw = ask_ai("You write language quizzes. Reply with valid JSON only.",
                     [{"role": "user", "content": prompt}], max_tokens=1400)
    parsed = parse_quiz(raw)
    if parsed:
        st.session_state.quiz = parsed
        st.session_state.quiz_checked = False
        st.session_state.quiz_id += 1
        st.rerun()
    else:
        st.sidebar.error("Couldn't make a quiz this time. Try again.")

if st.sidebar.button("🔄 New conversation"):
    reset_chat()
    st.rerun()

if st.session_state.summary:
    with st.expander("📝 Your session summary", expanded=True):
        st.markdown(st.session_state.summary)
