# Polaris-Calc

![Polaris Logo](assets/logo.png)

**Polaris-Calc** es una potente aplicación de hoja de cálculo científica y calculadora de incertidumbre avanzada de código abierto, desarrollada en **Python** utilizando el framework de interfaz de usuario **Flet**. Está especialmente diseñada para estudiantes, ingenieros y científicos que requieren rigor físico, análisis de incertidumbre conforme a estándares internacionales y manejo avanzado de unidades y tipos de datos complejos.

[![Python Version](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/UI-Flet-0B7D73?logo=flet&logoColor=white)](https://flet.dev/)
[![SymPy](https://img.shields.io/badge/Math-SymPy-3B5998?logo=python&logoColor=white)](https://www.sympy.org/)
[![Matplotlib](https://img.shields.io/badge/Plots-Matplotlib-11557C?logo=python&logoColor=white)](https://matplotlib.org/)

---

## 📋 Índice
1. [Características Principales](#-características-principales)
2. [Arquitectura y Tecnologías](#-arquitectura-y-tecnologías)
3. [Tipos de Variables Soportadas](#-tipos-de-variables-soportadas)
4. [Estructura del Proyecto](#-estructura-del-proyecto)
5. [Instalación y Configuración](#-instalación-y-configuración)
6. [Formato de Archivos (.plc)](#-formato-de-archivos-plc)
7. [Pruebas Unitarias](#-pruebas-unitarias)
8. [Contribuciones](#-contribuciones)
9. [Licencia](#-licencia)

---

## ✨ Características Principales

### 🧠 Propagación de Errores con Rigor Científico (Método GUM)
Implementa la metodología **GUM (Guide to the Expression of Uncertainty in Measurement)** de forma nativa:
- **Derivadas Simbólicas:** Utiliza SymPy para calcular de manera exacta $\frac{\partial f}{\partial x_i}$ para cualquier fórmula.
- **Análisis de Covarianza:** En conjuntos de datos con más de 4 muestras ($n > 4$), calcula automáticamente la matriz de covarianza de las variables de entrada para propagar errores correlacionados de forma matemática precisa.

### 📐 Motor de Unidades y Análisis Dimensional en 7D
Las unidades no son cadenas de texto simples; son representadas como coordenadas en un espacio vectorial de 7 dimensiones correspondiente al Sistema Internacional de Unidades `[Longitud (L), Masa (M), Tiempo (T), Corriente (I), Temperatura (Θ), Cantidad de sustancia (N), Intensidad luminosa (J)]`.
- **Validación Dimensional:** Evita errores físicos impidiendo operaciones incompatibles (como sumar longitud y tiempo: `L + T`).
- **Conversión Automática:** Simplifica y convierte expresiones compuestas como `kg·m/s²` a cualquier otra unidad compatible de forma transparente.
- **Detección Localizada de Números:** Soporta formatos numéricos locales con detección inteligente de separadores decimales y científicos (`e-3`).

### 📊 Visualización Avanzada e Informe de Residuos
Incluye un motor de gráficos basado en **Matplotlib** totalmente integrado:
- Generación de gráficos bidimensionales y estadísticos (`line`, `scatter`, `bar`, `histogram`, `boxplot`, `violin`, `heatmap`, `contour`, etc.).
- Diagnósticos estadísticos avanzados para análisis de regresión y residuos, incluyendo pruebas como Shapiro-Wilk (normalidad de residuos) y Durbin-Watson (autocorrelación).

### 🖥️ Interfaz de Usuario Multitabla Reactiva
Desarrollada en **Flet** para ofrecer un rendimiento óptimo y un diseño visualmente atractivo con soporte completo para:
- Modos Claro y Oscuro personalizados.
- Columnas de datos especializadas para tipos avanzados (Complejos, Vectores n-dimensionales, Matrices).
- Navegación mejorada por teclado y edición rápida de datos.

---

## 🛠️ Arquitectura y Tecnologías

Polaris-Calc se aleja del esquema tradicional web y aprovecha el ecosistema científico de Python:

- **Flet (Python UI framework):** Permite renderizar una interfaz fluida e interactiva compilada sobre Flutter, logrando velocidades nativas.
- **SymPy:** Motor de álgebra computacional (CAS) que realiza los reemplazos de funciones, derivadas simbólicas y parses LaTeX.
- **NumPy & SciPy:** Encargados del procesamiento matricial y el cálculo estadístico subyacente.
- **Matplotlib:** Biblioteca de graficado de alto nivel configurada de forma modular.

---

## 📂 Tipos de Variables Soportadas

| Tipo de Variable | Descripción | Soporte de Error / Propagación |
| :--- | :--- | :--- |
| **Constante** | Valores escalares numéricos estáticos. | Sí (Opcional, con o sin error) |
| **Columna de datos** | Listas de valores numéricos de longitud arbitraria. | Sí (Sin error, error global o error por valor) |
| **Fórmula matemática** | Expresiones evaluadas de forma dinámica en base a otras variables. | Sí (Propagación simbólica completa) |
| **Booleano** | Valores lógicos booleanos. | No aplica |
| **Columna Booleana** | Series de valores booleanos. | No aplica |
| **Fórmula Booleana** | Expresiones lógicas evaluadas sobre columnas/variables booleanas. | No aplica |
| **Complejo** | Números complejos representados en formato binomial ($a + bi$) o polar ($r\angle\theta$). Toggles globales para cambiar representación. | Sí |
| **Vector** | Vectores n-dimensionales con inicialización dinámica y tamaño adaptable. | Sí |
| **Matriz** | Arreglos bidimensionales para cálculos lineales de cualquier dimensión. | Sí |
| **Gráfico (Plot)** | Configuración visual y enlace a series de datos para renderizar. | No aplica |

---

## 📂 Estructura del Proyecto

La estructura de archivos sigue un patrón de diseño limpio y desacoplado:

```
Polaris-Calc/
├── assets/           # Recursos estáticos (Logos, fuentes personalizadas, traducciones.csv, etc.)
├── components/       # Componentes estructurales de la app (Topbar global, barra de menú)
├── docs/             # Manuales técnicos y documentación de soporte matemático
├── screens/          # Vistas principales de la aplicación
│   ├── home.py       # Pantalla de bienvenida (Crear nuevo, abrir archivo, configuraciones)
│   └── editor/       # Pantalla del editor de hojas de cálculo científicas y sus modales
├── utils/            # Lógica de cálculo y utilidades del sistema
│   ├── file_utils.py # Lectura/Escritura y normalización de archivos de proyecto (.plc)
│   ├── variable_types.py # Definición de los tipos y estados de las variables
│   └── math_utils/   # El motor matemático central
│       ├── derivatives.py          # Cálculo simbólico de derivadas con SymPy
│       ├── sympy_latex_parser.py   # Parseador de fórmulas en sintaxis LaTeX
│       ├── number_unit_parser.py   # Entrada inteligente de datos (número + unidad)
│       ├── uncertain_calculator.py # Propagación de incertidumbre de acuerdo con el GUM
│       ├── unit_conversor/         # Conversor de unidades de física y dimensiones SI
│       ├── plotter/                # Wrapper configurable sobre Matplotlib
│       └── complex_math_operations/# Módulos avanzados para matemáticas complejas
└── tests/            # Suite de pruebas unitarias para el motor matemático
```

---

## 🚀 Instalación y Configuración

### Requisitos Previos
- **Python 3.10 o superior**
- Administrador de paquetes **pip**

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/juanpa2005/Polaris-Calc.git
cd Polaris-Calc
```

### Paso 2: Crear y activar un entorno virtual (Recomendado)
En Windows:
```bash
python -m venv env
env\Scripts\activate
```
En macOS/Linux:
```bash
python3 -m venv env
source env/bin/activate
```

### Paso 3: Instalar las dependencias
Instala los paquetes esenciales para la ejecución:
```bash
pip install flet sympy numpy matplotlib scipy
```

### Paso 4: Ejecutar la aplicación
```bash
python main.py
```

La aplicación se iniciará por defecto en modo oscuro con la pantalla de bienvenida.

---

## 💾 Formato de Archivos (.plc)

Los proyectos en Polaris-Calc se guardan con la extensión personalizada `.plc` (Polaris Calc). Este formato es un estándar **JSON** serializado y normalizado que almacena:
- La lista completa de variables y tipos con sus correspondientes valores, errores, fórmulas y unidades.
- La disposición y pestañas de la hoja de trabajo actual (`layout`).

Ejemplo de estructura de un archivo `.plc`:
```json
{
    "version": 2,
    "columns": [
        {
            "name": "V1",
            "values": [1.0, 2.0, 3.0],
            "errors": [0.1, 0.1, 0.2],
            "type": "column_with_error_per_value",
            "magnitude": "length",
            "unit": "m",
            "description": "Distancia medida"
        }
    ],
    "layout": {
        "tabs": [
            {
                "name": "General",
                "columns": ["V1"]
            }
        ],
        "active_tab_index": 0
    }
}
```

---

## 🧪 Pruebas Unitarias

El proyecto cuenta con una suite de pruebas robusta para verificar la precisión matemática y de conversión de unidades. Puedes ejecutar los tests utilizando `pytest`:

```bash
# Instalar pytest si no está instalado
pip install pytest

# Ejecutar las pruebas
pytest
```

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si deseas mejorar Polaris-Calc, por favor sigue estos pasos:
1. Realiza un Fork del proyecto.
2. Crea una rama para tu nueva característica (`git checkout -b feature/NuevaCaracteristica`).
3. Realiza tus cambios y haz commits descriptivos.
4. Envía un Pull Request para su revisión.

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
