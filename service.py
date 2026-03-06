import streamlit as st
import pandas as pd

# Константы
TELEMETRY_MONTHLY = 5000
HOURS_PER_MONTH = 500
AKPP_REPAIR_BASE = 1200000 
VAT_RATE = 1.22  # НДС 22%

# Справочник цен ТМЦ и Категории
CAT_FILTERS = "📦 ФИЛЬТРЫ"
CAT_OILS = "🛢 МАСЛА И ЖИДКОСТИ"
CAT_PARTS = "⚙️ ПРОЧИЕ ЗАПЧАСТИ"

PRICES = {
    # Фильтры
    "Масляный фильтр 4190001633": (758.33, CAT_FILTERS),
    "Фильтр топливный г.оч (на раме)": (1300.00, CAT_FILTERS),
    "Фильтр топливный г.оч (557)": (1650.00, CAT_FILTERS),
    "Фильтр топливный т.оч (555)": (2410.00, CAT_FILTERS),
    "Фильтр сапуна бака": (1200.00, CAT_FILTERS),
    "Воздушный фильтр": (5983.33, CAT_FILTERS),
    "Фильтр гидросистемы": (2820.00, CAT_FILTERS),
    "Фильтр сапуна гидробака": (350.00, CAT_FILTERS),
    "Фильтр салона": (630.00, CAT_FILTERS),
    "Фильтр кондиционера": (367.00, CAT_FILTERS),
    "Фильтр АКПП (389-1085)": (9248.33, CAT_FILTERS),
    "Фильтр осушитель": (1567.00, CAT_FILTERS),
    # Масла
    "Масло моторное (Grizzli), л": (568.49, CAT_OILS),
    "Масло АКПП (ATF), л": (414.63, CAT_OILS),
    "Масло гидравлическое (HVLP 46), л": (353.60, CAT_OILS),
    "Масло трансмиссионное (75W-90), л": (391.80, CAT_OILS),
    "Масло М-8ДМ, л": (563.00, CAT_OILS),
    "Антифриз G-12 (красный), л": (350.00, CAT_OILS),
    # Прочее
    "Смазка LX EP2, кг": (695.00, CAT_PARTS),
    "Ремень генератора": (853.71, CAT_PARTS),
    "Ремень вентилятора": (1790.83, CAT_PARTS),
    "Натяжной ролик генератора": (4755.00, CAT_PARTS),
    "Натяжной ролик вентилятора": (4146.67, CAT_PARTS),
    "Сильфонный компенсатор": (7963.33, CAT_PARTS),
    "Заслонка горного тормоза": (10813.33, CAT_PARTS)
}

def get_tmc_and_notes(h):
    items = []
    notes = []
    if h > 0 and h % 1000 == 0: notes.append("🔧 ОБЯЗАТЕЛЬНО: Регулировка клапанов ДВС")
    if h % 250 == 0 or h == 100:
        items += [["Масляный фильтр 4190001633", 2], ["Фильтр топливный г.оч (на раме)", 2],
                  ["Фильтр топливный г.оч (557)", 1], ["Фильтр топливный т.оч (555)", 1],
                  ["Масло моторное (Grizzli), л", 30]]
    if h in [500, 1500, 2500, 3500, 4500, 5500]:
        notes.append("💻 СЕРВИС: Диагностика и калибровка АКПП")
        items += [["Фильтр АКПП (389-1085)", 1], ["Масло АКПП (ATF), л", 35], ["Воздушный фильтр", 1], ["Масло М-8ДМ, л", 4], ["Смазка LX EP2, кг", 1.5]]
    if h in [1000, 2000, 3000, 4000, 5000, 6000]:
        items += [["Фильтр салона", 1], ["Фильтр кондиционера", 1], ["Воздушный фильтр", 1], ["Масло М-8ДМ, л", 4]]
    if h in [3000, 6000]:
        items += [["Масло гидравлическое (HVLP 46), л", 160], ["Фильтр гидросистемы", 1], ["Фильтр сапуна гидробака", 1], ["Антифриз G-12 (красный), л", 60]]
    if h in [2000, 4000, 6000]:
        items += [["Масло трансмиссионное (75W-90), л", 70], ["Сильфонный компенсатор", 1]]
    if h == 6000:
        items += [["Ремень генератора", 1], ["Ремень вентилятора", 1], ["Натяжной ролик генератора", 1], ["Натяжной ролик вентилятора", 1], ["Заслонка горного тормоза", 1], ["Фильтр сапуна бака", 1], ["Фильтр осушитель", 1]]
    return items, notes

