# Estructura de Bouligand - Visualizador 3D Web

Aplicación web para generar y visualizar una estructura tipo Bouligand en 3D de forma interactiva.
Permite elegir:
- Sentido de giro (`izquierda` o `derecha`)
- Ángulo de rotación total entre la primera y la última capa

La visualización se genera con Plotly y se muestra en el navegador.

## Qué hace el proyecto

1. El usuario abre la interfaz web.
2. Selecciona parámetros de giro.
3. La app envía esos datos al backend (`Flask`).
4. El backend ejecuta la generación geométrica en `bouligand3D.py`.
5. Se guarda un HTML 3D en `outputs/cilindro.html`.
6. La interfaz carga ese HTML en un visor embebido.

## Estructura del repositorio

- `app.py`
  - Backend Flask.
  - Define rutas:
    - `GET /` -> carga la interfaz.
    - `POST /generar` -> genera la estructura 3D.
    - `GET /outputs/<archivo>` -> sirve los HTML generados.

- `bouligand3D.py`
  - Núcleo matemático y visual de la estructura.
  - Calcula geometría por capas y cilindros.
  - Aplica rotación por capa según sentido y ángulo.
  - Construye la malla 3D (`Mesh3d`) y contornos.
  - Exporta el resultado a HTML con Plotly.

- `templates/index.html`
  - Interfaz principal.
  - Contiene formulario de parámetros y visor (`iframe`).

- `static/app.js`
  - Lógica del frontend.
  - Envía parámetros al endpoint `/generar`.
  - Maneja respuesta y errores.
  - Actualiza el visor con el HTML recién generado.

- `static/styles.css`
  - Estilos visuales de la página.

- `outputs/`
  - Carpeta de archivos generados en ejecución.
  - El archivo principal generado es `cilindro.html`.

- `requirements.txt`
  - Dependencias Python necesarias para ejecutar.

- `Procfile`
  - Comando de arranque para Render: `gunicorn app:app`.

## Parámetros importantes en `bouligand3D.py`

- `LARGO_CILINDRO`: longitud de cada fibra.
- `ANCHO_CAPA`: ancho total ocupado por una capa.
- `N_CILINDROS`: número de fibras por capa.
- `N_CAPAS`: número de capas apiladas.
- `ANGULO_FINAL`: rotación acumulada de la última capa.
- `SENTIDO_GIRO`: `izquierda` o `derecha`.
- `RES_CIRCULO`: calidad de redondeo de cada cilindro (más alto = más detalle y más carga).
- `MARGEN_ENCUADRE`: margen del encuadre en la vista 3D.

## Flujo de generación (resumen técnico)

1. Se discretiza cada cilindro en segmentos angulares.
2. Cada capa aplica una rotación progresiva respecto a la anterior.
3. Se forman triángulos para la malla lateral y tapas.
4. Se colorean vértices según iluminación/sombreado.
5. Plotly renderiza la figura y la exporta a HTML interactivo.

## Ejecución local

1. Crear entorno virtual (opcional):
   - `python -m venv .venv`
   - Windows: `.venv\\Scripts\\activate`

2. Instalar dependencias:
   - `pip install -r requirements.txt`

3. Ejecutar servidor:
   - `python app.py`

4. Abrir en navegador:
   - `http://127.0.0.1:5000`

## Despliegue en Render

Configurar el servicio con:
- Runtime: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

## Notas útiles

- Si el navegador muestra errores de WebGL, usa Chrome/Firefox o habilita aceleración por hardware.
- Si no ves cambios tras deploy, fuerza recarga (`Ctrl + F5`).
- Para evitar confusión de sentido visual, prueba ángulos como `120` o `180` en lugar de `360`.
