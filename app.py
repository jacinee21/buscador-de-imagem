import streamlit as st
from PIL import Image
import pytesseract
import os
import tempfile

try:
    import pytesseract
except ModuleNotFoundError:
    st.error("⚠️ O módulo pytesseract não está instalado. Vá até o menu '⚙️ Settings' no Streamlit Cloud e adicione 'pytesseract' no arquivo requirements.txt do seu repositório.")

st.set_page_config(page_title="Buscador de Imagens por Nome na Embalagem", layout="wide")
st.title("🔍 Buscador de Imagens a partir do nome na embalagem")

st.markdown("""
Este aplicativo permite:
- Fazer upload de fotos de medicamentos para extrair o nome com OCR.
- Fazer upload de um banco de imagens de referência.
- Buscar e exibir imagens do banco que contenham nomes parecidos.

✅ Use sempre que quiser: publique este arquivo no Streamlit Cloud ou rode localmente.
""")

ocr_temp = tempfile.TemporaryDirectory()
banco_temp = tempfile.TemporaryDirectory()

st.header("📸 Upload das fotos para leitura (embalagens)")
ocr_files = st.file_uploader("Envie fotos (JPEG, PNG, etc.)", type=['png','jpg','jpeg'], accept_multiple_files=True)

st.header("🗂️ Upload do banco de imagens para buscar")
banco_files = st.file_uploader("Envie imagens do banco", type=['png','jpg','jpeg'], accept_multiple_files=True)

if st.button("🔍 Rodar busca"):
    if ocr_files and banco_files:
        nomes_detectados = []
        banco_nomes = []

        st.subheader("📄 Nomes detectados:")

        for file in ocr_files:
            path = os.path.join(ocr_temp.name, file.name)
            with open(path, "wb") as f:
                f.write(file.read())
            img = Image.open(path)
            texto = pytesseract.image_to_string(img, lang='por')
            linhas = [linha.strip() for linha in texto.split("\n") if len(linha.strip()) > 3]
            nome = linhas[0] if linhas else "NOME_NAO_DETECTADO"
            nomes_detectados.append({"arquivo": file.name, "nome": nome})
            st.write(f"📦 **{file.name}** → {nome}")

        for file in banco_files:
            path = os.path.join(banco_temp.name, file.name)
            with open(path, "wb") as f:
                f.write(file.read())
            banco_nomes.append({"arquivo": file.name, "path": path})

        st.subheader("🖼️ Resultados encontrados:")
        for item in nomes_detectados:
            nome = item['nome'].lower()
            achou = False
            for b in banco_nomes:
                if nome in b['arquivo'].lower():
                    st.write(f"✅ **{item['nome']}** → {b['arquivo']}")
                    img = Image.open(b['path'])
                    st.image(img, caption=b['arquivo'], width=200)
                    achou = True
            if not achou:
                st.write(f"⚠️ Nenhum resultado para **{item['nome']}**")
    else:
        st.warning("Envie arquivos para OCR e banco de imagens.")

st.markdown("---")

st.markdown("""
📝 **Como criar e publicar seu repositório no GitHub e usar no Streamlit Cloud:**
1. Crie uma conta no [GitHub](https://github.com) se ainda não tiver.
2. Clique em **New repository**, escolha um nome (ex.: `buscador-imagens-medicamentos`) e crie o repositório.
3. No seu computador, salve este código como `app.py` e envie (upload) para o repositório.
4. Vá até [Streamlit Cloud](https://share.streamlit.io/) e clique em **New app**.
5. Conecte sua conta do GitHub, escolha o repositório e selecione o arquivo `app.py`.
6. Clique em Deploy. Seu app ficará online e poderá ser usado sempre.

⚙️ Se quiser, pode gerar token do GitHub e autorizar o Streamlit Cloud quando solicitado.
""")
