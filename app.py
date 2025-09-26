import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Bonos",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Calculadora de Bonos")
st.markdown("---")

# Parámetros del bono
st.sidebar.header("Parámetros del Bono")
st.sidebar.write("**Fecha de emisión:** 10/09/2025")
st.sidebar.write("**Fecha de vencimiento:** 10/09/2035")
st.sidebar.write("**Cupón:** 10% anual (5% semestral)")
st.sidebar.write("**Base de cálculo:** 30/360")
st.sidebar.write("**Valor nominal:** 100")

# Inputs del usuario
st.header("📝 Datos de Entrada")
col1, col2 = st.columns(2)

with col1:
    settlement_date = st.date_input(
        "Fecha de liquidación",
        value=datetime(2025, 9, 10),
        min_value=datetime(2025, 9, 10),
        max_value=datetime(2035, 9, 10)
    )

with col2:
    bond_price = st.number_input(
        "Precio del bono (base 100)",
        min_value=0.0,
        max_value=200.0,
        value=100.0,
        step=0.01,
        format="%.2f"
    )

# Función para calcular días usando base 30/360
def days_30_360(start_date, end_date):
    """Calcula días entre fechas usando base 30/360"""
    d1 = min(start_date.day, 30)
    d2 = min(end_date.day, 30)
    
    # Si d1 es 30, entonces d2 también debe ser 30
    if start_date.day == 30:
        d2 = 30
    
    days = (end_date.year - start_date.year) * 360 + \
           (end_date.month - start_date.month) * 30 + \
           (d2 - d1)
    
    return days

# Función para generar fechas de pago de cupones
def generate_coupon_dates(issue_date, maturity_date, frequency=2):
    """Genera fechas de pago de cupones semestrales"""
    dates = []
    current_date = issue_date
    
    # Agregar fecha de emisión
    dates.append(issue_date)
    
    # Generar fechas semestrales
    while current_date < maturity_date:
        current_date = current_date + relativedelta(months=6)
        if current_date <= maturity_date:
            dates.append(current_date)
    
    # Asegurar que la fecha de vencimiento esté incluida
    if dates[-1] != maturity_date:
        dates.append(maturity_date)
    
    return dates

# Función para calcular flujos de caja
def calculate_cash_flows(coupon_dates, coupon_rate, face_value, settlement_date):
    """Calcula los flujos de caja del bono"""
    cash_flows = []
    coupon_payment = face_value * coupon_rate / 2  # Semestral
    
    for i, date in enumerate(coupon_dates):
        if date > settlement_date:
            if i == len(coupon_dates) - 1:  # Última fecha (vencimiento)
                cash_flow = face_value + coupon_payment
            else:
                cash_flow = coupon_payment
            
            cash_flows.append({
                'Fecha': date,
                'Flujo': cash_flow,
                'Días': days_30_360(settlement_date, date)
            })
    
    return cash_flows

# Función para calcular TIR usando Newton-Raphson
def calculate_ytm(cash_flows, price, face_value, settlement_date, max_iterations=100, tolerance=1e-6):
    """Calcula la TIR semestral usando el método Newton-Raphson"""
    
    def pv_function(yield_rate):
        """Función de valor presente"""
        pv = 0
        for cf in cash_flows:
            days = cf['Días']
            periods = days / 180  # Semestres
            pv += cf['Flujo'] / ((1 + yield_rate) ** periods)
        return pv
    
    def pv_derivative(yield_rate):
        """Derivada de la función de valor presente"""
        derivative = 0
        for cf in cash_flows:
            days = cf['Días']
            periods = days / 180
            derivative -= cf['Flujo'] * periods / ((1 + yield_rate) ** (periods + 1))
        return derivative
    
    # Estimación inicial
    ytm = 0.05  # 5% semestral como estimación inicial
    
    for i in range(max_iterations):
        pv = pv_function(ytm)
        derivative = pv_derivative(ytm)
        
        # Newton-Raphson: x_new = x_old - f(x)/f'(x)
        ytm_new = ytm - (pv - price) / derivative
        
        if abs(ytm_new - ytm) < tolerance:
            return ytm_new
        
        ytm = ytm_new
    
    return ytm

# Función para calcular Duración Macaulay
def calculate_macaulay_duration(cash_flows, ytm, price):
    """Calcula la Duración Macaulay"""
    weighted_pv = 0
    total_pv = 0
    
    for cf in cash_flows:
        days = cf['Días']
        periods = days / 180  # Semestres
        pv = cf['Flujo'] / ((1 + ytm) ** periods)
        weighted_pv += periods * pv
        total_pv += pv
    
    return weighted_pv / total_pv

# Función para calcular Duración Modificada
def calculate_modified_duration(macaulay_duration, ytm):
    """Calcula la Duración Modificada"""
    return macaulay_duration / (1 + ytm)

# Función para calcular interés corrido
def calculate_accrued_interest(settlement_date, issue_date, coupon_rate, face_value):
    """Calcula el interés corrido usando base 30/360"""
    # Encontrar la fecha del último cupón pagado
    current_date = issue_date
    last_coupon_date = issue_date
    
    while current_date <= settlement_date:
        last_coupon_date = current_date
        current_date = current_date + relativedelta(months=6)
    
    # Calcular días desde el último cupón
    days_since_coupon = days_30_360(last_coupon_date, settlement_date)
    days_in_period = 180  # 6 meses = 180 días en base 30/360
    
    accrued_interest = face_value * (coupon_rate / 2) * (days_since_coupon / days_in_period)
    
    return accrued_interest, last_coupon_date

