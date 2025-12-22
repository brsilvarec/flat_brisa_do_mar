import streamlit as st

def main():
    st.title("🏖️ Flat Brisa do Mar")
    st.subheader("Gerador de Documentos de Estadia")
    st.write("Faça upload do calendário de hóspedes para gerar os documentos de estadia!")
    
    # File uploader widget
    uploaded_file = st.file_uploader(
        "Escolha o arquivo do calendário", 
        type=None,  # Accept all file types
        help="Faça upload do arquivo contendo o calendário de hóspedes"
    )
    
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Display the file name in a success message
        st.success(f"📄 Arquivo carregado: **{uploaded_file.name}**")
        
        # You can also display additional file information
        st.info(f"Tamanho do arquivo: {uploaded_file.size} bytes")
        
        # Show file type if available
        if uploaded_file.type:
            st.info(f"Tipo do arquivo: {uploaded_file.type}")
            
        st.write("📋 Processando calendário para gerar documentos de estadia...")
        
    else:
        st.info("👆 Por favor, faça upload do calendário de hóspedes acima")
        st.write("ℹ️ Este sistema processa o calendário de hóspedes e gera automaticamente os documentos necessários para a estadia no Flat Brisa do Mar.")

if __name__ == "__main__":
    main()
