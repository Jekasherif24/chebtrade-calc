st.set_page_config(
    page_title="ChebTrade-Synergy: Аналитика TCO",
    page_icon="⚙️", # Здесь будет значок шестеренки во вкладке браузера
    layout="wide",
    initial_sidebar_state="expanded"
)

import streamlit as st
import pandas as pd

# Константы
TELEMETRY_MONTHLY = 5000
HOURS_PER_MONTH = 500
AKPP_REPAIR_BASE = 1200000 
VAT_RATE = 1.22  # НДС 22%

# Категории
CAT_FILTERS = "📦 ФИЛЬТРЫ"
CAT_OILS = "🛢 МАСЛА И ЖИДКОСТИ"
CAT_PARTS = "⚙️ ПРОЧИЕ ЗАПЧАСТИ"

# Справочник ТМЦ
PRICES = {
    "Масляный фильтр": ("4190001633", 758.33, CAT_FILTERS),
    "Фильтр топл. г.оч (рама)": ("4110001939068", 1300.00, CAT_FILTERS),
    "Фильтр топл. г.оч (557)": ("4110001939058", 1650.00, CAT_FILTERS),
    "Фильтр топл. т.оч (555)": ("4110001939059", 2410.00, CAT_FILTERS),
    "Фильтр сапуна топл. бака": ("4110001730", 1200.00, CAT_FILTERS),
    "Воздушный фильтр": ("4190704017", 5983.33, CAT_FILTERS),
    "Фильтр гидросистемы": ("4120001743", 2820.00, CAT_FILTERS),
    "Фильтр сапуна гидробака": ("4120000634", 350.00, CAT_FILTERS),
    "Фильтр салона": ("4190704008001", 630.00, CAT_FILTERS),
    "Фильтр кондиционера": ("4190703955001", 367.00, CAT_FILTERS),
    "Фильтр АКПП": ("4110001023057", 9248.33, CAT_FILTERS),
    "Фильтр осушитель": ("4120001086001", 1567.00, CAT_FILTERS),
    "Масло моторное (Grizzli), л": ("5W-40 API CK-4", 568.49, CAT_OILS),
    "Масло АКПП (ATF), л": ("DEX MULTI", 414.63, CAT_OILS),
    "Масло гидравлическое, л": ("HVLP 46", 353.60, CAT_OILS),
    "Масло трансмиссионное, л": ("75W-90 GL-5", 391.80, CAT_OILS),
    "Масло М-8ДМ, л": ("М-8ДМ", 563.00, CAT_OILS),
    "Антифриз G-12, л": ("Sintec LUX", 350.00, CAT_OILS),
    "Смазка LX EP2, кг": ("EP2", 695.00, CAT_PARTS),
    "Ремень генератора": ("4110002077008", 853.71, CAT_PARTS),
    "Ремень вентилятора": ("4110002077009", 1790.83, CAT_PARTS),
    "Натяжной ролик ген-ра": ("4110002077010", 4755.00, CAT_PARTS),
    "Натяжной ролик вент-ра": ("4110002077011", 4146.67, CAT_PARTS),
    "Сильфонный компенсатор": ("27240105521", 7963.33, CAT_PARTS),
    "Заслонка горного тормоза": ("4110000157", 10813.33, CAT_PARTS)
}

def get_tmc_and_notes(h):
    items, notes = [], []
    if h > 0 and h % 1000 == 0: notes.append("🔧 Регулировка клапанов ДВС")
    if h % 250 == 0 or h == 100:
        items += [["Масляный фильтр", 2], ["Фильтр топл. г.оч (рама)", 2], ["Фильтр топл. г.оч (557)", 1], ["Фильтр топл. т.оч (555)", 1], ["Масло моторное (Grizzli), л", 30]]
    if h in [500, 1500, 2500, 3500, 4500, 5500]:
        notes.append("💻 Диагностика и калибровка АКПП")
        items += [["Фильтр АКПП", 1], ["Масло АКПП (ATF), л", 35], ["Воздушный фильтр", 1], ["Масло М-8ДМ, л", 4], ["Смазка LX EP2, кг", 1.5]]
    if h in [1000, 2000, 3000, 4000, 5000, 6000]:
        items += [["Фильтр салона", 1], ["Фильтр кондиционера", 1], ["Воздушный фильтр", 1], ["Масло М-8ДМ, л", 4]]
    if h in [3000, 6000]:
        items += [["Масло гидравлическое, л", 160], ["Фильтр гидросистемы", 1], ["Фильтр сапуна гидробака", 1], ["Антифриз G-12, л", 60]]
    if h in [2000, 4000, 6000]:
        items += [["Масло трансмиссионное, л", 70], ["Сильфонный компенсатор", 1]]
    if h == 6000:
        items += [["Ремень генератора", 1], ["Ремень вентилятора", 1], ["Натяжной ролик ген-ра", 1], ["Натяжной ролик вент-ра", 1], ["Заслонка горного тормоза", 1], ["Фильтр сапуна топл. бака", 1], ["Фильтр осушитель", 1]]
    return items, notes

st.set_page_config(page_title="ChebTrade Аналитика", layout="wide")
st.title("🚜 Аналитика затрат парка ChebTrade")

