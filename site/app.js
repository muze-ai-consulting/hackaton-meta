// Ensayo · roadmap. Lee roadmap.json y pinta estado, "Hoy", línea de tiempo y riesgos.
(function () {
  const TZ = "America/Santiago";
  const STATUS_LABEL = { pendiente: "Pendiente", "en-curso": "En curso", hecho: "Hecho", bloqueado: "Bloqueado" };
  const $ = (id) => document.getElementById(id);

  function chileToday() {
    // YYYY-MM-DD en hora de Chile
    return new Intl.DateTimeFormat("en-CA", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  }

  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => {
      if (k === "text") node.textContent = v;
      else if (k === "class") node.className = v;
      else node.setAttribute(k, v);
    });
    (children || []).forEach((c) => c && node.appendChild(c));
    return node;
  }

  function slug(s) {
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z]+/g, "-");
  }

  function ownerTags(owner) {
    return owner.split(" y ").map((name) => el("span", { class: `owner ${slug(name)}`, text: name }));
  }

  function taskItem(task) {
    const status = task.status || "pendiente";
    const li = el("li", { class: status === "hecho" ? "is-done" : "" }, [
      el("span", { class: `status-icon ${status}`, "aria-hidden": "true" }),
      el("span", { class: "task-text", text: task.t }),
      ...ownerTags(task.owner),
      el("span", { class: "task-status", text: STATUS_LABEL[status] || status }),
    ]);
    return li;
  }

  function doneRatio(day) {
    const total = day.tasks.length;
    const done = day.tasks.filter((t) => t.status === "hecho").length;
    return { done, total };
  }

  function phaseOf(data, dayNum) {
    const p = data.phases.find((ph) => ph.days.includes(dayNum));
    return p ? p.name : "";
  }

  function renderCountdown(data) {
    const target = new Date(data.deadline).getTime();
    const node = $("countdown");
    const update = () => {
      const ms = target - Date.now();
      if (ms <= 0) { node.textContent = "Entrega cerrada"; return; }
      const days = Math.floor(ms / 86400000);
      const hours = Math.floor((ms % 86400000) / 3600000);
      node.innerHTML = "";
      node.append("Entrega en ", el("strong", { text: `${days} d ${hours} h` }));
    };
    update();
    setInterval(update, 60000);
  }

  function renderStatus(data, todayIdx) {
    const last = data.days.length - 1;
    const clamped = Math.max(0, Math.min(todayIdx, last));
    const before = todayIdx < 0;
    const after = todayIdx > last;
    $("today-label").textContent = before ? "Antes del día 0" : after ? "Hackatón cerrada" : `Día ${clamped} de ${last} · ${data.days[clamped].label}`;
    const pct = before ? 0 : after ? 100 : Math.round((clamped / last) * 100);
    $("progress-fill").style.width = `${pct}%`;
    $("progress").setAttribute("aria-valuenow", String(before ? 0 : clamped));
    const next = data.days.find((d, i) => i >= Math.max(todayIdx, 0) && (d.decision || d.milestone));
    $("next-milestone").textContent = next ? `${next.decision ? "Punto de decisión" : "Entrega"} · ${next.label.toLowerCase()}` : "—";
    $("updated").textContent = data.updated;
    $("owners-note").textContent = data.ownersNote || "";
  }

  function renderToday(data, todayIdx) {
    const list = $("today-tasks");
    list.innerHTML = "";
    const day = data.days[todayIdx];
    if (!day) {
      $("today-date").textContent = todayIdx < 0 ? "La hackatón parte el 26 de octubre." : "La entrega ya cerró.";
      $("today-goal").textContent = "";
      list.appendChild(el("li", {}, [el("span", { class: "empty", text: "Sin tareas para hoy." })]));
      return;
    }
    $("today-date").textContent = `Día ${day.day} · ${day.label} · ${phaseOf(data, day.day)}`;
    $("today-goal").textContent = day.goal;
    day.tasks.forEach((t) => list.appendChild(taskItem(t)));
  }

  function renderDetail(data, idx) {
    const day = data.days[idx];
    const box = $("day-detail");
    box.innerHTML = "";
    const { done, total } = doneRatio(day);
    const kind = day.decision ? " · Punto de decisión" : day.milestone ? " · Entrega" : "";
    const head = el("div", { class: "detail-head" }, [
      el("h3", { text: `Día ${day.day} · ${day.label}` }),
      el("p", { class: "detail-sub", text: `${phaseOf(data, day.day)}${kind} · ${done} de ${total} tareas hechas` }),
      el("p", { class: "detail-goal", text: day.goal }),
    ]);
    if (day.cut) {
      const cut = el("p", { class: "detail-cut" }, [el("strong", { text: "Corte: " })]);
      cut.append(day.cut);
      head.appendChild(cut);
    }
    const tasks = el("ul", { class: "task-list", "aria-label": `Tareas del día ${day.day}` });
    day.tasks.forEach((t) => tasks.appendChild(taskItem(t)));
    box.append(head, tasks);
  }

  function renderTimeline(data, todayIdx) {
    const phaseRow = $("phase-row");
    const dayRow = $("day-row");
    const todayPhase = phaseOf(data, todayIdx);
    data.phases.forEach((ph) => {
      const span = ph.days.length;
      const start = ph.days[0] + 1;
      const node = el("div", { class: `phase${ph.name === todayPhase ? " is-current" : ""}`, text: ph.name });
      node.style.gridColumn = `${start} / span ${span}`;
      phaseRow.appendChild(node);
    });

    const buttons = [];
    const select = (idx, focus) => {
      buttons.forEach((b, i) => b.setAttribute("aria-pressed", String(i === idx)));
      renderDetail(data, idx);
      if (focus) buttons[idx].focus();
    };

    data.days.forEach((day, i) => {
      const { done, total } = doneRatio(day);
      const flags = [];
      if (i === todayIdx) flags.push(el("span", { class: "day-flag today", text: "Hoy" }));
      if (day.decision) flags.push(el("span", { class: "day-flag decision" }, [el("span", { class: "mark-decision", "aria-hidden": "true" }), document.createTextNode("Decisión")]));
      if (day.milestone) flags.push(el("span", { class: "day-flag milestone" }, [el("span", { class: "mark-milestone", "aria-hidden": "true" }), document.createTextNode("Entrega")]));
      const bar = el("span", { class: "day-bar", "aria-hidden": "true" }, [el("span")]);
      bar.firstChild.style.width = `${total ? Math.round((done / total) * 100) : 0}%`;
      const cls = ["day", i < todayIdx ? "is-past" : "", i === todayIdx ? "is-today" : ""].join(" ").trim();
      const btn = el("button", { type: "button", class: cls, "aria-pressed": "false", "aria-label": `Día ${day.day}, ${day.label}, ${done} de ${total} tareas hechas` }, [
        el("span", { class: "day-phase", text: phaseOf(data, day.day) }),
        el("span", { class: "day-num", text: `Día ${day.day}` }),
        el("span", { class: "day-date", text: day.label }),
        ...flags,
        el("span", { class: "day-meta" }, [bar, el("span", { text: `${done}/${total}` })]),
      ]);
      btn.addEventListener("click", () => select(i, false));
      btn.addEventListener("keydown", (e) => {
        if (e.key === "ArrowRight" && i < data.days.length - 1) { e.preventDefault(); select(i + 1, true); }
        if (e.key === "ArrowLeft" && i > 0) { e.preventDefault(); select(i - 1, true); }
      });
      buttons.push(btn);
      dayRow.appendChild(btn);
    });

    const initial = Math.max(0, Math.min(todayIdx, data.days.length - 1));
    select(initial, false);
  }

  function renderRisks(data) {
    const list = $("risk-list");
    data.risks.forEach((r) => {
      list.appendChild(el("li", {}, [
        el("span", { class: `risk-tag ${r.status}`, text: r.status === "resuelto" ? "Resuelto" : "Abierto" }),
        el("span", { text: r.t }),
      ]));
    });
  }

  fetch("roadmap.json", { cache: "no-store" })
    .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
    .then((data) => {
      const today = chileToday();
      let todayIdx = data.days.findIndex((d) => d.date === today);
      if (todayIdx === -1) todayIdx = today < data.days[0].date ? -1 : data.days.length;
      renderCountdown(data);
      renderStatus(data, todayIdx);
      renderToday(data, todayIdx);
      renderTimeline(data, todayIdx);
      renderRisks(data);
    })
    .catch((err) => {
      $("day-detail").textContent = `No se pudo cargar el roadmap (${err.message}). Recarga la página.`;
    });
})();
