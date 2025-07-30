import streamlit as st
from PIL import Image
import os
import tempfile

# Verificação de dependências
try:
    import pytesseract
except ModuleNotFoundError:
    st.error("⚠️ O módulo pytesseract não está instalado. Vá até o menu '⚙️ Settings' no Streamlit Cloud e adicione 'pytesseract' no arquivo requirements.txt do seu repositório.")
    st.stop()

# Configuração da página
st.set_page_config(page_title="Buscador de Imagens por Nome na Embalagem", layout="wide")
st.title("🔍 Buscador de Imagens a partir do nome na embalagem")

st.markdown("""
Este aplicativo permite:
- Fazer upload de fotos de medicamentos para extrair o nome com OCR.
- Fazer upload de um banco de imagens de referência.
- Buscar e exibir imagens do banco que contenham nomes parecidos.

✅ Use sempre que quiser: publique este arquivo no Streamlit Cloud ou rode localmente.
""")

# Inicialização das variáveis de sessão
if 'ocr_temp' not in st.session_state:
    st.session_state.ocr_temp = tempfile.TemporaryDirectory()
if 'banco_temp' not in st.session_state:
    st.session_state.banco_temp = tempfile.TemporaryDirectory()

# Upload das fotos para OCR
st.header("📸 Upload das fotos para leitura (embalagens)")
ocr_files = st.file_uploader(
    "Envie fotos (JPEG, PNG, etc.)", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True,
    key="ocr_uploader"
)

# Upload do banco de imagens
st.header("🗂️ Upload do banco de imagens para buscar")
banco_files = st.file_uploader(
    "Envie imagens do banco", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True,
    key="banco_uploader"
)

# Função para processar OCR
def processar_ocr(file, temp_dir):
    """Processa uma imagem e extrai texto usando OCR"""
    try:
        path = os.path.join(temp_dir, file.name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        
        img = Image.open(path)
        texto = pytesseract.image_to_string(img, lang='por')
        linhas = [linha.strip() for linha in texto.split("\n") if len(linha.strip()) > 3]
        nome = linhas[0] if linhas else "NOME_NAO_DETECTADO"
        
        return {"arquivo": file.name, "nome": nome}
    except Exception as e:
        st.error(f"Erro ao processar {file.name}: {str(e)}")
        return {"arquivo": file.name, "nome": "ERRO_NO_PROCESSAMENTO"}

# Função para salvar imagens do banco
def salvar_imagem_banco(file, temp_dir):
    """Salva uma imagem do banco no diretório temporário"""
    try:
        path = os.path.join(temp_dir, file.name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        return {"arquivo": file.name, "path": path}
    except Exception as e:
        st.error(f"Erro ao salvar {file.name}: {str(e)}")
        return None

# Botão para executar a busca
if st.button("🔍 Rodar busca"):
    if ocr_files and banco_files:
        nomes_detectados = []
        banco_nomes = []
        
        # Processamento das imagens para OCR
        st.subheader("📄 Nomes detectados:")
        progress_bar = st.progress(0)
        
        for i, file in enumerate(ocr_files):
            resultado = processar_ocr(file, st.session_state.ocr_temp.name)
            nomes_detectados.append(resultado)
            st.write(f"📦 **{file.name}** → {resultado['nome']}")
            progress_bar.progress((i + 1) / len(ocr_files))
        
        # Processamento das imagens do banco
        st.subheader("🗂️ Preparando banco de imagens...")
        for file in banco_files:
            resultado = salvar_imagem_banco(file, st.session_state.banco_temp.name)
            if resultado:
                banco_nomes.append(resultado)
        
        # Busca por correspondências
        st.subheader("🖼️ Resultados encontrados:")
        
        for item in nomes_detectados:
            nome = item['nome'].lower()
            achou = False
            
            # Busca no nome do arquivo
            for b in banco_nomes:
                nome_arquivo = b['arquivo'].lower()
                
                # Busca por correspondência parcial
                if nome != "nome_nao_detectado" and nome != "erro_no_processamento":
                    # Divide o nome em palavras para busca mais flexível
                    palavras_nome = nome.split()
                    if any(palavra in nome_arquivo for palavra in palavras_nome if len(palavra) > 2):
                        st.write(f"✅ **{item['nome']}** → {b['arquivo']}")
                        try:
                            img = Image.open(b['path'])
                            st.image(img, caption=b['arquivo'], width=200)
                            achou = True
                        except Exception as e:
                            st.error(f"Erro ao exibir imagem {b['arquivo']}: {str(e)}")
            
            if not achou:
                st.write(f"⚠️ Nenhum resultado para **{item['nome']}**")
    
    else:
        st.warning("⚠️ Envie arquivos para OCR e banco de imagens antes de executar a busca.")

# Limpeza de cache (opcional)
if st.button("🗑️ Limpar cache de imagens"):
    if 'ocr_temp' in st.session_state:
        st.session_state.ocr_temp.cleanup()
        st.session_state.ocr_temp = tempfile.TemporaryDirectory()
    if 'banco_temp' in st.session_state:
        st.session_state.banco_temp.cleanup()
        st.session_state.banco_temp = tempfile.TemporaryDirectory()
    st.success("Cache limpo com sucesso!")

# Rodapé com instruções
st.markdown("---")
st.markdown("""
📝 **Como criar e publicar seu repositório no GitHub e usar no Streamlit Cloud:**

1. **Crie uma conta no GitHub** se ainda não tiver: [github.com](https://github.com)
2. **Novo repositório**: Clique em **New repository**, escolha um nome (ex.: `buscador-imagens-medicamentos`)
3. **Adicione os arquivos**:
   - Salve este código como `app.py`
   - Crie um arquivo `requirements.txt` com o conteúdo:
     ```
     streamlit
     Pillow
     pytesseract
     ```
4. **Deploy no Streamlit Cloud**:
   - Acesse [share.streamlit.io](https://share.streamlit.io/)
   - Clique em **New app**
   - Conecte sua conta do GitHub
   - Escolha o repositório e o arquivo `app.py`
   - Clique em **Deploy**

⚙️ **Nota importante**: Para usar pytesseract no Streamlit Cloud, você também pode precisar adicionar configurações específicas do sistema. Se encontrar problemas, consulte a documentação do Streamlit Cloud sobre dependências do sistema.
""")

# Informações técnicas
with st.expander("🔧 Informações técnicas"):
    st.write("""
    **Dependências necessárias:**
    - streamlit
    - Pillow (PIL)
    - pytesseract
    
    **Funcionalidades:**
    - OCR em português
    - Busca por correspondência parcial
    - Gerenciamento de arquivos temporários
    - Interface responsiva
    - Tratamento de erros
    """)
