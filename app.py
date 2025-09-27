import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math
import io

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Bonos",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("Calculadora de Bonos")
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
def process_irregular_flows(flows_df, settlement_date, dirty_price, base_calculo="ACT/365"):
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
def calculate_ytm_irregular(cash_flows, day_count_basis='ACT/365', max_iterations=100, tolerance=1e-8):
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
def calculate_duration_irregular(cash_flows, ytm, price, day_count_basis='ACT/365'):
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

def calculate_average_life(bono_flows, settlement_date, day_count_basis):
    """Calcula la vida media del bono considerando todos los repagos de capital desde liquidación hasta vencimiento"""
    
    # Filtrar flujos futuros desde la fecha de liquidación (incluyendo la fecha de liquidación)
    settlement_ts = pd.Timestamp(settlement_date)
    future_flows = bono_flows[bono_flows['fecha'] >= settlement_ts].copy()
    
    if len(future_flows) == 0:
        return 0.0
    
    # Ordenar por fecha
    future_flows = future_flows.sort_values('fecha')
    
    # Calcular días desde liquidación para cada flujo
    days_from_settlement = []
    capital_payments = []
    
    for _, row in future_flows.iterrows():
        flow_date = pd.Timestamp(row['fecha'])
        days = (flow_date - settlement_ts).days
        
        # Solo considerar flujos con pago de capital
        if row['pago_capital_porcentaje'] > 0:
            days_from_settlement.append(days)
            capital_payments.append(row['pago_capital_porcentaje'])
    
    if len(capital_payments) == 0:
        return 0.0
    
    # Calcular vida media ponderada por capital
    total_capital = sum(capital_payments)
    if total_capital == 0:
        return 0.0
    
    # Convertir días a años según la base de cálculo
    if day_count_basis == "ACT/365":
        divisor = 365.0
    elif day_count_basis == "ACT/360":
        divisor = 360.0
    elif day_count_basis == "30/360":
        divisor = 360.0
    else:
        divisor = 365.0
    
    weighted_years = 0.0
    for i, days in enumerate(days_from_settlement):
        years = days / divisor
        weight = capital_payments[i] / total_capital
        weighted_years += years * weight
    
    return weighted_years

def calculate_parity(clean_price, technical_value):
    """Calcula la paridad como precio limpio dividido por valor técnico"""
    if technical_value == 0:
        return 0.0
    return clean_price / technical_value

def find_next_coupon_date(bono_flows, settlement_date):
    """Encuentra la próxima fecha de pago de cupón más cercana a la fecha de liquidación"""
    
    # Filtrar flujos futuros desde la fecha de liquidación (incluyendo la fecha de liquidación)
    settlement_ts = pd.Timestamp(settlement_date)
    future_flows = bono_flows[bono_flows['fecha'] >= settlement_ts].copy()
    
    if len(future_flows) == 0:
        return None
    
    # Ordenar por fecha
    future_flows = future_flows.sort_values('fecha')
    
    # Buscar el primer flujo con pago de cupón
    for _, row in future_flows.iterrows():
        if row['cupon_porcentaje'] > 0:
            return row['fecha']
    
    return None

