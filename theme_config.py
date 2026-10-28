import streamlit as st

DARK = "dark"
LIGHT = "light"

_BASE_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap');
:root {
    color-scheme: light;
    --shc-bg: #f7f6f2; --shc-surface: #fffefa; --shc-surface-muted: #f0f1ed;
    --shc-text: #1d3037; --shc-muted: #53646a; --shc-accent: #2e6874;
    --shc-accent-soft: #e4eeec; --shc-line: #d6ddda; --shc-caution: #9a5148;
    --shc-success: #3d6b57; --shc-focus: #245f6c; --shc-button-text:#fffefa;
    --shc-font-body: 'IBM Plex Sans', 'Segoe UI', sans-serif;
    --shc-font-display: 'Newsreader', Georgia, serif;
}
html, body { min-width:320px; color:var(--shc-text); font-family:var(--shc-font-body); }
.block-container { max-width:1320px; padding-top:1.6rem; padding-bottom:3rem; }
[data-testid="stAppViewContainer"], [data-testid="stMain"], .stApp,
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
    background:var(--shc-bg); color:var(--shc-text);
}
h1,h2,h3,h4 { color:var(--shc-text); font-family:var(--shc-font-display); font-weight:500; letter-spacing:-.025em; }
p,li,label,[data-testid="stMarkdownContainer"] { color:var(--shc-text); }
a { color:var(--shc-accent); text-underline-offset:.18em; }
a:hover { color:var(--shc-text); }
button,input,textarea,[role="combobox"] { font-family:var(--shc-font-body); }
:focus-visible { outline:3px solid var(--shc-focus)!important; outline-offset:3px!important; }
::selection { color:var(--shc-text); background:var(--shc-accent-soft); }
@media(max-width:700px) { .block-container { padding:1rem 1rem 2.25rem; } }
</style>
"""

_EDITORIAL_OVERRIDES = """
<style>
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stSidebar"],[data-testid="stSidebarContent"] {
    background-color:var(--shc-bg)!important; color:var(--shc-text)!important;
    font-family:var(--shc-font-body)!important;
}
html body .stApp [data-testid="stMain"] [data-testid="stMarkdownContainer"] :is(h1,h2,h3,h4,p,li,label,span,strong,b,em) {
    color:var(--shc-text)!important; -webkit-text-fill-color:var(--shc-text)!important;
}
html body .stApp [data-testid="stMain"] :is(h1,h2,h3,h4,p,li,label,span,strong,b,em,small,div,section,article) {
    color:var(--shc-text)!important; -webkit-text-fill-color:var(--shc-text)!important;
}
html body .stApp [data-testid="stSidebar"] :is(h1,h2,h3,h4,p,li,label,span,strong,b,em,small,div,section,article) {
    color:var(--shc-text)!important; -webkit-text-fill-color:var(--shc-text)!important;
}
html body .stApp [data-testid="stMain"] a,
html body .stApp [data-testid="stMain"] a * {
    color:var(--shc-accent)!important; -webkit-text-fill-color:var(--shc-accent)!important;
}
html body .stApp [data-testid="stMain"] .stButton button,
html body .stApp [data-testid="stMain"] .stButton button * {
    color:var(--shc-button-text)!important; -webkit-text-fill-color:var(--shc-button-text)!important;
}
[data-testid="stMain"] .block-container { max-width:1320px!important; padding-top:1.4rem!important; }
[data-testid="stSidebar"] { border-right:1px solid var(--shc-line)!important; box-shadow:none!important; }
h1,h2,h3,h4,.md-title,[class*="section-title"] {
    color:var(--shc-text)!important; font-family:var(--shc-font-display)!important;
    font-weight:500!important; letter-spacing:-.025em!important; background:none!important;
    -webkit-text-fill-color:var(--shc-text)!important; text-shadow:none!important;
}
p,li,label,[data-testid="stMarkdownContainer"] p,[data-testid="stWidgetLabel"] p {
    color:var(--shc-text)!important; font-family:var(--shc-font-body)!important;
}
[data-testid="stMarkdownContainer"] { color:var(--shc-text)!important; }
span,strong,b,em { color:var(--shc-text)!important; -webkit-text-fill-color:var(--shc-text)!important; }
small,[class*="subtitle"],[class*="caption"],[class*="meta"] { color:var(--shc-muted)!important; }
a { color:var(--shc-accent)!important; text-underline-offset:.18em; }
a:hover { color:var(--shc-text)!important; }
.stApp [data-testid="stMain"] .stButton>button {
    min-height:44px; border:1px solid var(--shc-accent)!important; border-radius:5px!important;
    background:var(--shc-accent)!important; color:var(--shc-button-text)!important; box-shadow:none!important;
    font-family:var(--shc-font-body)!important; font-weight:600!important;
    transition:background-color 140ms ease,border-color 140ms ease!important;
}
.stApp [data-testid="stMain"] .stButton>button:hover {
    transform:none!important; filter:brightness(.92); border-color:var(--shc-accent)!important;
}
.stApp [data-testid="stMain"] .stButton>button:focus-visible,
.stApp [data-testid="stMain"] [data-testid="stPageLink"] a:focus-visible,
[data-testid="stSidebar"] a:focus-visible {
    outline:3px solid var(--shc-focus)!important; outline-offset:3px!important;
}
.stApp [data-testid="stMain"] .stButton>button * {
    color:var(--shc-button-text)!important; -webkit-text-fill-color:var(--shc-button-text)!important;
}
.stApp [data-testid="stMain"] [data-testid="stPageLink"] a {
    min-height:40px; border:0!important; border-radius:0!important;
    background:transparent!important; color:var(--shc-accent)!important;
    box-shadow:none!important; text-decoration:underline; text-underline-offset:.2em;
}
.stApp [data-testid="stMain"] [data-testid="stPageLink"] a * {
    color:var(--shc-accent)!important; -webkit-text-fill-color:var(--shc-accent)!important;
}
.stApp [data-testid="stMain"] [data-testid="stPageLink"] a:hover { color:var(--shc-text)!important; }
.stApp [data-testid="stMain"] [data-baseweb="select"]>div,
.stApp [data-testid="stMain"] input,.stApp [data-testid="stMain"] textarea,
.stApp [data-testid="stMain"] [data-baseweb="tag"] {
    border-color:var(--shc-line)!important; border-radius:5px!important;
    background:var(--shc-surface)!important; color:var(--shc-text)!important; box-shadow:none!important;
}
.stApp [data-testid="stMain"] [data-testid="stExpander"],
.stApp [data-testid="stMain"] [data-testid="stExpander"] details,
.stApp [data-testid="stMain"] [data-testid="stExpander"] summary,
.stApp [data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"],
.stApp [data-testid="stMain"] [data-testid="stChatMessage"] {
    background:var(--shc-surface)!important; color:var(--shc-text)!important;
    border-color:var(--shc-line)!important; box-shadow:none!important;
}
.stApp [data-testid="stMain"] input:focus,.stApp [data-testid="stMain"] textarea:focus,
.stApp [data-testid="stMain"] [data-baseweb="select"]>div:focus-within {
    border-color:var(--shc-accent)!important; box-shadow:0 0 0 2px var(--shc-accent-soft)!important;
}
.editorial-intro { max-width:900px; margin:2.8rem auto 3.5rem; }
.editorial-rule { width:54px; height:2px; margin-bottom:1.35rem; background:var(--shc-accent); }
.editorial-intro h1 { max-width:780px; margin:0 0 1rem; font-size:clamp(2.7rem,6vw,5.4rem); line-height:1.02; }
.editorial-deck { max-width:64ch; margin:0 0 2.2rem; color:var(--shc-muted)!important; font-size:1.15rem; line-height:1.65; }
.editorial-limit { display:flex; flex-wrap:wrap; gap:.45rem 1.1rem; padding:1rem 0; border-top:1px solid var(--shc-line); border-bottom:1px solid var(--shc-line); font-size:.92rem; line-height:1.55; }
.editorial-limit strong { color:var(--shc-caution); font-weight:600; }
.editorial-limit span { max-width:72ch; color:var(--shc-muted); }
.editorial-tool-index { margin-top:3rem; }
.editorial-section-head { display:flex; align-items:baseline; justify-content:space-between; gap:1rem; padding-bottom:.8rem; border-bottom:1px solid var(--shc-line); }
.editorial-section-head h2 { margin:0; font-size:clamp(1.7rem,3vw,2.3rem); }
.editorial-section-head span,.editorial-secondary-title { color:var(--shc-muted); font-size:.9rem; }
.editorial-tool-row { display:flex; align-items:flex-start; min-height:104px; padding:1.3rem .25rem; border-bottom:1px solid var(--shc-line); }
.editorial-tool-row h3 { margin:0 0 .25rem; font-family:var(--shc-font-body)!important; font-size:1.16rem; font-weight:600!important; letter-spacing:-.01em!important; }
.editorial-tool-row p { margin:0; max-width:66ch; color:var(--shc-muted)!important; line-height:1.5; }
.editorial-tool-index + div [data-testid="stPageLink"] { padding-top:1.6rem; }
.editorial-secondary-title { margin:2.3rem 0 .6rem; }
.editorial-brand { margin:.7rem 0 .25rem; font-family:var(--shc-font-display); font-size:1.65rem; color:var(--shc-text); }
.editorial-brand-note,.editorial-sidebar-note { color:var(--shc-muted); font-size:.87rem; line-height:1.55; }
.editorial-nav-label { margin:2rem 0 .5rem; color:var(--shc-muted); font-size:.75rem; letter-spacing:.08em; text-transform:uppercase; }
.editorial-sidebar-note { margin-top:2rem; padding-top:1rem; border-top:1px solid var(--shc-line); }
[data-testid="stSidebar"] [data-testid="stPageLink"] a { border:0!important; background:transparent!important; }
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover { color:var(--shc-accent)!important; }
.md-sb-stats-row { display:none!important; }
.md-sidebar-kicker { display:none!important; }
.md-sidebar-hero,.md-sidebar-note { border-radius:0!important; background:transparent!important; box-shadow:none!important; }
.stApp [data-testid="stMain"] [data-testid="stPageLink"] a { min-height:40px; }
[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    min-height:42px; border-radius:4px!important; color:var(--shc-text)!important;
    font-family:var(--shc-font-body)!important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background:var(--shc-accent-soft)!important; transform:none!important;
}
.md-hero,.hero-wrap,.hero-section,.hero-banner,.sb-hero-banner,
[class$="-hero"],[class$="-hero-wrap"] {
    border-color:transparent!important; border-radius:0!important; background:transparent!important;
    background-image:none!important; box-shadow:none!important; backdrop-filter:none!important;
}
.md-card,.feature-card,.md-stat-card,.md-risk-card,[class*="feature-card"],
[class*="stat-card"],[class*="info-card"],[class*="source-item"],
[class*="result-card"],[class*="tool-card"] {
    border-color:var(--shc-line)!important; border-radius:7px!important;
    background:var(--shc-surface)!important; background-image:none!important;
    box-shadow:none!important; backdrop-filter:none!important;
}
[class*="-card"],[class*="-panel"] {
    border-color:var(--shc-line)!important; border-radius:8px!important;
    background-color:var(--shc-surface)!important; background-image:none!important;
    box-shadow:none!important; backdrop-filter:none!important; color:var(--shc-text)!important;
}
[class*="-card"] :is(h1,h2,h3,h4,p,span,strong,b,em,li,label,div),
[class*="-panel"] :is(h1,h2,h3,h4,p,span,strong,b,em,li,label,div) {
    color:var(--shc-text)!important; -webkit-text-fill-color:var(--shc-text)!important;
}
[class*="-hero"],[class*="-banner"] {
    border-radius:0!important; background-color:transparent!important;
    background-image:none!important; box-shadow:none!important; backdrop-filter:none!important;
}
[class*="-hero"] :is(h1,h2,h3,h4,p,span,strong,b,em,li,label,div),
[class*="-banner"] :is(h1,h2,h3,h4,p,span,strong,b,em,li,label,div) {
    color:var(--shc-text)!important; -webkit-text-fill-color:var(--shc-text)!important;
}
[class*="chip"],[class*="badge"],[class*="pill"] { box-shadow:none!important; text-shadow:none!important; }
.stTabs [data-baseweb="tab-list"] {
    gap:.3rem; border-bottom:1px solid var(--shc-line)!important;
    background:transparent!important; box-shadow:none!important;
}
.stTabs [data-baseweb="tab"] { min-height:42px; border-radius:0!important; color:var(--shc-muted)!important; background:transparent!important; }
.stTabs [aria-selected="true"] {
    color:var(--shc-accent)!important; border-bottom:2px solid var(--shc-accent)!important; background:transparent!important;
}
html body .stApp .stTabs [aria-selected="true"] {
    color:var(--shc-accent)!important; -webkit-text-fill-color:var(--shc-accent)!important;
    background:var(--shc-accent-soft)!important;
}
[data-testid="stAlert"],[role="alert"] {
    border-radius:5px!important; box-shadow:none!important;
    background:var(--shc-surface-muted)!important; color:var(--shc-text)!important;
}
[data-testid="stSidebarCollapsedControl"] button {
    border-radius:4px!important; background:var(--shc-surface)!important;
    color:var(--shc-text)!important; box-shadow:none!important; transform:none!important;
}
@media(prefers-reduced-motion:reduce) {
    *,*::before,*::after { scroll-behavior:auto!important; animation-duration:.01ms!important;
        animation-iteration-count:1!important; transition-duration:.01ms!important; }
}
@media(max-width:700px) {
    [data-testid="stMain"] .block-container { padding:1rem!important; }
    [class*="hero-grid"],[class*="card-grid"],[class*="stat-grid"] { grid-template-columns:1fr!important; }
    .editorial-intro { margin:1.25rem auto 2.5rem; }
    .editorial-intro h1 { font-size:clamp(2.55rem,13vw,4rem); }
    .editorial-deck { font-size:1rem; }
    .editorial-tool-row { min-height:0; padding:1.1rem .15rem; }
    .editorial-section-head { align-items:flex-start; flex-direction:column; gap:.2rem; }
}
</style>
"""

_DARK_RUNTIME_STYLES = """
:root {
    color-scheme:dark;
    --shc-bg:#151c1d; --shc-surface:#1d2828; --shc-surface-muted:#253130;
    --shc-text:#edf1ed; --shc-muted:#b2bfba; --shc-accent:#9cc5c1;
    --shc-accent-soft:#263a38; --shc-line:#3a4945; --shc-caution:#e6a69b;
    --shc-success:#a1c6a9; --shc-focus:#9cc5c1; --shc-button-text:#151c1d;
}
"""

_LIGHT_RUNTIME_STYLES = """
:root {
    color-scheme:light;
    --shc-bg:#f7f6f2; --shc-surface:#fffefa; --shc-surface-muted:#f0f1ed;
    --shc-text:#1d3037; --shc-muted:#53646a; --shc-accent:#2e6874;
    --shc-accent-soft:#e4eeec; --shc-line:#d6ddda; --shc-caution:#9a5148;
    --shc-success:#3d6b57; --shc-focus:#245f6c; --shc-button-text:#fffefa;
}
"""


def init_theme() -> None:
    if "theme" not in st.session_state:
        st.session_state.theme = LIGHT


def toggle_theme() -> None:
    st.session_state.theme = LIGHT if st.session_state.theme == DARK else DARK


def get_theme_styles() -> str:
    return _BASE_STYLES


def get_editorial_styles() -> str:
    tokens = _DARK_RUNTIME_STYLES if st.session_state.get("theme") == DARK else _LIGHT_RUNTIME_STYLES
    return _EDITORIAL_OVERRIDES.replace("</style>", tokens + "\n</style>")


def apply_theme() -> None:
    st.html(get_theme_styles())


def render_theme_toggle() -> None:
    if "theme_toggle" not in st.session_state:
        st.session_state.theme_toggle = st.session_state.get("theme", LIGHT) == DARK

    def sync_theme() -> None:
        st.session_state.theme = DARK if st.session_state.theme_toggle else LIGHT

    dark_mode = st.sidebar.toggle(
        "Dark appearance",
        key="theme_toggle",
        on_change=sync_theme,
    )
    st.session_state.theme = DARK if dark_mode else LIGHT
