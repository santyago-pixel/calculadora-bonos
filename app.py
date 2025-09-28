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
    /* Estilos generales */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Sidebar */
    .stSidebar {
        background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
        color: white;
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
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.2;
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
        margin-bottom: 1.5rem;
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

# Cargar datos del Excel
try:
    df = pd.read_excel('bonos_flujos.xlsx', engine='openpyxl')
    
    # Extraer tipos de bonos de las celdas J6:J8
    tipos_bono = []
    try:
        for i in range(6, 9):  # J6, J7, J8
            valor = df.iloc[i-1, 9]  # Columna J (índice 9)
            if pd.notna(valor) and str(valor).strip():
                tipos_bono.append(str(valor).strip())
    except:
        pass
    
    if not tipos_bono:
        tipos_bono = ["Todos"]
    else:
        tipos_bono = ["Todos"] + tipos_bono
    
    # Procesar bonos
    bonos = []
    current_bono = None
    
    for index, row in df.iterrows():
        # Verificar si es el inicio de un nuevo bono (cualquier carácter que no sea fecha en columna A)
        if pd.notna(row.iloc[0]) and not isinstance(row.iloc[0], datetime):
            if current_bono:
                bonos.append(current_bono)
            
            current_bono = {
                'nombre': str(row.iloc[0]),
                'base_calculo': str(row.iloc[1]) if pd.notna(row.iloc[1]) else "ACT/365",
                'periodicidad': int(row.iloc[2]) if pd.notna(row.iloc[2]) else 2,
                'tipo_bono': str(row.iloc[3]) if pd.notna(row.iloc[3]) else "General",
                'tasa_cupon': float(row.iloc[4]) if pd.notna(row.iloc[4]) else 0.05,
                'flujos': []
            }
        elif current_bono and pd.notna(row.iloc[0]) and isinstance(row.iloc[0], datetime):
            # Es una fecha, agregar flujo
            fecha = row.iloc[0]
            cupon = float(row.iloc[2]) if pd.notna(row.iloc[2]) else 0  # Columna C
            capital = float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0  # Columna D
            total = float(row.iloc[4]) if pd.notna(row.iloc[4]) else 0  # Columna E
            
            current_bono['flujos'].append({
                'fecha': fecha,
                'cupon': cupon,
                'capital': capital,
                'total': total
            })
    
    if current_bono:
        bonos.append(current_bono)
    
    
    if not bonos:
        st.error("❌ No se encontraron bonos en el archivo")
        st.stop()
    
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
        bono_seleccionado = st.selectbox("Elija un Bono", nombres_bonos)
        
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
    
    # Contenido principal
    if calcular:
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
                    <div class="metric-value">{bono_actual['tasa_cupon']:.2%}</div>
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
        
        # COLUMNA DERECHA - FLUJO DE FONDOS COMPACTO
        with col2:
            st.markdown("## Flujo de Fondos")
            
            # Crear DataFrame compacto para la columna derecha
            cash_flows = []
            for i, (flujo, fecha, capital) in enumerate(zip(flujos, fechas, flujos_capital)):
                cupon = flujo - capital
                cash_flows.append({
                    'Fecha': fecha,
                    'Capital': capital,
                    'Cupón': cupon,
                    'Flujo Total': flujo
                })
            
            df_cash_flows_compact = pd.DataFrame(cash_flows)
            df_cash_flows_compact['Fecha'] = df_cash_flows_compact['Fecha'].dt.strftime('%d/%m/%y')
            df_cash_flows_compact['Capital'] = df_cash_flows_compact['Capital'].round(1)
            df_cash_flows_compact['Cupón'] = df_cash_flows_compact['Cupón'].round(1)
            df_cash_flows_compact['Flujo Total'] = df_cash_flows_compact['Flujo Total'].round(1)
            
            # Reemplazar 0 con vacío
            df_cash_flows_compact = df_cash_flows_compact.replace(0, '')
            
            # Mostrar tabla compacta
            st.table(df_cash_flows_compact)
            
            # SECCIÓN INFERIOR - GRÁFICO S&P 500
            st.markdown("## Gráfico S&P 500")
            st.markdown("""
            <div class="future-content" style="padding: 1rem;">
                <!-- TradingView S&P 500 Chart Widget BEGIN -->
                <div class="tradingview-widget-container">
                    <div id="tradingview_sp500" style="height: 500px; width: 100%;"></div>
                    <div class="tradingview-widget-copyright">
                        <a href="https://es.tradingview.com/" rel="noopener nofollow" target="_blank">
                            <span class="blue-text">Seguir todas las cotizaciones en TradingView</span>
                        </a>
                    </div>
                    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                    <script type="text/javascript">
                    new TradingView.widget({
                        "width": "100%",
                        "height": 500,
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
                        "container_id": "tradingview_sp500"
                    });
                    </script>
                </div>
                <!-- TradingView S&P 500 Chart Widget END -->
            </div>
            """, unsafe_allow_html=True)
            
    else:
        st.info("👆 Complete los parámetros en el sidebar y haga clic en 'Calcular' para ver los resultados")
        
        # Mapear periodicidad a texto
        periodicidad_texto = {
            1: "anual",
            2: "semestral", 
            3: "trimestral",
            4: "trimestral",
            6: "bimestral",
            12: "mensual"
        }.get(bono_actual['periodicidad'], f"{bono_actual['periodicidad']} veces al año")
        
        # Mostrar información del bono seleccionado
        st.markdown("## Información del Bono Seleccionado")
        st.markdown(f"**Nombre:** {bono_actual['nombre']}")
        st.markdown(f"**Tipo:** {bono_actual['tipo_bono']}")
        st.markdown(f"**Base de cálculo:** {bono_actual['base_calculo']}")
        st.markdown(f"**Periodicidad:** {periodicidad_texto}")
        st.markdown(f"**Tasa de cupón:** {bono_actual['tasa_cupon']:.2%}")
        st.markdown(f"**Número de flujos:** {len(bono_actual['flujos'])}")

except FileNotFoundError:
    st.error("❌ No se pudo cargar el archivo de datos")
    st.info("Asegúrese de que el archivo 'bonos_flujos.xlsx' esté en el directorio correcto")
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {e}")
