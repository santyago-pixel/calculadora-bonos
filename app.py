import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Bonos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para el dashboard
st.markdown("""
<style>
    /* Forzar tema claro */
    .stApp {
        background-color: white !important;
        color: black !important;
    }
    
    .stApp > div {
        background-color: white !important;
    }
    
    /* Estilos generales */
    .main > div {
        padding-top: 0rem;
    }
    
    /* Eliminar espaciado superior adicional */
    .main .block-container {
        padding-top: 0rem !important;
    }
    
    .main .element-container {
        margin-top: 0rem !important;
    }
    
    /* Eliminar espaciado del primer elemento */
    .main .element-container:first-child {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }
    
    /* Selectores más específicos para eliminar espaciado */
    .main .block-container > div {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    
    .main .block-container > div:first-child {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    
    /* Eliminar espaciado de columnas */
    .main .stColumn {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    
    .main .stColumn:first-child {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    
    /* Eliminar espaciado de contenedores de Streamlit */
    div[data-testid="stMarkdownContainer"] {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }
    
    div[data-testid="stMarkdownContainer"]:first-child {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }
    
    /* Reducir tamaño de títulos y alinear arriba */
    .main h1, .main h2, .main h3, 
    .main .element-container h1, .main .element-container h2, .main .element-container h3,
    .main .block-container h1, .main .block-container h2, .main .block-container h3 {
        margin-top: 0rem !important;
        margin-bottom: 0.5rem !important;
        padding-top: 0rem !important;
        font-size: 1.2rem !important;
        line-height: 1.2 !important;
    }
    
    .main h1, .main .element-container h1, .main .block-container h1 {
        font-size: 1.4rem !important;
    }
    
    .main h2, .main .element-container h2, .main .block-container h2 {
        font-size: 1.2rem !important;
    }
    
    .main h3, .main .element-container h3, .main .block-container h3 {
        font-size: 1.1rem !important;
    }
    
    /* Selectores más específicos para Streamlit */
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        margin-top: 0rem !important;
        margin-bottom: 0.5rem !important;
        padding-top: 0rem !important;
        font-size: 1.2rem !important;
        line-height: 1.2 !important;
    }
    
    /* Reducir espaciado en sidebar */
    .css-1d391kg {
        padding-top: 0.5rem !important;
    }
    
    .css-1d391kg .element-container {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    .css-1d391kg .stMarkdown {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* Reducir espaciado en sección principal */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    .main .element-container {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* Reducir espaciado entre elementos */
    .stSelectbox, .stDateInput, .stNumberInput, .stButton {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    div[data-testid="stMarkdownContainer"] h1 {
        font-size: 1.4rem !important;
    }
    
    div[data-testid="stMarkdownContainer"] h2 {
        font-size: 1.2rem !important;
    }
    
    div[data-testid="stMarkdownContainer"] h3 {
        font-size: 1.1rem !important;
    }
    
    /* Sidebar */
    .stSidebar {
        background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
        color: white;
    }
    
    /* Bajar el título del sidebar */
    .stSidebar h1 {
        margin-top: 0.8rem !important;
        padding-top: 0.8rem !important;
    }
    
    .stSidebar .element-container:first-child h1 {
        margin-top: 0.8rem !important;
        padding-top: 0.8rem !important;
    }
    
    .stSidebar .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    .stSidebar .stSelectbox label {
        color: white !important;
        font-weight: 600;
    }
    
    .stSidebar .stDateInput > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    .stSidebar .stDateInput label {
        color: white !important;
        font-weight: 600;
    }
    
    .stSidebar .stDateInput > div > div > input {
        color: white !important;
    }
    
    .stSidebar .stDateInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    .stSidebar .stNumberInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    .stSidebar .stNumberInput label {
        color: white !important;
        font-weight: 600;
    }
    
    .stSidebar .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
    }
    
    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Ocultar botones +/- del number input */
    .stNumberInput button {
        display: none !important;
    }
    
    /* Cards de métricas */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        height: 120px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.2;
        text-align: center;
    }
    
    /* Grid de métricas */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 0.75rem;
    }
    
    /* Info bullets */
    .info-bullets {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .info-bullets h4 {
        color: #475569;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .info-bullets p {
        color: #64748b;
        margin: 0.25rem 0;
        font-size: 0.85rem;
    }
    
    /* Future content */
    .future-content {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .future-content h3 {
        color: #1e293b;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    
    .future-content ul {
        color: #64748b;
        margin: 0;
        padding-left: 1.5rem;
    }
    
    .future-content li {
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    /* Cash flow table */
    .cashflow-table {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Ocultar bordes del dataframe */
    .stDataFrame {
        border: none !important;
    }
    
    .stDataFrame > div {
        border: none !important;
    }
    
    .stDataFrame table {
        border: none !important;
    }
    
    .stDataFrame th, .stDataFrame td {
        border: none !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    
    .stDataFrame th {
        background-color: #f8fafc !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    
    /* Ocultar menú del dataframe */
    .stDataFrame > div > div:first-child {
        display: none !important;
    }
    
    /* Ocultar barra de GitHub */
    .stDeployButton {
        display: none !important;
    }
    
    /* Ocultar elementos de GitHub/Streamlit Cloud */
    [data-testid="stDeployButton"] {
        display: none !important;
    }
    
    /* Ocultar cualquier elemento de deploy */
    .stDeployButton,
    .deploy-button,
    .github-button {
        display: none !important;
    }
    
    /* Ocultar barra superior de Streamlit Cloud */
    .stApp > header {
        display: none !important;
    }
    
    /* Ocultar elementos de la barra superior */
    .stApp > div > div > div:first-child {
        display: none !important;
    }
    
    /* Ocultar elementos específicos de GitHub */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    .stApp > div > div > div:first-child > div {
        display: none !important;
    }
    
    /* Ocultar cualquier elemento con texto "Deploy" o "GitHub" */
    a[href*="github"],
    a[href*="deploy"],
    button[title*="Deploy"],
    button[title*="GitHub"] {
        display: none !important;
    }
    
    /* Reducir tamaño de fuentes en widgets de TradingView */
    iframe[src*="tradingview"] {
        font-size: 10px !important;
    }
    
    /* Reducir tamaño de fuentes en contenedores de TradingView */
    div[data-testid="stIFrame"] iframe {
        font-size: 10px !important;
    }
    
    /* Reducir tamaño de fuentes en elementos de TradingView */
    .tradingview-widget-container {
        font-size: 10px !important;
    }
    
    .tradingview-widget-container * {
        font-size: 10px !important;
    }
    
    /* Reducir tamaño de fuentes en iframes de TradingView */
    iframe[title*="TradingView"] {
        font-size: 10px !important;
    }
    
    /* Reducir tamaño de fuentes en todos los iframes */
    iframe {
        font-size: 10px !important;
    }
    
    /* Reducir tamaño de fuentes específicamente en el widget Market Data */
    .tradingview-widget-container[style*="height: 800px"] {
        font-size: 8px !important;
    }
    
    .tradingview-widget-container[style*="height: 800px"] * {
        font-size: 8px !important;
    }
    
    /* Reducir tamaño de fuentes en el widget Market Data */
    div[data-testid="stIFrame"] iframe[src*="market-overview"] {
        font-size: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# Función para calcular el próximo día hábil
def get_next_business_day():
    today = datetime.now()
    next_day = today + timedelta(days=1)
    
    # Si es sábado (5) o domingo (6), ir al lunes
    if next_day.weekday() == 5:  # Sábado
        next_day += timedelta(days=2)
    elif next_day.weekday() == 6:  # Domingo
        next_day += timedelta(days=1)
    
    return next_day

# Función para calcular días entre fechas según base de cálculo
def calcular_dias(fecha1, fecha2, base_calculo):
    # Convertir ambas fechas a datetime para asegurar compatibilidad
    if hasattr(fecha1, 'date'):
        fecha1 = fecha1.date()
    if hasattr(fecha2, 'date'):
        fecha2 = fecha2.date()
    
    if base_calculo == "30/360":
        d1, m1, y1 = fecha1.day, fecha1.month, fecha1.year
        d2, m2, y2 = fecha2.day, fecha2.month, fecha2.year
        
        # Ajuste para 30/360
        if d1 == 31:
            d1 = 30
        if d2 == 31 and d1 == 30:
            d2 = 30
        
        dias = (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
        return dias
    elif base_calculo == "ACT/360":
        return (fecha2 - fecha1).days
    elif base_calculo == "ACT/365":
        return (fecha2 - fecha1).days
    elif base_calculo == "ACT/ACT":
        return (fecha2 - fecha1).days
    else:
        return (fecha2 - fecha1).days

# Función para calcular YTM usando Newton-Raphson
def calcular_ytm(precio_dirty, flujos, fechas, fecha_liquidacion, base_calculo="ACT/365", periodicidad=2):
    # Convertir fecha_liquidacion a date si es datetime
    fecha_liq = fecha_liquidacion
    if hasattr(fecha_liq, 'date'):
        fecha_liq = fecha_liq.date()
    
    def npv(rate):
        total = 0
        for i, (flujo, fecha) in enumerate(zip(flujos, fechas)):
            dias = calcular_dias(fecha_liq, fecha, base_calculo)
            if base_calculo == "30/360":
                factor_descuento = (1 + rate) ** (dias / 360)
            elif base_calculo == "ACT/360":
                factor_descuento = (1 + rate) ** (dias / 360)
            elif base_calculo == "ACT/365":
                factor_descuento = (1 + rate) ** (dias / 365)
            elif base_calculo == "ACT/ACT":
                factor_descuento = (1 + rate) ** (dias / 365)
            else:
                factor_descuento = (1 + rate) ** (dias / 365)
            total += flujo / factor_descuento
        return total - precio_dirty
    
    def npv_derivative(rate):
        total = 0
        for i, (flujo, fecha) in enumerate(zip(flujos, fechas)):
            dias = calcular_dias(fecha_liq, fecha, base_calculo)
            if base_calculo == "30/360":
                factor_descuento = (1 + rate) ** (dias / 360)
                derivada = -flujo * (dias / 360) * (1 + rate) ** (dias / 360 - 1)
            elif base_calculo == "ACT/360":
                factor_descuento = (1 + rate) ** (dias / 360)
                derivada = -flujo * (dias / 360) * (1 + rate) ** (dias / 360 - 1)
            elif base_calculo == "ACT/365":
                factor_descuento = (1 + rate) ** (dias / 365)
                derivada = -flujo * (dias / 365) * (1 + rate) ** (dias / 365 - 1)
            elif base_calculo == "ACT/ACT":
                factor_descuento = (1 + rate) ** (dias / 365)
                derivada = -flujo * (dias / 365) * (1 + rate) ** (dias / 365 - 1)
            else:
                factor_descuento = (1 + rate) ** (dias / 365)
                derivada = -flujo * (dias / 365) * (1 + rate) ** (dias / 365 - 1)
            total += derivada
        return total
    
    # Método de Newton-Raphson
    rate = 0.05  # Tasa inicial
    tolerance = 1e-8
    max_iterations = 100
    
    for i in range(max_iterations):
        npv_val = npv(rate)
        if abs(npv_val) < tolerance:
            break
    
        derivative = npv_derivative(rate)
        if abs(derivative) < 1e-12:
            break
    
        rate = rate - npv_val / derivative
    
    # Si no converge, usar búsqueda binaria
    if abs(npv(rate)) > tolerance:
        low, high = 0.0, 1.0
        for _ in range(100):
            mid = (low + high) / 2
            if npv(mid) > 0:
                low = mid
            else:
                high = mid
            if high - low < tolerance:
                break
        rate = (low + high) / 2
    
    return rate

# Función para calcular duración Macaulay
def calcular_duracion_macaulay(flujos, fechas, fecha_liquidacion, ytm, base_calculo="ACT/365"):
    # Convertir fecha_liquidacion a date si es datetime
    fecha_liq = fecha_liquidacion
    if hasattr(fecha_liq, 'date'):
        fecha_liq = fecha_liq.date()
    
    pv_total = 0
    pv_weighted = 0
    
    for flujo, fecha in zip(flujos, fechas):
        dias = calcular_dias(fecha_liq, fecha, base_calculo)
        if base_calculo == "30/360":
            factor_descuento = (1 + ytm) ** (dias / 360)
        elif base_calculo == "ACT/360":
            factor_descuento = (1 + ytm) ** (dias / 360)
        elif base_calculo == "ACT/365":
            factor_descuento = (1 + ytm) ** (dias / 365)
        elif base_calculo == "ACT/ACT":
            factor_descuento = (1 + ytm) ** (dias / 365)
        else:
            factor_descuento = (1 + ytm) ** (dias / 365)
        
        pv = flujo / factor_descuento
        pv_total += pv
        pv_weighted += pv * (dias / 365)
    
    if pv_total == 0:
        return 0
    
    return pv_weighted / pv_total

# Función para calcular duración modificada
def calcular_duracion_modificada(duracion_macaulay, ytm, periodicidad):
    return duracion_macaulay / (1 + ytm / periodicidad)

# Función para calcular intereses corridos
def calcular_intereses_corridos(fecha_liquidacion, fecha_ultimo_cupon, tasa_cupon, capital_residual, base_calculo="ACT/365"):
    # Convertir fecha_liquidacion a date si es datetime
    fecha_liq = fecha_liquidacion
    if hasattr(fecha_liq, 'date'):
        fecha_liq = fecha_liq.date()
    
    dias = calcular_dias(fecha_ultimo_cupon, fecha_liq, base_calculo)
    if base_calculo == "30/360":
        return (tasa_cupon * capital_residual) / 360 * dias
    elif base_calculo == "ACT/360":
        return (tasa_cupon * capital_residual) / 360 * dias
    elif base_calculo == "ACT/365":
        return (tasa_cupon * capital_residual) / 365 * dias
    elif base_calculo == "ACT/ACT":
        return (tasa_cupon * capital_residual) / 365 * dias
    else:
        return (tasa_cupon * capital_residual) / 365 * dias

# Función para encontrar el último cupón
def encontrar_ultimo_cupon(fecha_liquidacion, fechas_cupones):
    fechas_anteriores = [fecha for fecha in fechas_cupones if fecha <= fecha_liquidacion]
    if not fechas_anteriores:
        return None
    return max(fechas_anteriores)

# Función para calcular vida media
def calcular_vida_media(flujos_capital, fechas, fecha_liquidacion, base_calculo="ACT/365"):
    # Convertir fecha_liquidacion a date si es datetime
    fecha_liq = fecha_liquidacion
    if hasattr(fecha_liq, 'date'):
        fecha_liq = fecha_liq.date()
    
    if not flujos_capital or sum(flujos_capital) == 0:
        return 0
    
    total_capital = sum(flujos_capital)
    vida_media = 0
    
    for flujo, fecha in zip(flujos_capital, fechas):
        if flujo > 0:
            dias = calcular_dias(fecha_liq, fecha, base_calculo)
            peso = flujo / total_capital
            vida_media += peso * (dias / 365)
    
    return vida_media

# Función para encontrar el próximo cupón
def encontrar_proximo_cupon(fecha_liquidacion, fechas_cupones):
    fechas_futuras = [fecha for fecha in fechas_cupones if fecha > fecha_liquidacion]
    if not fechas_futuras:
        return None
    return min(fechas_futuras)

# Función para encontrar el cupón vigente
def encontrar_cupon_vigente(fecha_liquidacion, flujos):
    """
    Encuentra el cupón vigente basado en la fecha de liquidación.
    Busca la fila cuya fecha es la inmediatamente anterior a la fecha de liquidación.
    """
    # Convertir fecha_liquidacion a date si es datetime
    fecha_liq = fecha_liquidacion
    if hasattr(fecha_liq, 'date'):
        fecha_liq = fecha_liq.date()
    
    # Filtrar fechas anteriores o iguales a la fecha de liquidación
    fechas_anteriores = []
    for flujo in flujos:
        fecha_flujo = flujo['fecha']
        if hasattr(fecha_flujo, 'date'):
            fecha_flujo = fecha_flujo.date()
        
        if fecha_flujo <= fecha_liq:
            fechas_anteriores.append((fecha_flujo, flujo['cupon_vigente']))
    
    if not fechas_anteriores:
        return 0.0  # Valor por defecto si no se encuentra
    
    # Encontrar la fecha más cercana (inmediatamente anterior)
    fecha_mas_cercana = max(fechas_anteriores, key=lambda x: x[0])
    return fecha_mas_cercana[1]

# Función para encontrar la fecha de vencimiento
def encontrar_fecha_vencimiento(flujos):
    """
    Encuentra la fecha de vencimiento del bono (última fecha de los flujos).
    """
    if not flujos:
        return None
    
    # Encontrar la fecha máxima entre todos los flujos
    fechas = [flujo['fecha'] for flujo in flujos]
    fecha_vencimiento = max(fechas)
    
    return fecha_vencimiento

# Cargar datos del Excel
try:
    df = pd.read_excel('bonos_flujos.xlsx', engine='openpyxl')
    
    # Los tipos de bonos se generarán automáticamente después de procesar los bonos
    
    # Procesar bonos
    bonos = []
    current_bono = None
    
    # No procesar ningún bono antes del bucle principal
    
    for index, row in df.iterrows():
        # Verificar si es el inicio de un nuevo bono (cualquier carácter que no sea fecha en columna A)
        if pd.notna(row.iloc[0]) and not isinstance(row.iloc[0], datetime):
            if current_bono:
                bonos.append(current_bono)
            
            # Función auxiliar para convertir a float de forma segura
            def safe_float(value, default=0):
                if pd.isna(value):
                    return default
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default
            
            current_bono = {
                'nombre': str(row.iloc[0]),
                'base_calculo': str(row.iloc[1]) if pd.notna(row.iloc[1]) else "ACT/365",
                'periodicidad': int(row.iloc[2]) if pd.notna(row.iloc[2]) else 2,
                'tipo_bono': str(row.iloc[3]) if pd.notna(row.iloc[3]) else "General",
                'tasa_cupon': safe_float(row.iloc[4], 0.05),
                'ticker': str(row.iloc[4]) if pd.notna(row.iloc[4]) else "SPX500",  # Columna E - ticker
                'flujos': []
            }
        elif current_bono and pd.notna(row.iloc[0]) and isinstance(row.iloc[0], datetime):
            # Es una fecha, agregar flujo
            fecha = row.iloc[0]
            
            # Función auxiliar para convertir a float de forma segura
            def safe_float(value, default=0):
                if pd.isna(value):
                    return default
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default
            
            cupon = safe_float(row.iloc[2])  # Columna C
            capital = safe_float(row.iloc[3])  # Columna D
            total = safe_float(row.iloc[4])  # Columna E
            cupon_vigente = safe_float(row.iloc[1])  # Columna B - cupón vigente
            
            current_bono['flujos'].append({
                'fecha': fecha,
                'cupon': cupon,
                'capital': capital,
                'total': total,
                'cupon_vigente': cupon_vigente
            })
    
    if current_bono:
        bonos.append(current_bono)
    
    if not bonos:
        st.error("❌ No se encontraron bonos en el archivo")
        st.stop()
    
    # Generar tipos de bonos automáticamente a partir de los bonos procesados
    tipos_bono = list(set([bono['tipo_bono'] for bono in bonos]))
    tipos_bono.sort()  # Ordenar alfabéticamente
    tipos_bono = ["Todos"] + tipos_bono
    
    # Sidebar
    with st.sidebar:
        st.markdown("# CALCULADORA DE BONOS")
        
        # Filtro por tipo de bono
        tipo_seleccionado = st.selectbox("Tipo de Bono", tipos_bono)
        
        # Filtrar bonos por tipo
        if tipo_seleccionado == "Todos":
            bonos_filtrados = bonos
        else:
            bonos_filtrados = [bono for bono in bonos if bono['tipo_bono'] == tipo_seleccionado]
        
        if not bonos_filtrados:
            st.error("No hay bonos del tipo seleccionado")
            st.stop()
        
        # Selección de bono
        nombres_bonos = [bono['nombre'] for bono in bonos_filtrados]
        nombres_bonos.sort()  # Ordenar alfabéticamente
        bono_seleccionado = st.selectbox(
            "Elija un Bono", 
            nombres_bonos,
            index=None,  # Ningún bono seleccionado por defecto
            placeholder="Seleccione un bono..."
        )
        
        # Solo mostrar inputs si hay un bono seleccionado
        if bono_seleccionado:
            # Encontrar el bono seleccionado
            bono_actual = next(bono for bono in bonos_filtrados if bono['nombre'] == bono_seleccionado)
            
            # Inputs
            fecha_liquidacion = st.date_input(
                "Fecha de Liquidación",
                value=get_next_business_day(),
                format="DD/MM/YYYY"
            )
            
            precio_dirty = st.number_input(
                "Precio Dirty (base 100)",
            min_value=0.0,
            max_value=200.0,
            value=100.0,
            step=0.01,
            format="%.2f"
        )
    
            # Botón de cálculo
            calcular = st.button("Calcular", type="primary")
            
            # Mostrar información del bono seleccionado en el sidebar
            st.markdown("---")
            st.markdown("### Información del Bono")
            
            # Mapear periodicidad a texto
            periodicidad_texto = {
                1: "anual",
                2: "semestral", 
                3: "trimestral",
                4: "trimestral",
                6: "bimestral",
                12: "mensual"
            }.get(bono_actual['periodicidad'], f"{bono_actual['periodicidad']} veces al año")
            
            # Calcular fecha de vencimiento
            fecha_vencimiento = encontrar_fecha_vencimiento(bono_actual['flujos'])
            
            # Calcular cupón vigente basado en la fecha actual
            from datetime import date
            cupon_vigente_actual = encontrar_cupon_vigente(date.today(), bono_actual['flujos'])
            
            st.markdown(f"**Nombre:** {bono_actual['nombre']}")
            st.markdown(f"**Vencimiento:** {fecha_vencimiento.strftime('%d/%m/%Y') if fecha_vencimiento else 'N/A'}")
            st.markdown(f"**Tasa de cupón:** {cupon_vigente_actual:.2%}")
            st.markdown(f"**Periodicidad:** {periodicidad_texto}")
            st.markdown(f"**Base de cálculo:** {bono_actual['base_calculo']}")
            st.markdown(f"**Ticker:** {bono_actual['ticker']}")
        else:
            calcular = False
            bono_actual = None
    
    # Contenido principal
    if calcular and bono_seleccionado:
        # Convertir fecha_liquidacion a datetime para comparación
        fecha_liquidacion_dt = pd.to_datetime(fecha_liquidacion)
        
        # Calcular flujos de caja
        flujos = []
        fechas = []
        flujos_capital = []
        
        for flujo in bono_actual['flujos']:
            if flujo['fecha'] > fecha_liquidacion_dt:
                flujos.append(flujo['total'])
                fechas.append(flujo['fecha'])
                flujos_capital.append(flujo['capital'])
        
        if not flujos:
            st.error("❌ No hay flujos futuros para calcular")
            st.stop()
        
        
        # Calcular YTM
        ytm_efectiva = calcular_ytm(
            precio_dirty,
            flujos,
            fechas,
            fecha_liquidacion,
            bono_actual['base_calculo'],
            bono_actual['periodicidad']
        )
        
        # Calcular YTM anualizada según periodicidad
        ytm_anualizada = bono_actual['periodicidad'] * ((1 + ytm_efectiva) ** (1 / bono_actual['periodicidad']) - 1)
        
        # Calcular duración Macaulay
        duracion_macaulay = calcular_duracion_macaulay(
            flujos,
            fechas,
            fecha_liquidacion,
            ytm_efectiva,
            bono_actual['base_calculo']
        )
        
        # Calcular duración modificada
        duracion_modificada = calcular_duracion_modificada(
            duracion_macaulay,
            ytm_anualizada / bono_actual['periodicidad'],
            bono_actual['periodicidad']
        )
        
        # Calcular capital residual
        capital_residual = 100 - sum([flujo['capital'] for flujo in bono_actual['flujos'] if flujo['fecha'] <= fecha_liquidacion_dt])
        
        # Calcular intereses corridos
        fecha_ultimo_cupon = encontrar_ultimo_cupon(fecha_liquidacion_dt, [flujo['fecha'] for flujo in bono_actual['flujos']])
        if fecha_ultimo_cupon:
            intereses_corridos = calcular_intereses_corridos(
                fecha_liquidacion,
                fecha_ultimo_cupon,
                bono_actual['tasa_cupon'],
                capital_residual,
                bono_actual['base_calculo']
            )
        else:
            intereses_corridos = 0
        
        # Calcular precio limpio
        precio_limpio = precio_dirty - intereses_corridos
        
        # Calcular vida media
        vida_media = calcular_vida_media(
            flujos_capital,
            fechas,
            fecha_liquidacion,
            bono_actual['base_calculo']
        )
        
        # Calcular paridad
        valor_tecnico = capital_residual + intereses_corridos
        paridad = precio_limpio / valor_tecnico if valor_tecnico > 0 else 0
        
        # Encontrar próximo cupón
        proximo_cupon = encontrar_proximo_cupon(fecha_liquidacion_dt, [flujo['fecha'] for flujo in bono_actual['flujos']])
        
        # Calcular cupón vigente
        cupon_vigente = encontrar_cupon_vigente(fecha_liquidacion, bono_actual['flujos'])
        
        # Mapear periodicidad a texto
        periodicidad_texto = {
            1: "anual",
            2: "semestral", 
            3: "trimestral",
            4: "trimestral",
            6: "bimestral",
            12: "mensual"
        }.get(bono_actual['periodicidad'], f"{bono_actual['periodicidad']} veces al año")
        
        # Layout principal
        col1, col2 = st.columns([2, 1])
        
        # COLUMNA IZQUIERDA - RESULTADOS
        with col1:
            st.markdown("## Resultados del Análisis")
            
            # Información básica
            st.markdown(f'''
            <div class="info-bullets">
                <h4>Datos para el Cálculo</h4>
                <p><strong>Base de cálculo de días:</strong> {bono_actual['base_calculo']} | <strong>Periodicidad:</strong> {periodicidad_texto}</p>
                <p><strong>Cupón vigente:</strong> {bono_actual['tasa_cupon']:.2%}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Métricas principales
            st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
            
            # Primera fila
            col1_1, col1_2, col1_3, col1_4 = st.columns(4)
            with col1_1:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Precio Limpio</div>
                    <div class="metric-value">{precio_limpio:.4f}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col1_2:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Intereses Corridos</div>
                    <div class="metric-value">{intereses_corridos:.4f}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col1_3:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Capital Residual</div>
                    <div class="metric-value">{capital_residual:.2f}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col1_4:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Cupón Vigente</div>
                    <div class="metric-value">{cupon_vigente:.2%}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Segunda fila
            st.markdown('<div class="metrics-row">', unsafe_allow_html=True)
            col2_1, col2_2, col2_3, col2_4 = st.columns(4)
            
            with col2_1:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">TIR Efectiva</div>
                    <div class="metric-value">{ytm_efectiva:.4%}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2_2:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">TIR {periodicidad_texto.title()}</div>
                    <div class="metric-value">{ytm_anualizada:.4%}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2_3:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Duración Modificada</div>
                    <div class="metric-value">{duracion_modificada:.2f} años</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2_4:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Duración Macaulay</div>
                    <div class="metric-value">{duracion_macaulay:.2f} años</div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Tercera fila
            st.markdown('<div class="metrics-row">', unsafe_allow_html=True)
            col3_1, col3_2, col3_3, col3_4 = st.columns(4)
            
            with col3_1:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Valor Técnico</div>
                    <div class="metric-value">{valor_tecnico:.4f}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3_2:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Paridad</div>
                    <div class="metric-value">{paridad:.4f}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3_3:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Próximo Cupón</div>
                    <div class="metric-value">{proximo_cupon.strftime('%d/%m/%Y') if proximo_cupon else 'N/A'}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3_4:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Vida Media</div>
                    <div class="metric-value">{vida_media:.2f} años</div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        
        # COLUMNA DERECHA - GRÁFICOS DE TRADINGVIEW
        with col2:
            # Espaciado para alinear con las tarjetas
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # Minigráfico del bono seleccionado
            st.markdown(f"## Minigráfico {bono_actual['ticker']}")
            
            bono_html = f"""
            <div class="tradingview-widget-container" style="height: 270px; width: 100%;">
                <div class="tradingview-widget-container__widget" style="height: 100%; width: 100%;"></div>
                <div class="tradingview-widget-copyright">
                    <a href="https://es.tradingview.com/" rel="noopener nofollow" target="_blank">
                        <span class="blue-text">Seguir todas las cotizaciones en TradingView</span>
                    </a>
                </div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
                {{
                "symbol": "{bono_actual['ticker']}",
                "width": "100%",
                "height": "270",
                "locale": "es",
                "dateRange": "12M",
                "colorTheme": "light",
                "isTransparent": false,
                "autosize": false,
                "largeChartUrl": ""
                }}
                </script>
            </div>
            """
            
            st.components.v1.html(bono_html, height=270)
            
            # Tabla de Bonos Argentinos
            st.markdown("## Bonos Argentinos")
            
            bonos_html = """
            <div class="tradingview-widget-container" style="height: 270px; width: 100%; font-size: 8px;">
                <div class="tradingview-widget-container__widget" style="height: 100%; width: 100%; font-size: 8px;"></div>
                <div class="tradingview-widget-copyright" style="font-size: 8px;">
                    <a href="https://www.tradingview.com/markets/" rel="noopener nofollow" target="_blank">
                        <span class="blue-text">Market summary</span>
                    </a>
                    <span class="trademark"> by TradingView</span>
                </div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-quotes.js" async>
                {
                "colorTheme": "light",
                "locale": "es",
                "largeChartUrl": "",
                "isTransparent": false,
                "showSymbolLogo": true,
                "backgroundColor": "#FFFFFF",
                "support_host": "https://www.tradingview.com",
                "width": "100%",
                "height": "270",
                "symbolsGroups": [
                    {
                        "name": "Bonos Argentinos",
                        "symbols": [
                            {
                                "name": "GD30D",
                                "displayName": "GD30D"
                            },
                            {
                                "name": "AL30D",
                                "displayName": "AL30D"
                            },
                            {
                                "name": "GD29D",
                                "displayName": "GD29D"
                            },
                            {
                                "name": "AL29D",
                                "displayName": "AL29D"
                            },
                            {
                                "name": "GD28D",
                                "displayName": "GD28D"
                            },
                            {
                                "name": "AL28D",
                                "displayName": "AL28D"
                            }
                        ]
                    }
                ]
                }
                </script>
            </div>
            """
            
            st.components.v1.html(bonos_html, height=270)
        
        # SECCIÓN FLUJO DE FONDOS - FORMATO MEJORADO
        st.markdown("## Flujo de Fondos")
        
        # Crear DataFrame con formato mejorado
        # Primera fila: fecha de liquidación y precio pagado (negativo)
        fechas_con_liquidacion = [fecha_liquidacion] + fechas
        capital_con_liquidacion = [""] + [f"{c:.1f}" if c > 0 else "" for c in flujos_capital]
        cupon_con_liquidacion = [""] + [f"{f-c:.1f}" for f, c in zip(flujos, flujos_capital)]
        total_con_liquidacion = [f"-{precio_dirty:.1f}"] + [f"{f:.1f}" for f in flujos]
        
        df_simple = pd.DataFrame({
            'Fecha': [f.strftime('%d/%m/%Y') for f in fechas_con_liquidacion],
            'Capital': capital_con_liquidacion,
            'Cupón': cupon_con_liquidacion,
            'Total': total_con_liquidacion
        })
        
        # CSS para mejorar la visualización de la tabla
        st.markdown("""
        <style>
        .stTable {
            border: 2px solid #1f77b4 !important;
            border-radius: 8px !important;
            background-color: #f8f9fa !important;
        }
        .stTable table {
            width: 100% !important;
            border-collapse: collapse !important;
            font-size: 14px !important;
        }
        .stTable th {
            background-color: #1f77b4 !important;
            color: white !important;
            font-weight: bold !important;
            padding: 12px 8px !important;
            text-align: right !important;
            border: 1px solid #ddd !important;
        }
        .stTable td {
            padding: 10px 8px !important;
            text-align: right !important;
            border: 1px solid #ddd !important;
            background-color: white !important;
            color: black !important;
        }
        .stTable td:first-child {
            text-align: center !important;
            font-weight: bold !important;
        }
        
        /* Forzar alineación central para fechas */
        .stTable table tr td:first-child {
            text-align: center !important;
        }
        /* Ocultar la primera columna (índice) */
        .stTable table tr th:first-child,
        .stTable table tr td:first-child {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Mostrar tabla con formato mejorado
        st.table(df_simple)
        
        # Gráfico avanzado del bono seleccionado - Ancho completo
        st.markdown("## Gráfico Avanzado del Bono")
        bono_avanzado_html = f"""
        <div class="tradingview-widget-container" style="height: 500px; width: 100%;">
            <div class="tradingview-widget-container__widget" style="height: 100%; width: 100%;"></div>
            <div class="tradingview-widget-copyright">
                <a href="https://es.tradingview.com/" rel="noopener nofollow" target="_blank">
                    <span class="blue-text">Seguir todas las cotizaciones en TradingView</span>
                </a>
            </div>
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
            {{
            "autosize": false,
            "width": "100%",
            "height": "500",
            "symbol": "{bono_actual['ticker']}",
            "interval": "D",
            "timezone": "America/New_York",
            "theme": "light",
            "style": "2",
            "locale": "es",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "hide_top_toolbar": false,
            "hide_legend": false,
            "hide_volume": true,
            "save_image": false,
            "container_id": "tradingview_widget_bono_avanzado"
            }}
            </script>
        </div>
        """
        st.components.v1.html(bono_avanzado_html, height=500)
            
    else:
        # Mostrar los 4 gráficos de TradingView cuando no se ha calculado
        # Crear 2 filas de 2 columnas cada una
        col1, col2 = st.columns(2)
        
        with col1:
            # S&P 500
            st.markdown("### S&P 500")
            sp500_html = """
                <div class="tradingview-widget-container" style="height: 300px; width: 100%;">
                    <div class="tradingview-widget-container__widget" style="height: 100%; width: 100%;"></div>
                    <div class="tradingview-widget-copyright">
                        <a href="https://es.tradingview.com/" rel="noopener nofollow" target="_blank">
                            <span class="blue-text">Seguir todas las cotizaciones en TradingView</span>
                        </a>
                    </div>
                    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
                    {
                    "autosize": false,
                    "width": "100%",
                    "height": "300",
                    "symbol": "SPX500",
                    "interval": "D",
                    "timezone": "America/New_York",
                    "theme": "light",
                    "style": "1",
                    "locale": "es",
                    "toolbar_bg": "#f1f3f6",
                    "enable_publishing": false,
                    "hide_top_toolbar": false,
                    "hide_legend": false,
                    "save_image": false,
                    "container_id": "tradingview_widget"
                    }
                    </script>
                </div>
            """
            st.components.v1.html(sp500_html, height=300)
            
        with col2:
            # IMV Merval
            st.markdown("### IMV Merval")
            imv_html = """
            <div class="tradingview-widget-container" style="height: 300px; width: 100%;">
                <div class="tradingview-widget-container__widget" style="height: 100%; width: 100%;"></div>
                <div class="tradingview-widget-copyright">
                    <a href="https://es.tradingview.com/" rel="noopener nofollow" target="_blank">
                        <span class="blue-text">Seguir todas las cotizaciones en TradingView</span>
                    </a>
                </div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
                {
                "autosize": false,
                "width": "100%",
                "height": "300",
                "symbol": "IMV",
                "interval": "D",
                "timezone": "America/Argentina/Buenos_Aires",
                "theme": "light",
                "style": "1",
                "locale": "es",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "hide_top_toolbar": false,
                "hide_legend": false,
                "save_image": false,
                "container_id": "tradingview_widget"
                }
                </script>
            </div>
            """
            st.components.v1.html(imv_html, height=300)
        
        # Espaciado adicional antes de la tabla de datos de mercado
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Widget Market Data - Ancho completo
        st.markdown("## Datos de Mercado")
        market_data_html = """
        <div class="tradingview-widget-container" style="height: 800px; width: 100%; font-size: 8px;">
            <div class="tradingview-widget-container__widget" style="height: 100%; width: 100%; font-size: 8px;"></div>
            <div class="tradingview-widget-copyright" style="font-size: 8px;">
                <a href="https://www.tradingview.com/markets/" rel="noopener nofollow" target="_blank">
                    <span class="blue-text">Market summary</span>
                </a>
                <span class="trademark"> by TradingView</span>
            </div>
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-quotes.js" async>
            {
            "colorTheme": "light",
            "locale": "es",
            "largeChartUrl": "",
            "isTransparent": false,
            "showSymbolLogo": true,
            "backgroundColor": "#FFFFFF",
            "support_host": "https://www.tradingview.com",
            "width": "100%",
            "height": "800",
            "symbolsGroups": [
                {
                    "name": "Indices",
                    "symbols": [
                        {
                            "name": "SPX500",
                            "displayName": "S&P 500"
                        },
                        {
                            "name": "NASDAQ:IXIC",
                            "displayName": "NASDAQ"
                        },
                        {
                            "name": "DOWI",
                            "displayName": "Dow Jones"
                        },
                        {
                            "name": "IMV",
                            "displayName": "Merval"
                        }
                    ]
                },
                {
                    "name": "Bonos",
                    "symbols": [
                        {
                            "name": "GD30D",
                            "displayName": "GD30D"
                        },
                        {
                            "name": "AL30D",
                            "displayName": "AL30D"
                        },
                        {
                            "name": "GD29D",
                            "displayName": "GD29D"
                        },
                        {
                            "name": "AL29D",
                            "displayName": "AL29D"
                        }
                    ]
                }
            ]
            }
            </script>
        </div>
        """
        st.components.v1.html(market_data_html, height=800)
        
except FileNotFoundError:
    st.error("❌ No se pudo cargar el archivo de datos")
    st.info("Asegúrese de que el archivo 'bonos_flujos.xlsx' esté en el directorio correcto")
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {e}")
