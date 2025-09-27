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
    elif base == "ACT/365":
        days = (end_date - start_date).days
    elif base == "ACT/ACT":
        days = (end_date - start_date).days
    else:  # Default to 30/360
        days = days_calculation(start_date, end_date, "30/360")
    
    return days

# Función para procesar flujos irregulares
def process_irregular_flows(flows_df, settlement_date, dirty_price, base_calculo="30/360"):
    """Procesa flujos irregulares incluyendo el precio dirty como flujo inicial"""
    processed_flows = []
    
    # Agregar flujo inicial negativo (precio dirty pagado) en la fecha de liquidación
    processed_flows.append({
        'Fecha': settlement_date,
        'Pago_Capital': 0,
        'Cupon': 0,
        'Flujo_Total': -dirty_price,  # Flujo negativo (pago)
        'Días': 0
    })
    
    # Procesar flujos futuros
    for _, row in flows_df.iterrows():
        flow_date = pd.to_datetime(row['fecha']).date()
        
        if flow_date > settlement_date:
            days = days_calculation(settlement_date, flow_date, base_calculo)
            
            # Los porcentajes están sobre el valor nominal del bono (100)
            # Los flujos se calculan sobre el valor nominal, no sobre el precio dirty
            # El precio dirty solo afecta el flujo inicial (pago)
            capital_payment = row['pago_capital_porcentaje']  # 10% = 10
            coupon_payment = row['cupon_porcentaje']  # 4.5% = 4.5
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
def calculate_ytm_irregular(cash_flows, day_count_basis='30/360', max_iterations=100, tolerance=1e-8):
    """Calcula la TIR usando Newton-Raphson para flujos irregulares (equivalente a TIR.NO.PER de Excel)"""
    
    # Determinar el divisor según la base de cálculo
    if day_count_basis == "30/360":
        divisor = 360.0
    elif day_count_basis == "ACT/360":
        divisor = 360.0
    elif day_count_basis == "ACT/365":
        divisor = 365.0
    elif day_count_basis == "ACT/ACT":
        divisor = 365.0  # Para ACT/ACT usamos 365 como base estándar
    else:
        divisor = 360.0  # Default
    
    def pv_function(yield_rate):
        pv = 0
        for cf in cash_flows:
            days = cf['Días']
            periods = days / divisor
            pv += cf['Flujo_Total'] / ((1 + yield_rate) ** periods)
        return pv
    
    def pv_derivative(yield_rate):
        derivative = 0
        for cf in cash_flows:
            days = cf['Días']
            periods = days / divisor
            derivative -= cf['Flujo_Total'] * periods / ((1 + yield_rate) ** (periods + 1))
        return derivative
    
    # Usar búsqueda binaria como fallback si Newton-Raphson falla
    def binary_search_ytm():
        low, high = -0.99, 2.0  # Límites más conservadores para TIR
        for _ in range(200):  # Más iteraciones para mayor precisión
            mid = (low + high) / 2
            pv = pv_function(mid)
            if abs(pv) < tolerance:
                return mid
            elif pv < 0:
                high = mid
            else:
                low = mid
        return (low + high) / 2
    
    # Intentar Newton-Raphson primero
    ytm = 0.05  # Empezar con 5%
    for i in range(max_iterations):
        try:
            pv = pv_function(ytm)
            derivative = pv_derivative(ytm)
            
            if abs(derivative) < 1e-10:  # Evitar división por cero
                break
                
            ytm_new = ytm - pv / derivative
            
            # Verificar que no sea complejo y esté en rango razonable
            if isinstance(ytm_new, complex) or ytm_new < -0.99 or ytm_new > 2.0:
                return binary_search_ytm()
            
            if abs(ytm_new - ytm) < tolerance:
                return ytm_new
            
            ytm = ytm_new
        except:
            return binary_search_ytm()
    
    # Si Newton-Raphson falla, usar búsqueda binaria
    return binary_search_ytm()

