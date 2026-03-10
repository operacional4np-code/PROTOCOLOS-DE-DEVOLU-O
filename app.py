import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import re
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
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
    
    caminhos_possiveis = ["logo.png.jpeg", "logo.png", "logo.jpeg", "logo.jpg"]
    logo_path = next((f for f in caminhos_possiveis if os.path.exists(f)), None)

    for i, dados in enumerate(dados_lista):
        if i > 0 and i % 3 == 0:
            c.showPage()
            y_ini = altura - 30
            
        p_y = y_ini - ((i % 3) * (h_bloco + espac))
        
        # Moldura
        c.setLineWidth(1.5)
        c.rect(m_x, p_y - h_bloco, largura - 60, h_bloco)
        c.setLineWidth(1)
        c.line(m_x, p_y - 45, largura - 30, p_y - 45) 
        c.line(largura - 160, p_y, largura - 160, p_y - 45) 
        
        # Logo
        if logo_path:
            try:
                img = ImageReader(logo_path)
                c.drawImage(img, m_x + 10, p_y - 38, width=60, height=30, preserveAspectRatio=True, mask='auto')
            except:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(m_x + 10, p_y - 30, "NEW POST")
        else:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(m_x + 10, p_y - 30, "NEW POST")
        
        # Lógica de Prefixo e Destino
        destino = str(dados.get('DESTINO', '')).upper()
        protocolo_fonte = str(dados.get('PROTOCOLO_FONTE', ''))
        prefixo = "PE-" if "CABO DE SANTO AGOSTINHO" in destino else "MG-"

        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(largura/2 + 20, p_y - 25, "PROTOCOLO DE DEVOLUÇÃO")
        
        c.setFont("Helvetica", 9)
        c.drawString(largura - 155, p_y - 15, "PROTOCOLO Nº:")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(largura - 130, p_y - 32, f"{prefixo}") 
        
        # Dados Cliente
        c.setFont("Helvetica", 10)
        c.drawString(m_x + 5, p_y - 65, "CLIENTE:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(m_x + 60, p_y - 64, str(dados.get('NOME', '')))
        c.line(m_x + 55, p_y - 67, largura - 40, p_y - 67)
        
        # --- AJUSTE DE NOTAS FISCAIS ---
        notas_texto = str(dados.get('NOTA FISCAL', ''))
        c.setFont("Helvetica", 10)
        c.drawString(m_x + 5, p_y - 105, "Nº NOTA FISCAL:")
        
        # Se houver muitas notas, diminui a fonte para não bater no CTE
        tamanho_fonte_notas = 10 if len(notas_texto) < 25 else 8
        c.setFont("Helvetica-Bold", tamanho_fonte_notas)
        c.drawString(m_x + 95, p_y - 104, notas_texto)
        c.line(m_x + 90, p_y - 107, largura - 320, p_y - 107)
        
        c.setFont("Helvetica", 10)
        c.drawString(largura - 310, p_y - 105, "Nº CTE:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(largura - 265, p_y - 104, str(dados.get('CTE', '')))
        c.line(largura - 270, p_y - 107, largura - 40, p_y - 107)
        
        # Campos Vazios / Protocolo Cliente
        c.setFont("Helvetica", 10)
        c.drawString(m_x + 5, p_y - 145, "DATA:")
        c.line(m_x + 40, p_y - 147, largura - 320, p_y - 147)
        
        c.drawString(largura - 310, p_y - 145, "Nº PROTOCOLO CLIENTE:")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(largura - 175, p_y - 144, protocolo_fonte)
        c.line(largura - 180, p_y - 147, largura - 40, p_y - 147)
        
        # Assinaturas
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

# --- INTERFACE PRINCIPAL ---
def main():
    st.title("📦 Gerador de Protocolos")
    txt = st.text_area("Insira os números das NFs (uma por linha ou separadas por espaço/vírgula):", height=150)

    if st.button("Gerar PDF"):
        if txt:
            try:
                # Configurações da Planilha
                S_ID = "1f_NDUAezh4g0ztyHVUO_t33QxGai9TYcWOD-IAoPcuE"
                URL = f"https://docs.google.com/spreadsheets/d/{S_ID}/export?format=csv&gid=0"
                
                nfs_digitadas = [n.strip() for n in re.split(r'[,\s\n]+', txt) if n.strip()]
                df = pd.read_csv(URL)
                
                # Identificação de colunas por índice para evitar erros de nome
                df.columns.values[0] = 'PROTOCOLO_FONTE'
                if len(df.columns) >= 9:
                    df.columns.values[8] = 'DESTINO'
                
                # Limpeza de dados
                df['NOTA FISCAL'] = df['NOTA FISCAL'].astype(str).str.strip()
                df['PROTOCOLO_FONTE'] = df['PROTOCOLO_FONTE'].astype(str).str.strip()

                # --- LÓGICA DE CAPTURA DE MÚLTIPLAS NOTAS ---
                # 1. Encontrar quais são os números de protocolos das NFs informadas
                protocolos_alvo = df[df['NOTA FISCAL'].isin(nfs_digitadas)]['PROTOCOLO_FONTE'].unique()

                if len(protocolos_alvo) > 0:
                    # 2. Selecionar todas as linhas que possuem esses protocolos (traz as notas "irmãs")
                    df_filtrado = df[df['PROTOCOLO_FONTE'].isin(protocolos_alvo)].copy()

                    # 3. Agrupar os dados para que cada protocolo vire apenas 1 bloco no PDF
                    df_agrupado = df_filtrado.groupby('PROTOCOLO_FONTE').agg({
                        'NOME': 'first',
                        'DESTINO': 'first',
                        'CTE': 'first',
                        'NOTA FISCAL': lambda x: ' / '.join(sorted(set(x))) # Une as notas: "101 / 102"
                    }).reset_index()
                    
                    res = df_agrupado.to_dict('records')
                    
                    pdf_file = gerar_pdf(res)
                    st.success(f"Foram encontrados {len(res)} pedidos vinculados às NFs informadas.")
                    st.download_button(
                        label="📥 Baixar PDF de Protocolos",
                        data=pdf_file,
                        file_name=f"protocolos_{datetime.now().strftime('%d_%m_%H%M')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.warning("Nenhuma Nota Fiscal correspondente foi encontrada na planilha.")
            except Exception as e:
                st.error(f"Erro ao processar a planilha: {e}")
        else:
            st.info("Por favor, digite ao menos um número de Nota Fiscal.")

if __name__ == "__main__":
    from datetime import datetime
    main()
