import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="🍽️ Zomato Analysis",
    page_icon="🍽️",
    layout="wide"
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0f0f0f;
    color: #f0ece4;
}
.stApp {
    background: linear-gradient(135deg, #0f0f0f 0%, #1a0a0a 50%, #0f0f0f 100%);
}
h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 3rem !important;
    background: linear-gradient(90deg, #e63946, #ff6b6b, #ffd166);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
}
h2, h3 { font-family: 'Playfair Display', serif !important; color: #ffd166 !important; }
.metric-card {
    background: linear-gradient(135deg, #1c1c1c, #2a1010);
    border: 1px solid #e63946;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(230,57,70,0.2);
}
.metric-number { font-family: 'Playfair Display', serif; font-size: 2.2rem; color: #e63946; }
.metric-label { font-size: 0.8rem; color: #aaa; letter-spacing: 2px; text-transform: uppercase; }
.section-divider {
    border: none; height: 1px;
    background: linear-gradient(90deg, transparent, #e63946, transparent);
    margin: 25px 0;
}
.insight-box {
    background: linear-gradient(135deg, #1c1010, #2a1a1a);
    border-left: 4px solid #e63946;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
}
.no-data {
    background: #1a0808;
    border: 1px dashed #e63946;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    color: #aaa;
    font-size: 0.95rem;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111 0%, #1a0808 100%);
    border-right: 1px solid #e63946;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# GLOBAL CHART STYLE
# ─────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0f0f0f',
    'axes.facecolor':   '#1a0808',
    'axes.edgecolor':   '#e63946',
    'axes.labelcolor':  '#f0ece4',
    'axes.titlecolor':  '#ffd166',
    'axes.titlesize':   13,
    'axes.labelsize':   10,
    'xtick.color':      '#aaaaaa',
    'ytick.color':      '#aaaaaa',
    'text.color':       '#f0ece4',
    'grid.color':       '#2a1010',
    'grid.linestyle':   '--',
    'grid.alpha':       0.5,
})

COLORS = ['#e63946','#ffd166','#06d6a0','#118ab2','#ff6b6b',
          '#c77dff','#f4a261','#2ec4b6','#e76f51','#a8dadc']
RED  = '#e63946'
GOLD = '#ffd166'
BG   = '#0f0f0f'

# ─────────────────────────────────────────
# NO DATA MESSAGE HELPER
# ─────────────────────────────────────────
def no_data_msg(msg="Not enough data to display this chart"):
    st.markdown(f'<div class="no-data">⚠️ {msg}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# LOAD & CLEAN DATA
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('zomato.csv', encoding='latin-1')
    df.rename(columns={
        'Aggregate rating':     'rate',
        'Cuisines':             'cuisines',
        'City':                 'location',
        'Average Cost for two': 'cost',
        'Has Online delivery':  'online_order',
        'Has Table booking':    'book_table',
        'Price range':          'price_range',
        'Restaurant Name':      'name',
        'Votes':                'votes',
        'Rating text':          'rating_text',
    }, inplace=True)
    df.drop_duplicates(inplace=True)
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
    df = df[df['rate'] > 0]
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
    return df

df = load_data()

# ─────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1a0505,#2d0d0d);border:1px solid #e63946;
border-radius:20px;padding:35px;text-align:center;margin-bottom:25px;">
    <h1>🍽️ Zomato Data Analysis</h1>
    <p style="color:#aaa;letter-spacing:3px;text-transform:uppercase;font-size:0.95rem;">
    Restaurant Insights · Python · Pandas · Matplotlib · Seaborn · Streamlit</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")
    locations = ['All'] + sorted(df['location'].dropna().unique().tolist())
    selected_location = st.selectbox("📍 City", locations)
    min_r, max_r = float(df['rate'].min()), float(df['rate'].max())
    rating_range = st.slider("⭐ Rating Range", min_r, max_r, (min_r, max_r), 0.1)
    order_filter = st.selectbox("🛵 Online Delivery", ['All', 'Yes', 'No'])
    st.markdown("---")
    st.markdown(f"**Total Records:** `{len(df):,}`")

# APPLY FILTERS
filtered = df.copy()
if selected_location != 'All':
    filtered = filtered[filtered['location'] == selected_location]
filtered = filtered[filtered['rate'].between(rating_range[0], rating_range[1])]
if order_filter != 'All':
    filtered = filtered[filtered['online_order'] == order_filter]

# ─────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
kpis = [
    (f"{len(filtered):,}", "Restaurants"),
    (f"{filtered['rate'].mean():.2f} ⭐" if len(filtered) > 0 else "N/A", "Avg Rating"),
    (f"{filtered['location'].nunique()}", "Cities"),
    (f"{filtered['cuisines'].nunique()}", "Cuisines"),
]
for col, (val, label) in zip([c1, c2, c3, c4], kpis):
    col.markdown(f"""<div class="metric-card">
        <div class="metric-number">{val}</div>
        <div class="metric-label">{label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────
# EMPTY CHECK
# ─────────────────────────────────────────
if len(filtered) == 0:
    st.markdown('<div class="no-data">⚠️ No data found for selected filters. Please adjust your filters.</div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────
# ROW 1: RATINGS + CUISINES
# ─────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### ⭐ Ratings Distribution")
    if filtered['rate'].nunique() >= 2:
        fig, ax = plt.subplots(figsize=(8, 4), facecolor=BG)
        sns.histplot(filtered['rate'], bins=min(25, len(filtered)),
                     kde=False, ax=ax, color=RED, edgecolor='#2a1010')
        if len(filtered) >= 5:
            filtered['rate'].plot.kde(ax=ax, color=GOLD, lw=2)
        ax.axvline(filtered['rate'].mean(), color=GOLD, linestyle='--', lw=2,
                   label=f"Avg: {filtered['rate'].mean():.2f}")
        ax.legend(facecolor='#1a0808', edgecolor=RED)
        ax.grid(True)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        no_data_msg("Need more data for ratings chart")

with col_b:
    st.markdown("### 🍜 Top 10 Cuisines")
    if filtered['cuisines'].nunique() >= 1:
        top_c = filtered['cuisines'].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(8, 4), facecolor=BG)
        sns.barplot(x=top_c.values, y=top_c.index,
                    palette=COLORS[:len(top_c)], ax=ax, legend=False)
        for bar, val in zip(ax.patches, top_c.values):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                    f'{val:,}', va='center', fontsize=8, color=GOLD)
        ax.grid(True, axis='x')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        no_data_msg("No cuisine data available")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────
# ROW 2: LOCATIONS + PIE CHARTS
# ─────────────────────────────────────────
col_c, col_d = st.columns([2, 1])

with col_c:
    st.markdown("### 📍 Top 10 Cities")
    if filtered['location'].nunique() >= 1:
        top_l = filtered['location'].value_counts().head(10)
        n = len(top_l)
        fig, ax = plt.subplots(figsize=(10, 4), facecolor=BG)
        sns.barplot(x=top_l.index, y=top_l.values,
                    palette=sns.color_palette("flare", n), ax=ax, legend=False)
        for p in ax.patches:
            ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.5,
                    f'{int(p.get_height()):,}', ha='center', fontsize=8, color=GOLD)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
        ax.grid(True, axis='y')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        no_data_msg("No location data available")

with col_d:
    st.markdown("### 🛵 Online Delivery")
    counts = filtered['online_order'].value_counts()
    if len(counts) >= 1:
        fig, ax = plt.subplots(figsize=(5, 4), facecolor=BG)
        ax.pie(counts.values, labels=counts.index,
               autopct='%1.1f%%',
               colors=[RED, GOLD][:len(counts)],
               startangle=90,
               wedgeprops=dict(edgecolor='#0f0f0f', linewidth=2),
               pctdistance=0.75)
        ax.set_facecolor('#1a0808')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        no_data_msg("No delivery data available")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────
# ROW 3: COST + RATING VS COST
# ─────────────────────────────────────────
col_e, col_f = st.columns(2)

with col_e:
    st.markdown("### 💰 Cost Distribution")
    cost_clean = filtered['cost'].dropna()
    if len(cost_clean) >= 2:
        fig, ax = plt.subplots(figsize=(8, 4), facecolor=BG)
        sns.histplot(cost_clean, bins=min(35, len(cost_clean)),
                     kde=False, ax=ax, color=GOLD, edgecolor='#2a1010')
        if len(cost_clean) >= 5:
            cost_clean.plot.kde(ax=ax, color=RED, lw=2)
        ax.axvline(cost_clean.mean(), color=RED, linestyle='--', lw=2,
                   label=f"Avg: {cost_clean.mean():.0f}")
        ax.legend(facecolor='#1a0808', edgecolor=RED)
        ax.grid(True)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        no_data_msg("Not enough cost data available")

with col_f:
    st.markdown("### 🔥 Rating vs Cost")
    sc_df = filtered.dropna(subset=['cost', 'rate'])
    if len(sc_df) >= 2:
        fig, ax = plt.subplots(figsize=(8, 4), facecolor=BG)
        scatter = ax.scatter(sc_df['cost'], sc_df['rate'],
                             c=sc_df['rate'], cmap='YlOrRd',
                             alpha=0.5, edgecolors='none', s=20)
        plt.colorbar(scatter, ax=ax).set_label('Rating', color=GOLD)
        ax.set_xlabel('Cost for Two')
        ax.set_ylabel('Rating')
        ax.grid(True)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        no_data_msg("Not enough data for scatter plot")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────
# ROW 4: PRICE RANGE + RATING BY CITY
# ─────────────────────────────────────────
col_g, col_h = st.columns([1, 2])

with col_g:
    st.markdown("### 🏷️ Price Range")
    if filtered['price_range'].nunique() >= 1:
        top_t = filtered['price_range'].value_counts().sort_index()
        labels = {1:'💲 Budget', 2:'💲💲 Moderate',
                  3:'💲💲💲 Expensive', 4:'💲💲💲💲 Luxury'}
        top_t.index = [labels.get(i, str(i)) for i in top_t.index]
        n = len(top_t)
        fig, ax = plt.subplots(figsize=(5, 4), facecolor=BG)
        sns.barplot(x=top_t.index, y=top_t.values,
                    palette=sns.color_palette("magma", n), ax=ax, legend=False)
        for p in ax.patches:
            ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.5,
                    f'{int(p.get_height()):,}', ha='center', fontsize=8, color=GOLD)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha='right')
        ax.grid(True, axis='y')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        no_data_msg("No price range data available")

with col_h:
    st.markdown("### 📦 Rating by City")
    top_locs = filtered['location'].value_counts().head(8).index
    loc_df = filtered[filtered['location'].isin(top_locs)]
    if len(loc_df) >= 2 and loc_df['location'].nunique() >= 1:
        fig, ax = plt.subplots(figsize=(10, 4), facecolor=BG)
        sns.boxplot(data=loc_df, x='location', y='rate',
                    palette='flare', ax=ax, order=top_locs,
                    boxprops=dict(edgecolor=GOLD),
                    whiskerprops=dict(color=GOLD),
                    capprops=dict(color=GOLD),
                    medianprops=dict(color=RED, lw=2.5),
                    flierprops=dict(marker='o', color=RED, alpha=0.3, markersize=3))
        ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha='right')
        ax.grid(True, axis='y')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        no_data_msg("Not enough data for city comparison")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────
# KEY INSIGHTS
# ─────────────────────────────────────────
st.markdown("### 💡 Key Insights")
insights = [
    f"⭐ Average rating is <b>{filtered['rate'].mean():.2f}/5</b>",
    f"🍜 Most popular cuisine: <b>{filtered['cuisines'].value_counts().idxmax()}</b>",
    f"📍 Most restaurants in: <b>{filtered['location'].value_counts().idxmax()}</b>",
    f"🛵 <b>{(filtered['online_order']=='Yes').mean()*100:.1f}%</b> offer online delivery",
    f"💰 Average cost for two: <b>{filtered['cost'].dropna().mean():.0f}</b>",
]
cols = st.columns(3)
for i, insight in enumerate(insights):
    cols[i % 3].markdown(
        f'<div class="insight-box">{insight}</div>',
        unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# RAW DATA
with st.expander("🔍 Explore Raw Data"):
    st.dataframe(filtered.head(100), use_container_width=True)
    st.caption(f"Showing top 100 of {len(filtered):,} records")

st.markdown("""
<p style='text-align:center;color:#444;font-size:0.8rem;margin-top:20px;'>
Built by Mohammed Noshin · Zomato Data Analysis · Python & Streamlit</p>
""", unsafe_allow_html=True)