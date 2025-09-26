import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math
import io

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Bonos con Flujos Irregulares",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Calculadora de Bonos con Flujos Irregulares")
st.markdown("---")

# Función para calcular días usando diferentes bases
def days_calculation(start_date, end_date, base):
    """Calcula días entre fechas usando diferentes bases"""
    if base == "30/360":
        d1 = min(start_date.day, 30)
        d2 = min(end_date.day, 30)
        if start_date.day == 30:
            d2 = 30
        days = (end_date.year - start_date.year) * 360 + \
               (end_date.month - start_date.month) * 30 + \
               (d2 - d1)
    elif base == "ACT/360":
        days = (end_date - start_date).days
    elif base == "ACT/ACT":
        days = (end_date - start_date).days
    else:  # Default to 30/360
        days = days_calculation(start_date, end_date, "30/360")
    
    return days

# Función para procesar flujos irregulares
def process_irregular_flows(flows_df, settlement_date, base_calculo="30/360"):
    """Procesa flujos irregulares y calcula días desde liquidación"""
    processed_flows = []
    
    for _, row in flows_df.iterrows():
        flow_date = pd.to_datetime(row['fecha']).date()
        
        if flow_date > settlement_date:
            days = days_calculation(settlement_date, flow_date, base_calculo)
            
            # Calcular flujo total (capital + cupón)
            capital_payment = row['pago_capital_porcentaje'] / 100
            coupon_payment = row['cupon_porcentaje'] / 100
            total_flow = capital_payment + coupon_payment
            
            processed_flows.append({
                'Fecha': flow_date,
                'Pago_Capital': capital_payment,
                'Cupon': coupon_payment,
                'Flujo_Total': total_flow,
                'Días': days
            })
    
    return processed_flows

# Función para calcular TIR
def calculate_ytm_irregular(cash_flows, price, settlement_date, max_iterations=100, tolerance=1e-6):
    """Calcula la TIR usando Newton-Raphson para flujos irregulares"""
    
    def pv_function(yield_rate):
        pv = 0
        for cf in cash_flows:
            days = cf['Días']
            periods = days / 365  # Ajustar según la base
            pv += cf['Flujo_Total'] / ((1 + yield_rate) ** periods)
        return pv
    
    def pv_derivative(yield_rate):
        derivative = 0
        for cf in cash_flows:
            days = cf['Días']
            periods = days / 365
            derivative -= cf['Flujo_Total'] * periods / ((1 + yield_rate) ** (periods + 1))
        return derivative
    
    ytm = 0.05
    for i in range(max_iterations):
        pv = pv_function(ytm)
        derivative = pv_derivative(ytm)
        
        if abs(derivative) < 1e-10:  # Evitar división por cero
            break
            
        ytm_new = ytm - (pv - price) / derivative
        
        if abs(ytm_new - ytm) < tolerance:
            return ytm_new
        
        ytm = ytm_new
    
    return ytm

# Función para calcular duración
def calculate_duration_irregular(cash_flows, ytm, price):
    """Calcula duración Macaulay y modificada para flujos irregulares"""
    weighted_pv = 0
    total_pv = 0
    
    for cf in cash_flows:
        days = cf['Días']
        periods = days / 365
        pv = cf['Flujo_Total'] / ((1 + ytm) ** periods)
        weighted_pv += periods * pv
        total_pv += pv
    
    macaulay_duration = weighted_pv / total_pv if total_pv > 0 else 0
    modified_duration = macaulay_duration / (1 + ytm) if (1 + ytm) > 0 else 0
    
    return macaulay_duration, modified_duration

# Interfaz principal
st.header("📁 Cargar Bonos con Flujos Irregulares")

# Opción 1: Cargar archivo CSV
uploaded_file = st.file_uploader(
    "Cargar archivo CSV con flujos irregulares",
    type=['csv'],
    help="El archivo debe tener columnas: nombre_bono, fecha, pago_capital_porcentaje, cupon_porcentaje"
)

