import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pydeck as pdk
from plotly.colors import sample_colorscale
import numpy as np

#  1. GLOBAL CONFIGURATION                 
st.set_page_config(
    page_title="Where to live in the Valencian Community?",
    page_icon="🏠",
    layout="wide"
)
    # Colors we are going to use
PRIMARY       = "#0F62FE"
PRIMARY_DARK  = "#0043CE"
PRIMARY_LIGHT = "#E3EDFF" 
GRAY_50       = "#FAFBFC"
GRAY_100      = "#F1F3F5"
GRAY_200      = "#7E7E7E"
TEXT_COLOR    = "#222222"

    # Plotly configuration
corporate_layout = go.Layout(
    font=dict(family="Inter, sans-serif", color= TEXT_COLOR, size=13),
    title=dict(font=dict(family="Poppins, sans-serif", size=20,
                         color=PRIMARY_DARK)),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=True, gridcolor=GRAY_100,
               zerolinecolor=GRAY_100),
    yaxis=dict(showgrid=True, gridcolor=GRAY_100,
               zerolinecolor=GRAY_100),
    legend=dict(
        bgcolor="rgba(0,0,0,0)", orientation="h",
        y=-0.25, x=0.5, xanchor="center",
        font=dict(size=12)
    ),
    colorway=[PRIMARY, "#FF7E29", "#36C5F0", "#FF2D55"]
)
pio.templates["vcv"] = go.layout.Template(layout=corporate_layout)
px.defaults.template = "vcv"                                # <── tema por defecto
px.defaults.color_discrete_sequence = corporate_layout.colorway

#  2. GLOBAL STYLE (colours + layout)   
st.markdown(f"""

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
         
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Inter:wght@400;500&display=swap');
            
/* ICONS ON THE TABS (Font Awesome) */
button[data-baseweb="tab"]{{
    display:flex;              /* icon + text alinged */
    align-items:center;
    gap:6px;                   /* spacing */
    font-family:'Inter', sans-serif;}}  /* normal font for text */


/* Generic adjustment for the pseudo-icon */
button[data-baseweb="tab"]::before{{
    font-family:"Font Awesome 6 Free";   /* icon font  */
    font-weight: 900;                    /* solid (fa-solid) */
    display:inline-block;
    line-height:1;}}

/* HOME  → fa-house-chimney (U+F7F2) */
button[data-baseweb="tab"]:nth-child(1)::before{{ content:"\\f7f2"; }}

/* COMPARATOR → fa-chart-pie      (U+F200) */
button[data-baseweb="tab"]:nth-child(2)::before{{ content:"\\f200"; }}

/* VISUALIZATION → fa-map-location-dot (U+F5A0) */
button[data-baseweb="tab"]:nth-child(3)::before{{ content:"\\f5a0"; }}

/* EDUCATIONAL CENTERS → fa-school (U+F549) */
button[data-baseweb="tab"]:nth-child(4)::before{{ content:"\\f549"; }}

/* SEARCH → fa-magnifying-glass (U+F002) */
button[data-baseweb="tab"]:nth-child(5)::before{{ content:"\\f002"; }}


/* COLOR VARIABLES */
:root {{--primary:        {PRIMARY};
        --primary-dark:   {PRIMARY_DARK};
        --primary-light:  {PRIMARY_LIGHT};
        --gray-50:        {GRAY_50};
        --gray-100:       {GRAY_100};
        --gray-200:       {GRAY_200};
        --text:           {TEXT_COLOR};}}

/* TYPOGRAPHY */
html, body, div, p, span {{font-family: 'Inter', sans-serif; color: var(--text);}}

h1, h2, h3, h4, h5, h6 {{font-family: 'Poppins', sans-serif; font-weight: 600;
                            color: var(--primary-dark);}}

button[data-baseweb="tab"] span[class^="css"]::first-letter {{
    color: var(--primary) !important;}}

/* GLOBAL LAYOUT */
.block-container {{
    max-width: 1400px;
    padding-left: 2rem !important;
    padding-right: 2rem !important;}}

section.main > div {{
    padding-top: 1.2rem;
    padding-bottom: 1.2rem;}}

.stColumn > div {{
    padding-left: .75rem;
    padding-right: .75rem;}}

img {{ border-radius: 8px; }}

/* RE-USABLE BOXES */
.box {{
    background-color: var(--gray-50);
    padding: 20px 24px;
    border: 1px solid var(--gray-100);
    border-radius: 10px;
    margin-bottom: 1.5rem;}}
    
.callout {{
    background-color: var(--gray-100);
    padding: 18px 22px;
    border-left: 5px solid #FF2D55;
    border-radius: 8px;
    margin-bottom: 1.5rem;}}

/* STICK TAB BAR */
.stTabs > div[data-baseweb="tab-list"] {{
    position: sticky;
    top: 0;
    z-index: 999;
    background: white;
    padding: .5rem 0 .25rem 0;
    border-bottom: 1px solid var(--gray-200);}}

/* ACTIVE tab - border = background */
button[data-baseweb="tab"][aria-selected="true"]{{
    background-color: var(--primary-light) !important;   
    color: var(--primary-dark) !important;              
    border-radius: 50px !important;
    box-shadow: inset 0 0 0 2px var(--primary-light) !important;}}

/* Hover state for the other tabs */
button[data-baseweb="tab"]:not([aria-selected="true"]):hover {{
    background-color: var(--gray-100) !important;}}

/* REDUCE PX FOR THE MOBILE  */
@media (max-width:768px){{
  .block-container{{padding:0 1rem!important;}}
  h1{{font-size:1.75rem;}}
  h2{{font-size:1.4rem;}}
  .stTabs>div[data-baseweb="tab-list"]{{overflow-x:auto;white-space:nowrap;-webkit-overflow-scrolling:touch;}}
  button[data-baseweb="tab"]{{font-size:.85rem;padding:.35rem .7rem;}}
  div[data-testid="column"]{{width:100%!important;flex:1 1 100%!important;}}
  .box,.callout{{padding:14px 16px;}}}}

</style>
""", unsafe_allow_html=True)


