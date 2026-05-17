import numpy as np
from pathlib import Path
import plotly.graph_objects as go
from matplotlib.colors import to_rgb

LARGO_CILINDRO = 4.0  # Longitud de cada fibra (eje local x)
ANCHO_CAPA = 4.0  # Ancho total ocupado por una capa en y
N_CILINDROS = 25  # Fibras por capa
SEPARACION_LATERAL = 0.01  # Separacion extra entre fibras vecinas

N_CAPAS = 40  # Numero de capas apiladas 
ANGULO_FINAL = 180  # Giro acumulado de la ultima capa (grados)
SENTIDO_GIRO = "izquierda"  # "izquierda" o "derecha"

COLOR_FIBRA = "#6DD17A"
MODO_COLOR = "automatico"  # "automatico" o "fijo"
COLOR_SOMBRA_FIJA = "#0d3113"
COLOR_LUZ_FIJA = "#6cb945"
COLOR_TAPA_X0_FIJA = "#6cb945"
COLOR_TAPA_X1_FIJA = "#0d3113"
BASE_CONTORNO_FACTOR = 0.18
BASE_CONTORNO_WIDTH = 3

FACTOR_TAPA_X0 = 0.62
FACTOR_TAPA_X1 = 1.02
FACTOR_LATERAL_CLARO = 1.0
FACTOR_LATERAL_OSCURO = 0.0
DESFASE_SOMBRA_GRADOS = 22.0
SUAVIDAD_SOMBRA = 1.15

RES_CIRCULO = 24  # Resolucion circular: mas alto = mas suave y mas pesado

LUZ_X = 0.0
LUZ_Y = 0.0
LUZ_Z = 1.0
AMBIENT = 1.0
DIFFUSE = 0.0
SPECULAR = 0.0
ROUGHNESS = 1.0
FRESNEL = 0.0

PROYECCION = "perspective"  # "orthographic" o "perspective"
MARGEN_ENCUADRE = 0


def factor_sentido(sentido):
    s = str(sentido).strip().lower()
    if s == "derecha":
        return 1.0
    if s == "izquierda":
        return -1.0
    raise ValueError('SENTIDO_GIRO debe ser "derecha" o "izquierda".')


def rotar_xy(x, y, ang_deg):
    t = np.deg2rad(ang_deg)
    c, s = np.cos(t), np.sin(t)
    xr = c * x - s * y
    yr = s * x + c * y
    return xr, yr


def escalar_color(hex_color, factor):
    c = np.array(to_rgb(hex_color), dtype=float)
    c = np.clip(c * factor, 0.0, 1.0)
    return f"rgb({int(c[0] * 255)},{int(c[1] * 255)},{int(c[2] * 255)})"


def mezclar_colores(hex_a, hex_b, t):
    a = np.array(to_rgb(hex_a), dtype=float)
    b = np.array(to_rgb(hex_b), dtype=float)
    c = np.clip((1.0 - t) * a + t * b, 0.0, 1.0)
    return f"rgb({int(c[0] * 255)},{int(c[1] * 255)},{int(c[2] * 255)})"


def color_lateral_por_angulo(ang):
    fase = ang - np.deg2rad(DESFASE_SOMBRA_GRADOS)
    t = 0.5 * (1.0 + np.cos(fase))
    t = np.clip(t, 0.0, 1.0) ** (1.0 / SUAVIDAD_SOMBRA)

    if MODO_COLOR == "fijo":
        return mezclar_colores(COLOR_SOMBRA_FIJA, COLOR_LUZ_FIJA, t)

    factor = FACTOR_LATERAL_OSCURO + (FACTOR_LATERAL_CLARO - FACTOR_LATERAL_OSCURO) * t
    return escalar_color(COLOR_FIBRA, factor)


def append_polyline(xs, ys, zs, x, y, z):
    xs.extend(x.tolist())
    ys.extend(y.tolist())
    zs.extend(z.tolist())
    xs.append(None)
    ys.append(None)
    zs.append(None)


