// Adapts the existing TV1 view to the shared TV3 API contract.
function priceText(value, unit = AppState.unit || "") {
  return value == null
    ? "—"
    : `${Number(value).toLocaleString("vi-VN")} ${unit}`;
}

async function loadGoldCurrentAndHistory() {
  try {
    const types = await apiRequest("/api/gold/types");
    AppState.goldTypes = types;
    const models = await apiRequest("/api/model");
    const selected = types.find((t) => t.code === "XAU_VND_LUONG") || types[0];
    if (!selected) throw new Error("Chưa có chuỗi giá.");
    AppState.goldType = selected.code;
    AppState.unit = selected.unit;
    const select = document.getElementById("predictModel");
    const previous = select.value;
    select.replaceChildren(
      ...models.map((m) => new Option(`${m.name} (${m.version})`, String(m.id)))
    );
    if (models.some((m) => String(m.id) === previous)) select.value = previous;
    else
      select.value = String(
        (models.find((m) => m.is_active) || models[0])?.id || ""
      );
    document.getElementById("homeLiveModelName").textContent =
      models.find((m) => String(m.id) === select.value)?.name ||
      "Chưa có model";
    const current = await apiRequest(
      `/api/gold/current?type=${encodeURIComponent(selected.code)}`
    );
    document.getElementById("homeLiveClosePrice").textContent = priceText(
      current.close
    );
    document.getElementById("topTickerPrice").textContent = priceText(
      current.close
    );
    document.getElementById("homeLiveDate").textContent =
      `${current.date} · ${selected.source || "Chưa rõ nguồn"}`;
    const history = await apiRequest(
      `/api/gold/history?type=${encodeURIComponent(selected.code)}&page_size=365&order=desc`
    );
    AppState.priceHistoryData = history.items.slice().reverse();
    const last = history.items[0];
    document.getElementById("homeLiveHighPrice").textContent = priceText(
      last?.high
    );
    document.getElementById("homeLiveLowPrice").textContent = priceText(
      last?.low
    );
    renderPriceChart(AppState.priceHistoryData);
    document.getElementById("homeApiSyncTag").textContent =
      `${selected.code} · ${selected.unit} · ${selected.source || "Chưa rõ nguồn"}`;
  } catch (error) {
    document.getElementById("homeApiSyncTag").textContent = error.message;
  }
  try {
    const evaluation = await apiRequest("/api/model/evaluation");
    const metrics = evaluation.metrics || {};
    for (const [id, key] of [
      ["introMae", "mae"],
      ["introRmse", "rmse"],
      ["introMape", "mape"],
      ["introR2", "r2"],
    ]) {
      const value = metrics[key] ?? metrics[key.toUpperCase()];
      document.getElementById(id).textContent =
        value == null
          ? "Chưa có số liệu"
          : Number(value).toLocaleString("vi-VN") + (key === "mape" ? "%" : "");
    }
    document.getElementById("homeLiveMAPE").textContent =
      metrics.note ||
      "Chỉ số từ báo cáo API; chưa có số liệu thì không suy diễn.";
  } catch {
    document.getElementById("homeLiveMAPE").textContent =
      "Chưa có báo cáo đánh giá.";
  }
}

async function loadPredictionHistory() {
  const token = AppState.jwtToken;
  AppState.predictionHistory = [];
  AppState.historyTotal = 0;
  renderHistoryTable();
  if (!token) {
    document.getElementById("historyTableBody").textContent =
      "Đăng nhập để xem lịch sử dự đoán của bạn.";
    return;
  }
  try {
    const response = await apiRequest("/api/predictions/history");
    if (AppState.jwtToken !== token) return;
    AppState.predictionHistory = response.items;
    AppState.historyTotal = response.total;
    renderHistoryTable();
  } catch (error) {
    if (AppState.jwtToken === token)
      document.getElementById("historyTableBody").textContent = error.message;
  }
}

function renderHistoryTable() {
  const tbody = document.getElementById("historyTableBody");
  const query = document
    .getElementById("historySearchInput")
    .value.toLowerCase();
  document.getElementById("filterTrend").disabled = true;
  const rows = AppState.predictionHistory.filter((item) =>
    `${item.id} ${item.created_at}`.toLowerCase().includes(query)
  );
  tbody.replaceChildren();
  for (const item of rows) {
    const tr = document.createElement("tr");
    for (const value of [
      `#${item.id}`,
      item.created_at,
      item.gold_type,
      `${item.horizon_days} phiên`,
      Number(item.final_predicted_price).toLocaleString("vi-VN"),
      "—",
      item.model.name,
    ]) {
      const td = document.createElement("td");
      td.className = "py-2.5 px-3";
      td.textContent = value;
      tr.append(td);
    }
    const td = document.createElement("td");
    const button = document.createElement("button");
    button.className = "btn-detail-item px-3 py-2";
    button.textContent = "Chi tiết";
    button.addEventListener("click", () => openDetailModal(item.id));
    td.append(button);
    tr.append(td);
    tbody.append(tr);
  }
  if (!rows.length) tbody.textContent = "Chưa có lượt dự đoán phù hợp.";
  document.getElementById("historyRowCount").textContent =
    `Hiển thị ${rows.length} / ${AppState.historyTotal || 0} lượt (trang 1).`;
}

