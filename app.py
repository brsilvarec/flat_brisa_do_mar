import streamlit as st
import os
from datetime import date
from app.file_creator import load_config, override_config, convert_docx_with_config, generate_output_filename
import logging
import zipfile
from io import BytesIO
import pandas as pd

# Configure logging for Streamlit
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_zip_with_documents(document_paths):
    """
    Create a ZIP file containing all generated documents.
    
    Args:
        document_paths (list): List of paths to generated documents
        
    Returns:
        BytesIO: ZIP file as bytes
    """
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for doc_path in document_paths:
            if os.path.exists(doc_path):
                # Add file to ZIP with just the filename (no path)
                zip_file.write(doc_path, os.path.basename(doc_path))
    
    zip_buffer.seek(0)
    return zip_buffer

def main():
    st.title("🏖️ Flat Brisa do Mar")
    st.subheader("Gerador de Documentos de Estadia")
    st.write("Insira a lista de hóspedes e datas para gerar os documentos")
    
    # Initialize session state
    if 'guests_df' not in st.session_state:
        # Create initial dataframe with example rows
        st.session_state.guests_df = pd.DataFrame({
            'Nome do Hóspede': ['João Silva', 'Maria Santos', ''],
            'Data de Check-in': [date(2025, 12, 28), date(2026, 1, 2), date.today()],
            'Data de Check-out': [date(2025, 12, 31), date(2026, 1, 5), date.today()]
        })
    
    # Form section
    st.subheader("📝 Lista de Hóspedes")
    st.write("Edite a tabela abaixo para inserir os dados dos hóspedes:")
    
    # Data editor
    edited_df = st.data_editor(
        st.session_state.guests_df,
        column_config={
            "Nome do Hóspede": st.column_config.TextColumn(
                "Nome do Hóspede",
                help="Nome completo do hóspede",
                width="medium",
                required=True
            ),
            "Data de Check-in": st.column_config.DateColumn(
                "Data de Check-in",
                help="Data de entrada",
                width="small",
                format="DD/MM/YYYY",
                required=True
            ),
            "Data de Check-out": st.column_config.DateColumn(
                "Data de Check-out", 
                help="Data de saída",
                width="small",
                format="DD/MM/YYYY",
                required=True
            )
        },
        num_rows="dynamic",  # Allow adding/removing rows
        use_container_width=True,
        key="guests_editor"
    )
    
    # Update session state
    st.session_state.guests_df = edited_df
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("➕ Adicionar Linha", use_container_width=True):
            new_row = pd.DataFrame({
                'Nome do Hóspede': [''],
                'Data de Check-in': [date.today()],
                'Data de Check-out': [date.today()]
            })
            st.session_state.guests_df = pd.concat([st.session_state.guests_df, new_row], ignore_index=True)
            st.rerun()
    
    with col2:
        if st.button("🗑️ Limpar Tabela", use_container_width=True):
            st.session_state.guests_df = pd.DataFrame({
                'Nome do Hóspede': [''],
                'Data de Check-in': [date.today()],
                'Data de Check-out': [date.today()]
            })
            st.rerun()
    
    # Validate and show preview
    valid_guests = []
    
    for _, row in edited_df.iterrows():
        name = str(row['Nome do Hóspede']).strip()
        check_in = row['Data de Check-in']
        check_out = row['Data de Check-out']
        
        if name and name != '' and pd.notna(check_in) and pd.notna(check_out):
            if check_in < check_out:
                nights = (check_out - check_in).days
                valid_guests.append({
                    'name': name,
                    'start': check_in,
                    'end': check_out,
                    'nights': nights
                })
    
    # Display valid guests preview
    if valid_guests:
        st.subheader("👥 Resumo dos Hóspedes Válidos")
        
        for i, guest in enumerate(valid_guests, 1):
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**{i}. {guest['name']}**")
                with col2:
                    st.write(f"📅 {guest['start'].strftime('%d/%m/%Y')}")
                with col3:
                    st.write(f"📅 {guest['end'].strftime('%d/%m/%Y')}")
                with col4:
                    st.write(f"🌙 {guest['nights']} noites")
        
        st.info(f"Total de hóspedes válidos: **{len(valid_guests)}**")
        
        # Generate documents button
        with col3:
            if st.button("🏗️ Gerar Todos os Documentos", type="primary", use_container_width=True):
                # Show processing info
                with st.spinner("🔄 Gerando documentos..."):
                    try:
                        # File paths
                        config_path = "app/data/config.json"
                        template_path = "app/data/template.docx"
                        
                        # Check if required files exist
                        if not os.path.exists(config_path):
                            st.error(f"❌ Arquivo de configuração não encontrado: {config_path}")
                            st.info("💡 Certifique-se de que o arquivo config.json existe na pasta app/data/")
                            return
                        
                        if not os.path.exists(template_path):
                            st.error(f"❌ Template não encontrado: {template_path}")
                            st.info("💡 Certifique-se de que o arquivo template.docx existe na pasta app/data/")
                            return
                        
                        # Load base configuration
                        mapped_data = load_config(config_path)
                        
                        # Progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        generated_files = []
                        
                        # Process each guest
                        for i, guest in enumerate(valid_guests):
                            status_text.text(f"Processando {guest['name']}...")
                            
                            # Override with guest data
                            updated_config = override_config(
                                mapped_data,
                                guest=guest["name"],
                                start=guest["start"].strftime("%Y-%m-%d"),
                                end=guest["end"].strftime("%Y-%m-%d")
                            )
                            
                            # Generate output filename
                            output_path = generate_output_filename(template_path, updated_config)
                            
                            # Convert document
                            convert_docx_with_config(updated_config, template_path, output_path)
                            
                            if os.path.exists(output_path):
                                generated_files.append(output_path)
                            
                            # Update progress
                            progress = (i + 1) / len(valid_guests)
                            progress_bar.progress(progress)
                        
                        status_text.text("Finalizando...")
                        
                        # Success message
                        st.success(f"✅ {len(generated_files)} documentos gerados com sucesso!")
                        
                        # Display generated files
                        st.subheader("📋 Documentos Gerados:")
                        for file_path in generated_files:
                            filename = os.path.basename(file_path)
                            st.write(f"✅ {filename}")
                        
                        # Create ZIP file with all documents
                        if generated_files:
                            zip_buffer = create_zip_with_documents(generated_files)
                            
                            # Download ZIP button
                            st.download_button(
                                label="📦 Download Todos os Documentos (ZIP)",
                                data=zip_buffer.getvalue(),
                                file_name=f"documentos_estadia_{date.today().strftime('%Y%m%d')}.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                        
                        # Individual download buttons
                        with st.expander("📥 Downloads Individuais"):
                            for file_path in generated_files:
                                if os.path.exists(file_path):
                                    filename = os.path.basename(file_path)
                                    with open(file_path, "rb") as file:
                                        st.download_button(
                                            label=f"📄 {filename}",
                                            data=file.read(),
                                            file_name=filename,
                                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                            key=f"download_{filename}"
                                        )
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar documentos: {str(e)}")
                        logger.error(f"Error generating documents: {e}")
                        st.info("💡 Verifique os logs para mais detalhes sobre o erro.")
    
    else:
        st.warning("⚠️ Nenhum hóspede válido encontrado. Verifique os dados inseridos na tabela.")
        st.info("💡 Certifique-se de que:")
        st.write("• O nome do hóspede não está vazio")
        st.write("• As datas estão preenchidas corretamente")
        st.write("• A data de check-out é posterior à data de check-in")
    
    # Information section
    st.markdown("---")
    st.subheader("ℹ️ Como Usar")
    st.markdown("""
    **Passo a passo:**
    1. **Edite a tabela acima** inserindo nome e datas para cada hóspede
    2. **Use "➕ Adicionar Linha"** para incluir mais hóspedes
    3. **Verifique o resumo** dos hóspedes válidos
    4. **Clique em "Gerar Todos os Documentos"** para processar
    5. **Faça o download** individual ou em lote (ZIP)
    
    **Funcionalidades:**
    - ✅ Tabela editável para inserção de dados
    - ✅ Validação automática de dados
    - ✅ Cálculo automático de noites
    - ✅ Adicionar/remover linhas dinamicamente
    - ✅ Preview dos dados antes da geração
    - ✅ Download individual e em lote
    """)
    
    # Status section
    with st.expander("🔧 Status do Sistema"):
        config_exists = os.path.exists("app/data/config.json")
        template_exists = os.path.exists("app/data/template.docx")
        
        st.write("**Arquivos necessários:**")
        st.write(f"{'✅' if config_exists else '❌'} Configuração (config.json)")
        st.write(f"{'✅' if template_exists else '❌'} Template (template.docx)")
        
        if config_exists and template_exists:
            st.success("🎉 Sistema pronto para uso!")
        else:
            st.warning("⚠️ Alguns arquivos estão faltando. Verifique a configuração.")

if __name__ == "__main__":
    main()
