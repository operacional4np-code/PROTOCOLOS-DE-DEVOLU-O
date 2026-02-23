import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from datetime import datetime

# --- CONFIGURAÇÃO DA PLANILHA ---
# Substituímos o link de edição pelo link de exportação direta para CSV
SHEET_ID = "1f_NDUAezh4g0ztyHVUO_t33QxGai9TYcWOD-IAoPcuE"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

def gerar_pdf(dados_lista):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    
    # Configurações de layout (ajustado para 3 vias por página)
    margem_x = 30
    altura_bloco = 250
    espacamento = 20
    y_inicial = altura - 40
    
    for i, dados in enumerate(dados_lista):
        if i > 0 and i % 3 == 0:
            c.showPage() # Cria uma nova página a cada 3 protocolos
            y_inicial = altura - 40
            
        pos_y = y_inicial - ((i % 3) * (altura_bloco + espacamento))
        
        # Desenho da moldura
        c.setLineWidth(1)
        c.rect(margem_x, pos_y - altura_bloco, largura - 60, altura_bloco)
        
        # Cabeçalho
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margem_x + 10, pos_y - 25, "NEW POST")
        c.drawCentredString(largura/2, pos_y - 25, "PROTOCOLO DE DEVOLUÇÃO")
        
        c.setFont("Helvetica", 9)
        c.drawString(largura - 150, pos_y - 15, "PROTOCOLO Nº:")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(largura - 150, pos_y - 30, f"MG-{dados.get('PROTOCOLO', '---')}")
        
        # Linhas de dados preenchidas automaticamente
        c.setFont("Helvetica", 10)
        
        # Cliente
        c.drawString(margem_x + 10, pos_y - 60, f"CLIENTE: {dados.get('NOME', '')}")
        c.line(margem_x + 60, pos_y - 62, largura - 40, pos_y - 62)
        
        # NF e CTE
        c.drawString(margem_x + 10, pos_y - 100, f"Nº NOTA FISCAL: {dados.get('NOTA FISCAL', '')}")
        c.line(margem_x + 95, pos_y - 102, largura - 300, pos_y - 102)
        
        c.drawString(largura - 290, pos_y - 100, f"Nº CTE: {dados.get('CTE', '')}")
        c.line(largura - 250, pos_y - 102, largura - 40, pos_y - 102)
        
        # Data e Pedido
        data_str = datetime.now().strftime("%d/%m/%Y")
        c.drawString(margem_x + 10, pos_y - 140, f"DATA: {data_str}")
        c.line(margem_x + 45, pos_y - 142, largura - 300, pos_y - 142)
        
        c.drawString(largura - 290, pos_y - 140, f"Nº PEDIDO: {dados.get('PEDIDO', '')}")
        c.line(largura - 235, pos_y - 142, largura - 40, pos_y - 142)
        
        # Assinaturas (conforme seu modelo)
        c.drawString(margem_x + 10, pos_y - 180, "DADOS DO RECEBEDOR:")
        c.line(margem_x + 130, pos_y - 182, largura - 40, pos_y - 182)
        c.setFont("Helvetica", 7)
        c.drawCentredString(largura/2 + 50, pos_y - 190, "Nome legível e RG")
        
        c.setFont("Helvetica", 10)
        c.drawString(margem_x + 10, pos_y - 220, "ASSINATURA:")
        c.line(margem_x + 85, pos_y - 222, largura - 40, pos_y - 222)

    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Sistema New Post", page_icon="📦")

st.title("📦 Gerador de Protocolos")
st.info("Insira a Nota Fiscal abaixo. O sistema buscará os dados na planilha automaticamente.")

nf_input = st.text_input("Digite o número da Nota Fiscal:")

if nf_input:
    try:
        # Lendo a planilha do Google Sheets via Pandas
        df = pd.read_csv(SHEET_URL)
        
        # Limpeza de dados (converte tudo para string para evitar erros de busca)
        df['NOTA FISCAL'] = df['NOTA FISCAL'].astype(str).str.strip()
        
        # Busca a NF
        resultado = df[df['NOTA FISCAL'] == nf_input.strip()]
        
        if not resultado.empty:
            dados_encontrados = resultado.to_dict('records')
            pdf = gerar_pdf(dados_encontrados)
            
            st.success(f"✅ Protocolo para NF {nf_input} gerado com sucesso!")
            
            st.download_button(
                label="📥 Baixar Protocolo PDF",
                data=pdf,
                file_name=f"Protocolo_{nf_input}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("⚠️ Nota Fiscal não encontrada na base de dados.")
            
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