async function openDetailModal(id) {
  try {
    const item = await apiRequest(`/api/predictions/${encodeURIComponent(id)}`);
    const final = item.items[item.items.length - 1];
    if (!final) throw new Error("Lượt dự đoán chưa có điểm kết quả.");
    const unit =
      AppState.goldTypes?.find((t) => t.code === item.gold_type)?.unit ||
      item.gold_type;
    document.getElementById("detModalTitle").textContent =
      `Chi tiết dự đoán #${item.id}`;
    document.getElementById("detModalDate").textContent = item.created_at;
    document.getElementById("detHorizon").textContent =
      `${item.horizon_days} phiên`;
    document.getElementById("detAsset").textContent = item.gold_type;
    document.getElementById("detPredPrice").textContent = priceText(
      final.predicted_price,
      unit
    );
    document.getElementById("detTrend").textContent =
      "Không có dữ liệu xu hướng trong chi tiết";
    document.getElementById("detModel").textContent =
      `${item.model.name} (${item.model.version})`;
    document.getElementById("detMargin").textContent =
      final.lower == null || final.upper == null
        ? "Chưa có khoảng dự báo"
        : `${priceText(final.lower, unit)} – ${priceText(final.upper, unit)}`;
    openModal("modalDetail");
  } catch (error) {
    showToast(error.message, "error");
  }
}

function exportHistoryToCSV() {
  if (!AppState.predictionHistory.length) {
    showToast("Không có dữ liệu lịch sử để xuất.", "error");
    return;
  }
  const fields = [
    "ID",
    "Created_at",
    "Gold_type",
    "Horizon_sessions",
    "Final_target_date",
    "Final_predicted_price",
    "Model",
    "Version",
  ];
  const rows = AppState.predictionHistory.map((item) => [
    item.id,
    item.created_at,
    item.gold_type,
    item.horizon_days,
    item.final_target_date,
    item.final_predicted_price,
    item.model.name,
    item.model.version,
  ]);
  const quote = (value) => {
    const text = String(value ?? "");
    const safe = /^[=+\-@\t\r]/.test(text) ? `'${text}` : text;
    return `"${safe.replaceAll('"', '""')}"`;
  };
  const csv =
    "\uFEFF" +
    [fields, ...rows].map((row) => row.map(quote).join(",")).join("\r\n");
  const url = URL.createObjectURL(
    new Blob([csv], { type: "text/csv;charset=utf-8" })
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = "prediction-history.csv";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function submitPrediction(event) {
  event.preventDefault();
  const button = document.getElementById("btnRunPrediction");
  const badge = document.getElementById("predictResultBadge");
  const cards = document.getElementById("forecastCardsContainer");
  button.disabled = true;
  cards.replaceChildren();
  badge.textContent = "Đang dự đoán...";
  try {
    const modelId = Number(document.getElementById("predictModel").value);
    if (!modelId || !AppState.goldType)
      throw new Error(
        "Chưa tải được mô hình và chuỗi giá. Hãy làm mới dữ liệu."
      );
    const result = await apiRequest("/api/predict", {
      method: "POST",
      body: JSON.stringify({
        gold_type: AppState.goldType,
        horizon_days: Number(document.getElementById("predictDays").value),
        model_id: modelId,
      }),
    });
    for (const item of result.items) {
      const card = document.createElement("div");
      card.className = "p-3 bg-slate-950 rounded-lg border border-brand-border";
      for (const text of [
        item.target_date,
        priceText(item.predicted_price),
        `Xu hướng: ${result.trend}`,
        item.lower == null
          ? "Chưa có khoảng dự báo"
          : `${priceText(item.lower)} – ${priceText(item.upper)}`,
      ]) {
        const line = document.createElement("p");
        line.textContent = text;
        card.append(line);
      }
      cards.append(card);
    }
    badge.textContent = "Đã nhận kết quả API";
    document.getElementById("predictResponseTime").textContent =
      result.prediction_id == null
        ? "Chế độ khách: không lưu lịch sử."
        : `Đã lưu lượt #${result.prediction_id}`;
    if (typeof Chart !== "undefined") {
      AppState.chartInstances.forecastChart?.destroy();
      AppState.chartInstances.forecastChart = new Chart(
        document.getElementById("forecastChartCanvas"),
        {
          type: "line",
          data: {
            labels: [
              result.last_actual.date,
              ...result.items.map((i) => i.target_date),
            ],
            datasets: [
              {
                label: AppState.unit,
                borderColor: "#C5A059",
                data: [
                  result.last_actual.price,
                  ...result.items.map((i) => i.predicted_price),
                ],
              },
            ],
          },
          options: { responsive: true, maintainAspectRatio: false },
        }
      );
    }
    await loadPredictionHistory();
  } catch (error) {
    badge.textContent = "Không dự đoán được";
    showToast(error.message, "error");
  } finally {
    button.disabled = false;
  }
}
