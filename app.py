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
- Fazer upload de um arquivo de texto (.txt) com nomes de referência para comparar.
- Verificar se os nomes detectados nas imagens correspondem aos nomes do banco de texto.

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

# Upload do banco de nomes (arquivo de texto)
st.header("🗂️ Upload do banco de nomes para comparar")
banco_file = st.file_uploader(
    "Envie um arquivo de texto (.txt) com os nomes para comparar (um nome por linha)", 
    type=['txt'], 
    accept_multiple_files=False,
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

# Função para carregar nomes do arquivo de texto
def carregar_banco_nomes(file):
    """Carrega os nomes do arquivo de texto"""
    try:
        # Lê o conteúdo do arquivo
        content = file.getvalue().decode('utf-8')
        # Divide em linhas e remove espaços em branco
        nomes = [linha.strip() for linha in content.split('\n') if linha.strip()]
        return nomes
    except Exception as e:
        st.error(f"Erro ao carregar arquivo de nomes: {str(e)}")
        return []

# Botão para executar a busca
if st.button("🔍 Rodar busca"):
    if ocr_files and banco_file:
        nomes_detectados = []
        banco_nomes = []
        
        # Processamento das imagens para OCR
        st.subheader("📄 Nomes detectados nas imagens:")
        progress_bar = st.progress(0)
        
        for i, file in enumerate(ocr_files):
            resultado = processar_ocr(file, st.session_state.ocr_temp.name)
            nomes_detectados.append(resultado)
            st.write(f"📦 **{file.name}** → {resultado['nome']}")
            progress_bar.progress((i + 1) / len(ocr_files))
        
        # Carregamento do banco de nomes
        st.subheader("📋 Carregando banco de nomes...")
        banco_nomes = carregar_banco_nomes(banco_file)
        
        if banco_nomes:
            st.write(f"📊 **{len(banco_nomes)} nomes** carregados do banco:")
            # Mostra os primeiros 10 nomes como exemplo
            nomes_exemplo = banco_nomes[:10]
            st.write(", ".join(nomes_exemplo) + ("..." if len(banco_nomes) > 10 else ""))
        else:
            st.error("❌ Nenhum nome foi encontrado no arquivo de texto.")
            st.stop()
        
        # Busca por correspondências
        st.subheader("🖼️ Resultados da comparação:")
        
        for item in nomes_detectados:
            nome_detectado = item['nome'].lower()
            achou = False
            nomes_encontrados = []
            
            if nome_detectado not in ["nome_nao_detectado", "erro_no_processamento"]:
                # Busca por correspondências no banco de nomes
                for nome_banco in banco_nomes:
                    nome_banco_lower = nome_banco.lower()
                    
                    # Verifica se há correspondência (busca bidirecional)
                    palavras_detectado = nome_detectado.split()
                    palavras_banco = nome_banco_lower.split()
                    
                    # Verifica se alguma palavra do nome detectado está no nome do banco
                    for palavra in palavras_detectado:
                        if len(palavra) > 2 and palavra in nome_banco_lower:
                            nomes_encontrados.append(nome_banco)
                            achou = True
                            break
                    
                    # Verifica se alguma palavra do banco está no nome detectado
                    if not achou:
                        for palavra in palavras_banco:
                            if len(palavra) > 2 and palavra in nome_detectado:
                                nomes_encontrados.append(nome_banco)
                                achou = True
                                break
            
            # Exibe resultados
            if achou:
                st.write(f"✅ **{item['arquivo']}** (detectou: '{item['nome']}')")
                st.write(f"   🎯 **Correspondências encontradas:** {', '.join(set(nomes_encontrados))}")
            else:
                st.write(f"⚠️ **{item['arquivo']}** (detectou: '{item['nome']}') → Nenhuma correspondência no banco")
    
    else:
        st.warning("⚠️ Envie arquivos de imagem para OCR e um arquivo de texto com os nomes antes de executar a busca.")

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
