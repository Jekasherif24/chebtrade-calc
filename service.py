import streamlit as st
import pandas as pd

# --- КОНСТАНТЫ И НАСТРОЙКИ ---
TELEMETRY_MONTHLY = 5000
HOURS_PER_MONTH = 500
AKPP_REPAIR_COST = 1200000 
VAT_RATE = 1.22  # НДС 22%

# Конфигурация страницы
st.set_page_config(
    page_title="ChebTrade-Synergy: Аналитика TCO",
    page_icon="🚜",
    layout="wide"
)

# Категории ТМЦ
CAT_FILTERS = "📦 ФИЛЬТРЫ"
CAT_OILS = "🛢 МАСЛА И ЖИДКОСТИ"
CAT_PARTS = "⚙️ ПРОЧИЕ ЗАПЧАСТИ"

# --- СПРАВОЧНИК ТМЦ (Артикул, Цена без НДС, Категория) ---
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
    "Фильтр АКПП (389-1085)": ("4110001023057", 9248.33, CAT_FILTERS),
    "Фильтр осушитель": ("4120001086001", 1567.00, CAT_FILTERS),
    "Масло моторное (Grizzli), л": ("5W-40 API CK-4", 568.49, CAT_OILS),
    "Масло АКПП (ATF), л": ("DEX MULTI", 414.63, CAT_OILS),
    "Масло гидравлическое, л": ("HVLP 46", 353.60, CAT_OILS),
    "Масло трансмиссионное, л": ("75W-90 GL-5", 391.80, CAT_OILS),
    "Масло М-8ДМ, л": ("М-8ДМ", 563.00, CAT_OILS),
    "Антифриз G-12 (красный), л": ("Sintec LUX", 350.00, CAT_OILS),
    "Смазка LX EP2, кг": ("LX EP2", 695.00, CAT_PARTS),
    "Ремень генератора": ("4110002077008", 853.71, CAT_PARTS),
    "Ремень вентилятора": ("4110002077009", 1790.83, CAT_PARTS),
    "Натяжной ролик генератора": ("4110002077010", 4755.00, CAT_PARTS),
    "Натяжной ролик вентилятора": ("4110002077011", 4146.67, CAT_PARTS),
    "Сильфонный компенсатор": ("27240105521", 7963.33, CAT_PARTS),
    "Заслонка горного тормоза": ("4110000157", 10813.33, CAT_PARTS)
}

def get_tmc_and_notes(h):
    items, notes = [], []
    if h > 0 and h % 1000 == 0:
        notes.append("🔧 ОБЯЗАТЕЛЬНО: Регулировка клапанов ДВС")
    
    # База каждые 250 м.ч.
    if h % 250 == 0 or h == 100:
        items += [["Масляный фильтр", 2], ["Фильтр топл. г.оч (рама)", 2], ["Фильтр топл. г.оч (557)", 1], ["Фильтр топл. т.оч (555)", 1], ["Масло моторное (Grizzli), л", 30]]
    
    # Цикл АКПП
    if h in [500, 1500, 2500, 3500, 4500, 5500]:
        notes.append("💻 СЕРВИС: Диагностика и калибровка АКПП")
        items += [["Фильтр АКПП (389-1085)", 1], ["Масло АКПП (ATF), л", 35], ["Воздушный фильтр", 1], ["Масло М-8ДМ, л", 4], ["Смазка LX EP2, кг", 1.5]]
    
    # Гидравлика и Салон
    if h in [1000, 2000, 3000, 4000, 5000, 6000]:
        items += [["Фильтр салона", 1], ["Фильтр кондиционера", 1], ["Воздушный фильтр", 1], ["Масло М-8ДМ, л", 4]]
    
    if h in [3000, 6000]:
        items += [["Масло гидравлическое, л", 160], ["Фильтр гидросистемы", 1], ["Фильтр сапуна гидробака", 1], ["Антифриз G-12 (красный), л", 60]]
    
    if h in [2000, 4000, 6000]:
        items += [["Масло трансмиссионное, л", 70], ["Сильфонный компенсатор", 1]]
        
    if h == 6000:
        items += [["Ремень генератора", 1], ["Ремень вентилятора", 1], ["Натяжной ролик генератора", 1], ["Натяжной ролик вентилятора", 1], ["Заслонка горного тормоза", 1], ["Фильтр сапуна топл. бака", 1], ["Фильтр осушитель", 1]]
        notes.append("📢 ТО-6000: Замена ремней, роликов и элементов выхлопной системы")
        
    return items, notes

# --- ИНТЕРФЕЙС ---
st.title("🚜 ChebTrade-Synergy: Система управления парком")

c_img1, c_img2 = st.columns(2)
c_img1.image("https://i.ytimg.com/vi/OpHJWCBvfAY/maxresdefault.jpg", caption="LGMG SMT96", use_container_width=True)
c_img2.image("https://files.glotr.uz/company/000/032/458/products/2023/03/25/2023-03-25-15-18-06-470337-1d17e8c8aecfe1bb10ec6446f3fbbcdb.webp?_=ozb9y", caption="SANY SCT90", use_container_width=True)

