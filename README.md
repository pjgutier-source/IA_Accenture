# Especialización en Desarrollo con IA Generativa — Accenture

Proyecto para el uso de modelos de lenguaje (LLMs) mediante la API de Google Gemini, respetando prácticas de desarrollo robustas con manejo de variables de entorno, control de costos y validación de consistencia.

---

## Guía de instalación y uso

Sigue estos pasos para configurar y ejecutar el proyecto localmente desde cero:

### 1. Crear un entorno virtual nuevo desde cero

Abre tu terminal en la raíz del proyecto y crea un entorno virtual aislado:

```powershell
python -m venv .venv
```

Activa el entorno virtual:

- **En Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **En Windows (CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **En Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

---

### 2. Instalar las dependencias del repositorio

Instala exclusivamente las librerías declaradas en el archivo `requirements.txt`:

```powershell
pip install -r requirements.txt
```

---

### 3. Configurar las variables de entorno (`.env`)

Crea tu archivo `.env` a partir de la plantilla `env.example`:

- **En Windows (PowerShell):**
  ```powershell
  Copy-Item env.example .env
  ```
- **En Linux / macOS / Git Bash:**
  ```bash
  cp env.example .env
  ```

Abre el archivo `.env` y completa el valor de tu API Key de Gemini:

```env
GEMINI_API_KEY=tu_llave_aqui
```

> **Importante:** El archivo `.env` contiene credenciales sensibles y está excluido del control de versiones mediante `.gitignore`. Nunca lo compartas ni lo subas al repositorio.

---

### 4. Ejecutar el proyecto

Ejecuta el script principal [main.py](file:///c:/Users/pjgut/IA_Accenture/main.py):

```powershell
python main.py
```

#### Respuesta esperada en consola:

```text
Respuesta del modelo: {
  "rta": "Santiago es considerada la mejor ciudad debido a su excelente infraestructura, economia y gran oferta cultural chilena.",
  "poblacion": 6254314
}
Costo de la pregunta: 5.4e-06 USD
Proceso terminado sin errores.
```

---

## Ejecución de pruebas de consistencia

Para evaluar la consistencia de las respuestas y el cumplimiento de los esquemas JSON definidos en el banco de prompts, ejecuta:

```powershell
python tests/test_consistencia.py
```

Los resultados se guardarán automáticamente en `prompts/registro_resultados.json`.

---

## Estructura del proyecto

```text
├── docs/                 # Documentación técnica y decisiones de arquitectura
├── prompts/              # Registro de resultados de pruebas de prompts
├── src/                  # Código fuente
│   ├── banco_de_prompts.json               # Casos de prueba y schemas
│   └── consumir_gemini_refactorizada.py    # Lógica de consumo de la API de Gemini
├── tests/                # Pruebas automatizadas y de consistencia
│   └── test_consistencia.py
├── .env.example          # Plantilla de variables de entorno
├── .gitignore            # Archivos y carpetas ignorados por Git
├── main.py               # Punto de entrada de la aplicación
├── README.md             # Documentación del proyecto
└── requirements.txt      # Dependencias del proyecto
```
