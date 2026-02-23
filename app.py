import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime
import re
import os

# --- CONFIGURAÇÃO DA PLANILHA ---
SHEET_ID = "1f_NDUAezh4g0ztyHVUO_t33QxGai9TYcWOD-IAoPcuE"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

def gerar_pdf(dados_lista):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    
    margem_x = 30
    altura_bloco = 255
    espacamento = 15
    y_inicial = altura - 30
    
    # Nome do arquivo de logo que deve estar no GitHub
    logo_path = "logo.png.jpeg" 

    for i, dados in enumerate(dados_lista):
        if i > 0 and i % 3 == 0:
            c.showPage()
            y_inicial = altura - 30
            
        pos_y = y_inicial - ((i % 3) * (altura_bloco + espacamento))
        
        # Moldura externa
        c.setLineWidth(1.5)
        c.rect(margem_x, pos_y - altura_bloco, largura - 60, altura_bloco)
        
        # Linhas horizontais e verticais do cabeçalho
        c.setLineWidth(1)
        c.line(margem_x, pos_y - 45, largura - 30, pos_y - 45) 
        c.line(largura - 160, pos_y, largura - 160, pos_y - 45) 
        
        # --- LOGO ---
        if os.path.exists(logo_path):
            try:
                logo = ImageReader(logo_path)
                c.drawImage(logo, margem_x + 5, pos_y - 40, width=65, height=35, preserveAspectRatio=True, mask='auto')
            except:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(margem_x + 10, pos_y - 30, "NEW POST")
        else:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margem_x + 10, pos_y - 30, "NEW POST")
        
        # Título Central
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(largura/2 + 20, pos_y - 25, "PROTOCOLO DE DEVOLUÇÃO")
        
        # Protocolo MG
        c.setFont("Helvetica", 9)
        c.drawString(largura - 155, pos_y - 15, "PROTOCOLO Nº:")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(largura - 130, pos_y - 32, f"MG-{str(dados.get('PROTOCOLO', ''))}")
        
        # --- CAMPOS DE DADOS ---
        c.setFont("Helvetica", 10)
        
        # Cliente
        c.drawString(margem_x + 5, pos_y - 65, "CLIENTE:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_x + 60, pos_y - 64, str(dados.get('NOME', '')))
        c.line(margem_x + 55, pos_y - 67, largura - 40, pos_y - 67)
        
        # NF e CTE
        c.setFont("Helvetica", 10)
        c.drawString(margem_x + 5, pos_y - 105, "Nº NOTA FISCAL:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_x + 95, pos_y - 104, str(dados.get('NOTA FISCAL', '')))
        c.line(margem_x + 90, pos_y - 107, largura - 320, pos_y - 107)
        
        c.setFont("Helvetica", 10)
        c.drawString(largura - 310, pos_y - 105, "Nº CTE:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(largura - 265, pos_y - 104, str(dados.get('CTE', '')))
        c.line(largura - 270, pos_y - 107, largura - 40, pos_y - 107)
        
        # Data e Pedido (N. PROTOCOLO CLIENTE)
        data_atual = datetime.now().strftime("%d/%m/%Y")
        c.setFont("Helvetica", 10)
        c.drawString(margem_x + 5, pos_y - 145, "DATA:")
        c.drawString(margem_x + 45, pos_y - 144, data_atual)
        c.line(margem_x + 40, pos_y - 147, largura - 320, pos_y - 147)
        
        c.drawString(largura - 310, pos_y - 145, "Nº PROTOCOLO CLIENTE:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(largura - 175, pos_y - 144, str(dados.get('PEDIDO', '')))
        c.line(largura - 180, pos_y - 147, largura - 40, pos_y - 147)
        
        # Rodapé e Assinaturas
        c.setFont("Helvetica", 10)
        c.drawString(margem_x + 5, pos_y - 185, "DADOS DO RECEBEDOR:")
        c.line(margem_x + 125, pos_y - 187, largura - 40, pos_y - 187)
        c.setFont("Helvetica", 7)
        c.drawCentredString(largura/2 + 40, pos_y - 195, "Nome legível e RG")
        
        c.setFont("Helvetica", 10)
        c.drawString(margem_x + 5, pos_y - 230, "ASSINATURA:")
        c.line(margem_x + 80, pos_y - 232, largura - 40, pos_y - 232)

    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE STREAMLIT ---
st.set_page_
