import streamlit as st
import os
from datetime import datetime, date
from app.file_creator import load_config, override_config, convert_docx_with_config, generate_output_filename
import logging

# Configure logging for Streamlit
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    st.title("🏖️ Flat Brisa do Mar")
    st.subheader("Gerador de Documentos de Estadia")
    st.write("Teste de geração de documento com dados fixos")
    
    # Hardcoded test data
    guest_name = "João Silva"
    start_date = date(2025, 12, 28)
    end_date = date(2025, 12, 31)
    nights = (end_date - start_date).days
    
    # Display test data
    st.info("🧪 **Dados de Teste:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👤 Hóspede", guest_name)
    with col2:
        st.metric("📅 Check-in", start_date.strftime("%d/%m/%Y"))
    with col3:
        st.metric("🌙 Noites", nights)
    
    st.metric("📅 Check-out", end_date.strftime("%d/%m/%Y"))
    
    # Generate button
    if st.button("🏗️ Gerar Documento de Teste", type="primary", use_container_width=True):
        # Show processing info
        with st.spinner("🔄 Gerando documento..."):
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
                
                # Override with hardcoded test data
                updated_config = override_config(
                    mapped_data,
                    guest=guest_name,
                    start=start_date.strftime("%Y-%m-%d"),
                    end=end_date.strftime("%Y-%m-%d")
                )
                
                # Generate output filename
                output_path = generate_output_filename(template_path, updated_config)
                
                # Convert document
                convert_docx_with_config(updated_config, template_path, output_path)
                
                # Success message
                st.success("✅ Documento gerado com sucesso!")
                st.success(f"💾 **Arquivo salvo em:** `{output_path}`")
                
                # Download button if file exists
                if os.path.exists(output_path):
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="📥 Download do Documento",
                            data=file.read(),
                            file_name=os.path.basename(output_path),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                
            except Exception as e:
                st.error(f"❌ Erro ao gerar documento: {str(e)}")
                logger.error(f"Error generating document: {e}")
                st.info("💡 Verifique os logs para mais detalhes sobre o erro.")
    
    # Information section
    st.markdown("---")
    st.subheader("ℹ️ Sobre o Teste")
    st.markdown("""
    Esta é uma versão de teste que usa dados fixos:
    - **Hóspede:** João Silva
    - **Check-in:** 28/12/2025
    - **Check-out:** 31/12/2025
    - **Estadia:** 3 noites
    
    O sistema carrega a configuração base do arquivo `config.json` e substitui 
    apenas o nome do hóspede e as datas, mantendo todas as outras informações 
    do Flat Brisa do Mar.
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