from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from bouligand3D import generar_html

app = Flask(__name__)
OUTPUTS_DIR = Path(__file__).parent / "outputs"


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/generar")
def generar():
    data = request.get_json(silent=True) or {}
    sentido = str(data.get("sentido", "izquierda")).strip().lower()
    modo_estructura = str(data.get("modo_estructura", "fibras")).strip().lower()
    angulo_final = data.get("angulo_final", 180)
    if sentido not in {"derecha", "izquierda"}:
        return jsonify({"ok": False, "error": "Sentido invalido"}), 400
    if modo_estructura not in {"fibras", "capas_planas"}:
        return jsonify({"ok": False, "error": "Modo de capas invalido"}), 400
    try:
        angulo_final = float(angulo_final)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Angulo invalido"}), 400

    salida = OUTPUTS_DIR / "bouligand3D.html"
    try:
        generar_html(
            sentido_giro=sentido,
            salida=salida,
            angulo_final=angulo_final,
            modo_estructura=modo_estructura,
        )
    except Exception as exc:
        return jsonify({"ok": False, "error": f"Error generando figura: {exc}"}), 500
    return jsonify({"ok": True, "viewer_url": "/outputs/bouligand3D.html"})


@app.get("/outputs/<path:filename>")
def serve_outputs(filename):
    return send_from_directory(OUTPUTS_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)
