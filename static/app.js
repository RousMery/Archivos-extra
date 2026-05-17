const form = document.getElementById("form");
const estado = document.getElementById("estado");
const viewer = document.getElementById("viewer");

async function generar(sentido, anguloFinal) {
  estado.textContent = "Generando...";

  const res = await fetch("/generar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sentido, angulo_final: anguloFinal })
  });

  const data = await res.json();
  if (!res.ok || !data.ok) {
    throw new Error(data.error || "No se pudo generar la figura.");
  }

  viewer.src = `${data.viewer_url}?t=${Date.now()}`;
  estado.textContent = "Figura actualizada.";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const sentido = document.getElementById("sentido").value;
  const anguloFinal = document.getElementById("angulo_final").value;

  try {
    await generar(sentido, anguloFinal);
  } catch (error) {
    estado.textContent = error.message;
  }
});

generar("izquierda", 180).catch((error) => {
  estado.textContent = error.message;
});
