import streamlit as st
import matplotlib.pyplot as plt
from skimage import io, color, measure
from skimage.filters import threshold_otsu
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
import requests

# Parámetros iniciales
pixel_to_meter_ratio = 0.1  # Escala: 1 píxel = 0.1 metros
rect_width_m = 5  # Ancho de cada rectángulo en metros
rect_height_m = 3  # Altura de cada rectángulo en metros

# Parámetros de la API
api_key = "AIzaSyDDt1fiH2cTopWMX_qfg50nm0taKg4egV4"
url_base = "https://maps.googleapis.com/maps/api/staticmap"

# Inicializar el estado en Streamlit
if "top_regions" not in st.session_state:
    st.session_state.top_regions = None
    st.session_state.image = None
    st.session_state.selected_techo = None

# Función para obtener la imagen de Google Maps según coordenadas
def obtener_imagen_de_google_maps(lat, lng, zoom, ancho, alto):
    try:
        params = {
            "key": api_key,
            "center": f"{lat},{lng}",
            "zoom": zoom,
            "size": f"{ancho}x{alto}",
            "maptype": "satellite",
            "scale": 2
        }
        respuesta = requests.get(url_base, params=params)
        respuesta.raise_for_status()
        return io.imread(BytesIO(respuesta.content))
    except Exception as e:
        st.error(f"Error al obtener la imagen: {e}")
        return None

# Función para procesar la imagen y calcular áreas
def process_image(image, top_n=5):
    try:
        gray_image = color.rgb2gray(image / 255.0)
        thresh = threshold_otsu(gray_image)
        binary_image = gray_image > thresh

        labeled_image = measure.label(binary_image)
        regions = measure.regionprops(labeled_image)

        filtered_regions = [
            region for region in regions
            if region.area > 100
        ]

        areas_table = sorted(
            [
                (idx, region, region.area * (pixel_to_meter_ratio ** 2))
                for idx, region in enumerate(filtered_regions, start=1)
            ],
            key=lambda x: x[2], reverse=True
        )

        return areas_table[:top_n], binary_image, filtered_regions
    except Exception as e:
        st.error(f"Error al procesar la imagen: {e}")
        return None, None, None

# Función para organizar figuras geométricas
def arrange_figures(region, rect_width, rect_height, pattern):
    try:
        positions = []
        minr, minc, maxr, maxc = region.bbox
        if pattern == "H":
            group_positions = [
                (0, 0), (0, rect_height), (rect_width, rect_height),
                (2 * rect_width, 0), (2 * rect_width, rect_height)
            ]
        elif pattern == "L":
            group_positions = [
                (0, 0), (0, rect_height), (0, 2 * rect_height),
                (rect_width, 2 * rect_height)
            ]
        else:  # "Rectángulo simple"
            group_positions = [(0, 0)]

        for x, y in group_positions:
            pixel_x = int(x / pixel_to_meter_ratio) + minc
            pixel_y = int(y / pixel_to_meter_ratio) + minr
            positions.append((pixel_x, pixel_y))

        return positions
    except Exception as e:
        st.error(f"Error al organizar figuras: {e}")
        return []

# Configuración de la interfaz en Streamlit
st.title("Ajuste de Figuras en Techos")
st.sidebar.header("Configuración")

# Parámetros de la imagen
lat = st.sidebar.number_input("Latitud", value=-34.6074603)
lng = st.sidebar.number_input("Longitud", value=-58.4112768)
zoom = st.sidebar.slider("Zoom", min_value=16, max_value=20, value=18)
ancho = st.sidebar.slider("Ancho de la imagen", min_value=640, max_value=1280, value=640)
alto = st.sidebar.slider("Alto de la imagen", min_value=480, max_value=960, value=480)

uploaded_file = st.sidebar.file_uploader("Cargar una imagen de techos", type=["png", "jpg", "jpeg"])
pattern = st.sidebar.selectbox("Seleccionar el patrón geométrico", ["H", "L", "Rectángulo simple"])
top_n = st.sidebar.slider("Número de techos a considerar", min_value=1, max_value=10, value=5)

if st.button("Iniciar"):
    if uploaded_file:
        image = io.imread(uploaded_file)
    else:
        image = obtener_imagen_de_google_maps(lat, lng, zoom, ancho, alto)

    if image is None:
        st.error("No se pudo cargar la imagen.")
    else:
        top_regions, binary_image, filtered_regions = process_image(image, top_n)

        if not top_regions:
            st.error("No se detectaron techos significativos en la imagen.")
        else:
            st.session_state.top_regions = top_regions
            st.session_state.image = image

if st.session_state.top_regions:
    top_regions = st.session_state.top_regions
    image = st.session_state.image

    st.subheader("Imagen Original y Áreas Detectadas")
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(image)

    for idx, region, area_m2 in top_regions:
        minr, minc, maxr, maxc = region.bbox
        rect = plt.Rectangle((minc, minr), maxc - minc, maxr - minr,
                             edgecolor='red', facecolor='none', linewidth=2)
        ax.add_patch(rect)
        centroid = region.centroid
        ax.text(centroid[1], centroid[0], str(idx), color='yellow', fontsize=12,
                ha='center', bbox=dict(facecolor='black', alpha=0.5))

    ax.set_title("Techos Detectados")
    ax.axis('off')
    st.pyplot(fig)

    # Generar opciones para el selectbox
    opciones_techo = [f"Techo {idx}" for idx, _, _ in top_regions]

    # Mostrar el selectbox
    techo_elegido = st.selectbox(
        "Seleccione un techo para análisis detallado",
        options=opciones_techo,
        key="selected_techo"
    )

    # Depurar el valor seleccionado y la lista
    st.write(f"Techo elegido: {techo_elegido}")
    st.write(f"Lista de techos: {opciones_techo}")

    if st.session_state.selected_techo:
        # Extraer el índice seleccionado
        try:
            techo_idx = opciones_techo.index(techo_elegido)
            st.write(f"Índice seleccionado: {techo_idx}")

            if 0 <= techo_idx < len(top_regions):
                _, region, area_m2 = top_regions[techo_idx]
                st.subheader(f"Análisis del {techo_elegido}")
                st.write(f"Área total: {area_m2:.2f} m²")

                # Generar la distribución de figuras geométricas
                posiciones = arrange_figures(region, rect_width_m, rect_height_m, pattern)
                fig = go.Figure()

                for x, y in posiciones:
                    fig.add_trace(go.Scatter(
                        x=[x, x + rect_width_m, x + rect_width_m, x, x],
                        y=[y, y, y + rect_height_m, y + rect_height_m, y],
                        mode='lines',
                        fill='toself',
                        line=dict(color='blue'),
                        name=f'Rectángulo en {pattern}'
                    ))

                fig.update_layout(
                    title=f"Ajuste de figuras en patrón '{pattern}' para {techo_elegido}",
                    xaxis=dict(title="Coordenada X (m)"),
                    yaxis=dict(title="Coordenada Y (m)", scaleanchor="x", scaleratio=1),
                    showlegend=False,
                    height=600, width=800
                )
                st.plotly_chart(fig)
            else:
                st.error("El índice seleccionado está fuera del rango válido.")
        except Exception as e:
            st.error(f"Error al procesar el techo seleccionado: {e}")
