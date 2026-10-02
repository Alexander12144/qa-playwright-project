# QA Test Recorder

Aplicación de escritorio para grabar recorridos web, capturar evidencias, generar casos de prueba y reproducir flujos.

## Inicio

```powershell
python -m app.main
```

## Estructura

```text
app/
  main.py                         Punto de entrada Tkinter
  config.py                       Rutas y configuración compartida
  automation/                     Reproducción de flujos guardados
  evidence/                       Captura de screenshots
  models/                         Modelos de dominio (action.py)
  recorder/                       Captura, sanitización y transformación de eventos
  reporting/                      Generación de documentos Word
  services/                       Casos de uso que coordinan módulos
  storage/                        Persistencia JSON
  ui/                             Ventana y componentes visuales
    case_matrix_panel.py          Carga y selección de casos Excel

scripts/
  inspect_latest_execution.py     Diagnóstico manual de la última ejecución

docs/
  architecture.md                 Capas, criterios de diseño y calidad

data/
  executions/                     Artefactos técnicos de cada grabación
  flows/                          Flujos reutilizables
  test_cases/                     Casos de prueba Word
```

## Dónde tocar cada funcionalidad

- Cambiar la apariencia o botones: `app/ui/main_window.py`.
- Cambiar la experiencia de la matriz Excel: `app/ui/case_matrix_panel.py`.
- Cambiar captura de clicks, inputs o screenshots: `app/recorder/browser_recorder.py`.
- Cambiar qué valores se protegen antes de guardarse: `app/recorder/sensitive_data.py`.
- Cambiar agrupación y descripción de acciones QA: `app/recorder/event_parser.py`.
- Cambiar reproducción automática: `app/automation/flow_runner.py`.
- Cambiar estructura del Word: `app/reporting/test_case_report.py`.
- Cambiar qué archivos se crean al finalizar: `app/services/artifact_service.py`.
- Cambiar carpetas de salida: `app/config.py`.
- Cambiar persistencia JSON: `app/storage/json_repository.py`.

## Flujo de una ejecución

1. La UI crea un `BrowserRecorder`.
2. El recorder captura eventos y screenshots.
3. Al finalizar, `TestArtifactService` genera `actions.json`, `qa_actions.json`, el flujo reutilizable y el Word.
4. `FlowRunner` puede reproducir el último flujo guardado.

## Instalación

```powershell
python -m pip install -r requirements.txt
```

`recorder.py` es una implementación anterior mantenida solo por compatibilidad. El código activo está dentro de `app/`.

## Calidad y SonarQube

Para preparar el analisis local:

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s test
python -m bandit -r app -ll
python -m coverage run -m unittest discover -s test
python -m coverage xml
```

El archivo `sonar-project.properties` configura SonarQube para analizar `app/`, reconocer `test/` y leer `coverage.xml`. Instala SonarScanner aparte y configura `SONAR_HOST_URL` y `SONAR_TOKEN` como variables de entorno; no guardes credenciales en el repositorio. Consulta [docs/architecture.md](docs/architecture.md) para las responsabilidades por capa y el uso adecuado de POM.

El script de diagnóstico manual se ejecuta con:

```powershell
python scripts/inspect_latest_execution.py
```

## Crear ejecutable de Windows

En PowerShell, desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt pyinstaller
.\build.ps1
```

El resultado queda en `dist/QA-Test-Recorder/`. Debe copiarse la carpeta completa, no solo el `.exe`.

La PC destino debe tener instalado el **Microsoft Visual C++ Redistributable 2015-2022 x64**. El mensaje `python313.dll: no se puede encontrar el módulo especificado` suele indicar que falta ese runtime o que se está copiando solo una parte de la distribución.
