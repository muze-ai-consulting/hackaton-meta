// Demo de Ensayo: formulario de variantes, llamada a /api/simulate y tablero del backtest.
"use strict";

const LETTERS = "ABCDEF";
const MAX_VARIANTS = 6;
const EXAMPLE = {
  brand: "Café Andino (ejemplo)",
  variants: [
    { title: "Compra ahora", body: "Café de especialidad tostado esta semana. 20 % de descuento en tu primera bolsa." },
    { title: "Pruébalo gratis", body: "Más de 10.000 personas ya cambiaron su café de supermercado por el nuestro." },
    { title: "Descúbrelo", body: "¿Tu café de la mañana sabe a nada? Prueba uno tostado a mano en Viena." },
  ],
};

const $ = (sel, root = document) => root.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const pct = (x) => `${((x || 0) * 100).toLocaleString("es", { maximumFractionDigits: 1 })} %`;
const dec = (x, d = 3) => x.toLocaleString("es", { minimumFractionDigits: d, maximumFractionDigits: d });

let config = { real_allowed: false, real_max_personas: 300 };

// Pestañas
function showTab(name) {
  for (const t of ["ensayar", "prueba"]) {
    $(`#tab-${t}`).setAttribute("aria-selected", String(t === name));
    $(`#view-${t}`).hidden = t !== name;
  }
  if (name === "prueba") loadBacktest();
}
$("#tab-ensayar").addEventListener("click", () => showTab("ensayar"));
$("#tab-prueba").addEventListener("click", () => showTab("prueba"));

// Variantes
function relabel() {
  const items = [...document.querySelectorAll("#variants .variant")];
  items.forEach((el, i) => {
    $(".variant-label", el).textContent = `Variante ${LETTERS[i]}`;
    $(".remove", el).hidden = items.length <= 2;
  });
  $("#add-variant").disabled = items.length >= MAX_VARIANTS;
}

function addVariant(v = { title: "", body: "" }) {
  const el = $("#variant-tpl").content.firstElementChild.cloneNode(true);
  $(".v-title", el).value = v.title;
  $(".v-body", el).value = v.body;
  $(".remove", el).addEventListener("click", () => { el.remove(); relabel(); });
  const thumb = $(".thumb", el);
  const clear = $(".clear-image", el);
  if (v.image_url) { el.dataset.image = v.image_url; thumb.src = v.image_url; thumb.hidden = false; clear.hidden = false; }
  $(".v-image", el).addEventListener("change", (ev) => {
    const file = ev.target.files[0];
    if (!file) return;
    if (file.size > 3 * 1024 * 1024) { showError("La imagen pesa más de 3 MB."); ev.target.value = ""; return; }
    const reader = new FileReader();
    reader.onload = () => { el.dataset.image = reader.result; thumb.src = reader.result; thumb.hidden = false; clear.hidden = false; };
    reader.readAsDataURL(file);
  });
  clear.addEventListener("click", () => {
    delete el.dataset.image; thumb.hidden = true; clear.hidden = true; $(".v-image", el).value = "";
  });
  $("#variants").appendChild(el);
  relabel();
}

$("#add-variant").addEventListener("click", () => addVariant());

// Variantes generadas con Muse Image
let photo = null;
$("#photo").addEventListener("change", (ev) => {
  const file = ev.target.files[0];
  if (!file) return;
  if (file.size > 3 * 1024 * 1024) { showError("La foto pesa más de 3 MB."); ev.target.value = ""; return; }
  const reader = new FileReader();
  reader.onload = () => { photo = reader.result; $("#photo-thumb").src = photo; $("#photo-thumb").hidden = false; $("#photo-clear").hidden = false; };
  reader.readAsDataURL(file);
});
$("#photo-clear").addEventListener("click", () => {
  photo = null; $("#photo").value = ""; $("#photo-thumb").hidden = true; $("#photo-clear").hidden = true;
});

