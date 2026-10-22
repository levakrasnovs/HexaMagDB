"""HexaMagDB: element coverage, co-doping matrix, property plots and a record browser.
Run from HexaMagDB/:  streamlit run app/streamlit_app.py"""
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).resolve().parent / "data" / "hexamagdb.csv"
# magnet palette: south pole blue, north pole red, violet in between
SOUTH, NORTH, VIOLET, GOLD = "#4c8dff", "#ff4f5e", "#a66cff", "#ffd166"
ACCENT, MUTED, BG, PANEL = NORTH, "#8a93a8", "#070a12", "#0d1120"
FIELD_SCALE = [[0, "#141a2c"], [0.35, SOUTH], [0.7, VIOLET], [1, NORTH]]

# hysteresis loop with field lines, used in the header and the sidebar
LOOP_SVG = """<svg viewBox="0 0 120 80" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="ns" x1="0" x2="1"><stop offset="0" stop-color="#4c8dff"/><stop offset="0.5" stop-color="#a66cff"/>
<stop offset="1" stop-color="#ff4f5e"/></linearGradient></defs>
<line x1="6" y1="40" x2="114" y2="40" stroke="#2a3350" stroke-width="1"/><line x1="60" y1="6" x2="60" y2="74" stroke="#2a3350" stroke-width="1"/>
<path d="M8 68 C 44 68, 70 66, 76 40 S 98 12, 112 12 M112 12 C 76 12, 50 14, 44 40 S 22 68, 8 68"
 fill="none" stroke="url(#ns)" stroke-width="3.2" stroke-linecap="round"/></svg>"""

# (symbol, Z, row, column) in the 18-column layout; lanthanides on row 9, actinides on row 10
_PT = """H 1 1 1|He 2 1 18|Li 3 2 1|Be 4 2 2|B 5 2 13|C 6 2 14|N 7 2 15|O 8 2 16|F 9 2 17|Ne 10 2 18|
Na 11 3 1|Mg 12 3 2|Al 13 3 13|Si 14 3 14|P 15 3 15|S 16 3 16|Cl 17 3 17|Ar 18 3 18|
K 19 4 1|Ca 20 4 2|Sc 21 4 3|Ti 22 4 4|V 23 4 5|Cr 24 4 6|Mn 25 4 7|Fe 26 4 8|Co 27 4 9|Ni 28 4 10|Cu 29 4 11|
Zn 30 4 12|Ga 31 4 13|Ge 32 4 14|As 33 4 15|Se 34 4 16|Br 35 4 17|Kr 36 4 18|
Rb 37 5 1|Sr 38 5 2|Y 39 5 3|Zr 40 5 4|Nb 41 5 5|Mo 42 5 6|Tc 43 5 7|Ru 44 5 8|Rh 45 5 9|Pd 46 5 10|Ag 47 5 11|
Cd 48 5 12|In 49 5 13|Sn 50 5 14|Sb 51 5 15|Te 52 5 16|I 53 5 17|Xe 54 5 18|
Cs 55 6 1|Ba 56 6 2|Hf 72 6 4|Ta 73 6 5|W 74 6 6|Re 75 6 7|Os 76 6 8|Ir 77 6 9|Pt 78 6 10|Au 79 6 11|Hg 80 6 12|
Tl 81 6 13|Pb 82 6 14|Bi 83 6 15|Po 84 6 16|At 85 6 17|Rn 86 6 18|Fr 87 7 1|Ra 88 7 2|
La 57 9 4|Ce 58 9 5|Pr 59 9 6|Nd 60 9 7|Pm 61 9 8|Sm 62 9 9|Eu 63 9 10|Gd 64 9 11|Tb 65 9 12|Dy 66 9 13|
Ho 67 9 14|Er 68 9 15|Tm 69 9 16|Yb 70 9 17|Lu 71 9 18|
Ac 89 10 4|Th 90 10 5|Pa 91 10 6|U 92 10 7"""
PT = {s: (int(z), int(r), int(c)) for s, z, r, c in (e.split() for e in _PT.replace("\n", "").split("|"))}

st.set_page_config(page_title="HexaMagDB", page_icon="🧲", layout="wide", initial_sidebar_state="expanded")
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;700&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{ background-color:{BG} !important; font-family:'Space Grotesk',sans-serif; }}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stHeader"] {{ display:none !important; }}
[data-testid="stAppViewContainer"] {{ background-image:
   radial-gradient(ellipse 60% 40% at 0% 0%, rgba(76,141,255,0.10), transparent 70%),
   radial-gradient(ellipse 60% 40% at 100% 0%, rgba(255,79,94,0.10), transparent 70%) !important; }}
