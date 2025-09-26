# 📊 Calculadora de Bonos

Una aplicación web desarrollada en Python usando Streamlit para calcular métricas financieras de bonos, incluyendo TIR, duración y flujos de caja.

## 🎯 Características

- **Cálculo de TIR semestral y anual** usando el método Newton-Raphson
- **Duración Macaulay y Modificada** para análisis de sensibilidad
- **Interés corrido** calculado con base 30/360
- **Tabla de flujos de caja** con fechas de pago y valores presentes
- **Interfaz intuitiva** con inputs y outputs claros

## 📋 Parámetros del Bono

- **Fecha de emisión:** 10/09/2025
- **Fecha de vencimiento:** 10/09/2035
- **Cupón:** 10% anual (5% semestral)
- **Base de cálculo:** 30/360
- **Valor nominal:** 100

## 🚀 Instalación y Ejecución

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install streamlit numpy pandas python-dateutil
```

### 2. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en la dirección `http://localhost:8501`.

## 📖 Uso de la Aplicación

1. **Ingresa la fecha de liquidación** en el campo correspondiente
2. **Ingresa el precio del bono** (base 100)
3. **Haz clic en "Calcular"** para obtener los resultados

### Resultados que obtienes:

- **TIR Semestral y Anual:** Yield to Maturity
- **Duración Macaulay:** En semestres y años
- **Duración Modificada:** En semestres y años
- **Interés Corrido:** Calculado con base 30/360
- **Precio Sucio:** Precio limpio + interés corrido
- **Tabla de Flujos:** Fechas de pago, flujos de caja y valores presentes

## 🔧 Métodos de Cálculo

### TIR (Yield to Maturity)
- Implementado usando el método **Newton-Raphson**
- Convergencia iterativa hasta tolerancia de 1e-6
- Máximo 100 iteraciones

### Duración Macaulay
- Promedio ponderado de los períodos de los flujos de caja
- Ponderado por el valor presente de cada flujo

### Duración Modificada
- Duración Macaulay dividida por (1 + TIR)
- Mide la sensibilidad del precio ante cambios en la tasa

### Interés Corrido
- Calculado usando base **30/360**
- Desde la fecha del último cupón pagado hasta la fecha de liquidación

## 📁 Estructura del Proyecto

```
.
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
└── README.md          # Este archivo
```

## 🛠️ Tecnologías Utilizadas

- **Streamlit:** Framework para aplicaciones web en Python
- **NumPy:** Cálculos numéricos y matemáticos
- **Pandas:** Manipulación de datos y tablas
- **Python-dateutil:** Manejo avanzado de fechas

## 📝 Notas Técnicas

- Los cálculos asumen **pagos semestrales**
- La base **30/360** se usa para todos los cálculos de días
- La TIR se calcula iterativamente hasta convergencia
- Los resultados se muestran con 4 decimales de precisión

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request si encuentras algún error o tienes sugerencias de mejora.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
