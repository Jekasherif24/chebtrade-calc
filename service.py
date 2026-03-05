import streamlit as st
import pandas as pd

# Константы экономики ChebTrade
LABOR_COST = 4620
TELEMETRY_MONTHLY = 5000
HOURS_PER_MONTH = 500
AKPP_REPAIR_BASE = 1200000 

# Справочник цен ТМЦ
PRICES = {
    "Масляный фильтр 4190001633": 758.33,
    "Фильтр топливный г.оч (на раме)": 1300.00,
    "Фильтр топливный г.оч (557)": 1650.00,
    "Фильтр топливный т.оч (555)": 2410.00,
    "Фильтр сапуна бака": 1200.00,
    "Воздушный фильтр": 5983.33,
    "Фильтр гидросистемы": 2820.00,
    "Фильтр сапуна гидробака": 350.00,
    "Фильтр салона": 630.00,
    "Фильтр кондиционера": 367.00,
    "Фильтр АКПП (389-1085)": 9248.33,
    "Фильтр осушитель": 1567.00,
    "Масло моторное (Grizzli), л": 568.49,
    "Масло АКПП (ATF), л": 414.63,
    "Масло гидравлическое (HVLP 46), л": 353.60,
    "Масло трансмиссионное (75W-90), л": 391.80,
    "Масло М-8ДМ, л": 563.00,
    "Смазка LX EP2, кг": 695.00,
    "Антифриз G-12 (красный), л": 350.00,
    "Ремень генератора": 853.71,
    "Ремень вентилятора": 1790.83,
    "Натяжной ролик генератора": 4755.00,
    "Натяжной ролик вентилятора": 4146.67,
    "Сильфонный компенсатор": 7963.33,
    "Заслонка горного тормоза": 10813.33
}

def get_tmc_and_notes(h):
    items = []
    notes = []
    if h > 0 and h % 1000 == 0:
        notes.append("🔧 ОБЯЗАТЕЛЬНО: Регулировка клапанов ДВС")
    if h % 250 == 0 or h == 100:
        items += [["Масляный фильтр 4190001633", 2], ["Фильтр топливный г.оч (на раме)", 2],
                  ["Фильтр топливный г.оч (557)", 1], ["Фильтр топливный т.оч (555)", 1],
                  ["Масло моторное (Grizzli), л", 30]]
    if h in [500, 1500, 2500, 3500, 4500, 5500]:
        notes.append("💻 СЕРВИС: Диагностика и калибровка АКПП")
        items += [["Фильтр АКПП (389-1085)", 1], ["Масло АКПП (ATF), л", 35], 
                  ["Воздушный фильтр", 1], ["Масло М-8ДМ, л", 4], ["Смазка LX EP2, кг", 1.5]]
    if h in [1000, 2000, 3000, 4000, 5000, 6000]:
        items += [["Фильтр салона", 1], ["Фильтр кондиционера", 1], ["Воздушный фильтр", 1], ["Масло М-8ДМ, л", 4]]
    if h in [3000, 6000]:
        items += [["Масло гидравлическое (HVLP 46), л", 160], ["Фильтр гидросистемы", 1], ["Фильтр сапуна гидробака", 1], ["Антифриз G-12 (красный), л", 60]]
    if h in [2000, 4000, 6000]:
        items += [["Масло трансмиссионное (75W-90), л", 70], ["Сильфонный компенсатор", 1]]
    if h == 6000:
        items += [["Ремень генератора", 1], ["Ремень вентилятора", 1], ["Натяжной ролик генератора", 1], 
                  ["Натяжной ролик вентилятора", 1], ["Заслонка горного тормоза", 1], ["Фильтр сапуна бака", 1], ["Фильтр осушитель", 1]]
        notes.append("📢 ВНИМАНИЕ: Замена ремней, роликов и элементов выхлопной системы")
    return items, notes

st.set_page_config(page_title="ChebTrade-Synergy Service", layout="wide")
st.title("🚜 Аналитика TCO: SANY SCT90 / LGMG")

