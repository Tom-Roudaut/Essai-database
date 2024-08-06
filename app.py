import streamlit as st
import pandas as pd
import openai

# Configurez votre clé API OpenAI
openai.api_key = 'sk-proj-rrkq0z6BsuwuThCqtH9kT3BlbkFJLtDVAOyWW0zJNtm4fKTl'

# Chemin vers le fichier Excel stocké
EXCEL_FILE_PATH = '/Users/sachadoliner/Desktop/NeumannGPT - fichier import fonds - 17.07.xlsx'

# Fonction pour charger les données Excel
def load_data(file_path):
    data = pd.read_excel(file_path)
    return data

# Fonction pour envoyer une requête à ChatGPT avec InstructGPT
def query_instructgpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content'].strip()

# Fonction pour filtrer les données en fonction de la réponse de ChatGPT
def filter_data_with_instructgpt(data, query):
    unique_values = {}
    for col in data.columns:
        if col not in ['Investors', 'Last Investment Company', 'Website']:
            unique_values[col] = data[col].unique().tolist()[:100] if col == 'Preferred Industry' else data[col].unique().tolist()
    
    prompt = f"Voici les valeurs uniques pour chaque colonne du dataset:\n{unique_values}\n\n"
    prompt += f"Filtrer les données dans les colonnes qui répondent à la requête suivante : {query}. Donne les conditions de filtrage sous la forme 'colonne=valeur', 'colonne>valeur' ou 'colonne<valeur' et sépare chaque condition par un point-virgule (;)."

    response = query_instructgpt(prompt)

    # Nettoyer la réponse brute pour supprimer les apostrophes inutiles≠
    response = response.replace("'", "")

    # Afficher la réponse brute de ChatGPT pour débogage
    st.write(f"Réponse brute de ChatGPT: {response}")

    filtered_data = data.copy()
    try:
        conditions = response.split(';')
        
        for cond in conditions:
            cond = cond.strip()
            if '=' in cond or '>' in cond or '<' in cond:
                try:
                    if '=' in cond:
                        column, value = cond.split('=', 1)
                        operator = '='
                    elif '>' in cond:
                        column, value = cond.split('>', 1)
                        operator = '>'
                    elif '<' in cond:
                        column, value = cond.split('<', 1)
                        operator = '<'
                    column = column.strip()
                    value = value.strip()
                    st.write(f"Filtrage sur colonne: {column} avec valeur: {value} et opérateur: {operator}")
                    if column in data.columns:
                        if operator == '=':
                            filtered_data = filtered_data[filtered_data[column].str.contains(value, case=False, na=False)]
                        elif operator == '>':
                            filtered_data = filtered_data[filtered_data[column].astype(float) > float(value)]
                        elif operator == '<':
                            filtered_data = filtered_data[filtered_data[column].astype(float) < float(value)]
                    else:
                        st.error(f"Colonne inconnue: {column}")
                except ValueError:
                    st.error(f"Condition mal formée: {cond}")
            else:
                st.error(f"Condition mal formée: {cond}")
                
        return filtered_data
    except Exception as e:
        st.error(f"Erreur lors du filtrage des données: {e}")
        return data

# Fonction principale pour Streamlit
def main():
    st.title("NeumannGPT - Investment Funds and Start-ups Data Filtering")
    st.write("Upload an Excel file and provide a query to filter the data based on ChatGPT's response.")
    
    # Téléchargement du fichier (pour mise à jour mensuelle)
    if st.checkbox("Upload a new Excel file for monthly update"):
        uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
        if uploaded_file is not None:
            with open(EXCEL_FILE_PATH, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("File uploaded and stored successfully.")
    
    # Charger les données stockées
    data = load_data(EXCEL_FILE_PATH)
    st.write("Data loaded successfully. Here are the first few rows:")
    st.write(data.head())
    
    # Entrée de la requête utilisateur
    query = st.text_input("Enter your query to filter the data:")
    
    if st.button("Filter Data"):
        filtered_data = filter_data_with_instructgpt(data, query)
        st.write("Filtered data:")
        st.write(filtered_data)
    
        # Téléchargement du fichier filtré
        output_file = 'filtered_data.xlsx'
        filtered_data.to_excel(output_file, index=False)
        with open(output_file, "rb") as file:
            btn = st.download_button(
                label="Download filtered data",
                data=file,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()