# Cálculos principales
if st.button("🔄 Calcular", type="primary"):
    
    # Parámetros del bono
    issue_date = datetime(2025, 9, 10).date()
    maturity_date = datetime(2035, 9, 10).date()
    coupon_rate = 0.10  # 10% anual
    face_value = 100
    
    # Generar fechas de cupones
    coupon_dates = generate_coupon_dates(issue_date, maturity_date)
    
    # Calcular flujos de caja
    cash_flows = calculate_cash_flows(coupon_dates, coupon_rate, face_value, settlement_date)
    
    # Calcular TIR
    ytm_semestral = calculate_ytm(cash_flows, bond_price, face_value, settlement_date)
    ytm_anual = (1 + ytm_semestral) ** 2 - 1
    
    # Calcular duraciones
    macaulay_duration = calculate_macaulay_duration(cash_flows, ytm_semestral, bond_price)
    modified_duration = calculate_modified_duration(macaulay_duration, ytm_semestral)
    
    # Calcular interés corrido
    accrued_interest, last_coupon_date = calculate_accrued_interest(
        settlement_date, issue_date, coupon_rate, face_value
    )
    
    # Mostrar resultados
    st.header("📈 Resultados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "TIR Semestral",
            f"{ytm_semestral:.4%}",
            help="Yield to Maturity semestral"
        )
    
    with col2:
        st.metric(
            "TIR Anual",
            f"{ytm_anual:.4%}",
            help="Yield to Maturity anualizada"
        )
    
    with col3:
        st.metric(
            "Duración Macaulay",
            f"{macaulay_duration:.2f}",
            help="Duración Macaulay en semestres"
        )
    
    with col4:
        st.metric(
            "Duración Modificada",
            f"{modified_duration:.2f}",
            help="Duración Modificada en semestres"
        )
    
    # Información adicional
    st.subheader("ℹ️ Información Adicional")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Interés Corrido",
            f"{accrued_interest:.4f}",
            help=f"Interés corrido desde {last_coupon_date.strftime('%d/%m/%Y')}"
        )
    
    with col2:
        dirty_price = bond_price + accrued_interest
        st.metric(
            "Precio Sucio",
            f"{dirty_price:.4f}",
            help="Precio limpio + interés corrido"
        )
    
    # Tabla de flujos de caja
    st.subheader("💰 Flujos de Caja")
    
    df_cash_flows = pd.DataFrame(cash_flows)
    df_cash_flows['Fecha'] = pd.to_datetime(df_cash_flows['Fecha']).dt.strftime('%d/%m/%Y')
    df_cash_flows['Flujo'] = df_cash_flows['Flujo'].round(4)
    df_cash_flows['Días'] = df_cash_flows['Días'].astype(int)
    df_cash_flows['Períodos'] = (df_cash_flows['Días'] / 180).round(4)
    df_cash_flows['VP'] = (df_cash_flows['Flujo'] / ((1 + ytm_semestral) ** df_cash_flows['Períodos'])).round(4)
    
    df_cash_flows.columns = ['Fecha', 'Flujo de Caja', 'Días', 'Períodos (semestres)', 'Valor Presente']
    
    st.dataframe(
        df_cash_flows,
        use_container_width=True,
        hide_index=True
    )
    
    # Resumen de cálculos
    st.subheader("📊 Resumen de Cálculos")
    
    summary_data = {
        'Métrica': [
            'Fecha de Liquidación',
            'Precio del Bono',
            'TIR Semestral',
            'TIR Anual',
            'Duración Macaulay (semestres)',
            'Duración Macaulay (años)',
            'Duración Modificada (semestres)',
            'Duración Modificada (años)',
            'Interés Corrido',
            'Precio Sucio'
        ],
        'Valor': [
            settlement_date.strftime('%d/%m/%Y'),
            f'{bond_price:.4f}',
            f'{ytm_semestral:.4%}',
            f'{ytm_anual:.4%}',
            f'{macaulay_duration:.4f}',
            f'{macaulay_duration/2:.4f}',
            f'{modified_duration:.4f}',
            f'{modified_duration/2:.4f}',
            f'{accrued_interest:.4f}',
            f'{dirty_price:.4f}'
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

# Información sobre la aplicación
st.markdown("---")
st.markdown("""
### 📚 Información sobre la Calculadora

**Características del Bono:**
- **Emisión:** 10/09/2025
- **Vencimiento:** 10/09/2035
- **Cupón:** 10% anual (5% semestral)
- **Base de cálculo:** 30/360
- **Valor nominal:** 100

**Métodos de Cálculo:**
- **TIR:** Método Newton-Raphson
- **Duración Macaulay:** Promedio ponderado de los períodos de los flujos
- **Duración Modificada:** Duración Macaulay / (1 + TIR)
- **Interés Corrido:** Base 30/360 desde el último cupón pagado

**Notas:**
- Los cálculos asumen pagos semestrales
- La base 30/360 se usa para cálculos de días
- La TIR se calcula iterativamente hasta convergencia
""")