def topologia_cilindro(nseg):
    caras = []
    for k in range(nseg):
        kn = (k + 1) % nseg
        caras.append((k, kn, nseg + k))
        caras.append((kn, nseg + kn, nseg + k))
    i_ring0_cap = 2 * nseg
    i_ring1_cap = 3 * nseg
    i_c0 = 4 * nseg
    i_c1 = 4 * nseg + 1
    for k in range(nseg):
        kn = (k + 1) % nseg
        caras.append((i_c0, i_ring0_cap + kn, i_ring0_cap + k))
    for k in range(nseg):
        kn = (k + 1) % nseg
        caras.append((i_c1, i_ring1_cap + k, i_ring1_cap + kn))
    return np.array(caras, dtype=int)


def agregar_cilindro_mesh(vertices, vcolors, tris, x0, x1, yc, zc, r, ang_deg, side_colors, tri_base, nseg=36):
    base = len(vertices)
    th = np.linspace(0.0, 2.0 * np.pi, nseg, endpoint=False)

    y0 = yc + r * np.cos(th)
    z0 = zc + r * np.sin(th)

    x0a = np.full_like(th, x0)
    x1a = np.full_like(th, x1)

    x0r, y0r = rotar_xy(x0a, y0, ang_deg)
    x1r, y1r = rotar_xy(x1a, y0, ang_deg)

    ring0_side = np.column_stack([x0r, y0r, z0])
    ring1_side = np.column_stack([x1r, y1r, z0])
    ring0_cap = ring0_side.copy()
    ring1_cap = ring1_side.copy()

    cx0, cy0 = rotar_xy(np.array([x0]), np.array([yc]), ang_deg)
    cx1, cy1 = rotar_xy(np.array([x1]), np.array([yc]), ang_deg)
    c0 = np.array([[cx0[0], cy0[0], zc]])
    c1 = np.array([[cx1[0], cy1[0], zc]])

    verts_local = np.vstack([ring0_side, ring1_side, ring0_cap, ring1_cap, c0, c1])
    vertices.extend(verts_local.tolist())

    if MODO_COLOR == "fijo":
        tapa0 = COLOR_TAPA_X0_FIJA
        tapa1 = COLOR_TAPA_X1_FIJA
    else:
        tapa0 = escalar_color(COLOR_FIBRA, FACTOR_TAPA_X0)
        tapa1 = escalar_color(COLOR_FIBRA, FACTOR_TAPA_X1)

    vcolors.extend(side_colors)
    vcolors.extend(side_colors)
    for _ in th:
        vcolors.append(tapa0)
    for _ in th:
        vcolors.append(tapa1)
    vcolors.append(tapa0)
    vcolors.append(tapa1)
    tris.extend((tri_base + base).tolist())