def calculate_accrued_interest(bono_flows, settlement_date, base_calculo_bono, periodicidad):
    """Calcula intereses corridos hasta la fecha de liquidación sobre el capital residual no amortizado"""
    
    # Filtrar solo flujos de cupón (donde hay tasa de cupón)
    cupon_flows = bono_flows[bono_flows['tasa_cupon'] > 0].copy()
    
    if len(cupon_flows) == 0:
        return 0.0
    
    # Ordenar por fecha
    cupon_flows = cupon_flows.sort_values('fecha')
    
    # Convertir settlement_date a Timestamp para comparación
    settlement_ts = pd.Timestamp(settlement_date)
    
    # Encontrar el último pago de cupón anterior a la fecha de liquidación
    last_coupon_date = None
    current_coupon_rate = 0.0
    
    # Buscar el pago de cupón inmediatamente anterior a la fecha de liquidación
    for _, row in cupon_flows.iterrows():
        row_date = pd.Timestamp(row['fecha'])
        if row_date < settlement_ts:
            last_coupon_date = row['fecha']
            current_coupon_rate = row['tasa_cupon']
        else:
            break
    
    if last_coupon_date is None:
        return 0.0
    
    # Calcular capital residual no amortizado
    # Capital residual = 100 - sumatoria de todos los flujos de capital anteriores a la fecha de liquidación
    capital_amortizado = 0.0
    for _, row in bono_flows.iterrows():
        row_date = pd.Timestamp(row['fecha'])
        if row_date < settlement_ts:
            capital_amortizado += row['pago_capital_porcentaje']
    
    capital_residual = 100.0 - capital_amortizado
    
    # Calcular días según la base de cálculo del bono
    last_coupon_ts = pd.Timestamp(last_coupon_date)
    days = (settlement_ts - last_coupon_ts).days
    
    # Calcular intereses corridos sobre el capital residual
    # Fórmula: (Tasa cupón × Capital residual) / 365 × Días transcurridos
    if base_calculo_bono == "ACT/365":
        accrued_interest = (current_coupon_rate * capital_residual) / 365.0 * days
    elif base_calculo_bono == "ACT/360":
        accrued_interest = (current_coupon_rate * capital_residual) / 360.0 * days
    elif base_calculo_bono == "30/360":
        accrued_interest = (current_coupon_rate * capital_residual) / 360.0 * days
    else:  # Default ACT/365
        accrued_interest = (current_coupon_rate * capital_residual) / 365.0 * days
    
    # Debug info (temporal)
    print(f"DEBUG - Último cupón: {last_coupon_date}, Settlement: {settlement_date}")
    print(f"DEBUG - Capital amortizado: {capital_amortizado}, Capital residual: {capital_residual}")
    print(f"DEBUG - Días transcurridos: {days}, Base: {base_calculo_bono}")
    print(f"DEBUG - Tasa cupón: {current_coupon_rate}%, Intereses corridos: {accrued_interest}")
    
    return accrued_interest

# Interfaz principal

