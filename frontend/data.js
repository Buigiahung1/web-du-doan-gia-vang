// Adapts the existing TV1 view to the shared TV3 API contract.
function priceText(value, unit = AppState.unit || "") {
  return value == null
    ? "—"
    : `${Number(value).toLocaleString("vi-VN")} ${unit}`;
}

async function loadGoldCurrentAndHistory(goldTypeCode) {
  try {
    const types = await apiRequest("/api/gold/types");
    AppState.goldTypes = types;
    const models = await apiRequest("/api/model");
    AppState.models = models;

    const selectedCode = goldTypeCode || AppState.goldType || "XAU_VND_LUONG";
    const selected = types.find((t) => t.code === selectedCode) || types[0];
    if (!selected) throw new Error("Chưa có chuỗi giá.");
    AppState.goldType = selected.code;
    AppState.unit = selected.unit;

    // Helper đồng bộ Options cho các dropdown loại vàng
    const populateSelect = (selectEl, defaultVal) => {
      if (!selectEl) return;
      selectEl.replaceChildren(
        ...types.map((t) => new Option(`${t.name} (${t.code})`, t.code))
      );
      selectEl.value = defaultVal;
    };

    // 1. Dropdown loại vàng trên Dashboard (Mục 2.2, 4.3 & TV2)
    const homeSelect = document.getElementById("homeGoldTypeSelect");
    if (homeSelect) {
      populateSelect(homeSelect, selected.code);
      homeSelect.onchange = (e) => {
        const newCode = e.target.value;
        const sel = types.find((t) => t.code === newCode);
        if (sel) {
          AppState.goldType = sel.code;
          AppState.unit = sel.unit;
        }
        const filterSelect = document.getElementById("filterGoldType");
        if (filterSelect) filterSelect.value = newCode;
        const predSelect = document.getElementById("predictGoldType");
        if (predSelect) predSelect.value = newCode;
        loadGoldCurrentAndHistory(newCode);
      };
    }

    // 2. Dropdown loại vàng trên Tab Giá vàng
    const filterSelect = document.getElementById("filterGoldType");
    if (filterSelect) {
      populateSelect(filterSelect, selected.code);
    }

    // 3. Dropdown loại vàng trên Form Dự đoán (Mục 4.4)
    const predSelect = document.getElementById("predictGoldType");
    if (predSelect) {
      populateSelect(predSelect, selected.code);
    }

    // Danh sách Mô hình AI (đầy đủ cả 3 mô hình: Naive stub v0, LightGBM v1, LSTM Deep Learning v1)
    const select = document.getElementById("predictModel");
    const previous = select.value;
    select.replaceChildren(
      ...models.map((m) => new Option(`${m.name} (${m.version})`, String(m.id)))
    );
    if (models.some((m) => String(m.id) === previous)) {
      select.value = previous;
    } else {
      const activeOne = models.find((m) => m.is_active) || models[0];
      select.value = String(activeOne?.id || "");
    }
    document.getElementById("homeLiveModelName").textContent =
      models.find((m) => String(m.id) === select.value)?.name ||
      "Chưa có model";
    select.onchange = (e) => {
      const chosen = models.find((m) => String(m.id) === e.target.value);
      if (chosen) {
        document.getElementById("homeLiveModelName").textContent = chosen.name;
      }
      updateModelEvaluation(e.target.value);
    };

    // Gọi song song GET /api/gold/current, GET /api/gold/summary và GET /api/gold/history
    const [current, summary, history] = await Promise.all([
      apiRequest(`/api/gold/current?type=${encodeURIComponent(selected.code)}`),
      apiRequest(
        `/api/gold/summary?type=${encodeURIComponent(selected.code)}`
      ).catch(() => null),
      apiRequest(
        `/api/gold/history?type=${encodeURIComponent(selected.code)}&page_size=365&order=desc`
      ),
    ]);

    // Cập nhật giá đóng cửa (Close)
    document.getElementById("homeLiveClosePrice").textContent = priceText(
      current.close
    );
    const topTicker = document.getElementById("topTickerPrice");
    if (topTicker) topTicker.textContent = priceText(current.close);

    // Cập nhật giá Mua vào và Bán ra (Mục 4.3 & TV2)
    const buyEl = document.getElementById("homeLiveBuyPrice");
    if (buyEl) buyEl.textContent = priceText(current.buy);
    const sellEl = document.getElementById("homeLiveSellPrice");
    if (sellEl) sellEl.textContent = priceText(current.sell);

    // Cập nhật ngày & nguồn
    document.getElementById("homeLiveDate").textContent = current.date;

    // Cập nhật Tỷ lệ biến động (+X.X% / -X.X%)
    const changePctEl = document.getElementById("homeLiveChangePct");
    if (changePctEl) {
      const ch1d = summary?.change_1d_pct ?? 0;
      const sign = ch1d > 0 ? "+" : "";
      changePctEl.textContent = `${sign}${Number(ch1d).toFixed(2)}%`;
      if (ch1d >= 0) {
        changePctEl.className =
          "px-2.5 py-1 rounded text-xs font-mono font-bold bg-[#997E67]/20 text-[#C4B4A5] border border-[#997E67]/40";
      } else {
        changePctEl.className =
          "px-2.5 py-1 rounded text-xs font-mono font-bold bg-rose-950/60 text-rose-400 border border-rose-800/50";
      }
    }

    // Cập nhật High/Low từ phiên gần nhất
    AppState.priceHistoryData = history.items.slice().reverse();
    const last = history.items[0];
    document.getElementById("homeLiveHighPrice").textContent = priceText(
      last?.high
    );
    document.getElementById("homeLiveLowPrice").textContent = priceText(
      last?.low
    );
    renderPriceChart(AppState.priceHistoryData);

    // Nạp dữ liệu vào Bảng Dữ Liệu Lịch Sử OHLCV (Mục 2.3 & TV2)
    loadGoldHistoryTable(1);

    document.getElementById("homeApiSyncTag").textContent =
      `${selected.code} · ${selected.unit} · ${selected.source || "Chưa rõ nguồn"}`;
  } catch (error) {
    document.getElementById("homeApiSyncTag").textContent = error.message;
  }
  await updateModelEvaluation(document.getElementById("predictModel").value);
}

