import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import simpledialog, messagebox

# Función para simular la inversión mensual
def simulate_investment(symbol, investment_amount, start_date, end_date):
    # Descargar datos históricos de la acción
    stock = yf.Ticker(symbol)
    hist = stock.history(start=start_date, end=end_date, interval="1mo")
    
    # Inicializar variables
    total_invested = 0
    total_shares = 0
    investment_data = []
    
    # Simular la inversión mensual
    for date, row in hist.iterrows():
        close_price = row['Close']
        shares_bought = investment_amount / close_price
        total_shares += shares_bought
        total_invested += investment_amount
        total_value = total_shares * close_price
        
        # Guardar los resultados en la lista
        investment_data.append({
            "Date": date,
            "Invested": total_invested,
            "Shares": total_shares,
            "Total Value": total_value
        })
    
    # Convertir la lista a un DataFrame
    investment_df = pd.DataFrame(investment_data)
    return investment_df

# Función para obtener los símbolos de las acciones desde la interfaz
def get_symbols():
    symbols = simpledialog.askstring("Input", "Ingrese los símbolos de las acciones separados por comas:")
    if symbols:
        return [symbol.strip() for symbol in symbols.split(',')]
    return None

# Función para realizar la simulación y actualizar el label
def run_simulation():
    try:
        total_investment_amount = float(investment_amount_entry.get())
        years = int(years_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos para el monto y los años.")
        return

    start_date = datetime.now() - timedelta(days=years*365)
    end_date = datetime.now()

    symbols = get_symbols()
    if symbols is None:
        return

    investment_amount_per_stock = total_investment_amount / len(symbols)
    investment_results = {}
    invalid_symbols = []

    for symbol in symbols:
        symbol = symbol.strip()
        stock = yf.Ticker(symbol)
        try:
            hist = stock.history(start=start_date, end=end_date, interval="1mo")
            if hist.empty:
                invalid_symbols.append(symbol)
            else:
                investment_results[symbol] = simulate_investment(symbol, investment_amount_per_stock, start_date, end_date)
        except Exception as e:
            invalid_symbols.append(symbol)

    if invalid_symbols:
        messagebox.showerror("Error", f"Los siguientes símbolos no son válidos: {', '.join(invalid_symbols)}")
        return

    combined_investment_data = []

    valid_symbols = [symbol for symbol in symbols if symbol not in invalid_symbols]
    for i in range(len(investment_results[valid_symbols[0]])):
        date = investment_results[valid_symbols[0]].iloc[i]["Date"]
        total_invested = sum(investment_results[symbol].iloc[i]["Invested"] for symbol in valid_symbols)
        total_value = sum(investment_results[symbol].iloc[i]["Total Value"] for symbol in valid_symbols)
        
        combined_investment_data.append({
            "Date": date,
            "Total Invested": total_invested,
            "Total Value": total_value
        })

    combined_investment_df = pd.DataFrame(combined_investment_data)

    total_invested_combined = combined_investment_df["Total Invested"].iloc[-1]
    total_value_combined = combined_investment_df["Total Value"].iloc[-1]

    percentage_return = ((total_value_combined - total_invested_combined) / total_invested_combined) * 100

    # Formatear los números con comas como separadores de miles
    total_invested_formatted = f"{total_invested_combined:,.2f}"
    total_value_formatted = f"{total_value_combined:,.2f}"
    percentage_return_formatted = f"{percentage_return:.2f}%"

    plt.figure(figsize=(12, 8))
    plt.plot(combined_investment_df["Date"], combined_investment_df["Total Value"], label=f"Valor Total de la Inversión Combinada: ${total_value_formatted}")
    plt.plot(combined_investment_df["Date"], combined_investment_df["Total Invested"], label=f"Total Invertido Combinado: ${total_invested_formatted}")
    plt.xlabel("Fecha")
    plt.ylabel("Valor en USD")
    plt.title(f"Simulación de Inversión Combinada\nRetorno: {percentage_return_formatted}")
    plt.legend()
    plt.grid(True)
    plt.show()

    result_text = f"Total invertido combinado: ${total_invested_formatted}\nValor total de la inversión combinada: ${total_value_formatted}"
    result_label.config(text=result_text)

# Crear la ventana principal
root = tk.Tk()
root.title("Simulación de Inversión")

# Crear campos de entrada para el monto de inversión y los años
tk.Label(root, text="Monto de inversión mensual:").pack(pady=5)
investment_amount_entry = tk.Entry(root)
investment_amount_entry.pack(pady=5)

tk.Label(root, text="Cantidad de años:").pack(pady=5)
years_entry = tk.Entry(root)
years_entry.pack(pady=5)

# Crear un botón para iniciar la simulación
start_button = tk.Button(root, text="Iniciar Simulación", command=run_simulation)
start_button.pack(pady=20)

# Crear un label para mostrar los resultados
result_label = tk.Label(root, text="", justify=tk.LEFT)
result_label.pack(pady=20)

# Ejecutar la aplicación
root.mainloop()