def generar_figura(sentido_giro="izquierda", angulo_final=None):
    sentido = factor_sentido(sentido_giro)
    angulo_objetivo = ANGULO_FINAL if angulo_final is None else float(angulo_final)

    n_cil = max(1, int(N_CILINDROS))
    n_stack = max(1, int(N_CAPAS))

    diametro = ANCHO_CAPA / n_cil
    radio = diametro / 2.0
    grosor_capa_ajustado = diametro
    altura_total = n_stack * grosor_capa_ajustado
    paso_lateral = diametro + max(0.0, SEPARACION_LATERAL)
    ancho_util = n_cil * diametro + (n_cil - 1) * max(0.0, SEPARACION_LATERAL)

    x0, x1 = -LARGO_CILINDRO / 2.0, LARGO_CILINDRO / 2.0
    y_inicio = -ancho_util / 2.0 + radio

    vertices, vcolors, triangulos = [], [], []
    base_x, base_y, base_z = [], [], []

    th_closed = np.linspace(0.0, 2.0 * np.pi, RES_CIRCULO + 1)
    th = np.linspace(0.0, 2.0 * np.pi, RES_CIRCULO, endpoint=False)
    side_colors = [color_lateral_por_angulo(ang) for ang in th]
    tri_base = topologia_cilindro(RES_CIRCULO)

    for i in range(n_stack):
        z_centro_capa = i * grosor_capa_ajustado + radio

        if n_stack <= 1:
            ang_base = 0.0
        else:
            ang_base = (angulo_objetivo * i) / (n_stack - 1)
        ang_i = sentido * ang_base

        for j in range(n_cil):
            yc = y_inicio + j * paso_lateral

            agregar_cilindro_mesh(
                vertices,
                vcolors,
                triangulos,
                x0,
                x1,
                yc,
                z_centro_capa,
                radio,
                ang_i,
                side_colors,
                tri_base,
                RES_CIRCULO,
            )

            yb = yc + radio * np.cos(th_closed)
            zb = z_centro_capa + radio * np.sin(th_closed)
            xb0 = np.full_like(th_closed, x0)
            xb1 = np.full_like(th_closed, x1)
            xb0r, yb0r = rotar_xy(xb0, yb, ang_i)
            xb1r, yb1r = rotar_xy(xb1, yb, ang_i)
            append_polyline(base_x, base_y, base_z, xb0r, yb0r, zb)
            append_polyline(base_x, base_y, base_z, xb1r, yb1r, zb)

    v = np.array(vertices)
    tri = np.array(triangulos)

    base_color = escalar_color(COLOR_FIBRA, BASE_CONTORNO_FACTOR)

    fig = go.Figure()
    fig.add_trace(
        go.Mesh3d(
            x=v[:, 0],
            y=v[:, 1],
            z=v[:, 2],
            i=tri[:, 0],
            j=tri[:, 1],
            k=tri[:, 2],
            vertexcolor=vcolors,
            opacity=1.0,
            flatshading=True,
            lighting=dict(
                ambient=AMBIENT,
                diffuse=DIFFUSE,
                specular=SPECULAR,
                roughness=ROUGHNESS,
                fresnel=FRESNEL,
            ),
            lightposition=dict(x=LUZ_X, y=LUZ_Y, z=LUZ_Z),
            hoverinfo="skip",
            showscale=False,
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=base_x,
            y=base_y,
            z=base_z,
            mode="lines",
            line=dict(color=base_color, width=BASE_CONTORNO_WIDTH),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    x_min, x_max = float(v[:, 0].min()), float(v[:, 0].max())
    y_min, y_max = float(v[:, 1].min()), float(v[:, 1].max())
    z_min, z_max = float(v[:, 2].min()), float(v[:, 2].max())

    cx = 0.5 * (x_min + x_max)
    cy = 0.5 * (y_min + y_max)
    cz = 0.5 * (z_min + z_max)

    x_span = max(x_max - x_min, 1e-6)
    y_span = max(y_max - y_min, 1e-6)
    z_span = max(z_max - z_min, 1e-6)

    # Caja cubica de encuadre: asegura que toda la estructura entre completa
    half = 0.5 * max(x_span, y_span, z_span) * (1.0 + MARGEN_ENCUADRE)

    fig.update_layout(
        width=1100,
        height=900,
        scene=dict(
            xaxis=dict(visible=False, range=[cx - half, cx + half]),
            yaxis=dict(visible=False, range=[cy - half, cy + half]),
            zaxis=dict(visible=False, range=[cz - half, cz + half]),
            aspectmode="cube",
            camera=dict(
                eye=dict(x=1.65, y=1.65, z=1.2),
                up=dict(x=0.0, y=0.0, z=1.0),
                projection=dict(type=PROYECCION),
            ),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
    )

    return fig


def generar_html(sentido_giro="izquierda", salida=None, angulo_final=None):
    fig = generar_figura(sentido_giro=sentido_giro, angulo_final=angulo_final)
    if salida is None:
        salida = Path.home() / "Desktop" / "bouligand3D.html"
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(salida), include_plotlyjs="cdn")
    return salida


if __name__ == "__main__":
    salida = generar_html(sentido_giro=SENTIDO_GIRO)
    print(salida)