#  3. DATA LOADING                       

@st.cache_data
def load_data():
    return pd.read_csv("data/indicadores_municipios.csv")
df = load_data()

@st.cache_data
def load_centros():
    return pd.read_csv("data/centroseducativos_filtrados.csv")
centros_df = load_centros()

#  4. MAIN HEADER
with st.container():
    st.markdown("""<h1 style='text-align:center; color:var(--primary);'> Where to live in the Valencian Community?
                    </h1>""", unsafe_allow_html=True)
    
    st.markdown("""<p style='text-align:center; font-size:22px; color:var(--gray-200);'>
            Find the best place to live based on your needs and preferences.</p> """, unsafe_allow_html=True)
    
#  5. TABS
# Tabs with icons + text
tabs = st.tabs([
    f" HOME",
    f" COMPARATOR",
    f" VISUALIZATION",
    f" EDUCATIONAL CENTERS",
    f" SEARCH"])

##   5.1 HOME

with tabs[0]:
    with st.container():
        st.image("collage.png", use_container_width=True)

        st.markdown("""
        <p style='text-align:center;font-size:18px;'>
        This interactive tool helps you compare municipalities based on three key factors:<br><br>
        <b><i class="fa-solid fa-graduation-cap"></i> Education</b> ·
        <b><i class="fa-solid fa-house-chimney"></i> Housing</b> ·
        <b><i class="fa-solid fa-briefcase"></i> Employment</b><br><br>
        </p> """, unsafe_allow_html=True)

        st.markdown("### What can you do with this app?")
        st.markdown(f"""
        <div class='callout'>
          <ul style="list-style-type:none;margin:0;">
            <li><i class="fa-solid fa-chart-pie"></i> <b>Municipality Comparator</b><br>
                Compare up to 3 municipalities using interactive visualizations like radar, bar & pie charts.
            </li><br>
            <li><i class="fa-solid fa-map-location-dot"></i> <b>Municipality Map</b><br>
                Display education, housing or business activity on a map.
            </li><br>
            <li><i class="fa-solid fa-school"></i> <b>Educational Centers Map</b><br>
                Explore the geographic distribution of schools by municipality or by individual center.
            </li><br>
            <li><i class="fa-solid fa-magnifying-glass"></i> <b>Custom Search</b><br>
                Find municipalities that meet your minimum requirements.
            </li>
          </ul>
        </div> """, unsafe_allow_html=True)          

        st.markdown("""
        <div class='box'>
        <i class="fa-solid fa-circle-info"></i> <i>Data based on public sources and local statistics.</i><br>
        <i class="fa-solid fa-code"></i> <i>Developed by Andrea Almela, Anna Aparici and Sergi Martínez</i>
        </div> """, unsafe_allow_html=True)

