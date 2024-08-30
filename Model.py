import pandas as pd
from tabulate import tabulate

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            print(f"File '{file_path}' is empty.")
        else:
            print("Dataset loaded successfully.")
        return df
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        print(f"File '{file_path}' is empty.")
        return pd.DataFrame()
    except pd.errors.ParserError:
        print(f"Error parsing the file '{file_path}'.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

def get_suggestions(df, medicine_name):
    if not medicine_name.strip():
        return "Invalid input. Please enter a valid medicine name.", None
    filtered_medicines = df[df['name'].str.lower().str.contains(medicine_name.lower(), na=False)]
    if filtered_medicines.empty:
        return "No medicine found with that name.", None
    options = filtered_medicines['name'].drop_duplicates().tolist()
    return None, options

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
            row_data = [
                f"Substitute {i + 1}",
                filtered_medicines.iloc[0].get(substitute_col, 'N/A'),
                filtered_medicines.iloc[0].get(side_effect_col, 'N/A'),
                filtered_medicines.iloc[0].get('Use', 'N/A'),
                filtered_medicines.iloc[0].get('Habit Forming', 'N/A'),
                filtered_medicines.iloc[0].get('Therapeutic Class', 'N/A')
            ]
            table_data.append(row_data)
        else:
            break
    return None, table_data

if __name__ == "__main__":
    df = load_data('indian_medicine_with_substitutes (1).csv')
    medicine_name = input("Enter the medicine name: ")
    error, suggestions = get_suggestions(df, medicine_name)
    if error:
        print(error)
    else:
        print("Suggestions:", suggestions)
        if suggestions:
            selected_medicine = input("Enter the name of the medicine you want details for: ")
            error, details = get_medicine_details(df, selected_medicine)
            if error:
                print(error)
            else:
                print("Medicine Details:")
                headers = ["Substitute #", "Medicine", "Side Effects", "Use", "Habit Forming", "Therapeutic Class"]
                print(tabulate(details, headers=headers, tablefmt="grid"))