# Cargar automáticamente el archivo por defecto
try:
    # Leer el archivo por defecto con múltiples estrategias para compatibilidad
    flows_df = None
    
    # Estrategia 1: openpyxl (más compatible con archivos modernos)
    try:
        flows_df = pd.read_excel('bonos_flujos.xlsx', header=None, engine='openpyxl')
    except:
        pass
    
    # Estrategia 2: xlrd (para archivos más antiguos)
    if flows_df is None:
        try:
            flows_df = pd.read_excel('bonos_flujos.xlsx', header=None, engine='xlrd')
        except:
            pass
    
    # Estrategia 3: pandas por defecto
    if flows_df is None:
        try:
            flows_df = pd.read_excel('bonos_flujos.xlsx', header=None)
        except:
            pass
    
    # Estrategia 4: con diferentes parámetros
    if flows_df is None:
        try:
            flows_df = pd.read_excel('bonos_flujos.xlsx', header=None, engine='openpyxl', na_values=[''])
        except:
            pass
    
    # Estrategia 5: ignorar validaciones y formato
    if flows_df is None:
        try:
            flows_df = pd.read_excel('bonos_flujos.xlsx', header=None, engine='openpyxl', 
                                   na_values=['', ' ', 'N/A', 'n/a'], 
                                   keep_default_na=False)
        except:
            pass
    
    # Estrategia 6: leer como texto puro
    if flows_df is None:
        try:
            flows_df = pd.read_excel('bonos_flujos.xlsx', header=None, engine='openpyxl', 
                                   dtype=str, na_values=[''])
        except:
            pass
    
    if flows_df is None:
        raise Exception("No se pudo cargar el archivo con ninguna estrategia")
    
    # Procesar datos - manejar múltiples bonos
    processed_data = []
    current_bono_name = None
    
    for _, row in flows_df.iterrows():
        if len(row) >= 5 and not pd.isna(row[0]):
            # Convertir a string y limpiar
            cell_value = str(row[0]).strip()
            
            # Saltar filas vacías o con solo espacios
            if not cell_value or cell_value.lower() in ['nan', 'none', '']:
                continue
            
            # Verificar si es el inicio de un nuevo bono (cualquier carácter que no sea una fecha)
            try:
                # Intentar convertir a fecha
                pd.to_datetime(cell_value, errors='raise')
                # Si llegamos aquí, es una fecha válida, continuar procesando
            except:
                # No es una fecha, es el inicio de un nuevo bono
                current_bono_name = cell_value
                # Extraer base de cálculo de la celda contigua (columna B)
                try:
                    base_calculo_bono = str(row[1]).strip() if not pd.isna(row[1]) else "ACT/365"
                except:
                    base_calculo_bono = "ACT/365"
                
                # Extraer periodicidad de la siguiente celda (columna C)
                try:
                    periodicidad = int(float(str(row[2]))) if not pd.isna(row[2]) and str(row[2]).strip() not in ['', 'nan'] else 12
                except:
                    periodicidad = 12
                continue
            
            # Si tenemos un nombre de bono y es una fecha válida, procesar
            if current_bono_name:
                try:
                    # Intentar convertir fecha con múltiples formatos
                    fecha_valida = pd.to_datetime(row[0], errors='coerce')
                    if not pd.isna(fecha_valida):
                        # Procesar valores numéricos de forma más robusta
                        # Nueva estructura: A=fecha, B=tasa_cupon, C=cupon, D=capital, E=total
                        tasa_cupon = 0.0
                        cupon = 0.0
                        capital = 0.0
                        flujo_total = 0.0
                        
                        try:
                            tasa_cupon = float(str(row[1]).replace(',', '.')) if not pd.isna(row[1]) and str(row[1]).strip() not in ['', 'nan'] else 0.0
                        except:
                            tasa_cupon = 0.0
                            
                        try:
                            cupon = float(str(row[2]).replace(',', '.')) if not pd.isna(row[2]) and str(row[2]).strip() not in ['', 'nan'] else 0.0
                        except:
                            cupon = 0.0
                            
                        try:
                            capital = float(str(row[3]).replace(',', '.')) if not pd.isna(row[3]) and str(row[3]).strip() not in ['', 'nan'] else 0.0
                        except:
                            capital = 0.0
                            
                        try:
                            flujo_total = float(str(row[4]).replace(',', '.')) if not pd.isna(row[4]) and str(row[4]).strip() not in ['', 'nan'] else 0.0
                        except:
                            flujo_total = cupon + capital
                        
                        processed_data.append({
                            'nombre_bono': current_bono_name,
                            'base_calculo': base_calculo_bono,
                            'periodicidad': periodicidad,
                            'fecha': fecha_valida,
                            'tasa_cupon': tasa_cupon,
                            'cupon_porcentaje': cupon,
                            'pago_capital_porcentaje': capital,
                            'flujo_total': flujo_total
                        })
                except:
                    # Si la fecha no es válida, saltar esta fila
                    continue
    
    flows_df = pd.DataFrame(processed_data)
    
    if len(flows_df) == 0:
        st.error("❌ No se encontraron flujos válidos en el archivo")
        flows_df = None
        
except Exception as e:
    st.error(f"❌ Error al cargar el archivo: {e}")
    flows_df = None