with st.sidebar:
    st.header("⚙️ Параметры")
    num_trucks = st.number_input("Машин в парке", 1, 100, 14)
    labor_rate = st.radio("Стоимость нормо-часа", [3300, 4200])
    tele_on = st.toggle("Телеметрия Synergy (5000 ₽/мес)", value=True)
    show_vat = st.checkbox("Показать суммы с НДС (22%)", value=True)

current_h = st.select_slider("Выберите пробег (моточасы):", options=list(range(0, 6001, 250)) + [100])
if current_h == 0: current_h = 100
vat_m = VAT_RATE if show_vat else 1.0

# --- РАСЧЕТЫ ---
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

# Текущее ТО
curr_tmc_it, curr_notes = get_tmc_and_notes(current_h)
curr_tmc_sum = sum([PRICES[n][1] * q for n, q in curr_tmc_it])
curr_l_h = 26 if current_h % 6000 == 0 else (20 if current_h % 3000 == 0 else (12 if current_h % 500 == 0 else 6))
curr_lab_sum = curr_l_h * labor_rate

# --- ВЫВОД ДАННЫХ ---
st.divider()
st.subheader("📊 Аналитика затрат (на 1 единицу)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Накоплено: ТМЦ", f"{acc_tmc * vat_m:,.0f} ₽")
m2.metric("Накоплено: РАБОТЫ", f"{acc_labor * vat_m:,.0f} ₽")
m3.metric("ИТОГО (TCO)", f"{(acc_tmc + acc_labor + tele_cost_acc) * vat_m:,.0f} ₽")
m4.metric("Телеметрия (всего)", f"{tele_cost_acc * vat_m:,.0f} ₽")

st.subheader(f"🏢 Итого по ПАРКУ ({num_trucks} машин)")
f1, f2, f3 = st.columns(3)
f1.metric("ТМЦ (Текущее ТО)", f"{curr_tmc_sum * num_trucks * vat_m:,.0f} ₽")
f2.metric("РАБОТЫ (Текущее ТО)", f"{curr_lab_sum * num_trucks * vat_m:,.0f} ₽")
f3.metric("ИТОГО ЗА ТО (Парк)", f"{(curr_tmc_sum + curr_lab_sum) * num_trucks * vat_m:,.0f} ₽")

f4, f5, f6 = st.columns(3)
f4.metric("Накоплено: ТМЦ (Парк)", f"{acc_tmc * num_trucks * vat_m:,.0f} ₽")
f5.metric("Накоплено: РАБОТЫ (Парк)", f"{acc_labor * num_trucks * vat_m:,.0f} ₽")
f6.metric("ОБЩИЕ ЗАТРАТЫ ПАРКА", f"{(acc_tmc + acc_labor + tele_cost_acc) * num_trucks * vat_m:,.0f} ₽")

if curr_notes:
    st.info(" | ".join(curr_notes))

# Логика 6000 м.ч.
if current_h == 6000:
    st.write("---")
    if not tele_on:
        st.error(f"🚨 КРИТИЧЕСКИЙ РИСК: Ремонт АКПП наступит при 9000 м.ч. Убыток парка: +{(AKPP_REPAIR_BASE * num_trucks * vat_m):,.0f} ₽")
    else:
        st.success(f"🟢 КОНТРОЛЬ SYNERGY: Ресурс агрегатов продлен до 15000 м.ч. Ваша экономия подтверждена.")

# --- ТАБЛИЦА ТМЦ ---
st.subheader(f"📋 Детализация ТМЦ на текущем ТО ({current_h} м.ч.)")
if curr_tmc_it:
    res = []
    for n, q in curr_tmc_it:
        art, pr, cat = PRICES[n]
        res.append({
            "Категория": cat, "Артикул": art, "Наименование": n, "Кол-во (ТО)": q,
            "Цена (ед)": pr * vat_m, "Сумма (ТО)": pr * q * vat_m, 
            "Сумма ПАРК": pr * q * num_trucks * vat_m, "Всего потрачено (шт/л)": cumulative_qty.get(n, 0)
        })
    df = pd.DataFrame(res).sort_values(["Категория", "Наименование"])
    for cat in [CAT_FILTERS, CAT_OILS, CAT_PARTS]:
        df_c = df[df["Категория"] == cat]
        if not df_c.empty:
            st.write(f"#### {cat}")
            st.table(df_c.drop(columns="Категория").style.format("{:,.2f}", subset=["Цена (ед)", "Сумма (ТО)", "Сумма ПАРК"]))

st.caption(f"НДС: 22%. Ставка часа: {labor_rate} ₽. Расчет: ChebTrade-Synergy.")