# Función para calcular duración
def calculate_duration_irregular(cash_flows, ytm, price, day_count_basis='30/360'):
    """Calcula duración Macaulay y modificada para flujos irregulares en años"""
    
    # Para duración, siempre usar años (365 días) para el descuento
    # La TIR ya está en términos anuales
    weighted_pv = 0
    total_pv = 0
    
    for cf in cash_flows:
        days = cf['Días']
        # Calcular años para duración (siempre usando 365 días por año)
        years = days / 365.0
        
        # Usar la TIR anual directamente para descontar
        pv = cf['Flujo_Total'] / ((1 + ytm) ** years)
        
        # Solo incluir flujos positivos en el cálculo de duración
        if cf['Flujo_Total'] > 0:
            weighted_pv += years * pv  # Usar años para la duración
            total_pv += pv
    
    macaulay_duration = weighted_pv / total_pv if total_pv > 0 else 0
    modified_duration = macaulay_duration / (1 + ytm) if (1 + ytm) > 0 else 0
    
    return macaulay_duration, modified_duration

# Interfaz principal
st.header("📁 Cargar Bonos con Flujos Irregulares")

# Opción 1: Cargar archivo Excel personalizado
uploaded_file = st.file_uploader(
    "Cargar archivo Excel con flujos irregulares",
    type=['xlsx', 'xls'],
    help="Estructura: A1=nombre bono, Col A=fechas, Col B=cupones, Col C=capital, Col D=total"
)

# Opción 2: Usar archivo por defecto
if st.checkbox("Usar archivo por defecto (bonos_flujos.xlsx)"):
    try:
        # Leer el archivo por defecto
        flows_df = pd.read_excel('bonos_flujos.xlsx', header=None)
        
        # Extraer nombre del bono de la celda A1
        bono_name = str(flows_df.iloc[0, 0]) if not pd.isna(flows_df.iloc[0, 0]) else "Bono por defecto"
        
        # Procesar datos - manejar múltiples bonos
        processed_data = []
        current_bono_name = None
        
        for _, row in flows_df.iterrows():
            if len(row) >= 4 and not pd.isna(row[0]):
                cell_value = str(row[0]).strip()
                
                # Verificar si es un nombre de bono (contiene "bono" y no es una fecha)
                if cell_value.lower().startswith('bono'):
                    current_bono_name = cell_value
                    continue
                
                # Si tenemos un nombre de bono y es una fecha válida, procesar
                if current_bono_name:
                    try:
                        fecha_valida = pd.to_datetime(row[0])
                        if not pd.isna(fecha_valida):
                            processed_data.append({
                                'nombre_bono': current_bono_name,
                                'fecha': fecha_valida,  # Columna A (convertida a datetime)
                                'cupon_porcentaje': float(row[1]) if not pd.isna(row[1]) else 0.0,  # Columna B
                                'pago_capital_porcentaje': float(row[2]) if not pd.isna(row[2]) else 0.0,  # Columna C
                                'flujo_total': float(row[3]) if not pd.isna(row[3]) else 0.0  # Columna D
                            })
                    except:
                        # Si la fecha no es válida, saltar esta fila
                        continue
        
        flows_df = pd.DataFrame(processed_data)
        if len(flows_df) > 0:
            unique_bonos = flows_df['nombre_bono'].unique()
            st.success(f"Archivo por defecto cargado: {len(flows_df)} flujos para {len(unique_bonos)} bonos")
            st.write(f"Bonos encontrados: {', '.join(unique_bonos)}")
        else:
            st.warning("No se encontraron flujos válidos en el archivo")
        
    except Exception as e:
        st.error(f"Error al cargar el archivo por defecto: {e}")
        flows_df = None