# Mostrar selector de bonos
if flows_df is not None and 'nombre_bono' in flows_df.columns:
    st.subheader("Elija un Bono")
    
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
    st.subheader("Datos para el Cálculo")
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
    
    # Base de cálculo fija en ACT/365
    day_count_basis = "ACT/365"
    
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
                
                # Calcular TIR según periodicidad (anualizada)
                periodicidad = bono_flows['periodicidad'].iloc[0] if 'periodicidad' in bono_flows.columns else 12
                # Fórmula: periodicidad * ((1 + TIR efectiva)^(1/periodicidad) - 1)
                ytm_anualizada = periodicidad * ((1 + ytm) ** (1.0 / periodicidad) - 1)
                
                # Calcular duraciones
                macaulay_duration, modified_duration = calculate_duration_irregular(cash_flows, ytm, bond_price, day_count_basis)
                
                # Calcular vida media
                average_life = calculate_average_life(bono_flows, settlement_date, day_count_basis)
                
                # Calcular intereses corridos
                base_calculo_bono = bono_flows['base_calculo'].iloc[0] if 'base_calculo' in bono_flows.columns else "ACT/365"
                periodicidad = bono_flows['periodicidad'].iloc[0] if 'periodicidad' in bono_flows.columns else 12
                accrued_interest = calculate_accrued_interest(bono_flows, settlement_date, base_calculo_bono, periodicidad)
                
                # Calcular paridad y próximo cupón
                clean_price = bond_price - accrued_interest
                capital_amortizado = 0.0
                settlement_ts = pd.Timestamp(settlement_date)
                for _, row in bono_flows.iterrows():
                    row_date = pd.Timestamp(row['fecha'])
                    if row_date < settlement_ts:
                        capital_amortizado += row['pago_capital_porcentaje']
                capital_residual = 100.0 - capital_amortizado
                technical_value = capital_residual + accrued_interest
                parity = calculate_parity(clean_price, technical_value)
                next_coupon_date = find_next_coupon_date(bono_flows, settlement_date)
                
                # Mostrar resultados
                st.subheader("Resultados")
                
                # Información de la base de cálculo y periodicidad
                # Convertir periodicidad a texto descriptivo
                if periodicidad == 1:
                    periodicidad_texto = "anual"
                elif periodicidad == 2:
                    periodicidad_texto = "semestral"
                elif periodicidad == 4:
                    periodicidad_texto = "trimestral"
                elif periodicidad == 12:
                    periodicidad_texto = "mensual"
                else:
                    periodicidad_texto = f"{periodicidad} meses"
                
                st.info(f"**Base de cálculo de días:** {base_calculo_bono} | **Periodicidad:** {periodicidad_texto}")
                
                # Convertir periodicidad a texto para el título
                if periodicidad == 1:
                    periodicidad_titulo = "Anual"
                elif periodicidad == 2:
                    periodicidad_titulo = "Semianual"
                elif periodicidad == 4:
                    periodicidad_titulo = "Trimestral"
                elif periodicidad == 12:
                    periodicidad_titulo = "Mensual"
                else:
                    periodicidad_titulo = f"Cada {12//periodicidad} meses"
                
                # Primera fila - Precio Limpio, Intereses Corridos, Capital Residual, Cupón Vigente
                col1, col2, col3, col4 = st.columns(4)
                
                # Obtener la tasa de cupón vigente usada para calcular intereses corridos
                cupon_vigente = 0.0
                settlement_ts = pd.Timestamp(settlement_date)
                for _, row in bono_flows.iterrows():
                    row_date = pd.Timestamp(row['fecha'])
                    if row_date < settlement_ts and row['tasa_cupon'] > 0:
                        cupon_vigente = row['tasa_cupon']
                
                with col1:
                    st.markdown("**Precio Limpio**")
                    st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{clean_price:.2f}</h3>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**Intereses Corridos**")
                    st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{accrued_interest:.4f}</h3>", unsafe_allow_html=True)
                
                with col3:
                    st.markdown("**Capital Residual**")
                    st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{capital_residual:.2f}</h3>", unsafe_allow_html=True)
                
                with col4:
                    st.markdown("**Valor Técnico**")
                    st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{technical_value:.2f}</h3>", unsafe_allow_html=True)
                
                # Segunda fila - Cupón Vigente, Vida Media, Paridad, Próximo Cupón
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown("**Cupón Vigente**")
                    st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{(cupon_vigente * 100):.2f}%</h3>", unsafe_allow_html=True)
                with col2:
                    st.markdown("**Vida Media**")
                    st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{average_life:.2f} años</h3>", unsafe_allow_html=True)
                with col3:
                    st.markdown("**Paridad**")
                    st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{parity:.4f}</h3>", unsafe_allow_html=True)
                with col4:
                    st.markdown("**Próximo Cupón**")
                    if next_coupon_date:
                        next_coupon_str = next_coupon_date.strftime('%d/%m/%Y')
                        st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{next_coupon_str}</h3>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>N/A</h3>", unsafe_allow_html=True)
                
                # Tercera fila - TIR Efectiva, TIR según período, Duración Modificada, Duración Macaulay
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown("**TIR Efectiva**")
                    st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{ytm:.4%}</h3>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**TIR {periodicidad_titulo}**")
                    st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{ytm_anualizada:.4%}</h3>", unsafe_allow_html=True)
                with col3:
                    st.markdown("**Duración Modificada**")
                    st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{modified_duration:.2f} años</h3>", unsafe_allow_html=True)
                with col4:
                    st.markdown("**Duración Macaulay**")
                    st.markdown(f"<h3 style='margin-top: -30px; margin-bottom: 0; line-height: 1.2;'>{macaulay_duration:.2f} años</h3>", unsafe_allow_html=True)
                
                # Tabla de flujos detallada
                st.subheader("Flujo de Fondos")
                
                df_cash_flows = pd.DataFrame(cash_flows)
                df_cash_flows['Fecha'] = pd.to_datetime(df_cash_flows['Fecha']).dt.strftime('%d/%m/%Y')
                
                # Formatear valores numéricos y manejar ceros
                def format_value(value):
                    if value == 0 or pd.isna(value):
                        return ""
                    else:
                        return f"{value:.2f}"
                
                df_cash_flows['Pago_Capital'] = df_cash_flows['Pago_Capital'].apply(format_value)
                df_cash_flows['Cupon'] = df_cash_flows['Cupon'].apply(format_value)
                df_cash_flows['Flujo_Total'] = df_cash_flows['Flujo_Total'].apply(format_value)
                
                # Renombrar columnas para mejor presentación
                df_cash_flows = df_cash_flows.rename(columns={
                    'Fecha': 'Fecha de Pago',
                    'Pago_Capital': 'Capital',
                    'Cupon': 'Cupón',
                    'Flujo_Total': 'Flujo Total'
                })
                
                # Eliminar la columna de días
                df_cash_flows = df_cash_flows.drop('Días', axis=1)
                
                # Crear tabla HTML personalizada para control total
                html_table = "<table style='width: 100%; border-collapse: collapse;'>"
                html_table += "<thead><tr>"
                html_table += "<th style='text-align: left; padding: 8px; border-bottom: 1px solid #ddd;'>Fecha de Pago</th>"
                html_table += "<th style='text-align: right; padding: 8px; border-bottom: 1px solid #ddd;'>Capital</th>"
                html_table += "<th style='text-align: right; padding: 8px; border-bottom: 1px solid #ddd;'>Cupón</th>"
                html_table += "<th style='text-align: right; padding: 8px; border-bottom: 1px solid #ddd;'>Flujo Total</th>"
                html_table += "</tr></thead><tbody>"
                
                for _, row in df_cash_flows.iterrows():
                    html_table += "<tr>"
                    html_table += f"<td style='text-align: left; padding: 8px; border-bottom: 1px solid #eee;'>{row['Fecha de Pago']}</td>"
                    html_table += f"<td style='text-align: right; padding: 8px; border-bottom: 1px solid #eee;'>{row['Capital']}</td>"
                    html_table += f"<td style='text-align: right; padding: 8px; border-bottom: 1px solid #eee;'>{row['Cupón']}</td>"
                    html_table += f"<td style='text-align: right; padding: 8px; border-bottom: 1px solid #eee;'>{row['Flujo Total']}</td>"
                    html_table += "</tr>"
                
                html_table += "</tbody></table>"
                
                st.markdown(html_table, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error en el cálculo: {e}")