# Opción 2: Bonos de ejemplo
if st.checkbox("Usar bonos de ejemplo"):
    sample_data = {
        'nombre_bono': ['Bono Irregular 1', 'Bono Irregular 1', 'Bono Irregular 1', 'Bono Irregular 1', 'Bono Irregular 1', 'Bono Irregular 1', 'Bono Irregular 1', 'Bono Irregular 1', 'Bono Irregular 1', 'Bono Irregular 1', 'Bono Irregular 2', 'Bono Irregular 2', 'Bono Irregular 2', 'Bono Irregular 2', 'Bono Irregular 2', 'Bono Irregular 2', 'Bono Irregular 2', 'Bono Irregular 2'],
        'fecha': ['2025-03-15', '2025-09-15', '2026-03-15', '2026-09-15', '2027-03-15', '2027-09-15', '2028-03-15', '2028-09-15', '2029-03-15', '2029-09-15', '2025-06-01', '2025-12-01', '2026-06-01', '2026-12-01', '2027-06-01', '2027-12-01', '2028-06-01', '2028-12-01'],
        'pago_capital_porcentaje': [0, 0, 10, 0, 20, 0, 30, 0, 40, 0, 0, 0, 0, 25, 0, 25, 0, 50],
        'cupon_porcentaje': [4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0]
    }
    flows_df = pd.DataFrame(sample_data)
    st.success("Cargados bonos de ejemplo")
else:
    flows_df = None

# Procesar archivo cargado
if uploaded_file is not None:
    try:
        flows_df = pd.read_csv(uploaded_file)
        st.success(f"Archivo cargado exitosamente: {len(flows_df)} flujos")
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")

# Mostrar flujos cargados
if flows_df is not None:
    st.subheader("📋 Flujos Cargados")
    
    # Agrupar por nombre de bono
    unique_bonos = flows_df['nombre_bono'].unique()
    
    # Selector de bono
    bono_selected = st.selectbox(
        "Selecciona un bono:",
        options=unique_bonos
    )
    
    # Filtrar flujos del bono seleccionado
    bono_flows = flows_df[flows_df['nombre_bono'] == bono_selected].copy()
    bono_flows = bono_flows.sort_values('fecha')
    
    st.subheader(f"📊 Flujos del Bono: {bono_selected}")
    st.dataframe(bono_flows, use_container_width=True)
    
    # Parámetros adicionales
    st.subheader("⚙️ Parámetros Adicionales")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        base_calculo = st.selectbox(
            "Base de cálculo:",
            options=["30/360", "ACT/360", "ACT/ACT"],
            index=0
        )
    
    with col2:
        valor_nominal = st.number_input(
            "Valor nominal:",
            min_value=1.0,
            value=100.0,
            step=1.0
        )
    
    with col3:
        st.write("")  # Espacio en blanco para alineación
    
    # Inputs para cálculo
    st.subheader("📝 Datos para Cálculo")
    col1, col2 = st.columns(2)
    
    with col1:
        settlement_date = st.date_input(
            "Fecha de liquidación:",
            value=datetime(2025, 9, 10),
            min_value=pd.to_datetime(bono_flows['fecha'].min()).date(),
            max_value=pd.to_datetime(bono_flows['fecha'].max()).date()
        )
    
    with col2:
        bond_price = st.number_input(
            "Precio del bono (base 100):",
            min_value=0.0,
            max_value=200.0,
            value=100.0,
            step=0.01,
            format="%.2f"
        )
    
    # Calcular
    if st.button("🔄 Calcular", type="primary"):
        try:
            # Procesar flujos
            cash_flows = process_irregular_flows(bono_flows, settlement_date, base_calculo)
            
            if not cash_flows:
                st.error("No hay flujos de caja futuros para la fecha de liquidación seleccionada")
            else:
                # Calcular TIR
                ytm = calculate_ytm_irregular(cash_flows, bond_price, settlement_date)
                
                # Calcular duraciones
                macaulay_duration, modified_duration = calculate_duration_irregular(cash_flows, ytm, bond_price)
                
                # Mostrar resultados
                st.subheader("📈 Resultados")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("TIR Anual", f"{ytm:.4%}")
                
                with col2:
                    st.metric("TIR Efectiva", f"{((1 + ytm) ** 2 - 1):.4%}")
                
                with col3:
                    st.metric("Duración Macaulay", f"{macaulay_duration:.2f} años")
                
                with col4:
                    st.metric("Duración Modificada", f"{modified_duration:.2f} años")
                
                # Tabla de flujos detallada
                st.subheader("💰 Flujos de Caja Detallados")
                df_cash_flows = pd.DataFrame(cash_flows)
                df_cash_flows['Fecha'] = pd.to_datetime(df_cash_flows['Fecha']).dt.strftime('%d/%m/%Y')
                df_cash_flows['Pago_Capital'] = (df_cash_flows['Pago_Capital'] * valor_nominal).round(2)
                df_cash_flows['Cupon'] = (df_cash_flows['Cupon'] * valor_nominal).round(2)
                df_cash_flows['Flujo_Total'] = (df_cash_flows['Flujo_Total'] * valor_nominal).round(2)
                df_cash_flows['Días'] = df_cash_flows['Días'].astype(int)
                df_cash_flows['Períodos'] = (df_cash_flows['Días'] / 365).round(4)
                df_cash_flows['VP'] = (df_cash_flows['Flujo_Total'] / ((1 + ytm) ** df_cash_flows['Períodos'])).round(2)
                
                df_cash_flows.columns = ['Fecha', 'Pago Capital', 'Cupón', 'Flujo Total', 'Días', 'Períodos (años)', 'Valor Presente']
                st.dataframe(df_cash_flows, use_container_width=True, hide_index=True)
                
                # Resumen de pagos
                st.subheader("📊 Resumen de Pagos")
                col1, col2, col3 = st.columns(3)
                
                total_capital = df_cash_flows['Pago Capital'].sum()
                total_coupons = df_cash_flows['Cupón'].sum()
                total_flows = df_cash_flows['Flujo Total'].sum()
                
                with col1:
                    st.metric("Total Capital", f"${total_capital:,.2f}")
                
                with col2:
                    st.metric("Total Cupones", f"${total_coupons:,.2f}")
                
                with col3:
                    st.metric("Total Flujos", f"${total_flows:,.2f}")
                
        except Exception as e:
            st.error(f"Error en el cálculo: {e}")