##   5.2 COMPARATOR
with tabs[1]:
    with st.container():
        st.header("MUNICIPALITY COMPARATOR")
        st.markdown("### <i class='fa-solid fa-receipt'></i> What can you do here?",
            unsafe_allow_html=True)

        st.markdown("""
        Compare different municipalities in the Valencian Community by access to:

        - 🏫 **Educational centers**  
        - 🏘️ **Available housing**  
        - 💼 **Registered companies**

        All indicators are **normalized per 1000 inhabitants**.  
        The **opportunity index** combines them (40 % education, 30 % housing, 30 % employment).""")

        municipios = df["municipio"].unique()
        seleccionados = st.multiselect(
            "Select up to 3 municipalities to compare:",
            municipios, default=municipios[:2])

        if len(seleccionados) == 0:
            st.info("Please select at least one municipality to compare.")
        elif len(seleccionados) > 3:
            st.warning("You can only select up to 3 municipalities.")
        else:
            df_sel = df[df["municipio"].isin(seleccionados)]

            st.markdown(
                "#### <i class='fa-solid fa-clipboard-list'></i> Indicators per municipality",
                unsafe_allow_html=True)
            st.dataframe(df_sel.set_index("municipio"))

            # warning for very small municipalities
            pequeños = df_sel[df_sel["Poblacion_Total"] < 1000]["municipio"].tolist()
            if pequeños:
                st.warning(
                    "⚠ The following municipalities have fewer than 1000 inhabitants, "
                    f"so ratios may be distorted: {', '.join(pequeños)}")

            # absolute-value table
            st.markdown("#### <i class='fa-solid fa-receipt'></i> Absolute values", unsafe_allow_html=True)

            tabla_abs = (
                df_sel[["municipio", "Poblacion_Total", "n_centros_total",
                        "total_ofertas", "empresas_total"]]
                .rename(columns={
                    "Poblacion_Total": "Population", "n_centros_total": "Schools",
                    "total_ofertas": "Housing offers", "empresas_total": "Companies"
                })
                .set_index("municipio"))
            st.dataframe(tabla_abs)

            # bar comparison
            st.markdown("#### <i class='fa-solid fa-chart-column'></i> Indicator comparison", unsafe_allow_html=True)

            ver_reales = st.checkbox("🔁 Show real values (not normalized)", value=False)

            df_graf = df_sel.set_index("municipio")[["centros_por_1000hab", "viviendas_por_1000hab", "empresas_por_1000hab"]]
            if not ver_reales:
                df_graf = df_graf / df_graf.max()

            fig_bar = px.bar(
                df_graf.reset_index(), x="municipio",
                y=df_graf.columns.tolist(), barmode="group",
                labels={"value": "Value", "variable": "Indicator"},
                title="Indicator comparison" + (" (normalized)" if not ver_reales else ""))
            st.plotly_chart(fig_bar, use_container_width=True)

            # individual indicators
            st.markdown("#### <i class='fa-solid fa-chart-column'></i> Individual indicators", unsafe_allow_html=True)
            for ind in ["centros_por_1000hab", "viviendas_por_1000hab", "empresas_por_1000hab"]:
                st.plotly_chart(
                    px.bar(df_sel, x="municipio", y=ind,
                           title=ind.replace('_', ' ').capitalize()),
                    use_container_width=True)

            # radar
            st.markdown("#### <i class='fa-solid fa-chart-column'></i> Relative profile (Radar)", unsafe_allow_html=True)
            df_norm = (df_sel.set_index("municipio")[["centros_por_1000hab", "viviendas_por_1000hab", "empresas_por_1000hab"]] /
                        df_sel[["centros_por_1000hab", "viviendas_por_1000hab", "empresas_por_1000hab"]].max())

            fig_rad = go.Figure()
            for m in df_norm.index:
                fig_rad.add_trace(go.Scatterpolar(
                    r=df_norm.loc[m].values, theta=df_norm.columns,
                    fill='toself', name=m))
            fig_rad.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
            st.plotly_chart(fig_rad, use_container_width=True)

            # pie charts
            st.markdown("#### <i class='fa-solid fa-chart-pie'></i> Normalized distribution of indicators", unsafe_allow_html=True)

            maximos = df[["centros_por_1000hab", "viviendas_por_1000hab", "empresas_por_1000hab"]].max()
            for _, row in df_sel.iterrows():
                vals = [
                    row["centros_por_1000hab"] / maximos["centros_por_1000hab"],
                    row["viviendas_por_1000hab"] / maximos["viviendas_por_1000hab"],
                    row["empresas_por_1000hab"] / maximos["empresas_por_1000hab"]]
                st.plotly_chart(
                    px.pie(names=["Education", "Housing", "Employment"],
                           values=vals, title=row["municipio"]),use_container_width=True)

            # opportunity index + scatter + summary
            st.markdown("#### <i class='fa-solid fa-star'></i> Opportunity index", unsafe_allow_html=True)

            st.plotly_chart(
                px.bar(df_sel, x="municipio", y="indice_oportunidad",
                       title="Opportunity index comparison"),
                use_container_width=True)
            
            st.markdown("#### <i class='fa-solid fa-chart-column'></i> Housing vs companies relationship", unsafe_allow_html=True)
            st.plotly_chart(
                px.scatter(df_sel, x="viviendas_por_1000hab", y="empresas_por_1000hab",
                           color="municipio", size="indice_oportunidad",
                           hover_name="municipio",
                           title="Housing (per 1000 inh.) vs Companies (per 1000 inh.)"),
                use_container_width=True)

            st.subheader("📌 Summary of results")
            mejor  = df_sel.loc[df_sel["indice_oportunidad"].idxmax(), "municipio"]
            centros = df_sel.loc[df_sel["centros_por_1000hab"].idxmax(), "municipio"]
            viv     = df_sel.loc[df_sel["viviendas_por_1000hab"].idxmax(), "municipio"]
            emp     = df_sel.loc[df_sel["empresas_por_1000hab"].idxmax(), "municipio"]

            col1, col2 = st.columns(2, gap="large")
            col1.success(f"🥇 Highest opportunity index: **{mejor}**")
            col1.info   (f"🏫 Most schools /1k inh.: **{centros}**")
            col2.info   (f"🏘️ Most housing offers /1k inh.: **{viv}**")
            col2.info   (f"💼 Most companies /1k inh.: **{emp}**")