$("#gen-variants").addEventListener("click", async () => {
  const brief = $("#brief").value.trim();
  if (!brief && !photo) { showError("Describe el producto o sube una foto para generar variantes."); return; }
  showError("");
  const n = Number($("#n-variants").value);
  const mode = document.querySelector('input[name="mode"]:checked').value;
  const btn = $("#gen-variants");
  const status = $("#gen-status");
  btn.disabled = true;
  btn.textContent = "Generando…";
  status.textContent = `Escribiendo ${n} ángulos y generando ${n} imágenes…`;
  try {
    const res = await fetch("api/variants", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ brand: $("#brand").value.trim(), brief, photo_url: photo, n, mode }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Revisa los datos.");
    $("#variants").innerHTML = "";
    data.variants.forEach(addVariant);
    status.textContent = data.mode === "mock"
      ? `Listo: ${data.variants.length} variantes de prueba con imágenes de relleno (costaría US$ ${dec(data.usd)} en real).`
      : `Listo: ${data.variants.length} variantes con Muse Image · costo: US$ ${dec(data.usd)}.`;
  } catch (err) {
    status.textContent = "";
    showError(`No se pudieron generar las variantes: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "Generar variantes";
  }
});
$("#personas").addEventListener("input", (e) => { $("#personas-out").textContent = e.target.value; });

function showError(msg) {
  const box = $("#form-error");
  box.textContent = msg;
  box.hidden = !msg;
}

function readForm() {
  const variants = [...document.querySelectorAll("#variants .variant")].map((el) => ({
    title: $(".v-title", el).value.trim(),
    body: $(".v-body", el).value.trim(),
    image_url: el.dataset.image || null,
  }));
  return {
    brand: $("#brand").value.trim(),
    variants,
    target: {
      age_min: Number($("#age-min").value),
      age_max: Number($("#age-max").value),
      gender: $("#gender").value,
      countries: $("#countries").value.split(",").map((c) => c.trim()).filter(Boolean),
    },
    personas: Number($("#personas").value),
    mode: document.querySelector('input[name="mode"]:checked').value,
  };
}

function validate(req) {
  if (req.variants.some((v) => !v.title && !v.body && !v.image_url)) return "Cada variante necesita título, texto o imagen.";
  const { age_min, age_max } = req.target;
  if (!(age_min >= 18 && age_max <= 65 && age_min <= age_max)) return "La edad va de 18 a 65, y «desde» no puede superar a «hasta».";
  if (req.target.countries.some((c) => !/^[A-Za-z]{2}$/.test(c))) return "Usa códigos de país de dos letras, como GB, DE o FR.";
  return "";
}

// Ensayo
$("#form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const req = readForm();
  const problem = validate(req);
  showError(problem);
  if (problem) return;
  const btn = $("#run");
  btn.disabled = true;
  btn.textContent = "Ensayando…";
  const calls = Math.ceil(req.personas / 20) + 1;
  $("#results").innerHTML = `
    <p class="notice">Simulando ${req.personas} personas en ${calls} llamadas…</p>
    <div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div>`;
  try {
    const res = await fetch("api/simulate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(req) });
    const data = await res.json();
    if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Revisa los datos del formulario.");
    renderResult(req, data);
  } catch (err) {
    $("#results").innerHTML = `<div class="panel"><p class="error">No se pudo ensayar: ${esc(err.message)}</p></div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = "Ensayar";
  }
});

function renderResult(req, data) {
  const pop = data.population;
  const label = Object.fromEntries(req.variants.map((_, i) => [`v${i + 1}`, LETTERS[i]]));
  const byId = Object.fromEntries(req.variants.map((v, i) => [`v${i + 1}`, v]));
  const winner = pop.ranking[0];
  const maxScore = Math.max(...pop.ranking.map((id) => pop.stats[id].stop_rate), 0.01);
  const singleTop = data.single_call.ranking[0];
  const agree = singleTop === winner;

  const notice = data.mode === "mock"
    ? `<p class="notice warn">Modo prueba: las reacciones salen del servidor falso y no tienen señal. Sirven para ver el circuito, no para decidir.</p>`
    : `<p class="notice">Simulado con ${esc(data.model)} · costo de este ensayo: US$ ${dec(data.usd)}</p>`;

  const rows = pop.ranking.map((id, i) => {
    const s = pop.stats[id];
    const v = byId[id];
    const reasons = s.click_reasons.length
      ? `<details><summary>Por qué hicieron clic (${s.click_reasons.length})</summary><ul>${s.click_reasons.map((r) => `<li>${esc(r)}</li>`).join("")}</ul></details>`
      : "";
    return `
      <li class="${i === 0 ? "first" : ""}">
        <span class="pos" aria-label="Puesto ${i + 1}">${i + 1}</span>
        <div class="r-main">
          <div class="r-head">
            ${v.image_url ? `<img src="${v.image_url}" alt="Imagen de la variante ${label[id]}">` : ""}
            <div>
              <div class="r-title">Variante ${label[id]} · ${esc(v.title || "(sin título)")}</div>
              <div class="r-body">${esc(v.body)}</div>
            </div>
          </div>
          <div class="bars">
            <span>Se detienen</span><div class="bar stop"><span style="width:${(s.stop_rate / maxScore) * 100}%"></span></div><span class="num">${pct(s.stop_rate)}</span>
            <span>Hacen clic</span><div class="bar click"><span style="width:${(s.click_rate / maxScore) * 100}%"></span></div><span class="num">${pct(s.click_rate)}</span>
          </div>
          ${reasons}
        </div>
      </li>`;
  }).join("");

  const segments = Object.keys(pop.stats[winner].stop_rate_by_segment);
  const heatMax = Math.max(0.01, ...pop.ranking.flatMap((id) => Object.values(pop.stats[id].stop_rate_by_segment)));
  const table = `
    <table>
      <thead><tr><th scope="col">Segmento</th>${pop.ranking.map((id) => `<th scope="col">${label[id]}</th>`).join("")}</tr></thead>
      <tbody>${segments.map((seg) => `
        <tr><th scope="row">${esc(seg.replace("instagram", "Instagram").replace("facebook", "Facebook"))}</th>${pop.ranking.map((id) => {
          const x = pop.stats[id].stop_rate_by_segment[seg] || 0;
          return `<td class="heat" style="background: rgba(168,85,247,${(0.06 + 0.4 * x / heatMax).toFixed(2)})">${pct(x)}</td>`;
        }).join("")}</tr>`).join("")}
      </tbody>
    </table>`;

  const order = (ranking) => `<ol class="order">${ranking.map((id, i) => `<li class="${i === 0 ? "top" : ""}">${label[id]}</li>`).join("")}</ol>`;

  const people = pop.sample_reactions.map((p, i) => `
    <div class="person">
      <div class="who">${esc(p.persona)}</div>
      <div class="what">${p.stopped.length ? `Se detiene en ${p.stopped.map((id) => label[id]).join(", ")}` : "Pasa de largo todos los anuncios"}${p.clicked.length ? ` · clic en ${p.clicked.map((id) => label[id]).join(", ")}` : ""}</div>
      ${p.reason ? `<div class="why">${esc(p.reason)}</div>` : ""}
      <button type="button" class="btn-secondary talk" data-person="${i}">Conversar</button>
    </div>`).join("");

  $("#results").innerHTML = `
    ${notice}
    <div class="summary">
      <div class="kpi win"><div class="k-label">Gana</div><div class="k-value">Variante ${label[winner]}</div></div>
      <div class="kpi"><div class="k-label">Personas</div><div class="k-value">${data.personas}</div></div>
      <div class="kpi"><div class="k-label">Se detienen en la ganadora</div><div class="k-value">${pct(pop.stats[winner].stop_rate)}</div></div>
      <div class="kpi"><div class="k-label">Llamadas al modelo</div><div class="k-value">${pop.calls + 1}</div></div>
    </div>
    <section class="panel"><h2>Ranking de la audiencia</h2><ol class="rank">${rows}</ol></section>
    <section class="panel">
      <h2>Audiencia contra una sola llamada</h2>
      <div class="compare">
        <div><h3>Audiencia sintética</h3>${order(pop.ranking)}</div>
        <div><h3>Spark 1.3 en una llamada</h3>${order(data.single_call.ranking)}</div>
      </div>
      <p class="hint">${agree ? "Las dos coinciden en la ganadora." : "No coinciden en la ganadora: la audiencia ve algo que la llamada única no ve, o al revés. El backtest dice cuál acierta más."}</p>
    </section>
    <section class="panel"><h2>Quién se detiene, por segmento</h2><div class="table-wrap">${table}</div></section>
    <section class="panel"><h2>Algunas personas de la audiencia</h2><p class="hint">Pregúntale a cualquiera por qué se detuvo, hizo clic o pasó de largo.</p><div class="people">${people}</div></section>
    <section class="panel chat" id="chat" hidden></section>`;
  document.querySelectorAll("#results .talk").forEach((b) => b.addEventListener("click", () => openChat(req, data, pop.sample_reactions[Number(b.dataset.person)], label)));
}

// Conversar con una persona
const SUGGESTED = ["¿Por qué te detuviste en ese anuncio?", "¿Qué tendría que decir el anuncio para que hicieras clic?", "¿Cuánto pagarías por esto?"];

function openChat(req, data, person, label) {
  const box = $("#chat");
  const history = [];
  const reaction = person.stopped.length ? `Se detuvo en ${person.stopped.map((id) => label[id]).join(", ")}` : "Pasó de largo todos los anuncios";
  box.hidden = false;
  box.innerHTML = `
    <div class="chat-head">
      <div><h2>Conversación</h2><p class="hint">${esc(person.persona)}</p><p class="chip">${esc(reaction)}</p></div>
      <button type="button" class="link chat-close">Cerrar</button>
    </div>
    ${data.mode === "mock" ? `<p class="notice warn">Modo prueba: las respuestas salen del servidor falso.</p>` : ""}
    <div class="messages" aria-live="polite"></div>
    <div class="suggested">${SUGGESTED.map((q) => `<button type="button" class="chip-btn">${esc(q)}</button>`).join("")}</div>
    <form class="chat-form">
      <input type="text" maxlength="500" placeholder="Escribe una pregunta…" aria-label="Pregunta para la persona" required>
      <button type="submit" class="btn-primary">Enviar</button>
    </form>`;
  const list = $(".messages", box);
  const input = $(".chat-form input", box);
  const send = async (question) => {
    question = question.trim();
    if (!question) return;
    list.insertAdjacentHTML("beforeend", `<div class="msg user">${esc(question)}</div><div class="msg persona typing">…</div>`);
    list.scrollTop = list.scrollHeight;
    input.value = "";
    const pending = list.lastElementChild;
    try {
      const res = await fetch("api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brand: req.brand, persona: person.persona, variants: req.variants,
          stopped: person.stopped, clicked: person.clicked, reason: person.reason,
          history, question, mode: data.mode,
        }),
      });
      const out = await res.json();
      if (!res.ok) throw new Error(typeof out.detail === "string" ? out.detail : "Error");
      pending.classList.remove("typing");
      pending.textContent = out.answer;
      history.push({ role: "user", text: question }, { role: "persona", text: out.answer });
    } catch (err) {
      pending.classList.remove("typing");
      pending.classList.add("error");
      pending.textContent = `No respondió: ${err.message}`;
    }
    list.scrollTop = list.scrollHeight;
  };
  $(".chat-form", box).addEventListener("submit", (ev) => { ev.preventDefault(); send(input.value); });
  box.querySelectorAll(".chip-btn").forEach((b) => b.addEventListener("click", () => send(b.textContent)));
  $(".chat-close", box).addEventListener("click", () => { box.hidden = true; });
  box.scrollIntoView({ behavior: "smooth", block: "start" });
  input.focus();
}

