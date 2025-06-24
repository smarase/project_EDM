import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# Cargar datos
@st.cache_data
def load_data():
    return pd.read_csv("data/indicadores_municipios.csv")

df = load_data()

@st.cache_data
def load_centros():
    return pd.read_csv("data/centroseducativos_filtrados.csv")

centros_df = load_centros()


# Título principal
# st.title("¿Dónde vivir en la Comunidad Valenciana?")
# st.markdown("Explora municipios según educación, vivienda y empleo.")





import streamlit as st
st.set_page_config(layout="wide")




st.markdown("""
<style>
/* Contenedor horizontal de navegación */
.nav-container {
    display: flex;
    justify-content: space-evenly;
    align-items: center;
    width: 100%;
    background-color: #f8f9fa;
    padding: 16px 0;
    border-bottom: 1px solid #ccc;
    flex-wrap: wrap;
    box-sizing: border-box;
    margin: 0 auto;
}

/* Botones del menú */
.nav-button {
    margin: 0 8px;
    padding: 10px 20px;
    font-weight: 500;
    border-radius: 20px;
    background-color: #e9ecef;
    color: #333;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
}

/* Hover */
.nav-button:hover {
    background-color: #d6d8db;
}

/* Activo */
.nav-active {
    background-color: #cfe2ff;
    color: #084298;
    box-shadow: 0 0 8px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)


tabs = st.tabs([
    "🏠 HOME",
    "📊 COMPARATOR",
    "🗺️ VISUALIZATION",
    "🎓 EDUCATIONAL CENTERS",
    "🔍 SEARCH"
])

st.markdown("""
<style>
/* Selecciona solo los emojis al comienzo del texto */
button[data-baseweb="tab"] span[class^="css"]::first-letter {
    color: #ff4b4b !important; /* Cambia este color a tu gusto */
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# Página principal: Portada
with tabs[0]:
    #st.header("🏠 Inicio")
    st.markdown("<h1 style='text-align: center;'>Where to live in the Valencian Community?</h1>", unsafe_allow_html=True)

    st.markdown("""
<div style='text-align: center; font-size: 22px;'>
Find the best place to live based on your needs and preferences.
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style='text-align: center; font-size: 18px;'>
This interactive tool helps you compare municipalities based on three key factors:<br><br>
<b>🎓 Education</b> · <b>🏘️ Housing</b> · <b>💼 Employment</b><br><br>
</div>
""", unsafe_allow_html=True)

    st.markdown("### 🔎 What can you do with this app?")
    st.markdown("""
- **📊 Municipality comparator**  
  Compare up to 3 municipalities with interactive charts: radar, bar, pie, and more.

- **🗺️ Indicator map**  
  Visualize education, housing, or employment levels per municipality on a map.

- **🔍 Search by minimum conditions**  
  Filter municipalities based on your minimum criteria for education, housing, or businesses.
""")

    st.markdown("### 🖼️ Image gallery")
    imagenes = {
        "Vista aérea de municipio": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
        "Calles y vida local": "https://images.unsplash.com/photo-1601597111524-2b12b6dd4290",
        "Entorno natural": "https://images.unsplash.com/photo-1503437313881-503a91226422"
    }
    opcion = st.selectbox("Select an image:", list(imagenes.keys()))
    st.image(imagenes[opcion], caption=opcion, use_container_width=True)

st.markdown("📌 *Data based on public sources and local statistics.*")
st.markdown("📊 *Developed by Andrea Almela, Anna Aparici and Sergi Martínez*")

# 1. Comparador de municipios
with tabs[1]:
    st.header("📊 Municipality Comparator")
    st.markdown("### 🧾 What can you do here?")

    st.markdown("""
Compare different municipalities in the Valencian Community by access to:
- 🏫 **Educational centers**
- 🏘️ **Available housing**
- 💼 **Registered companies**

All indicators are **normalized per 1000 inhabitants**, allowing fair comparison across differently sized municipalities.

The **opportunity index** is a composite metric weighted as follows:
- 40% education
- 30% housing
- 30% employment
""")


    municipios = df["municipio"].unique()
    seleccionados = st.multiselect("Select up to 3 municipalities to compare:", municipios, default=municipios[:2])

    if len(seleccionados) == 0:
        st.info("Please select at least one municipality to compare.")
    elif len(seleccionados) > 3:
        st.warning("You can only select up to 3 municipalities.")
    else:
        df_sel = df[df["municipio"].isin(seleccionados)]

        # --------------------------
        # Tabla de datos
        # --------------------------
        # Mostrar tabla con ratios
        st.subheader("📋 Indicadores por municipio")
        st.dataframe(df_sel.set_index("municipio"))

        # --- NUEVO: Aviso si hay municipios con < 1000 hab ---
        municipios_pequenos = df_sel[df_sel["Poblacion_Total"] < 1000]["municipio"].tolist()

        if municipios_pequenos:
            st.warning(f"⚠ The following municipalities have fewer than 1000 inhabitants, so ratios may be distorted: {', '.join(municipios_pequenos)}")

        # --- NUEVO: Tabla con valores absolutos ---
        st.markdown("### 🧾 Absolute values")
        st.markdown("The following shows the real values of each indicator for more context:")


        tabla_abs = df_sel[["municipio", "Poblacion_Total", "n_centros_total", "total_ofertas", "empresas_total"]]
        tabla_abs = tabla_abs.rename(columns={
            "Poblacion_Total": "Población",
            "n_centros_total": "Centros",
            "total_ofertas": "Viviendas ofertadas",
            "empresas_total": "Empresas"
        })
        st.dataframe(tabla_abs.set_index("municipio"))



        # -----------------------------
        # Gráfico de barras con opción de normalizar
        # -----------------------------
        # -----------------------------
        # Comparativa de indicadores
        # -----------------------------
        st.subheader("📊 Indicator comparison")

        ver_reales = st.checkbox("🔁 Show real values (not normalized)", value=False)

        df_grafico = df_sel.set_index("municipio")[["centros_por_1000hab", "viviendas_por_1000hab", "empresas_por_1000hab"]]

        if ver_reales:
            titulo = "Normalized indicator comparison (0–1)"
        else:
            df_grafico = df_grafico / df_grafico.max()  # normalización por columna
            titulo = "Indicator comparison (real values)"

        fig_bar = px.bar(df_grafico.reset_index(), x="municipio",
                        y=df_grafico.columns.tolist(),
                        barmode="group",
                        labels={"value": "Valor", "variable": "Indicador"},
                        title=titulo)
        st.plotly_chart(fig_bar)

        # -----------------------------
        # Indicadores individuales
        # -----------------------------
        st.markdown("### 📈 Individual indicators")
        st.markdown("View each indicator separately for more clarity:")

        for indicador in ["centros_por_1000hab", "viviendas_por_1000hab", "empresas_por_1000hab"]:
            fig = px.bar(df_sel, x="municipio", y=indicador,
                        title=indicador.replace("_", " ").capitalize())
            st.plotly_chart(fig)



        # -----------------------------
        # Radar chart (perfil relativo)
        # -----------------------------
        st.subheader("📈 Relative profile of municipalities (Radar Chart)")

        import plotly.graph_objects as go

        df_norm = df_sel.set_index("municipio")[["centros_por_1000hab", "viviendas_por_1000hab", "empresas_por_1000hab"]]
        df_norm = df_norm / df_norm.max()  # normalización local

        fig_radar = go.Figure()
        for municipio in df_norm.index:
            fig_radar.add_trace(go.Scatterpolar(
                r=df_norm.loc[municipio].values,
                theta=df_norm.columns,
                fill='toself',
                name=municipio
            ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True
        )
        st.plotly_chart(fig_radar)

        # -----------------------------
        # Pie charts normalizados por máximo global
        # -----------------------------
        st.subheader("🥧 Normalized relative distribution of indicators")

        st.markdown("""
        ℹ This chart shows the *relative* proportion of each indicator per municipality, 
*normalized with respect to the maximum value in the dataset*.
This avoids distortion caused by indicators with very large values (e.g., companies).
""")

        # Calcular máximos globales por cada indicador
        maximos = df[["centros_por_1000hab", "viviendas_por_1000hab", "empresas_por_1000hab"]].max()

        for _, row in df_sel.iterrows():
            municipio = row["municipio"]
            values = [
                row["centros_por_1000hab"] / maximos["centros_por_1000hab"],
                row["viviendas_por_1000hab"] / maximos["viviendas_por_1000hab"],
                row["empresas_por_1000hab"] / maximos["empresas_por_1000hab"]
            ]
            labels = ["Educación", "Vivienda", "Empleo"]
            
            fig_pie = px.pie(
                names=labels,
                values=values,
                title=municipio
            )
            st.plotly_chart(fig_pie)


        # -----------------------------
        # Índice de oportunidad
        # -----------------------------
        st.subheader("⭐ Opportunity index")
        fig_oportunidad = px.bar(df_sel, x="municipio", y="indice_oportunidad",
                                title="Comparación del índice de oportunidad")
        st.plotly_chart(fig_oportunidad)

        # -----------------------------
        # Scatter plot: viviendas vs empresas
        # -----------------------------
        st.subheader("📉 Housing vs companies relationship")
        fig_scatter = px.scatter(df_sel,
                                x="viviendas_por_1000hab",
                                y="empresas_por_1000hab",
                                color="municipio",
                                size="indice_oportunidad",
                                hover_name="municipio",
                                title="Relación entre viviendas y empresas")
        st.plotly_chart(fig_scatter)

    # -----------------------------
        # Resumen de resultados destacados
        # -----------------------------
        st.subheader("📌 Summary of results")

        mejor_oportunidad = df_sel.loc[df_sel["indice_oportunidad"].idxmax(), "municipio"]
        mas_centros = df_sel.loc[df_sel["centros_por_1000hab"].idxmax(), "municipio"]
        mas_viviendas = df_sel.loc[df_sel["viviendas_por_1000hab"].idxmax(), "municipio"]
        mas_empresas = df_sel.loc[df_sel["empresas_por_1000hab"].idxmax(), "municipio"]

        col1, col2 = st.columns(2)

        with col1:
            st.success(f"🥇 Highest opportunity index: **{mejor_oportunidad}**")
            st.info(f"🏫 Most educational centers per 1000 inhabitants: **{mas_centros}**")
        with col2:
            st.info(f"🏘️ Most housing offers per 1000 inhabitants: **{mas_viviendas}**")
            st.info(f"💼 Most companies per 1000 inhabitants: **{mas_empresas}**")

# 2. Mapa de indicadores
with tabs[2]:
    st.header("🗺️ Indicator Map")

    indicador = st.selectbox("Select an indicator for the map", [
        "centros_por_1000hab",
        "viviendas_por_1000hab",
        "empresas_por_1000hab",
        "indice_oportunidad"
    ])

    columnas_necesarias = ["lat", "lon", indicador]
    if all(col in df.columns for col in columnas_necesarias):
        df_mapa = df.dropna(subset=columnas_necesarias)

        min_val = df_mapa[indicador].min()
        max_val = df_mapa[indicador].max()

        view_state = pdk.ViewState(
            latitude=df_mapa["lat"].mean(),
            longitude=df_mapa["lon"].mean(),
            zoom=7,
            pitch=0
        )

        # Capa con color variable
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_mapa,
            get_position='[lon, lat]',
            get_radius=4000,
            get_fill_color=f"""[
                255 * ({indicador}) / {max_val},
                255 * (1 - ({indicador}) / {max_val}),
                100,
                180
            ]""",
            pickable=True
        )

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="road",  # fondo blanco
            tooltip={"text": "{municipio}\n" + indicador + ": {" + indicador + "}"}
        ))

        fig_legenda = go.Figure(go.Heatmap(
    z=[[min_val, max_val]],
    colorscale="RdYlGn",  # o "Viridis", "Bluered", etc.
    showscale=True,
    colorbar=dict(
        orientation="h",
        title=indicador,
        x=0.5,
        xanchor="center"
    )
))
        fig_legenda.update_layout(height=150, margin=dict(t=20, b=20))
        st.plotly_chart(fig_legenda)

    else:
        st.error("Missing required columns to generate the map.")

    