// Bảng Dữ liệu Lịch sử OHLCV với Bộ lọc & Phân trang động (Mục 2.3 & TV2)
async function loadGoldHistoryTable(page = 1) {
  const tbody = document.getElementById("goldHistoryTableBody");
  if (!tbody) return;

  const type =
    document.getElementById("filterGoldType")?.value ||
    AppState.goldType ||
    "XAU_VND_LUONG";
  const dateFrom = document.getElementById("filterDateFrom")?.value || "";
  const dateTo = document.getElementById("filterDateTo")?.value || "";
  const interval = document.getElementById("filterInterval")?.value || "day";

  if (dateFrom && dateTo && dateFrom > dateTo) {
    showToast("Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc", "error");
    return;
  }

  tbody.replaceChildren();
  const loadingRow = document.createElement("tr");
  const loadingTd = document.createElement("td");
  loadingTd.colSpan = 7;
  loadingTd.className = "py-6 text-center text-xs text-brand-textSecondary";
  loadingTd.textContent = "Đang tải dữ liệu lịch sử từ API...";
  loadingRow.appendChild(loadingTd);
  tbody.appendChild(loadingRow);

  try {
    let url = `/api/gold/history?type=${encodeURIComponent(type)}&interval=${encodeURIComponent(interval)}&page=${page}&page_size=20&order=desc`;
    if (dateFrom) url += `&from=${encodeURIComponent(dateFrom)}`;
    if (dateTo) url += `&to=${encodeURIComponent(dateTo)}`;

    const res = await apiRequest(url);
    const items = res.items || [];
    tbody.replaceChildren();

    if (items.length === 0) {
      const emptyRow = document.createElement("tr");
      const emptyTd = document.createElement("td");
      emptyTd.colSpan = 7;
      emptyTd.className = "py-6 text-center text-xs text-brand-textSecondary";
      emptyTd.textContent =
        "Không tìm thấy dữ liệu giá cho khoảng thời gian này.";
      emptyRow.appendChild(emptyTd);
      tbody.appendChild(emptyRow);
      return;
    }

    for (const item of items) {
      const tr = document.createElement("tr");
      tr.className = "hover:bg-slate-900/50 transition";

      // 1. Ngày ghi nhận
      const tdDate = document.createElement("td");
      tdDate.className =
        "py-2.5 px-3 text-slate-200 whitespace-nowrap font-medium";
      tdDate.textContent = item.date;
      tr.appendChild(tdDate);

      // 2. Open
      const tdOpen = document.createElement("td");
      tdOpen.className =
        "py-2.5 px-3 text-right text-slate-300 whitespace-nowrap";
      tdOpen.textContent = Number(item.open).toLocaleString("vi-VN");
      tr.appendChild(tdOpen);

      // 3. High
      const tdHigh = document.createElement("td");
      tdHigh.className =
        "py-2.5 px-3 text-right text-[#C4B4A5] whitespace-nowrap";
      tdHigh.textContent = Number(item.high).toLocaleString("vi-VN");
      tr.appendChild(tdHigh);

      // 4. Low
      const tdLow = document.createElement("td");
      tdLow.className =
        "py-2.5 px-3 text-right text-rose-400 whitespace-nowrap";
      tdLow.textContent = Number(item.low).toLocaleString("vi-VN");
      tr.appendChild(tdLow);

      // 5. Close
      const tdClose = document.createElement("td");
      tdClose.className =
        "py-2.5 px-3 text-right text-white font-bold whitespace-nowrap";
      tdClose.textContent = Number(item.close).toLocaleString("vi-VN");
      tr.appendChild(tdClose);

      // 6. Volume
      const tdVol = document.createElement("td");
      tdVol.className =
        "py-2.5 px-3 text-right text-slate-400 whitespace-nowrap";
      tdVol.textContent =
        item.volume != null ? Number(item.volume).toLocaleString("vi-VN") : "—";
      tr.appendChild(tdVol);

      // 7. Biến động phiên (Close vs Open)
      const tdChange = document.createElement("td");
      tdChange.className = "py-2.5 px-3 text-center whitespace-nowrap";
      const openVal = Number(item.open) || 0;
      const closeVal = Number(item.close) || 0;
      const diffPct = openVal > 0 ? ((closeVal - openVal) / openVal) * 100 : 0;
      const badge = document.createElement("span");
      if (diffPct >= 0) {
        badge.className =
          "px-2 py-0.5 rounded text-[11px] font-semibold bg-[#997E67]/20 text-[#C4B4A5] border border-[#997E67]/40";
        badge.textContent = `+${diffPct.toFixed(2)}%`;
      } else {
        badge.className =
          "px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-950/60 text-rose-400 border border-rose-800/40";
        badge.textContent = `${diffPct.toFixed(2)}%`;
      }
      tdChange.appendChild(badge);
      tr.appendChild(tdChange);

      tbody.appendChild(tr);
    }

    // Pagination
    const total = res.total || 0;
    const pageSize = res.page_size || 20;
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    const currentPage = res.page || page;

    const totalEl = document.getElementById("priceHistoryTotalCount");
    if (totalEl)
      totalEl.textContent = `Hiển thị ${items.length} / ${total} bản ghi (Khung: ${interval.toUpperCase()})`;

    const pageIndicator = document.getElementById("priceHistoryPageIndicator");
    if (pageIndicator)
      pageIndicator.textContent = `Trang ${currentPage} / ${totalPages}`;

    const prevBtn = document.getElementById("btnPriceHistoryPrev");
    if (prevBtn) {
      prevBtn.disabled = currentPage <= 1;
      prevBtn.onclick = () => {
        if (currentPage > 1) loadGoldHistoryTable(currentPage - 1);
      };
    }

    const nextBtn = document.getElementById("btnPriceHistoryNext");
    if (nextBtn) {
      nextBtn.disabled = currentPage >= totalPages;
      nextBtn.onclick = () => {
        if (currentPage < totalPages) loadGoldHistoryTable(currentPage + 1);
      };
    }
  } catch (err) {
    tbody.replaceChildren();
    const errRow = document.createElement("tr");
    const errTd = document.createElement("td");
    errTd.colSpan = 7;
    errTd.className = "py-6 text-center text-xs text-rose-400";
    errTd.textContent = "Lỗi nạp dữ liệu lịch sử: " + err.message;
    errRow.appendChild(errTd);
    tbody.appendChild(errRow);
  }
}

