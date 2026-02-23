import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime
import re
import os

# 1. Configuração inicial
st.set_page_config(page_title="Sistema New Post", page_icon="📦")

# --- FUNÇÃO DE GERAÇÃO DE PDF ---
def gerar_pdf(dados_lista):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    
    m_x = 30
    h_bloco = 255
    espac = 15
    y_ini = altura - 30
    
    # Tentativa de encontrar o logo com diferentes nomes possíveis
    caminhos_possiveis = ["logo.png.jpeg", "logo.png", "logo.jpeg", "logo.jpg"]
    logo_path = None
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            logo_path = caminho
            break

    for i, dados in enumerate(dados_lista):
        if i > 0 and i % 3 == 0:
            c.showPage()
            y_ini = altura - 30
            
        p_y = y_ini - ((i % 3) * (h_bloco + espac))
        
        # Moldura externa
        c.setLineWidth(1.5)
        c.rect(m_x, p_y - h_bloco, largura - 60, h_bloco)
        
        # Linhas do cabeçalho
        c.setLineWidth(1)
        c.line(m_x, p_y - 45, largura - 30, p_y - 45) 
        c.line(largura - 160, p_y, largura - 160, p_y - 45) 
        
        # --- INSERÇÃO DO LOGO CORRIGIDA ---
        if logo_path:
            try:
                img = ImageReader(logo_path)
                # Ajuste de posição para o canto superior esquerdo do bloco
                c.drawImage(img, m_x + 10, p_y - 38, width=60, height=30, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                # Se der erro na leitura da imagem, coloca o texto
                c.setFont("Helvetica-Bold", 12)
                c.drawString(m_x + 10, p_y - 30, "NEW POST")
        else:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(m_x + 10, p_y - 30, "NEW POST")
        
        # Títulos e Protocolo
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(largura/2 + 20, p_y - 25, "PROTOCOLO DE DEVOLUÇÃO")
        c.setFont("Helvetica", 9)
        c.drawString(largura - 155, p_y - 15, "PROTOCOLO Nº:")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(largura - 130, p_y - 32, f"MG-{str(dados.get('PROTOCOLO', ''))}")
        
        # Dados do Formulário
        c.setFont("Helvetica", 10)
        c.drawString(m_x + 5, p_y - 65, "CLIENTE:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(m_x + 60, p_y - 64, str(dados.get('NOME', '')))
        c.line(m_x + 55, p_y - 67, largura - 40, p_y - 67)
        
        c.drawString(m_x + 5, p_y - 105, "Nº NOTA FISCAL:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(m_x + 95, p_y - 104, str(dados.get('NOTA FISCAL', '')))
        c.line(m_x + 90, p_y - 107, largura - 320, p_y - 107)
        
        c.drawString(largura - 310, p_y - 105, "Nº CTE:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(largura - 265, p_y - 104, str(dados.get('CTE', '')))
        c.line(largura - 270, p_y - 107, largura - 40, p_y - 107)
        
        data_at = datetime.now().strftime("%d/%m/%Y")
        c.drawString(m_x + 5, p_y - 145, "DATA:")
        c.drawString(m_x + 45, p_y - 144, data_at)
        c.line(m_x + 40, p_y - 147, largura - 320, p_y - 147)
        
        c.drawString(largura - 310, p_y - 145, "Nº PROTOCOLO CLIENTE:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(largura - 175, p_y - 144, str(dados.get('PEDIDO', '')))
        c.line(largura - 180, p_y - 147, largura - 40, p_y - 147)
        
        # Rodapé e Assinaturas
        c.setFont("Helvetica", 10)
        c.drawString(m_x + 5, p_y - 185, "DADOS DO RECEBEDOR:")
        c.line(m_x + 125, p_y - 187, largura - 40, p_y - 187)
        c.setFont("Helvetica", 7)
        c.drawCentredString(largura/2 + 40, p_y - 195, "Nome legível e RG")
        
        c.setFont("Helvetica", 10)
        c.drawString(m_x + 5, p_y - 230, "ASSINATURA:")
        c.line(m_x + 80, p_y - 232, largura - 40, p_y - 232)

    c.save()
    buffer.seek(0)
    return buffer

# --- LOGICA DA INTERFACE ---
st.title("📦 Gerador de Protocolos")

txt = st.text_area("Insira as NFs abaixo (uma por linha ou separadas por vírgula):", height=150)

if st.button("Gerar PDF"):
    if txt:
        try:
            S_ID = "1f_NDUAezh4g0ztyHVUO_t33QxGai9TYcWOD-IAoPcuE"
            URL = f"https://docs.google.com/spreadsheets/d/{S_ID}/export?format=csv&gid=0"
            
            nfs = [n.strip() for n in re.split(r'[,\s\n]+', txt) if n.strip()]
            df = pd.read_csv(URL)
            df['NOTA FISCAL'] = df['NOTA FISCAL'].astype(str).str.strip()
            res = df[df['NOTA FISCAL'].isin(nfs)].to_dict('records')
            
            if res:
                pdf = gerar_pdf(res)
                st.success(f"{len(res)} protocolos gerados!")
                st.download_button("📥 Baixar PDF", pdf, "protocolos.pdf", "application/pdf")
            else:
                st.error("Nenhuma NF encontrada na planilha.")
        except Exception as e:
            st.error(f"Erro técnico: {e}")
    else:
        st.warning("Por favor, digite uma NF.")