// Prueba del modelo
async function loadBacktest() {
  const box = $("#backtest");
  box.innerHTML = `<div class="skeleton"></div>`;
  try {
    const res = await fetch("api/backtest");
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Sin resultados.");
    renderBacktest(data);
  } catch (err) {
    box.innerHTML = `<div class="panel"><h2>Prueba del modelo</h2><p>${esc(err.message)}</p></div>`;
  }
}

function ciRows(summary, metric, chance) {
  const rivals = [["population", "Audiencia sintética", "pop"], ["single_call", "Llamada única", ""], ["random", "Azar", ""]];
  const lo = 0, hi = 1;
  const x = (v) => `${((v - lo) / (hi - lo)) * 100}%`;
  return rivals.filter(([k]) => summary[k]?.[metric]).map(([k, name, cls]) => {
    const m = summary[k][metric];
    return `
      <div class="ci-row ${cls}">
        <span>${name}</span>
        <div class="ci-track" role="img" aria-label="${name}: ${dec(m.mean)} (intervalo ${dec(m.ci95[0], 2)} a ${dec(m.ci95[1], 2)})">
          ${chance != null ? `<span class="ci-chance" style="left:${x(chance)}"></span>` : ""}
          <span class="ci-range" style="left:${x(m.ci95[0])}; width:calc(${x(m.ci95[1])} - ${x(m.ci95[0])})"></span>
          <span class="ci-dot" style="left:${x(m.mean)}"></span>
        </div>
        <span class="num">${dec(m.mean)} <span class="hint">[${dec(m.ci95[0], 2)}–${dec(m.ci95[1], 2)}]</span></span>
      </div>`;
  }).join("");
}

