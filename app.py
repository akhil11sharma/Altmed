import streamlit as st
import pandas as pd
import json
import speech_recognition as sr

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"File '{file_path}' not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

def save_review(medicine_name, available_medicines):
    data = {"medicine_name": medicine_name, "available_medicines": available_medicines}
    try:
        with open("avail.json", "r") as f:
            all_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_data = []
    all_data.append(data)
    with open("avail.json", "w") as f:
        json.dump(all_data, f, indent=4)

def get_suggestions(df, medicine_name):
    if not medicine_name.strip():
        return []
    
    # Update to match medicines that start with the user's input
    filtered_medicines = df[df['name'].str.lower().str.startswith(medicine_name.lower(), na=False)]
    options = filtered_medicines['name'].drop_duplicates().tolist()
    return options

def get_medicine_details(df, medicine_name):
    if not medicine_name.strip():
        return "Invalid input. Please enter a valid medicine name.", None
    filtered_medicines = df[df['name'].str.lower() == medicine_name.lower()]
    if filtered_medicines.empty:
        return "No medicine found with that name.", None
    table_data = []
    for i in range(5):
        substitute_col = f'substitute{i}'
        side_effect_col = f'sideEffect{i}'
        if substitute_col in filtered_medicines.columns and pd.notna(filtered_medicines.iloc[0][substitute_col]):
            table_data.append([
                f"Substitute {i + 1}",
                filtered_medicines.iloc[0][substitute_col],
                filtered_medicines.iloc[0][side_effect_col],
                filtered_medicines.iloc[0]['Use'],
                filtered_medicines.iloc[0]['Habit Forming'],
                filtered_medicines.iloc[0]['Therapeutic Class']
            ])
        else:
            break
    return None, table_data

def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

# Sidebar for "Mental Health Analysis"
with st.sidebar:
    option = st.button("Mental Health Analysis")
    if option:
        st.write("Under Construction")
        st.stop()

# Main content
st.title("Medicine Substitute Finder")

df = load_data('indian_medicine_with_substitutes (1).csv')

if df.empty:
    st.error("Dataset could not be loaded.")
else:
    # Horizontal layout for quick-select buttons
    st.write("Select a medicine or enter a new one:")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Paracetamol"):
            st.session_state.medicine_name = "Paracetamol"

    with col2:
        if st.button("Crocin"):
            st.session_state.medicine_name = "Crocin"

    with col3:
        if st.button("Disprin"):
            st.session_state.medicine_name = "Disprin"

    # Add voice input button
    if st.button("🎙️ Voice Input"):
        voice_text = get_voice_input()
        st.session_state.medicine_name = voice_text 

    # Initialize session state variables if not present
    if 'medicine_name' not in st.session_state:
        st.session_state.medicine_name = ''

    # Input field for medicine name with dynamic recommendations
    medicine_name = st.text_input(
        "Enter the medicine name:",
        value=st.session_state.get('medicine_name', ''),
        key="medicine_name_input"
    )

    # Fetch suggestions based on user input
    if medicine_name:
        suggestions = get_suggestions(df, medicine_name)
        if suggestions:
            st.session_state.suggestions = suggestions
        else:
            st.session_state.suggestions = []

    # Dropdown for selecting a suggested medicine
    if st.session_state.get('suggestions'):
        choice = st.selectbox("Select a medicine:", st.session_state.suggestions)
        if choice:
            st.session_state.medicine_name = choice
            error, table_data = get_medicine_details(df, choice)
            if error:
                st.write(error)
            elif table_data:
                headers = ["Substitute #", "Medicine", "Side Effects", "Use", "Habit Forming", "Therapeutic Class"]
                df_table = pd.DataFrame(table_data, columns=headers)
                df_table["Availability"] = ["No" for _ in range(len(df_table))]
                st.write("Select availability for each substitute:")
                updated_table_data = []
                for i, row in df_table.iterrows():
                    is_available = st.checkbox(f"Available: {row['Medicine']}", key=f"availability_{i}")
                    updated_table_data.append([
                        row["Substitute #"],
                        row["Medicine"],
                        row["Side Effects"],
                        row["Use"],
                        row["Habit Forming"],
                        row["Therapeutic Class"],
                        "Yes" if is_available else "No"
                    ])
                df_updated = pd.DataFrame(updated_table_data, columns=headers + ["Availability"])
                st.table(df_updated)
                available_medicines = df_updated[df_updated["Availability"] == "Yes"].to_dict(orient="records")
                if available_medicines:
                    save_review(medicine_name, available_medicines)
            else:
                st.write("No details available.")