with st.sidebar:
    st.header("⚙️ Управление")
    num_trucks = st.number_input("Машин в парке", 1, 100, 14)
    tele_on = st.toggle("Телеметрия Synergy (5000 ₽/мес)", value=True)
    show_vat = st.checkbox("Показать с НДС (20%)", value=False)

current_h = st.select_slider("Наработка (моточасы):", options=list(range(0, 6001, 250)) + [100])
if current_h == 0: current_h = 100

vat_m = 1.2 if show_vat else 1.0

# РАСЧЕТ НАКОПИТЕЛЬНЫМ ИТОГОМ
total_tmc_acc = 0
total_labor_acc = 0
for h in range(100, current_h + 1, 50):
    if h in [100] or (h > 0 and h % 250 == 0):
        items_acc, _ = get_tmc_and_notes(h)
        total_tmc_acc += sum([PRICES.get(name, 0) * qty for name, qty in items_acc])
        l_hrs = 26 if h % 6000 == 0 else (20 if h % 3000 == 0 else (12 if h % 500 == 0 else 6))
        total_labor_acc += l_hrs * LABOR_COST

# Стоимость телеметрии (только если включена)
tele_accum_per_truck = (current_h / HOURS_PER_MONTH) * TELEMETRY_MONTHLY if tele_on else 0
grand_total_per_truck = (total_tmc_acc + total_labor_acc + tele_accum_per_truck)

# Текущее ТО
curr_items, curr_notes = get_tmc_and_notes(current_h)
curr_tmc_sum = sum([PRICES.get(name, 0) * qty for name, qty in curr_items])
curr_l_hrs = 26 if current_h % 6000 == 0 else (20 if current_h % 3000 == 0 else (12 if current_h % 500 == 0 else 6))
current_to_cost_park = (curr_tmc_sum + curr_l_hrs * LABOR_COST) * num_trucks

st.divider()
# МЕТРИКИ
m1, m2, m3 = st.columns(3)
m1.metric("Текущее ТО (на весь парк)", f"{current_to_cost_park * vat_m:,.0f} ₽")
m2.metric("Всего затрачено на 1 машину", f"{grand_total_per_truck * vat_m:,.0f} ₽", 
          delta=f"{tele_accum_per_truck * vat_m:,.0f} ₽ (телеметрия)" if tele_on else None)
m3.metric("Стоимость телеметрии (парк)", f"{tele_accum_per_truck * num_trucks * vat_m:,.0f} ₽")

if curr_notes:
    st.info("\n".join(curr_notes))

# Логика 6000 м.ч.
if current_h == 6000:
    st.write("---")
    if not tele_on:
        st.error(f"⚠️ РЕЖИМ РИСКА: Телеметрия отключена. Прогноз ремонта АКПП на 9000 м.ч. Бюджет: + {AKPP_REPAIR_BASE * num_trucks * vat_m:,.0f} ₽")
    else:
        st.success(f"✅ КОНТРОЛЬ SYNERGY: Ресурс АКПП продлен до 15000 м.ч. Ваши инвестиции в телеметрию ({tele_accum_per_truck * vat_m:,.0f} ₽) защищают от затрат в {AKPP_REPAIR_BASE * vat_m:,.0f} ₽")

# Таблица ТМЦ
st.subheader(f"📋 Ведомость ТМЦ на {current_h} м.ч.")
if curr_items:
    df_tmc = pd.DataFrame(curr_items, columns=["Наименование", "Кол-во"])
    df_tmc["Цена ед."] = df_tmc["Наименование"].map(PRICES) * vat_m
    df_tmc["Итого"] = df_tmc["Цена ед."] * df_tmc["Кол-во"]
    st.table(df_tmc.style.format("{:,.2f}", subset=["Цена ед.", "Итого"]))

st.caption(f"Средняя наработка: {HOURS_PER_MONTH} м.ч./мес. Ставка работ: {LABOR_COST} руб/н.ч.")