function renderBacktest(d) {
  const s = d.summary;
  const pw = (k) => s[k]?.pairwise?.mean;
  const beats = pw("population") != null && pw("single_call") != null && pw("population") > pw("single_call");
  const notice = d.mock
    ? `<p class="notice warn">Estos números vienen del servidor falso con lotes de ejemplo: miden que el circuito funciona, no que el modelo acierte. Se reemplazan por la corrida real con anuncios de la Biblioteca de anuncios de Meta.</p>`
    : `<p class="notice">Corrida real con ${esc(d.model)} sobre ${d.batches} lotes (${esc(d.source)}). Costo: US$ ${dec(Number(d.usd), 2)}.</p>`;
  $("#backtest").innerHTML = `
    ${notice}
    <div class="summary">
      <div class="kpi ${beats ? "win" : ""}"><div class="k-label">Pares bien ordenados, audiencia</div><div class="k-value">${pw("population") != null ? dec(pw("population")) : "—"}</div></div>
      <div class="kpi"><div class="k-label">Llamada única</div><div class="k-value">${pw("single_call") != null ? dec(pw("single_call")) : "—"}</div></div>
      <div class="kpi"><div class="k-label">Azar</div><div class="k-value">${pw("random") != null ? dec(pw("random")) : "—"}</div></div>
      <div class="kpi"><div class="k-label">Lotes comparados</div><div class="k-value">${d.batches}</div></div>
    </div>
    <section class="panel">
      <h2>Pares bien ordenados, con intervalo del 95 %</h2>
      <p class="hint">De cada par de anuncios del mismo anunciante y la misma semana, qué fracción ordena bien según el alcance real en la UE. El azar acierta la mitad (línea punteada).</p>
      <div class="ci">${ciRows(s, "pairwise", 0.5)}</div>
      <div class="ci-axis" aria-hidden="true"><span>0</span><span>0,5</span><span>1</span></div>
    </section>
    <section class="panel">
      <h2>Acierto de la ganadora</h2>
      <p class="hint">Si el anuncio que cada método pone primero es el de mayor alcance real.</p>
      <div class="ci">${ciRows(s, "top1", null)}</div>
      <div class="ci-axis" aria-hidden="true"><span>0</span><span>0,5</span><span>1</span></div>
    </section>
    <section class="panel">
      <h2>Cómo se mide</h2>
      <ol class="steps">
        <li>Solo anuncios que empezaron después del 2 de septiembre de 2026, cuando salió Muse Spark 1.3: el modelo no pudo haberlos visto.</li>
        <li>Se compara dentro de cada anunciante y semana de lanzamiento, porque el alcance bruto depende del presupuesto.</li>
        <li>Las etiquetas del set sellado tienen su SHA-256 publicado antes de correr el modelo, y los rankings también.</li>
        <li>Rivales obligatorios: el azar y una sola llamada a Spark 1.3 sin audiencia.</li>
      </ol>
      <p class="hint">Archivo: ${esc(d.file)} · ${esc(d.ran_at)}</p>
    </section>`;
}

// Inicio
async function init() {
  $("#brand").value = EXAMPLE.brand;
  EXAMPLE.variants.forEach(addVariant);
  try {
    config = await (await fetch("api/config")).json();
  } catch { /* sin config: queda solo el modo prueba */ }
  const real = $("#mode-real");
  real.disabled = !config.real_allowed;
  $("#real-hint").textContent = config.real_allowed
    ? `(gasta créditos; máximo ${config.real_max_personas} personas)`
    : "(desactivado en este servidor)";
}
init();