[data-testid="stSidebar"] {{ background:{PANEL} !important; border-right:1px solid transparent;
   border-image:linear-gradient(180deg,{SOUTH},{VIOLET},{NORTH}) 1; }}
.hero {{ position:relative; overflow:hidden; border-radius:14px; padding:22px 26px; margin-bottom:14px;
   background:linear-gradient(120deg, rgba(76,141,255,0.10), rgba(166,108,255,0.06) 50%, rgba(255,79,94,0.10)), {PANEL};
   border:1px solid rgba(255,255,255,0.06); display:flex; align-items:center; gap:24px; }}
.hero .lines {{ position:absolute; inset:0; opacity:0.35; pointer-events:none; }}
.hero h1 {{ margin:0 !important; font-size:2.1rem !important; font-weight:700 !important; letter-spacing:-0.02em;
   background:linear-gradient(90deg,{SOUTH},{VIOLET},{NORTH}); -webkit-background-clip:text; background-clip:text; color:transparent !important; }}
.hero .sub {{ color:{MUTED}; font-size:0.92rem; margin-top:4px; }}
.hero .tag {{ font-family:'Space Grotesk',sans-serif; font-size:1.15rem; font-weight:500; letter-spacing:0.01em; color:{GOLD}; }}
[data-testid="stMainBlockContainer"] {{ padding-top:1.2rem !important; }}
h1, h2, h3 {{ font-family:'Space Grotesk',sans-serif !important; color:#e8ecf4 !important; }}
p, li {{ color:{MUTED}; }}
[data-testid="stSidebar"] [data-testid="stRadio"] label {{ padding:8px 12px; border-radius:8px; width:100%; }}
[data-testid="stSidebar"] [data-testid="stRadio"] div[data-baseweb="radio"]:has(input:checked) label {{ background:linear-gradient(90deg, rgba(76,141,255,0.16), rgba(255,79,94,0.16)); color:#fff !important; box-shadow:inset 3px 0 0 {NORTH}; }}
[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {{ display:none; }}
.kpi {{ position:relative; background:{PANEL}; border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:16px 16px 14px; overflow:hidden; }}
.kpi:before {{ content:''; position:absolute; left:0; right:0; top:0; height:3px; background:linear-gradient(90deg,{SOUTH} 0 50%,{NORTH} 50% 100%); }}
.kpi .v {{ font-family:'Space Grotesk',sans-serif; font-size:1.7rem; font-weight:700; color:#eef1f8; }}
.kpi .l {{ font-family:'JetBrains Mono',monospace; font-size:0.65rem; letter-spacing:0.1em; text-transform:uppercase; color:#4a5568; }}
.pt {{ display:grid; grid-template-columns:repeat(18, minmax(0,1fr)); gap:3px; max-width:980px; }}
.pt div, .pt a {{ text-decoration:none; }}
.pt a:hover {{ outline:2px solid {GOLD}; transform:translateY(-1px); box-shadow:0 0 14px rgba(255,209,102,0.35); }}
.pt div, .pt a {{ aspect-ratio:1; border-radius:5px; display:flex; flex-direction:column; align-items:center; justify-content:center;
          font-family:'JetBrains Mono',monospace; line-height:1.05; }}
.pt .s {{ font-size:0.85rem; font-weight:500; }}
.pt .n {{ font-size:0.58rem; opacity:0.85; }}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load(mtime):
    """mtime only keys the cache, so a rebuilt CSV is picked up without restarting."""
    d = pd.read_csv(DATA, keep_default_na=False, dtype=str)
    for c in ("Year", "Annealing_Temperature_C", "a_A", "c_A", "V_A3", "Crystallite_Size_nm", "Ms_emu_g",
              "Mr_emu_g", "Hc_kOe", "Mr_Ms", "Tc_K", "Maximum_Field_kOe"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    has_ba, has_sr = d.Formula.str.contains("Ba"), d.Formula.str.contains("Sr")
    d["Host"] = np.select([has_ba & has_sr, has_ba, has_sr], ["Ba–Sr", "Ba", "Sr"], "other")
    d["Elements"] = d.Dopant.map(lambda s: sorted({e for e in s.split(";") if e}, key=lambda e: PT.get(e, (999,))[0]))
    d["N_dopants"] = d.Elements.map(len)
    return d


def kpi(col, value, label):
    col.markdown(f"<div class='kpi'><div class='v'>{value}</div><div class='l'>{label}</div></div>", unsafe_allow_html=True)


def shade(frac):
    """Colour on the blue-violet-red field scale."""
    t = 0.2 + 0.8 * frac
    stops = [(p, np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)])) for p, c in FIELD_SCALE]
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if t <= p1:
            rgb = (c0 + (c1 - c0) * (t - p0) / (p1 - p0)).astype(int)
            break
    return "#%02x%02x%02x" % tuple(rgb), "#f4f6fb"


def periodic_table(counts, hosts=("Ba", "Sr"), unit="records", selected=None):
    mx = np.log1p(max(counts.values())) if counts else 1
    cells = []
    for sym, (z, r, c) in PT.items():
        style = f"grid-row:{r};grid-column:{c};"
        n = counts.get(sym, 0)
        if sym in hosts or sym in ("Fe", "O"):
            cells.append(f"<div style='{style}background:repeating-linear-gradient(135deg,#1c2338 0 4px,#232c46 4px 8px);color:#9fb3d9;' title='{sym}: host lattice'>"
                         f"<span class='s'>{sym}</span><span class='n'>host</span></div>")
        elif n:
            bg, fg = shade(np.log1p(n) / mx)
            ring = f"outline:2px solid {GOLD};box-shadow:0 0 16px rgba(255,209,102,0.5);" if sym == selected else ""
            cells.append(f"<a href='?el={sym}' target='_self' style='{style}{ring}background:{bg};color:{fg};' title='{sym}: {n} {unit}'>"
                         f"<span class='s'>{sym}</span><span class='n'>{n}</span></a>")
        else:
            cells.append(f"<div style='{style}background:#0b0f1a;color:#323a52;border:1px solid rgba(255,255,255,0.04);' "
                         f"title='{sym}: no data'><span class='s'>{sym}</span></div>")
    gap = "<div style='grid-row:8;grid-column:1;aspect-ratio:auto;height:8px;'></div>"
    return f"<div class='pt'>{''.join(cells)}{gap}</div>"


def pair_counts(df, by_doi):
    rows = []
    for _, r in df.iterrows():
        els = r.Elements
        if len(els) == 1:
            rows.append((els[0], els[0], r.DOI))
        for a, b in combinations(els, 2):
            rows.append((a, b, r.DOI)); rows.append((b, a, r.DOI))
    p = pd.DataFrame(rows, columns=["A", "B", "DOI"])
    if p.empty:
        return p
    return (p.groupby(["A", "B"]).DOI.nunique() if by_doi else p.groupby(["A", "B"]).size()).rename("n").reset_index()


DIST_PROPS = [("Ms_emu_g", "Ms, emu/g"), ("Mr_emu_g", "Mr, emu/g"), ("Hc_kOe", "Hc, kOe"), ("Mr_Ms", "Mr/Ms"),
              ("Crystallite_Size_nm", "Crystallite size, nm"), ("Annealing_Temperature_C", "Annealing T, °C")]


def show_distributions(df, hit, label):
    """Histograms of the selection against the rest of the filtered database, as densities."""
    st.markdown(f"<div style='color:{MUTED};font-size:0.85rem;margin:4px 0 2px;'>Property distributions: "
                f"<b style='color:{GOLD};'>{label}</b> vs <b style='color:{SOUTH};'>rest of the database</b></div>",
                unsafe_allow_html=True)
    rest = df[~df.index.isin(hit.index)]
    cols = st.columns(3)
    for i, (col, name) in enumerate(DIST_PROPS):
        sel, oth = hit[col].dropna(), rest[col].dropna()
        lo, hi = np.nanpercentile(pd.concat([sel, oth]), [1, 99]) if len(sel) + len(oth) else (0, 1)
        fig = go.Figure()
        bins = dict(start=lo, end=hi, size=(hi - lo) / 30 or 1)
        fig.add_histogram(x=sel.clip(lo, hi), histnorm="probability density", xbins=bins, name=label,
                          marker_color=GOLD, opacity=0.75)
        # the rest of the base as an outline on top, so both shapes stay visible
        fig.add_histogram(x=oth.clip(lo, hi), histnorm="probability density", xbins=bins, name="rest",
                          marker=dict(color="rgba(0,0,0,0)", line=dict(color=SOUTH, width=1.5)))
        med = f"median {sel.median():.3g}" if len(sel) else "no data"
        fig.update_layout(barmode="overlay", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=PANEL,
                          height=210, margin=dict(l=0, r=0, t=28, b=0), showlegend=False, bargap=0.05,
                          title=dict(text=f"{name}  <span style='font-size:11px;color:{MUTED}'>n = {len(sel)}, {med}</span>",
                                     font=dict(size=13), x=0, y=0.97),
                          yaxis=dict(showticklabels=False))
        cols[i % 3].plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"dist_{col}_{label}")


def show_hits(df, els, alone=False):
    """Records and articles that contain all of els (alone: the element is the only dopant)."""
    hit = df[df.Elements.map(lambda e: (e == els) if alone else set(els) <= set(e))]
    label = " + ".join(els) + (" (only dopant)" if alone else "")
    st.markdown(f"### {label}: {len(hit)} records, {hit.DOI.nunique()} articles")
    if hit.empty:
        return
    arts = (hit.groupby("DOI").agg(Year=("Year", "first"), Journal=("Journal", "first"), Records=("Record_ID", "size"),
                                    Formulas=("Formula", lambda x: ", ".join(dict.fromkeys(x))))
            .reset_index().sort_values(["Year", "DOI"]))
    arts["Link"] = "https://doi.org/" + arts.DOI
    show_distributions(df, hit, label)
    t1, t2 = st.tabs(["Articles", "Records"])
    t1.dataframe(arts, hide_index=True, use_container_width=True,
                 column_config={"Link": st.column_config.LinkColumn("Link", display_text="open ↗"),
                                "Year": st.column_config.NumberColumn(format="%d")})
    t2.dataframe(hit[RECORD_COLS], hide_index=True, use_container_width=True,
                 column_config={"Year": st.column_config.NumberColumn(format="%d")})
    t2.download_button("Download these records (CSV)", hit.drop(columns=["Elements", "N_dopants"]).to_csv(index=False),
                       f"hexamagdb_{'_'.join(els)}.csv", "text/csv")


RECORD_COLS = ["Record_ID", "Formula", "Dopant", "Substitution", "Synthesis_Method", "Annealing_Temperature_C", "a_A", "c_A",
               "Crystallite_Size_nm", "Phase_Purity", "Sample_Form", "Ms_emu_g", "Mr_emu_g", "Hc_kOe", "Mr_Ms", "Tc_K", "DOI", "Year"]

d = load(DATA.stat().st_mtime)
with st.sidebar:
    st.markdown(f"""<div style="display:flex;align-items:center;gap:10px;padding:2px 0 14px;">{LOOP_SVG.format(w=54, h=36)}
        <div><div style="font-family:'Space Grotesk',sans-serif;font-size:1.3rem;font-weight:700;color:#eef1f8;line-height:1;">
        Hexa<span style="background:linear-gradient(90deg,{SOUTH},{NORTH});-webkit-background-clip:text;color:transparent;">Mag</span>DB</div></div></div>""", unsafe_allow_html=True)
    page = st.radio("Navigation", ["◈  Element coverage", "⊞  Co-doping matrix", "∿  Properties", "≡  Records"],
                    label_visibility="collapsed")
    st.markdown("<hr style='border-color:rgba(255,255,255,0.07)'>", unsafe_allow_html=True)
    host = st.multiselect("Host", ["Ba", "Sr", "Ba–Sr"], default=["Ba", "Sr", "Ba–Sr"])
    methods = st.multiselect("Synthesis", sorted(m for m in d.Synthesis_Method.unique() if m), placeholder="all methods")
    yr = st.slider("Year", int(d.Year.min()), int(d.Year.max()), (int(d.Year.min()), int(d.Year.max())))
    st.caption(f"Built from `{DATA.name}`, {len(d)} records.")

f = d[d.Host.isin(host) & d.Year.between(*yr)]
if methods:
    f = f[f.Synthesis_Method.isin(methods)]

FIELD_LINES = "".join(f"<ellipse cx='50%' cy='120%' rx='{r}%' ry='{r * 1.6}%' fill='none' stroke='url(#fl)' stroke-width='1'/>"
                      for r in range(12, 120, 12))
st.markdown(f"""<div class="hero"><svg class="lines" width="100%" height="100%" preserveAspectRatio="none">
<defs><linearGradient id="fl" x1="0" x2="1"><stop offset="0" stop-color="{SOUTH}"/><stop offset="1" stop-color="{NORTH}"/></linearGradient></defs>
{FIELD_LINES}</svg>{LOOP_SVG.format(w=120, h=80)}<div style="position:relative;"><div class="tag">M-type hexaferrites · BaFe<sub>12</sub>O<sub>19</sub> · SrFe<sub>12</sub>O<sub>19</sub></div>
<h1>HexaMagDB</h1><div class="sub">Doped Ba and Sr hexaferrites from the literature: composition, synthesis, structure,
saturation magnetization and coercivity.</div></div></div>""", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
kpi(c1, len(f), "records"); kpi(c2, f.DOI.nunique(), "articles")
kpi(c3, f.Elements.explode().dropna().nunique(), "dopant elements")
kpi(c4, int((f.N_dopants >= 2).sum()), "co-doped records"); kpi(c5, int((f.N_dopants == 0).sum()), "undoped references")
st.write("")

if page.startswith("◈"):
    unit = st.radio("Count", ["records", "articles"], horizontal=True)
    ex = f[["Elements", "DOI"]].explode("Elements").dropna()
    counts = (ex.groupby("Elements").DOI.nunique() if unit == "articles" else ex.Elements.value_counts()).to_dict()
    sel = st.query_params.get("el")
    st.markdown(periodic_table(counts, unit=unit, selected=sel), unsafe_allow_html=True)
    st.caption("Dark: no records. Hatched: host lattice (Ba, Sr, Fe, O). Colour runs blue → violet → red on a log scale. Click an element to list its articles and records.")
    if sel in counts:
        show_hits(f, [sel])
    present = [e for e in PT if e in counts]
    absent_tm = [e for e in ("Sc Ti V Cr Mn Co Ni Cu Zn Ga Y Zr Nb Mo Ru Rh Pd Ag Cd In Sn Sb Hf Ta W Re Ir Pt "
                             "La Ce Pr Nd Sm Eu Gd Tb Dy Ho Er Tm Yb Lu").split() if e not in counts]
    a, b = st.columns([3, 2])
    with a:
        t = pd.DataFrame({"Element": present, unit: [counts[e] for e in present]}).sort_values(unit, ascending=False)
        fig = px.bar(t, x="Element", y=unit, color=unit, color_continuous_scale=FIELD_SCALE)
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, height=330, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)
    with b:
        st.markdown("**Not covered** (d- and f-block elements without a single record)")
        st.markdown(" ".join(f"`{e}`" for e in absent_tm) or "—")
        solo = f[f.N_dopants == 1].Elements.str[0].value_counts()
        only_co = sorted((set(counts) - set(solo.index)), key=lambda e: PT[e][0])
        st.markdown("**Only as a co-dopant** (never alone)")
        st.markdown(" ".join(f"`{e}`" for e in only_co) or "—")

elif page.startswith("⊞"):
    l, r = st.columns([1, 1])
    unit = l.radio("Count", ["records", "articles"], horizontal=True)
    order = r.radio("Order", ["atomic number", "frequency"], horizontal=True)
    p = pair_counts(f[f.N_dopants > 0], unit == "articles")
    if p.empty:
        st.info("Nothing for this filter.")
        st.stop()
    els = sorted(set(p.A), key=lambda e: PT[e][0])
    if order == "frequency":
        els = p.groupby("A").n.sum().sort_values(ascending=False).index.tolist()
    m = p.pivot(index="A", columns="B", values="n").reindex(index=els, columns=els)
    text = m.map(lambda v: "" if pd.isna(v) else str(int(v)))
    z = np.log1p(m.fillna(0)).where(m.notna())
    fig = go.Figure(go.Heatmap(z=z.values, x=els, y=els, text=text.values, texttemplate="%{text}",
                               textfont=dict(size=9), customdata=m.fillna(0).values,
                               hovertemplate="%{y} + %{x}: %{customdata} " + unit + "<extra></extra>",
                               colorscale=FIELD_SCALE, showscale=False, xgap=1, ygap=1))
    side = max(520, 22 * len(els))
    # heatmaps emit no selection events, so an almost invisible square marker on every filled cell takes the click
    filled = m.stack().reset_index()
    filled.columns = ["A", "B", "n"]
    fig.add_trace(go.Scatter(x=filled.B, y=filled.A, mode="markers", customdata=filled.n,
                             marker=dict(symbol="square", size=max(8, side / len(els) - 4), color="rgba(0,0,0,0.01)"),
                             selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=1)),
                             hovertemplate="%{y} + %{x}: %{customdata} " + unit + "<extra></extra>", showlegend=False))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=PANEL, height=side, width=side + 60,
                      margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
                      xaxis=dict(side="top", tickfont=dict(size=10)))
    ev = st.plotly_chart(fig, use_container_width=False, on_select="rerun", selection_mode="points", key="matrix")
    pts = ev.selection.points if ev and ev.selection else []
    st.caption("Diagonal: the element is the only dopant. Off-diagonal: both elements in the same composition "
               "(triple co-doping counts in every pair). Empty cell: combination absent.")
    if pts and (pts[0]["y"], pts[0]["x"]) != st.session_state.get("last_click"):
        # apply a click once, so the select boxes stay free to change afterwards
        st.session_state.last_click = (pts[0]["y"], pts[0]["x"])
        st.session_state.pair_a, st.session_state.pair_b = st.session_state.last_click
    s1, s2 = st.columns(2)
    a_ = s1.selectbox("Element A (or click a cell)", els, key="pair_a")
    b_ = s2.selectbox("Element B (same as A: only dopant)", els, key="pair_b")
    show_hits(f, [a_] if a_ == b_ else sorted({a_, b_}, key=lambda e: PT[e][0]), alone=(a_ == b_))
    e = st.selectbox("Partners of", els)
    part = p[(p.A == e) & (p.B != e)].sort_values("n", ascending=False)
    st.markdown(f"**{e}**: alone in {int(p[(p.A == e) & (p.B == e)].n.sum())} {unit}; "
                f"co-doped with {len(part)} elements — " + (", ".join(f"{b} ({n})" for b, n in zip(part.B, part.n)) or "none"))

elif page.startswith("∿"):
    num = {"Ms, emu/g": "Ms_emu_g", "Hc, kOe": "Hc_kOe", "Mr, emu/g": "Mr_emu_g", "Mr/Ms": "Mr_Ms", "a, Å": "a_A",
           "c, Å": "c_A", "V, Å³": "V_A3", "Crystallite size, nm": "Crystallite_Size_nm", "Tc, K": "Tc_K",
           "Annealing T, °C": "Annealing_Temperature_C", "Year": "Year"}
    a, b, c = st.columns(3)
    xs = a.selectbox("x", list(num), index=list(num).index("Annealing T, °C"))
    ys = b.selectbox("y", list(num), index=0)
    el = c.selectbox("Highlight dopant", ["—"] + sorted(f.Elements.explode().dropna().unique(), key=lambda e: PT[e][0]))
    g = f.dropna(subset=[num[xs], num[ys]]).copy()
    g["Group"] = g.Host if el == "—" else np.where(g.Elements.map(lambda s: el in s), el, "other")
    fig = px.scatter(g, x=num[xs], y=num[ys], color="Group", hover_data=["Record_ID", "Formula", "DOI"],
                     labels={num[xs]: xs, num[ys]: ys}, opacity=0.75,
                     color_discrete_map={"Ba": SOUTH, "Sr": NORTH, "Ba–Sr": VIOLET, el: GOLD, "other": "#2c3450"})
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=PANEL, height=560, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"{len(g)} records have both values.")

else:
    q = st.text_input("Search formula, DOI or dopant", placeholder="e.g. SrFe11.5Co0.5O19, Zr, 10.1016/j.jmmm")
    cols = RECORD_COLS
    g = f
    if q:
        s = q.strip()
        g = f[f.Formula.str.contains(s, case=False, regex=False) | f.DOI.str.contains(s, case=False, regex=False)
              | f.Elements.map(lambda els: s in els)]
    st.caption(f"{len(g)} records")
    st.dataframe(g[cols], use_container_width=True, hide_index=True, height=620,
                 column_config={"DOI": st.column_config.TextColumn("DOI"), "Year": st.column_config.NumberColumn(format="%d")})
    st.download_button("Download selection (CSV)", g.drop(columns=["Elements", "N_dopants"]).to_csv(index=False),
                       "hexamagdb_selection.csv", "text/csv")