# 3. Buscador por condiciones
with tabs[4]:
    st.header("🔍 Search by minimum conditions")
    min_centros = st.slider("Minimum educational centers per 1000 inhabitants:", 0.0, 10.0, 1.0)
    min_viviendas = st.slider("Minimum housing per 1000 inhabitan" \
    "ts:", 0.0, 10.0, 1.0)
    min_empresas = st.slider("Minimum companies per 1000 inhabitants:", 0.0, 1000.0, 100.0)
    resultado = df[
        (df["centros_por_1000hab"] >= min_centros) &
        (df["viviendas_por_1000hab"] >= min_viviendas) &
        (df["empresas_por_1000hab"] >= min_empresas)
    ].sort_values("indice_oportunidad", ascending=False)

    st.dataframe(resultado)

    if not resultado.empty:
        st.success(f"{len(resultado)} cities meet your criteria.")


# 4. Mapa de centros educativos
with tabs[3]:
    st.header("🎓 Map of Educational Centers")

    # Selección de régimen
    regimenes = centros_df["regimen"].dropna().unique().tolist()
    regimen_seleccionado = st.selectbox("Select the center type:", sorted(regimenes))

    # Filtrar por régimen
    df_filtrado = centros_df[centros_df["regimen"] == regimen_seleccionado]

    # Crear resumen por localidad para vista general
    marcadores_localidad = (
        df_filtrado.groupby("localidad")
        .agg(
            n_centros=("DENOMINACION", "count"),
            lat=("LATITUD", "mean"),
            lon=("LONGITUD", "mean")
        )
        .reset_index()
    )

    # Selector de vista
    vista = st.radio("Select map detail level:", [
    "📍 General view by municipality",
    "🔎 Detailed view by center"
])

    # Asignar colores por régimen
    color_map = {
        "púb.": [0, 128, 0, 160],
        "priv. conc.": [255, 165, 0, 160],
        "priv.": [220, 20, 60, 160]
    }
    df_filtrado["color"] = df_filtrado["regimen"].apply(lambda r: color_map.get(r, [100, 100, 100, 160]))

    # Vista inicial del mapa
    view_state = pdk.ViewState(
        latitude=df_filtrado["LATITUD"].mean(),
        longitude=df_filtrado["LONGITUD"].mean(),
        zoom=7
    )

    # Capas del mapa
    if vista == "📍 Vista general por municipio":
        layer = pdk.Layer(
            "ColumnLayer",
            data=marcadores_localidad,
            get_position='[lon, lat]',
            get_elevation="n_centros",
            elevation_scale=300,
            radius=1000,
            get_fill_color='[255, 180, 0, 140]',
            pickable=True,
            auto_highlight=True
        )
        tooltip = {"text": "{localidad}\nCentros: {n_centros}"}
    else:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_filtrado,
            get_position='[LONGITUD, LATITUD]',
            get_radius=100,
            get_fill_color='color',
            pickable=True
        )
        tooltip = {"text": "{DENOMINACION}\nTipo: {tipo}"}

    # Mostrar el mapa
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="road"
    ))