# Opción 3: Bonos de ejemplo
elif st.checkbox("Usar bonos de ejemplo"):
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
        # Leer archivo Excel sin header
        raw_df = pd.read_excel(uploaded_file, header=None)
        
        # Extraer nombre del bono de la celda A1
        bono_name = str(raw_df.iloc[0, 0]) if not pd.isna(raw_df.iloc[0, 0]) else "Bono cargado"
        
        # Procesar datos - manejar múltiples bonos
        processed_data = []
        current_bono_name = None
        
        for _, row in raw_df.iterrows():
            if len(row) >= 4 and not pd.isna(row[0]):
                cell_value = str(row[0]).strip()
                
                # Verificar si es un nombre de bono (contiene "bono" y no es una fecha)
                if cell_value.lower().startswith('bono'):
                    current_bono_name = cell_value
                    continue
                
                # Si tenemos un nombre de bono y es una fecha válida, procesar
                if current_bono_name:
                    try:
                        fecha_valida = pd.to_datetime(row[0])
                        if not pd.isna(fecha_valida):
                            processed_data.append({
                                'nombre_bono': current_bono_name,
                                'fecha': fecha_valida,  # Columna A (convertida a datetime)
                                'cupon_porcentaje': float(row[1]) if not pd.isna(row[1]) else 0.0,  # Columna B
                                'pago_capital_porcentaje': float(row[2]) if not pd.isna(row[2]) else 0.0,  # Columna C
                                'flujo_total': float(row[3]) if not pd.isna(row[3]) else 0.0  # Columna D
                            })
                    except:
                        # Si la fecha no es válida, saltar esta fila
                        continue
        
        flows_df = pd.DataFrame(processed_data)
        if len(flows_df) > 0:
            unique_bonos = flows_df['nombre_bono'].unique()
            st.success(f"Archivo cargado exitosamente: {len(flows_df)} flujos para {len(unique_bonos)} bonos")
            st.write(f"Bonos encontrados: {', '.join(unique_bonos)}")
        else:
            st.warning("No se encontraron flujos válidos en el archivo")
        
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")

