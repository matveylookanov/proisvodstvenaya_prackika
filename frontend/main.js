const form = document.getElementById("metrics-form");
const statusDiv = document.getElementById("status");
const metricsItems = document.getElementById("metrics-items");

function setStatus(message, type) {
  statusDiv.textContent = message;
  statusDiv.className = "status " + (type || "");
}

function toNullableNumber(value) {
  if (value === "" || value === null || value === undefined) return null;
  return Number(value);
}

function loadMetrics() {
  fetch("/metrics?limit=10")
    .then((r) => r.json())
    .then((data) => {
      metricsItems.innerHTML = "";
      data.forEach((m) => {
        const div = document.createElement("div");
        div.className = "metric-item";
        const dt = m.run_datetime || m.created_at;
        const strategyText = m.strategy === "mobile" ? "Мобильная" : "Десктоп";
        div.innerHTML = `
          <span><strong>${m.url}</strong></span>
          <span>${strategyText}</span>
          <span>Производительность: ${m.score_performance ?? "-"}</span>
          <span>Отрисовка крупнейшего элемента: ${m.lcp_ms ?? "-"} мс</span>
          <span>Смещение макета: ${m.cls ?? "-"}</span>
          <span>${new Date(dt).toLocaleString()}</span>
        `;
        metricsItems.appendChild(div);
      });
    })
    .catch(() => {});
}

form.addEventListener("submit", function (e) {
  e.preventDefault();
  setStatus("Сохраняю...", "");

  const formData = new FormData(form);
  const strategy = formData.get("strategy") || "mobile";

  const payload = {
    url: formData.get("url"),
    run_datetime: formData.get("run_datetime") || null,
    strategy: strategy,
    score_performance: toNullableNumber(formData.get("score_performance")),
    score_accessibility: toNullableNumber(formData.get("score_accessibility")),
    score_best_practices: toNullableNumber(formData.get("score_best_practices")),
    score_seo: toNullableNumber(formData.get("score_seo")),
    fcp_ms: toNullableNumber(formData.get("fcp_ms")),
    lcp_ms: toNullableNumber(formData.get("lcp_ms")),
    inp_ms: toNullableNumber(formData.get("inp_ms")),
    ttfb_ms: toNullableNumber(formData.get("ttfb_ms")),
    cls: formData.get("cls") === "" ? null : Number(formData.get("cls")),
    speed_index_ms: toNullableNumber(formData.get("speed_index_ms")),
    tbt_ms: toNullableNumber(formData.get("tbt_ms")),
    total_requests: toNullableNumber(formData.get("total_requests")),
    total_transfer_kb: toNullableNumber(formData.get("total_transfer_kb")),
    notes: formData.get("notes") || null,
  };

  fetch("/metrics", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
    .then(async (r) => {
      if (!r.ok) {
        const err = await r.json().catch(() => ({}));
        throw new Error(err.detail || "Ошибка сохранения");
      }
      return r.json();
    })
    .then(() => {
      setStatus("Сохранено ✅", "success");
      loadMetrics();
    })
    .catch((err) => {
      setStatus("Ошибка: " + err.message, "error");
    });
});

loadMetrics();