async function updateModelEvaluation(modelId) {
  try {
    const evalUrl = modelId
      ? `/api/model/evaluation?model_id=${encodeURIComponent(modelId)}`
      : "/api/model/evaluation";
    const evaluation = await apiRequest(evalUrl);
    const metrics = evaluation.metrics || {};

    // Đủ 5 chỉ số MAE, MSE, RMSE, MAPE, R2 (Mục 2.6)
    for (const [id, key] of [
      ["introMae", "mae"],
      ["introMse", "mse"],
      ["introRmse", "rmse"],
      ["introMape", "mape"],
      ["introR2", "r2"],
    ]) {
      const value = metrics[key] ?? metrics[key.toUpperCase()];
      const el = document.getElementById(id);
      if (el) {
        if (value == null) {
          el.textContent = "Chưa có số liệu";
        } else if (key === "r2") {
          el.textContent = Number(value).toFixed(4);
        } else if (key === "mape") {
          el.textContent = Number(value).toFixed(2) + "%";
        } else if (key === "mse") {
          el.textContent = Number(value).toLocaleString("vi-VN", {
            maximumFractionDigits: 2,
          });
        } else {
          el.textContent = Number(value).toLocaleString("vi-VN");
        }
      }
    }

    const homeMapeEl = document.getElementById("homeLiveMAPE");
    if (homeMapeEl) {
      if (metrics.mape != null) {
        homeMapeEl.textContent = `MAPE: ${Number(metrics.mape).toFixed(2)}% · RMSE: ${Number(metrics.rmse || 0).toLocaleString("vi-VN")} · R²: ${Number(metrics.r2 || 0).toFixed(4)}`;
      } else {
        homeMapeEl.textContent =
          metrics.note || "Mô hình sẵn sàng phục vụ dự báo.";
      }
    }

    // Biểu đồ Đối sánh Actual Price vs Predicted Price (Mục 2.4 & TV2)
    const series = evaluation.series;
    const evalCanvas = document.getElementById("evalComparisonChartCanvas");
    if (
      evalCanvas &&
      series &&
      series.dates &&
      series.dates.length &&
      typeof Chart !== "undefined"
    ) {
      if (AppState.chartInstances.evalComparisonChart) {
        AppState.chartInstances.evalComparisonChart.destroy();
      }
      AppState.chartInstances.evalComparisonChart = new Chart(evalCanvas, {
        type: "line",
        data: {
          labels: series.dates,
          datasets: [
            {
              label: "Giá thực tế (Actual Price)",
              data: series.actual,
              borderColor: "#997E67",
              backgroundColor: "rgba(153, 126, 103, 0.12)",
              borderWidth: 2,
              pointRadius: 2,
              pointHoverRadius: 5,
              tension: 0.15,
              fill: false,
            },
            {
              label: "Giá dự báo (Predicted Price)",
              data: series.predicted,
              borderColor: "#B88A30",
              borderDash: [5, 5],
              backgroundColor: "rgba(197, 160, 89, 0.08)",
              borderWidth: 2,
              pointRadius: 2,
              pointHoverRadius: 5,
              pointBackgroundColor: "#B88A30",
              tension: 0.15,
              fill: false,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: "index",
            intersect: false,
          },
          plugins: {
            legend: {
              labels: {
                color: "#67716C",
                font: { size: 11, family: "JetBrains Mono, monospace" },
              },
            },
            tooltip: {
              callbacks: {
                label(context) {
                  return `${context.dataset.label}: ${Number(context.raw).toLocaleString("vi-VN")} VNĐ/lượng`;
                },
              },
            },
          },
          scales: {
            x: {
              grid: { color: "rgba(228, 230, 223, 0.8)" },
              ticks: { color: "#67716C", maxTicksLimit: 10 },
            },
            y: {
              grid: { color: "rgba(228, 230, 223, 0.8)" },
              ticks: {
                color: "#4B5563",
                callback: (v) => Number(v).toLocaleString("vi-VN"),
              },
            },
          },
        },
      });
    }

    // Bảng Đối Chuẩn Baseline Models (Mục 2.6 & TV2/TV5/TV6)
    const baselineTbody = document.getElementById(
      "baselineComparisonTableBody"
    );
    if (baselineTbody && evaluation.baseline_comparison) {
      baselineTbody.replaceChildren();
      const modelsMap = [
        {
          key: "linear_regression",
          name: "Linear Regression",
          desc: "Mô hình tuyến tính cổ điển OLS",
        },
        {
          key: "random_forest",
          name: "Random Forest Regressor",
          desc: "Ensemble cây quyết định đa cây (100 Trees)",
        },
        {
          key: "lightgbm",
          name: "LightGBM Regressor",
          desc: "Gradient Boosting chuỗi thời gian (TV5)",
        },
      ];

      for (const mInfo of modelsMap) {
        const m = evaluation.baseline_comparison[mInfo.key];
        if (!m) continue;

        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-900/50 transition";

        // Tên mô hình
        const tdName = document.createElement("td");
        tdName.className = "py-2.5 px-3 text-white font-bold whitespace-nowrap";
        tdName.textContent = mInfo.name;
        tr.appendChild(tdName);

        // Thuật toán
        const tdDesc = document.createElement("td");
        tdDesc.className =
          "py-2.5 px-3 text-brand-textSecondary text-xs whitespace-nowrap";
        tdDesc.textContent = mInfo.desc;
        tr.appendChild(tdDesc);

        // MAE
        const tdMae = document.createElement("td");
        tdMae.className =
          "py-2.5 px-3 text-right text-slate-200 whitespace-nowrap";
        tdMae.textContent = Number(m.mae).toLocaleString("vi-VN", {
          maximumFractionDigits: 2,
        });
        tr.appendChild(tdMae);

        // MSE
        const tdMse = document.createElement("td");
        tdMse.className =
          "py-2.5 px-3 text-right text-slate-200 whitespace-nowrap";
        tdMse.textContent = Number(m.mse).toLocaleString("vi-VN", {
          maximumFractionDigits: 2,
        });
        tr.appendChild(tdMse);

        // RMSE
        const tdRmse = document.createElement("td");
        tdRmse.className =
          "py-2.5 px-3 text-right text-slate-200 whitespace-nowrap";
        tdRmse.textContent = Number(m.rmse).toLocaleString("vi-VN", {
          maximumFractionDigits: 2,
        });
        tr.appendChild(tdRmse);

        // MAPE
        const tdMape = document.createElement("td");
        tdMape.className =
          "py-2.5 px-3 text-right text-[#C4B4A5] font-semibold whitespace-nowrap";
        tdMape.textContent = `${Number(m.mape).toFixed(2)}%`;
        tr.appendChild(tdMape);

        // R2
        const tdR2 = document.createElement("td");
        tdR2.className =
          "py-2.5 px-3 text-right text-brand-gold font-bold whitespace-nowrap";
        tdR2.textContent = Number(m.r2).toFixed(4);
        tr.appendChild(tdR2);

        baselineTbody.appendChild(tr);
      }
    }
  } catch {
    const homeMapeEl = document.getElementById("homeLiveMAPE");
    if (homeMapeEl)
      homeMapeEl.textContent = "Chưa có báo cáo đánh giá cho model này.";
  }
}

async function loadPredictionHistory(page = AppState.historyPage || 1) {
  const token = AppState.jwtToken;
  AppState.historyPage = page;
  AppState.historyPageSize = 10;
  AppState.predictionHistory = [];
  AppState.historyTotal = 0;
  renderHistoryTable();
  if (!token) {
    document.getElementById("historyTableBody").textContent =
      "Đăng nhập để xem lịch sử dự đoán của bạn.";
    return;
  }
  try {
    const response = await apiRequest(
      `/api/predictions/history?page=${page}&page_size=${AppState.historyPageSize}`
    );
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
  const total = AppState.historyTotal || 0;
  const pageSize = AppState.historyPageSize || 10;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const currentPage = AppState.historyPage || 1;

  document.getElementById("historyRowCount").textContent =
    `Hiển thị ${rows.length} / ${total} lượt (Trang ${currentPage}/${totalPages}).`;

  const prevBtn = document.getElementById("btnHistoryPrev");
  const nextBtn = document.getElementById("btnHistoryNext");
  const pageIndicator = document.getElementById("historyPageIndicator");

  if (pageIndicator)
    pageIndicator.textContent = `Trang ${currentPage} / ${totalPages}`;
  if (prevBtn) {
    prevBtn.disabled = currentPage <= 1;
    prevBtn.onclick = () => {
      if (currentPage > 1) loadPredictionHistory(currentPage - 1);
    };
  }
  if (nextBtn) {
    nextBtn.disabled = currentPage >= totalPages;
    nextBtn.onclick = () => {
      if (currentPage < totalPages) loadPredictionHistory(currentPage + 1);
    };
  }
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
    const goldType =
      document.getElementById("predictGoldType")?.value ||
      AppState.goldType ||
      "XAU_VND_LUONG";
    const horizonDays = Number(document.getElementById("predictDays").value);
    const dateFrom = document.getElementById("predictDateFrom")?.value || null;
    const dateTo = document.getElementById("predictDateTo")?.value || null;

    if (!modelId || !goldType)
      throw new Error(
        "Chưa tải được mô hình và chuỗi giá. Hãy làm mới dữ liệu."
      );

    if (dateFrom && dateTo && dateFrom > dateTo) {
      throw new Error("Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc.");
    }

    const payload = {
      gold_type: goldType,
      horizon_days: horizonDays,
      model_id: modelId,
    };
    if (dateFrom) payload.date_from = dateFrom;
    if (dateTo) payload.date_to = dateTo;

    const result = await apiRequest("/api/predict", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    for (const item of result.items) {
      const card = document.createElement("div");
      card.className =
        "p-3.5 bg-white rounded-xl border-2 border-[#DDE1DA] shadow-sm hover:border-[#997E67] transition";

      const pDate = document.createElement("p");
      pDate.className = "text-xs font-bold text-gray-900";
      pDate.textContent = item.target_date;

      const pPrice = document.createElement("p");
      pPrice.className =
        "text-base font-extrabold text-[#7A614D] font-mono my-1";
      pPrice.textContent = priceText(item.predicted_price);

      const pTrend = document.createElement("p");
      pTrend.className = "text-xs font-bold text-emerald-700";
      pTrend.textContent = `Xu hướng: ${result.trend}`;

      const pRange = document.createElement("p");
      pRange.className = "text-[11px] font-semibold text-gray-700";
      pRange.textContent =
        item.lower == null
          ? "Chưa có khoảng dự báo"
          : `${priceText(item.lower)} – ${priceText(item.upper)}`;

      card.append(pDate, pPrice, pTrend, pRange);
      cards.append(card);
    }
    badge.textContent = "Đã nhận kết quả API";
    document.getElementById("predictResponseTime").textContent =
      result.prediction_id == null
        ? "Chế độ khách: không lưu lịch sử."
        : `Đã lưu lượt #${result.prediction_id}`;
    if (typeof Chart !== "undefined") {
      AppState.chartInstances.forecastChart?.destroy();
      const labels = [
        result.last_actual.date,
        ...result.items.map((i) => i.target_date),
      ];
      const predictedData = [
        result.last_actual.price,
        ...result.items.map((i) => i.predicted_price),
      ];
      const upperData = [
        result.last_actual.price,
        ...result.items.map((i) => i.upper ?? i.predicted_price),
      ];
      const lowerData = [
        result.last_actual.price,
        ...result.items.map((i) => i.lower ?? i.predicted_price),
      ];

      AppState.chartInstances.forecastChart = new Chart(
        document.getElementById("forecastChartCanvas"),
        {
          type: "line",
          data: {
            labels,
            datasets: [
              {
                label: `Cận trên (+95%)`,
                borderColor: "rgba(153, 126, 103, 0.7)",
                borderDash: [4, 4],
                pointRadius: 2,
                fill: false,
                data: upperData,
              },
              {
                label: `Giá dự đoán (${AppState.unit || "VNĐ/lượng"})`,
                borderColor: "#B88A30",
                backgroundColor: "rgba(197, 160, 89, 0.15)",
                borderWidth: 3.5,
                pointRadius: 4,
                pointBackgroundColor: "#B88A30",
                fill: false,
                data: predictedData,
              },
              {
                label: `Cận dưới (-95%)`,
                borderColor: "rgba(177, 63, 54, 0.7)",
                borderDash: [4, 4],
                pointRadius: 2,
                fill: "-2", // Vùng tin cậy phủ giữa cận trên và cận dưới
                backgroundColor: "rgba(197, 160, 89, 0.08)",
                data: lowerData,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                labels: { color: "#67716C", font: { size: 10 } },
              },
              tooltip: {
                callbacks: {
                  label(context) {
                    return `${context.dataset.label}: ${Number(context.raw).toLocaleString("vi-VN")}`;
                  },
                },
              },
            },
            scales: {
              x: {
                grid: { color: "rgba(228, 230, 223, 0.8)" },
                ticks: { color: "#67716C" },
              },
              y: {
                grid: { color: "rgba(228, 230, 223, 0.8)" },
                ticks: {
                  color: "#4B5563",
                  callback: (v) => Number(v).toLocaleString("vi-VN"),
                },
              },
            },
          },
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

// Lắng nghe sự kiện Lọc Dữ Liệu Lịch Sử Giá Vàng (#priceFilterForm)
if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    const priceFilterForm = document.getElementById("priceFilterForm");
    if (priceFilterForm) {
      priceFilterForm.addEventListener("submit", (e) => {
        e.preventDefault();
        loadGoldHistoryTable(1);
      });
    }
  });
}
