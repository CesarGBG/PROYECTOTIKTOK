import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import re

st.title("🔍 Análisis Avanzado de Comentarios en TikTok")

# SUBIDA DE ARCHIVOS CSV
archivos = st.file_uploader("Sube uno o varios archivos CSV de comentarios", type="csv", accept_multiple_files=True)

if archivos:
    df_total = pd.concat([pd.read_csv(archivo, encoding='latin-1') for archivo in archivos], ignore_index=True)

    if 'text' not in df_total.columns or 'diggCount' not in df_total.columns:
        st.error("Asegúrate de que los archivos tengan las columnas 'text' y 'diggCount'.")
    else:
        # LIMPIEZA DE TEXTO
        def limpiar_texto(texto):
            texto = str(texto).lower()
            texto = re.sub(r"http\S+|www\S+|https\S+", '', texto)
            texto = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]", '', texto)
            return texto

        df_total['texto_limpio'] = df_total['text'].apply(limpiar_texto)

        # DETECCIÓN DE OFENSAS (por raíz)
        palabras_ofensivas = [
            "cerru", "feo", "bello", "guapo", "guapa", "bonita", "verde", "arbol", "fallout",
            "wall-e", "marte", "marrón", "indígena", "negro", "polvoru",
            "gatito", "cerruano", "portal esperanza", "perú debo ser un", "peru seria un",
            "perukistan", "perusalen", "mierdu", "piedru", "pueblo marrón",
            "ilegal plantar", "parte de europa", "robó toda la belleza", "comepaloma"
        ]

        def es_ofensivo(texto):
            return any(re.search(rf"\b{re.escape(p)}\w*\b", texto) for p in palabras_ofensivas)

        df_total['ofensivo'] = df_total['texto_limpio'].apply(es_ofensivo)

        # COMENTARIOS CON MÁS LIKES
        st.subheader("🔥 Comentarios con más likes")
        cantidad = st.slider("¿Cuántos comentarios quieres ver?", min_value=5, max_value=100, value=10)
        top_likes = df_total.sort_values(by="diggCount", ascending=False)
        st.write(top_likes[["text", "diggCount"]].head(cantidad))

        # NUBE DE PALABRAS
        st.subheader("☁️ Palabras más comunes")
        palabras_excluidas = set(STOPWORDS)
        adicionales = {
            "de", "la", "que", "el", "en", "y", "a", "los", "se", "del", "las", "por", "un", "para", "con", "no",
            "una", "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque",
            "esta", "entre", "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde",
            "quien", "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra", "otros",
            "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos", "qué", "unos", "yo", "otro",
            "otras", "otra", "él", "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos", "cual",
            "poco", "ella", "estar", "estas", "algunas", "algo", "nosotros", "mi", "mis", "tú", "te", "ti",
            "tu", "tus", "ellas", "nosotras", "vosotros", "vosotras", "os", "mío", "mía", "míos", "mías",
            "tuyo", "tuya", "tuyos", "tuyas", "suyo", "suya", "suyos", "suyas", "nuestro", "nuestra", "nuestros",
            "nuestras", "vuestro", "vuestra", "vuestros", "vuestras", "esos", "esas", "estoy", "estás",
            "está", "estamos", "estáis", "están", "esté", "estés", "estemos", "estéis", "estén"
        }
        palabras_excluidas.update(adicionales)

        todo_el_texto = ' '.join(df_total['texto_limpio'])
        nube = WordCloud(width=800, height=300, background_color='white', stopwords=palabras_excluidas).generate(todo_el_texto)
        st.image(nube.to_array())

        # FRECUENCIA DE PALABRAS OFENSIVAS (por coincidencia parcial)
        st.subheader("💬 Palabras ofensivas más frecuentes")
        texto_ofensivo = ' '.join(df_total[df_total["ofensivo"] == True]["texto_limpio"])

        frecuencia = {}
        for palabra in palabras_ofensivas:
            coincidencias = re.findall(rf"\b{re.escape(palabra)}\w*\b", texto_ofensivo)
            frecuencia[palabra] = len(coincidencias)

        df_frecuencia = pd.DataFrame(list(frecuencia.items()), columns=["Palabra Ofensiva", "Frecuencia"])
        df_frecuencia = df_frecuencia[df_frecuencia["Frecuencia"] > 0].sort_values(by="Frecuencia", ascending=False)

        st.dataframe(df_frecuencia)

        if not df_frecuencia.empty:
            st.bar_chart(df_frecuencia.set_index("Palabra Ofensiva"))

        # PROPORCIÓN DE COMENTARIOS OFENSIVOS
        st.subheader("📊 Proporción de comentarios ofensivos")
        conteo_ofensivo = df_total['ofensivo'].value_counts()
        st.bar_chart(conteo_ofensivo.rename({True: "Ofensivo", False: "No Ofensivo"}))




   

