import numpy as np
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import warnings

warnings.filterwarnings('ignore')

def calculate_rebound_height(H0, e):
    """
    Обчислює максимальну висоту першого підскоку.
    H0: початкова висота (м)
    e: коефіцієнт відновлення (безрозмірний)
    Повертає: максимальна висота підскоку (м)
    """
    if not (0 <= e <= 1 and H0 > 0):
        return np.nan # Повертаємо Not a Number для нефізичних значень
    return (e ** 2) * H0


#Вплив H0 на H_max при різних e
E_SCENARIO_1 = [0.2, 0.5, 0.8, 1.0]
H0_RANGE = np.linspace(1, 10, 50) # від 1 м до 10 м

results_H0_vs_Hmax = {}
for e in E_SCENARIO_1:
    Hmax_values = [calculate_rebound_height(h0, e) for h0 in H0_RANGE]
    results_H0_vs_Hmax[e] = Hmax_values

# Вплив e на H_max при різних H0 
# Фіксовані початкові висоти (H0)
H0_SCENARIO_2 = [1, 3, 5, 10]
# Діапазон коефіцієнтів відновлення (e)
E_RANGE = np.linspace(0, 1, 50) # від 0 до 1

results_e_vs_Hmax = {}
for h0 in H0_SCENARIO_2:
    Hmax_values = [calculate_rebound_height(h0, e) for e in E_RANGE]
    results_e_vs_Hmax[h0] = Hmax_values
    
# Підсумкова таблиця для конкретних точок 
H0_TABLE = [10, 5, 2, 1]
E_TABLE = [0.1, 0.3, 0.5, 0.7, 0.9]

table_data = []
for h0 in H0_TABLE:
    row = [f'H0 = {h0} м']
    for e in E_TABLE:
        h_max = calculate_rebound_height(h0, e)
        row.append(f'{h_max:.3f}')
    table_data.append(row)

#Графік 1 Залежність H_max від H0 (сімейство кривих по e)
plt.figure(figsize=(10, 6))
for e, Hmax_values in results_H0_vs_Hmax.items():
    plt.plot(H0_RANGE, Hmax_values, label=f'e = {e:.1f}')

plt.title('Залежність максимальної висоти підскоку від початкової висоти')
plt.xlabel('Початкова висота, $H_0$ (м)')
plt.ylabel('Максимальна висота підскоку, $H_{max}$ (м)')
plt.legend(title='Коеф. відновлення (e)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.xlim(H0_RANGE.min(), H0_RANGE.max())
plt.ylim(0, max(max(v) for v in results_H0_vs_Hmax.values()) * 1.05)
plt.show()


# Графік 2 Залежність H_max від e (сімейство кривих по H0)
plt.figure(figsize=(10, 6))
for h0, Hmax_values in results_e_vs_Hmax.items():
    plt.plot(E_RANGE, Hmax_values, label=f'$H_0$ = {h0:.0f} м')

plt.title('Залежність максимальної висоти підскоку від коефіцієнта відновлення')
plt.xlabel('Коефіцієнт відновлення, $e$')
plt.ylabel('Максимальна висота підскоку, $H_{max}$ (м)')
plt.legend(title='Початкова висота ($H_0$)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.xlim(E_RANGE.min(), E_RANGE.max())
plt.ylim(0, max(max(v) for v in results_e_vs_Hmax.values()) * 1.05)
plt.show()

# Стовпчаста діаграма
# 4 точки для порівняння: H0=10м, e=[0.4, 0.6, 0.8, 1.0]
e_bar = [0.4, 0.6, 0.8, 1.0]
H0_bar = 10
Hmax_bar = [calculate_rebound_height(H0_bar, e) for e in e_bar]

plt.figure(figsize=(8, 5))
bars = plt.bar([f'e={e}' for e in e_bar], Hmax_bar, color=['blue', 'green', 'orange', 'red'])
plt.title(f'Порівняння Hmax для H0 = {H0_bar} м при різних e')
plt.xlabel('Коефіцієнт відновлення, $e$')
plt.ylabel('Максимальна висота підскоку, $H_{max}$ (м)')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.ylim(0, H0_bar * 1.05)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f'{yval:.2f}', ha='center', va='bottom')
plt.show()

#Верифікація моделі
H_check = calculate_rebound_height(5, 0.5)
print(f"Верифікація моделі: {H_check}")

#Таблиця з підсумковими результатами
table = PrettyTable()
table.title = "Підсумкові результати моделювання Hmax = e^2 * H0"
table.field_names = ["Вхідні дані"] + [f"e={e}" for e in E_TABLE]
table.add_rows(table_data)

print("\n" + str(table) + "\n")