##   5.3 VISUALIZATION (Map)
with tabs[2]:
    st.header("INDICATOR MAP")

    indicador = st.selectbox("Select an indicator for the map", [
        "centros_por_1000hab",
        "viviendas_por_1000hab",
        "empresas_por_1000hab",
        "indice_oportunidad"])

    columnas_necesarias = ["lat", "lon", indicador]
    if all(col in df.columns for col in columnas_necesarias):
        df_mapa = df.dropna(subset=columnas_necesarias)

        min_val = df_mapa[indicador].min()
        max_val = df_mapa[indicador].max()

        view_state = pdk.ViewState(
            latitude=df_mapa["lat"].mean(),
            longitude=df_mapa["lon"].mean(),
            zoom=7, pitch=0)

        # Layer with variable colour
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_mapa,
            get_position='[lon, lat]',
            get_radius=2000,
            get_fill_color=f"""[
                255 * ({indicador}) / {max_val},
                255 * (1 - ({indicador}) / {max_val}),
                100, 180 ]""", pickable=True)

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="road",
            tooltip={"text": "{municipio}\n" + indicador + ": {" + indicador + "}"}))
        
        fig_legenda = go.Figure(go.Scatter(
                x=[None], y=[None],
                mode="markers",
                marker=dict(
                    colorscale="RdYlGn",
                    cmin=min_val,
                    cmax=max_val,
                    showscale=True,
                    colorbar=dict(
                        orientation="h",
                        title=indicador,
                        x=0, xanchor="left",
                        len=1.0, thickness=30,
                        thicknessmode="pixels",
                        outlinewidth=0),   
                    size=1, color=[min_val]),
                hoverinfo="skip"))
        
        fig_legenda.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=140,                
            margin=dict(t=10, b=10, l=50, r=0))

        st.plotly_chart(fig_legenda, use_container_width=True)

    else:
        st.error("Missing required columns to generate the map.")

