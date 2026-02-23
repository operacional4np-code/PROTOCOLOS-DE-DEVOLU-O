import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from datetime import datetime
import re

# --- CONFIGURAÇÃO DA PLANILHA ---
SHEET_ID = "1f_NDUAezh4g0ztyHVUO_t33QxGai9TYcWOD-IAoPcuE"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

def gerar_pdf(dados_lista):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    
    # Parâmetros de layout para bater com a imagem
    margem_x = 30
    altura_bloco = 255
    espacamento = 15
    y_inicial = altura - 30
    
    for i, dados in enumerate(dados_lista):
        # Gerencia nova página a cada 3 protocolos
        if i > 0 and i % 3 == 0:
            c.showPage()
            y_inicial = altura - 30
            
        pos_y = y_inicial - ((i % 3) * (altura_bloco + espacamento))
        
        # 1. Moldura externa grossa
        c.setLineWidth(1.5)
        c.rect(margem_x, pos_y - altura_bloco, largura - 60, altura_bloco)
        
        # 2. Cabeçalho (Linhas horizontais e verticais)
        c.setLineWidth(1)
        c.line(margem_x, pos_y - 45, largura - 30, pos_y - 45) # Linha horizontal do topo
        c.line(largura - 160, pos_y, largura - 160, pos_y - 45) # Linha vertical do protocolo
        
        # Logo e Títulos
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margem_x + 8, pos_y - 28, "new post") 
        
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(largura/2, pos_y - 25, "PROTOCOLO DE DEVOLUÇÃO")
        
        c.setFont("Helvetica", 9)
        c.drawString(largura - 155, pos_y - 15, "PROTOCOLO Nº:")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(largura - 130, pos_y - 32, f"MG-{dados.get('PROTOCOLO', '')}")
        
        # 3. Campos de Dados (Posicionados exatamente sobre as linhas da imagem)
        c.setFont("Helvetica", 10)
        
        # Cliente
        c.drawString(margem_x + 5, pos_y - 65, "CLIENTE:")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margem_x + 60, pos_y - 64, str(dados.get('NOME', '')))
        c.line(margem_x + 55, pos_y - 67, largura - 40, pos_y - 67) # Linha do Cliente
        
        # NF e CTE
        c.setFont("Helvetica", 10)
        c.drawString(margem_x + 5, pos_y - 105, "Nº NOTA FISCAL:")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margem_x + 95, pos_y - 104, str(dados.get('NOTA FISCAL', '')))
        c.line(margem_x + 90, pos_y - 107, largura - 320, pos_y - 107)
        
        c.setFont("Helvetica", 10)
        c.drawString(largura - 310, pos_y - 105, "Nº CTE:")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(largura - 265, pos_y - 104, str(dados.get('CTE', '')))
        c.line(largura - 270, pos_y - 107, largura - 40, pos_y - 107)
        
        # Data e Protocolo Cliente (Pedido)
        c.setFont("Helvetica", 10)
        data_atual = datetime.now().strftime("%d/%m/%Y")
        c.drawString(margem_x + 5, pos_y - 145, "DATA:")
        c.drawString(margem_x + 45, pos_y - 144, data_atual)
        c.line(margem_x + 40, pos_y - 147, largura - 320, pos_y - 147)
        
        c.drawString(largura - 310, pos_y - 145, "Nº PROTOCOLO CLIENTE:")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(largura - 175, pos_y - 144, str(dados.get('PEDIDO', '')))
        c.line(largura - 180, pos_y - 147, largura - 40, pos_y - 147)
        
        # 4. Rodapé de Assinatura
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

# --- INTERFACE ---
st.set_page_config(page_title="Expedição New Post", page_icon="📝")

st.title("📋 Gerador de Protocolos Múltiplos")
st.write("Busque várias NFs de uma vez separando-as por **vírgula** ou **espaço**.")

# Input melhorado
entrada = st.text_area("Insira as Notas Fiscais:", placeholder="Ex: 1542, 1890, 2100")

if st.button("Gerar Todos os Protocolos"):
    if entrada:
        try:
            # 1. Limpeza do Input (converte "123, 456 789" em ['123', '456', '789'])
            lista_nfs = re.split(r'[,\s]+', entrada.strip())
            
            # 2. Carregar Planilha
            df = pd.read_csv(SHEET_URL)
            df['NOTA FISCAL'] = df['NOTA FISCAL'].astype(str).str.strip()
            
            # 3. Filtrar Dados
            resultados = df[df['NOTA FISCAL'].isin(lista_nfs)].to_dict('records')
            
            if resultados:
                pdf_output = gerar_pdf(resultados)
                st.success(f"Encontrados {len(resultados)} de {len(lista_nfs)} protocolos!")
                
                st.download_button(
                    label="💾 Baixar Arquivo PDF Único",
                    data=pdf_output,
                    file_name="protocolos_devolucao.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Nenhuma das Notas Fiscais foi encontrada na planilha.")
        except Exception as e:
            st.error(f"Erro técnico: {e}")
    else:
        st.warning("Digite ao menos um número de nota fiscal.")