with st.sidebar:
    st.header("⚙️ Управление")
    num_trucks = st.number_input("Машин в парке", 1, 100, 14)
    labor_rate = st.radio("Ставка нормо-часа", [3300, 4200])
    tele_on = st.toggle("Телеметрия Synergy", value=True)
    show_vat = st.checkbox("Показать с НДС (22%)", value=True)

current_h = st.select_slider("Наработка (моточасы):", options=list(range(0, 6001, 250)) + [100])
if current_h == 0: current_h = 100
vat_m = VAT_RATE if show_vat else 1.0

# НАКОПИТЕЛЬНЫЙ РАСЧЕТ
acc_tmc, acc_labor, cumulative_qty = 0, 0, {}
for h in range(100, current_h + 1, 50):
    if h in [100] or (h > 0 and h % 250 == 0):
        it, _ = get_tmc_and_notes(h)
        for name, qty in it:
            acc_tmc += PRICES[name][1] * qty
            cumulative_qty[name] = cumulative_qty.get(name, 0) + qty
        l_h = 26 if h % 6000 == 0 else (20 if h % 3000 == 0 else (12 if h % 500 == 0 else 6))
        acc_labor += l_h * labor_rate

tele_cost_acc = (current_h / HOURS_PER_MONTH) * TELEMETRY_MONTHLY if tele_on else 0

# ТЕКУЩЕЕ ТО
curr_tmc_it, curr_notes = get_tmc_and_notes(current_h)
curr_tmc_sum = sum([PRICES[n][1] * q for n, q in curr_tmc_it])
curr_l_h = 26 if current_h % 6000 == 0 else (20 if current_h % 3000 == 0 else (12 if current_h % 500 == 0 else 6))
curr_lab_sum = curr_l_h * labor_rate

st.divider()
# БЛОК 1: НА ОДНУ МАШИНУ
st.subheader("👤 Затраты на 1 единицу техники")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Накоплено: ТМЦ", f"{acc_tmc * vat_m:,.0f} ₽")
c2.metric("Накоплено: РАБОТЫ", f"{acc_labor * vat_m:,.0f} ₽")
c3.metric("ВСЕГО (TCO)", f"{(acc_tmc + acc_labor + tele_cost_acc) * vat_m:,.0f} ₽")
c4.metric("Телеметрия (итого)", f"{tele_cost_acc * vat_m:,.0f} ₽")

# БЛОК 2: НА ВЕСЬ ПАРК (ТО, ЧТО ВЫ ПРОСИЛИ)
st.subheader(f"🏢 ИТОГО ПО ВСЕМУ ПАРКУ ({num_trucks} машин)")
f1, f2, f3 = st.columns(3)
# Текущий заезд для парка
f1.metric("ТМЦ (Текущее ТО)", f"{curr_tmc_sum * num_trucks * vat_m:,.0f} ₽")
f2.metric("РАБОТЫ (Текущее ТО)", f"{curr_lab_sum * num_trucks * vat_m:,.0f} ₽")
f3.metric("ИТОГО ЗА ТЕКУЩЕЕ ТО", f"{(curr_tmc_sum + curr_lab_sum) * num_trucks * vat_m:,.0f} ₽")

f4, f5, f6 = st.columns(3)
# Накопленные затраты для парка
f4.metric("Накоплено: ТМЦ (Парк)", f"{acc_tmc * num_trucks * vat_m:,.0f} ₽")
f5.metric("Накоплено: РАБОТЫ (Парк)", f"{acc_labor * num_trucks * vat_m:,.0f} ₽")
f6.metric("ОБЩИЕ ЗАТРАТЫ ПАРКА", f"{(acc_tmc + acc_labor + tele_cost_acc) * num_trucks * vat_m:,.0f} ₽")

if curr_notes: st.warning(" | ".join(curr_notes))

# ДЕТАЛИЗАЦИЯ ТМЦ
st.subheader(f"📋 Ведомость ТМЦ на {current_h} м.ч.")
if curr_tmc_it:
    res = []
    for n, q in curr_tmc_it:
        art, pr, cat = PRICES[n]
        res.append({
            "Категория": cat, "Артикул": art, "Наименование": n, "Кол-во (ТО)": q,
            "Цена (ед)": pr * vat_m, "Сумма (за ТО)": pr * q * vat_m, "Итого на ПАРК": pr * q * num_trucks * vat_m, "Всего потрачено (шт/л)": cumulative_qty.get(n, 0)
        })
    df = pd.DataFrame(res).sort_values(["Категория", "Наименование"])
    for cat in [CAT_FILTERS, CAT_OILS, CAT_PARTS]:
        df_c = df[df["Категория"] == cat]
        if not df_c.empty:
            st.write(f"### {cat}")
            st.table(df_c.drop(columns="Категория").style.format("{:,.2f}", subset=["Цена (ед)", "Сумма (за ТО)", "Итого на ПАРК"]))

if current_h == 6000:
    st.write("---")
    if not tele_on: st.error(f"🚨 РИСК: Ремонт АКПП на 9000 м.ч. Убыток парка: +{(AKPP_REPAIR_BASE * num_trucks * vat_m):,.0f} ₽")
    else: st.success("🟢 СИНЕРГИЯ: Ресурс парка под защитой до 15000 м.ч.")

