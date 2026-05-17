# Bouligand Fibras Web

Proyecto para generar la geometria Bouligand con seleccion de giro izquierda/derecha desde una interfaz HTML.

## Estructura

- `bouligandfibras.py`: logica de generacion de la figura Plotly.
- `app.py`: servidor Flask.
- `templates/index.html`: interfaz principal.
- `static/app.js`: llamada al endpoint para generar figura.
- `static/styles.css`: estilos.
- `outputs/`: archivos HTML de salida generados.

## Ejecutar local

1. Crear entorno virtual (opcional):
   - `python -m venv .venv`
   - `.venv\\Scripts\\activate`
2. Instalar dependencias:
   - `pip install -r requirements.txt`
3. Levantar app:
   - `python app.py`
4. Abrir en navegador:
   - `http://127.0.0.1:5000`

Tip: para notar claramente la diferencia entre izquierda/derecha, usa `Angulo final = 120` o `180`.
Con `360`, la figura puede verse casi igual por simetria.

## Subir a GitHub

1. `git init`
2. `git add .`
3. `git commit -m "Primera version web de Bouligand Fibras"`
4. Crear repo en GitHub y conectar remote:
   - `git remote add origin https://github.com/TU_USUARIO/TU_REPO.git`
5. `git branch -M main`
6. `git push -u origin main`

## Desplegar en Render

1. En Render, crear `New +` -> `Web Service`.
2. Conectar tu repo de GitHub.
3. Configurar:
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Deploy.
5. Abrir la URL publica de Render.

Nota: agrega `gunicorn` en `requirements.txt` (ya incluido).