st.set_page_config(page_title="ChebTrade-Synergy Analytics", layout="wide")
st.title("🚜 Калькулятор TCO: SANY SCT90 / LGMG")

with st.sidebar:
    st.header("⚙️ Управление")
    num_trucks = st.number_input("Машин в парке", 1, 100, 14)
    labor_rate = st.radio("Стоимость нормо-часа", [3300, 4200])
    tele_on = st.toggle("Телеметрия Synergy", value=True)
    show_vat = st.checkbox("Показать с НДС (22%)", value=False)

current_h = st.select_slider("Наработка (моточасы):", options=list(range(0, 6001, 250)) + [100])
if current_h == 0: current_h = 100

vat_m = VAT_RATE if show_vat else 1.0

# РАСЧЕТ НАКОПИТЕЛЬНЫМ ИТОГОМ И КУМУЛЯТИВ ТМЦ
total_tmc_acc = 0
total_labor_acc = 0
cumulative_parts = {}

for h in range(100, current_h + 1, 50):
    if h in [100] or (h > 0 and h % 250 == 0):
        items_acc, _ = get_tmc_and_notes(h)
        for name, qty in items_acc:
            total_tmc_acc += PRICES[name][0] * qty
            cumulative_parts[name] = cumulative_parts.get(name, 0) + qty
        l_hrs = 26 if h % 6000 == 0 else (20 if h % 3000 == 0 else (12 if h % 500 == 0 else 6))
        total_labor_acc += l_hrs * labor_rate

tele_acc = (current_h / HOURS_PER_MONTH) * TELEMETRY_MONTHLY if tele_on else 0
grand_tco = (total_tmc_acc + total_labor_acc + tele_acc)

# Текущее ТО
curr_tmc_list, curr_notes = get_tmc_and_notes(current_h)
curr_tmc_cost = sum([PRICES[name][0] * qty for name, qty in curr_tmc_list])
curr_l_hrs = 26 if current_h % 6000 == 0 else (20 if current_h % 3000 == 0 else (12 if current_h % 500 == 0 else 6))
curr_labor_cost = curr_l_hrs * labor_rate

st.divider()
# МЕТРИКИ
c1, c2, c3, c4 = st.columns(4)
c1.metric("Работы (Текущее ТО)", f"{curr_labor_cost * num_trucks * vat_m:,.0f} ₽")
c2.metric("ТМЦ (Текущее ТО)", f"{curr_tmc_cost * num_trucks * vat_m:,.0f} ₽")
c3.metric("Затрачено на 1 машину", f"{grand_tco * vat_m:,.0f} ₽")
c4.metric("Телеметрия (Парк)", f"{tele_acc * num_trucks * vat_m:,.0f} ₽")

if curr_notes: st.info("\n".join(curr_notes))

if current_h == 6000:
    st.write("---")
    if not tele_on: st.error(f"⚠️ РИСК: Прогноз ремонта АКПП на 9000 м.ч. Бюджет: + {AKPP_REPAIR_BASE * num_trucks * vat_m:,.0f} ₽")
    else: st.success(f"✅ КОНТРОЛЬ: Ресурс АКПП продлен до 15000 м.ч. Экономия: {AKPP_REPAIR_BASE * vat_m:,.0f} ₽")

# ТАБЛИЦА ТМЦ С КАТЕГОРИЯМИ И КУМУЛЯТИВОМ
st.subheader(f"📋 Детализация ТМЦ на {current_h} м.ч.")
if curr_tmc_list:
    data = []
    for name, qty in curr_tmc_list:
        price_unit, cat = PRICES[name]
        data.append({
            "Категория": cat,
            "Наименование": name,
            "Кол-во на ТО": qty,
            "Цена за ед.": price_unit * vat_m,
            "Итого (Текущее)": price_unit * qty * vat_m,
            "Всего потрачено (кумулятив)": cumulative_parts.get(name, 0)
        })
    
    df_res = pd.DataFrame(data).sort_values(["Категория", "Наименование"])
    
    # Отображение по категориям
    for category in [CAT_FILTERS, CAT_OILS, CAT_PARTS]:
        df_cat = df_res[df_res["Категория"] == category]
        if not df_cat.empty:
            st.write(f"#### {category}")
            st.table(df_cat.drop(columns=["Категория"]).style.format("{:,.2f}", subset=["Цена за ед.", "Итого (Текущее)"]))

st.caption(f"НДС: 22%. Ставка: {labor_rate} руб/час. Наработка: {HOURS_PER_MONTH} м.ч./мес.")