##   5.4 MAP OF EDUAATIONAL CENTERS
with tabs[3]:
    st.header("MAP OF EDUCATIONAL CENTERS")

    regimenes = centros_df["regimen"].dropna().unique().tolist()
    regimen_seleccionado = st.selectbox("Select the center type:", sorted(regimenes))

    df_filtrado = centros_df[centros_df["regimen"] == regimen_seleccionado]

    # 
    marcadores_localidad = (
        df_filtrado.groupby("localidad")
        .agg(n_centros=("DENOMINACION", "count"),
             lat=("LATITUD", "mean"),
             lon=("LONGITUD", "mean"))
        .reset_index())

    vista = st.radio(
        "Select map detail level:",
        ["📍 General view by municipality", "🔎 Detailed view by center"])

    # Colours by centre type (only for detailed view)
    color_map = {
        "púb.":        [0, 128, 0, 160],
        "priv. conc.": [255, 165, 0, 160],
        "priv.":       [220, 20, 60, 160]}
    
    df_filtrado["color"] = df_filtrado["regimen"].apply(
        lambda r: color_map.get(r, [100, 100, 100, 160]))

    view_state = pdk.ViewState(
        latitude=df_filtrado["LATITUD"].mean(),
        longitude=df_filtrado["LONGITUD"].mean(),
        zoom=7)

    # GENERAL view: circles + gradient
    if vista == "📍 General view by municipality":
        # 1. Normalize number of schools 0-1
        n_min, n_max = marcadores_localidad["n_centros"].min(), marcadores_localidad["n_centros"].max()
        marcadores_localidad["ratio"] = (marcadores_localidad["n_centros"] - n_min) / (n_max - n_min)

        # 2. Three-tone palette
        CLR_A = "#FF9D00"
        CLR_B = "#4DD0E1"   
        CLR_C = "#062E57"   
        ALPHA = 180        

        def hex2rgb(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
        rgb_a, rgb_b, rgb_c = map(hex2rgb, (CLR_A, CLR_B, CLR_C))

        def tritone(t: float) -> list[int]:
            """Linear blend A→B (0-0.5) then B→C (0.5-1). Returns [r, g, b, α]."""
            if t <= 0.5:
                w = t * 2
                r = int(rgb_a[0] + (rgb_b[0]-rgb_a[0])*w)
                g = int(rgb_a[1] + (rgb_b[1]-rgb_a[1])*w)
                b = int(rgb_a[2] + (rgb_b[2]-rgb_a[2])*w)
            else:
                w = (t-0.5) * 2
                r = int(rgb_b[0] + (rgb_c[0]-rgb_b[0])*w)
                g = int(rgb_b[1] + (rgb_c[1]-rgb_b[1])*w)
                b = int(rgb_b[2] + (rgb_c[2]-rgb_b[2])*w)
            return [r, g, b, ALPHA]

        marcadores_localidad["fill_color"] = marcadores_localidad["ratio"].apply(tritone)

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=marcadores_localidad,
            get_position='[lon, lat]',
            get_radius=2000,               
            get_fill_color='fill_color',
            pickable=True,
            auto_highlight=True)
        tooltip = {"text": "{localidad}\nSchools: {n_centros}"}

    # DETAILED view: individual centres
    else:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_filtrado,
            get_position='[LONGITUD, LATITUD]',
            get_radius=100,
            get_fill_color='color',
            pickable=True
        )
        tooltip = {"text": "{DENOMINACION}\nType: {tipo}"}

    # 3. Render map
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="road"
    ))

    # 4. Gradient legend (general view only)
    if vista == "📍 General view by municipality":
        scale = [[0, CLR_A], [0.5, CLR_B], [1, CLR_C]]

        fig_leg = go.Figure(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(colorscale=scale,
                        cmin=n_min, cmax=n_max,
                        showscale=True,
                        colorbar=dict(
                            orientation="h",
                            title="Number of schools",
                            x=0, xanchor="left",
                            len=1.0, thickness=30, thicknessmode="pixels",
                            outlinewidth=0)),
            hoverinfo="skip",
            marker_color=[n_min]))

        fig_leg.update_layout(
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            height=140, margin=dict(t=10, b=10, l=50, r=0))

        st.plotly_chart(fig_leg, use_container_width=True)

##   5.5 SEARCH
with tabs[4]:
    st.markdown("""
        <div style="margin-top:0;">
        <h2 style="margin:0;">
            SEARCH BY MINIMUM CONDITIONS
        </h2>
        </div>
        """, unsafe_allow_html=True)
    
    min_centros = st.slider("Minimum educational centers per 1000 inhabitants:", 0.0, 10.0, 1.0)
    min_viviendas = st.slider("Minimum housing per 1000 inhabitants:", 0.0, 10.0, 1.0)
    min_empresas = st.slider("Minimum companies per 1000 inhabitants:", 0.0, 1000.0, 100.0)

    resultado = (df[
            (df["centros_por_1000hab"] >= min_centros) &
            (df["viviendas_por_1000hab"] >= min_viviendas) &
            (df["empresas_por_1000hab"] >= min_empresas)]
        .sort_values("indice_oportunidad", ascending=False))

    st.dataframe(resultado)

    if not resultado.empty:
        st.success(f"{len(resultado)} cities meet your criteria.")