# Información sobre el formato del archivo CSV
st.markdown("---")
st.subheader("📋 Formato del Archivo CSV")

st.markdown("""
El archivo CSV debe tener las siguientes columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `nombre_bono` | Nombre del bono | "Bono Irregular 1" |
| `fecha` | Fecha del flujo | "2025-03-15" |
| `pago_capital_porcentaje` | Pago de capital (% del valor nominal) | 10.0 |
| `cupon_porcentaje` | Cupón (% del valor nominal) | 4.5 |

**Ejemplo de archivo CSV:**
```csv
nombre_bono,fecha,pago_capital_porcentaje,cupon_porcentaje
Bono Irregular 1,2025-03-15,0,4.5
Bono Irregular 1,2025-09-15,0,4.5
Bono Irregular 1,2026-03-15,10,4.5
Bono Irregular 1,2026-09-15,0,4.5
Bono Irregular 1,2027-03-15,20,4.5
Bono Irregular 1,2027-09-15,0,4.5
Bono Irregular 1,2028-03-15,30,4.5
Bono Irregular 1,2028-09-15,0,4.5
Bono Irregular 1,2029-03-15,40,4.5
Bono Irregular 1,2029-09-15,0,4.5
```

**Notas:**
- Los porcentajes se expresan sobre el valor nominal (ej: 10% = 10.0)
- Las fechas deben estar en formato YYYY-MM-DD
- Puedes tener múltiples bonos en el mismo archivo
- Los flujos se ordenan automáticamente por fecha
""")

# Botón para descargar plantilla
if st.button("📥 Descargar Plantilla CSV"):
    sample_data = {
        'nombre_bono': ['Bono Ejemplo', 'Bono Ejemplo', 'Bono Ejemplo', 'Bono Ejemplo', 'Bono Ejemplo'],
        'fecha': ['2025-03-15', '2025-09-15', '2026-03-15', '2026-09-15', '2027-03-15'],
        'pago_capital_porcentaje': [0, 0, 25, 0, 75],
        'cupon_porcentaje': [5.0, 5.0, 5.0, 5.0, 5.0]
    }
    
    df_template = pd.DataFrame(sample_data)
    csv = df_template.to_csv(index=False)
    
    st.download_button(
        label="Descargar plantilla CSV",
        data=csv,
        file_name="plantilla_bonos_irregulares.csv",
        mime="text/csv"
    )