# Mostrar flujos cargados
if flows_df is not None and 'nombre_bono' in flows_df.columns:
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
    
    # Convertir fechas a datetime y ordenar
    bono_flows['fecha'] = pd.to_datetime(bono_flows['fecha'], errors='coerce')
    bono_flows = bono_flows.sort_values('fecha')
    
    
    
    # Inputs para cálculo
    st.subheader("📝 Datos para Cálculo")
    col1, col2 = st.columns(2)
    
    with col1:
        settlement_date = st.date_input(
            "Fecha de liquidación:",
            value=datetime(2025, 9, 16),  # Cambiado a 16 de septiembre
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
    
    # Selector de base de cálculo
    day_count_basis = st.selectbox(
        "Base de cálculo:",
        options=["30/360", "ACT/360", "ACT/365", "ACT/ACT"],
        index=0,
        help="30/360: Base estándar, ACT/360: Días reales/360, ACT/365: Días reales/365, ACT/ACT: Días reales/365"
    )
    
    # Calcular
    if st.button("🔄 Calcular", type="primary"):
        try:
            # Procesar flujos
            cash_flows = process_irregular_flows(bono_flows, settlement_date, bond_price, day_count_basis)
            
            if len(cash_flows) <= 1:
                st.error("No hay flujos de caja futuros para la fecha de liquidación seleccionada")
            elif len(cash_flows) == 1:
                st.error("Solo hay el flujo inicial. No hay flujos futuros para calcular TIR")
            else:
                # Calcular TIR
                ytm = calculate_ytm_irregular(cash_flows, day_count_basis)
                
                # Calcular duraciones
                macaulay_duration, modified_duration = calculate_duration_irregular(cash_flows, ytm, bond_price, day_count_basis)
                
                # Mostrar resultados
                st.subheader("📈 Resultados del Análisis")
                
                # Información de la base de cálculo
                st.info(f"**Base de cálculo utilizada:** {day_count_basis}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("TIR Anual", f"{ytm:.4%}", help="Tasa Interna de Retorno anual")
                
                with col2:
                    st.metric("TIR Efectiva", f"{ytm:.4%}", help="TIR efectiva (equivalente a TIR.NO.PER de Excel)")
                
                with col3:
                    st.metric("Duración Macaulay", f"{macaulay_duration:.2f} años", help="Tiempo promedio ponderado de los flujos de caja")
                
                with col4:
                    st.metric("Duración Modificada", f"{modified_duration:.2f} años", help="Sensibilidad del precio a cambios en la tasa de interés")
                
                # Tabla de flujos detallada
                st.subheader("💰 Flujos de Caja Detallados")
                df_cash_flows = pd.DataFrame(cash_flows)
                df_cash_flows['Fecha'] = pd.to_datetime(df_cash_flows['Fecha']).dt.strftime('%d/%m/%Y')
                df_cash_flows['Pago_Capital'] = df_cash_flows['Pago_Capital'].round(2)
                df_cash_flows['Cupon'] = df_cash_flows['Cupon'].round(2)
                df_cash_flows['Flujo_Total'] = df_cash_flows['Flujo_Total'].round(2)
                df_cash_flows['Días'] = df_cash_flows['Días'].astype(int)
                
                # Renombrar columnas para mejor presentación
                df_cash_flows = df_cash_flows.rename(columns={
                    'Fecha': 'Fecha de Pago',
                    'Pago_Capital': 'Capital (%)',
                    'Cupon': 'Cupón (%)',
                    'Flujo_Total': 'Flujo Total',
                    'Días': 'Días desde Liquidación'
                })
                
                # Mostrar tabla con mejor formato
                st.dataframe(
                    df_cash_flows, 
                    use_container_width=True,
                    hide_index=True
                )
                
                # Resumen de pagos
                st.subheader("📊 Resumen de Pagos")
                col1, col2, col3 = st.columns(3)
                
                # Calcular totales solo de flujos positivos (excluyendo el precio dirty)
                positive_flows = df_cash_flows[df_cash_flows['Flujo Total'] > 0]
                total_capital = positive_flows['Capital (%)'].sum()
                total_coupons = positive_flows['Cupón (%)'].sum()
                total_flows = positive_flows['Flujo Total'].sum()
                
                with col1:
                    st.metric("Total Capital", f"{total_capital:.2f}%", help="Suma de todos los pagos de capital")
                
                with col2:
                    st.metric("Total Cupones", f"{total_coupons:.2f}%", help="Suma de todos los pagos de cupón")
                
                with col3:
                    st.metric("Total Flujos", f"{total_flows:.2f}%", help="Suma de todos los flujos futuros")
                
        except Exception as e:
            st.error(f"Error en el cálculo: {e}")

# Información sobre el formato del archivo CSV
st.markdown("---")
st.subheader("📋 Formato del Archivo CSV")

st.markdown("""
El archivo Excel debe tener las siguientes columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `nombre_bono` | Nombre del bono | "Bono Irregular 1" |
| `fecha` | Fecha del flujo | "2025-03-15" |
| `pago_capital_porcentaje` | Pago de capital (% del valor nominal) | 10.0 |
| `cupon_porcentaje` | Cupón (% del valor nominal) | 4.5 |

**Ejemplo de archivo Excel:**
```
| nombre_bono | fecha | pago_capital_porcentaje | cupon_porcentaje |
|-------------|-------|------------------------|------------------|
| Bono Irregular 1 | 2025-03-15 | 0 | 4.5 |
| Bono Irregular 1 | 2025-09-15 | 0 | 4.5 |
| Bono Irregular 1 | 2026-03-15 | 10 | 4.5 |
| Bono Irregular 1 | 2026-09-15 | 0 | 4.5 |
| Bono Irregular 1 | 2027-03-15 | 20 | 4.5 |
| Bono Irregular 1 | 2027-09-15 | 0 | 4.5 |
| Bono Irregular 1 | 2028-03-15 | 30 | 4.5 |
| Bono Irregular 1 | 2028-09-15 | 0 | 4.5 |
| Bono Irregular 1 | 2029-03-15 | 40 | 4.5 |
| Bono Irregular 1 | 2029-09-15 | 0 | 4.5 |
```

**Notas:**
- Los porcentajes se expresan sobre el valor nominal (ej: 10% = 10.0)
- Las fechas pueden estar en formato de fecha de Excel o texto
- Puedes tener múltiples bonos en el mismo archivo
- Los flujos se ordenan automáticamente por fecha
- **Ventajas de Excel**: Más fácil de editar, formato de fechas automático, mejor visualización
""")

# Botón para descargar plantilla
if st.button("📥 Descargar Plantilla Excel"):
    sample_data = {
        'nombre_bono': ['Bono Ejemplo', 'Bono Ejemplo', 'Bono Ejemplo', 'Bono Ejemplo', 'Bono Ejemplo'],
        'fecha': ['2025-03-15', '2025-09-15', '2026-03-15', '2026-09-15', '2027-03-15'],
        'pago_capital_porcentaje': [0, 0, 25, 0, 75],
        'cupon_porcentaje': [5.0, 5.0, 5.0, 5.0, 5.0]
    }
    
    df_template = pd.DataFrame(sample_data)
    
    # Crear archivo Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_template.to_excel(writer, index=False, sheet_name='Bonos')
    
    excel_data = output.getvalue()
    
    st.download_button(
        label="Descargar plantilla Excel",
        data=excel_data,
        file_name="plantilla_bonos_irregulares.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
