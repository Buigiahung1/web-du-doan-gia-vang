/**
 * VÀNGSỐ PRO ANALYTICS - MAIN APPLICATION JQUERY WORKFLOW
 */

$(document).ready(function () {
  // 1. Dữ liệu & Trạng thái khởi tạo
  let rawData = window.GoldDatasetEngine.getRawData();
  let enrichedData = window.GoldDatasetEngine.getEnrichedData(rawData);
  let brandQuotes = window.GoldDatasetEngine.getBrandQuotes();
  let forecastEngine = new window.GoldForecastEngine(enrichedData);
  let goldChart = null;

  // Cấu hình tương tác biểu đồ
  const chartState = {
    target: "sjcSell",   // sjcSell | sjcBuy | worldUsd
    model: "holt",       // holt | arima | macro
    horizon: 14,         // 7 | 14 | 30
    timeframe: "all",    // 30 | 90 | 180 | 365 | all
    showSma: true,
    showConfidence: true
  };

  // 2. Đồng hồ thị trường theo giờ địa phương Việt Nam
  function updateLiveClock() {
    const now = new Date();
    const formatted = now.toLocaleDateString("vi-VN") + " " + now.toLocaleTimeString("vi-VN");
    $("#live-time").text(formatted);
  }
  setInterval(updateLiveClock, 1000);
  updateLiveClock();

  // 3. Render Bảng Giá Thương Hiệu Lớn (Cột phải)
  function renderBrandQuotes() {
    const container = $("#brand-quotes-container");
    container.empty();

    brandQuotes.forEach(item => {
      const row = `
        <div class="brand-row">
          <div class="brand-meta">
            <span class="brand-title">${item.brand}</span>
            <span class="brand-city">${item.city} &bull; Chênh M-B: <span class="num-mono">${item.spread.toFixed(2)}</span> Tr</span>
          </div>
          <div class="brand-prices">
            <span class="brand-sell num-mono">${item.sell.toFixed(2)} Tr</span>
            <span class="brand-buy-spread num-mono">Mua: ${item.buy.toFixed(2)} Tr (<span class="text-success">${item.change}</span>)</span>
          </div>
        </div>
      `;
      container.append(row);
    });
  }

  // 4. Cập nhật các thẻ KPI trên cùng
  function updateTopKpis() {
    if (!enrichedData || enrichedData.length === 0) return;
    const latest = enrichedData[enrichedData.length - 1];

    $("#card-sjc-sell").html(`${latest.sjcSell.toFixed(2)} <span class="kpi-unit">Tr/Lượng</span>`);
    $("#card-sjc-buy").text(latest.sjcBuy.toFixed(2));
    $("#card-sjc-spread").text((latest.sjcSell - latest.sjcBuy).toFixed(2));

    const ringGoldEst = (latest.sjcSell - 5.80).toFixed(2);
    $("#card-ring-gold").html(`${ringGoldEst} <span class="kpi-unit">Tr/Lượng</span>`);

    $("#card-kitco-spot").html(`$${latest.worldUsd.toLocaleString('en-US', { minimumFractionDigits: 1 })} <span class="kpi-unit">USD/oz</span>`);
    $("#card-world-converted").text(latest.worldVnd.toFixed(2));

    $("#ribbon-usdvnd").text(latest.usdVnd.toLocaleString('vi-VN'));
    $("#ribbon-premium").text(`+${(latest.sjcSell - latest.worldVnd).toFixed(2)} Tr`);
  }

  // 5. Render Bảng Dataset Lịch Sử (Tab 1)
  function renderDatasetGrid() {
    const tbody = $("#dataset-table-body");
    tbody.empty();

    const searchTerm = $("#table-search").val().trim().toLowerCase();
    let list = [...enrichedData];

    if (searchTerm) {
      list = list.filter(item => item.date.toLowerCase().includes(searchTerm));
    }

    $("#dataset-total-count").text(list.length);
    const reversed = [...list].reverse();

    if (reversed.length === 0) {
      tbody.append('<tr><td colspan="8" style="text-align:center; padding: 20px; color: var(--text-muted);">Không tìm thấy dữ liệu phù hợp.</td></tr>');
      return;
    }

    reversed.forEach(item => {
      const changeClass = item.changePct >= 0 ? "badge-up" : "badge-down";
      const changeSign = item.changePct > 0 ? "+" : "";

      const tr = `
        <tr>
          <td><strong class="num-mono">${item.date}</strong></td>
          <td class="num-mono">${item.sjcBuy.toFixed(2)}</td>
          <td class="num-mono"><strong>${item.sjcSell.toFixed(2)}</strong></td>
          <td><span class="badge-tag ${changeClass} num-mono">${changeSign}${item.changePct}%</span></td>
          <td class="num-mono">$${item.worldUsd.toFixed(1)}</td>
          <td class="num-mono">${item.usdVnd.toLocaleString('vi-VN')}</td>
          <td class="num-mono">${item.worldVnd.toFixed(2)}</td>
          <td class="num-mono" style="color: ${item.premiumWorld >= 0 ? '#10b981' : '#f43f5e'};">
            ${item.premiumWorld > 0 ? '+' : ''}${item.premiumWorld.toFixed(2)} Tr
          </td>
        </tr>
      `;
      tbody.append(tr);
    });
  }

  // 6. Tính toán & Cập nhật Biểu đồ Chart.js (TradingView / Fintech Style)
  function updateChartAndForecasts() {
    forecastEngine.setDataset(enrichedData);

    // Cắt dữ liệu theo khung thời gian đã chọn (1M, 3M, 6M, 1Y, ALL)
    let displayData = [...enrichedData];
    if (chartState.timeframe !== "all") {
      const count = parseInt(chartState.timeframe, 10);
      displayData = displayData.slice(-count);
    }

    const series = displayData.map(d => d[chartState.target]);
    const dates = displayData.map(d => d.date);

    // Tính chỉ báo kỹ thuật RSI & SMA
    const indicators = forecastEngine.calculateIndicators(series, 14);

    // Cập nhật Thước đo Tâm lý thị trường (RSI Gauge)
    const lastRsi = indicators.rsi[indicators.rsi.length - 1] || 55;
    const clampedRsi = Math.max(10, Math.min(90, lastRsi));
    $("#sentiment-meter-pointer").css("left", `${clampedRsi}%`);

    let sentimentText = "Trung Tính (50)";
    let sentimentBadge = "badge-tag badge-gold";
    if (lastRsi > 60) {
      sentimentText = `Lạc quan (RSI: ${lastRsi.toFixed(1)})`;
      sentimentBadge = "badge-tag badge-up";
    } else if (lastRsi < 40) {
      sentimentText = `Áp lực bán (RSI: ${lastRsi.toFixed(1)})`;
      sentimentBadge = "badge-tag badge-down";
    }
    $("#sentiment-status-label").attr("class", sentimentBadge).text(sentimentText);

    // Chạy mô hình dự báo
    let forecastResult = null;
    if (chartState.model === "holt") {
      forecastResult = forecastEngine.runHoltModel(series, chartState.horizon);
    } else if (chartState.model === "arima") {
      forecastResult = forecastEngine.runARIMAModel(series, chartState.horizon);
    } else {
      forecastResult = forecastEngine.runMacroFactorModel(displayData, chartState.horizon);
    }

    if (!forecastResult) return;

    // Watermark text
    const watermarkText = chartState.target === "worldUsd" ? "KITCO / USD" : "SJC / VND";
    $("#chart-watermark-text").text(watermarkText);

    // Nhãn ngày tương lai
    const lastDate = new Date(dates[dates.length - 1]);
    const futureLabels = [];
    for (let i = 1; i <= chartState.horizon; i++) {
      const d = new Date(lastDate);
      d.setDate(lastDate.getDate() + i * 2);
      futureLabels.push(d.toISOString().split("T")[0] + " (Dự báo)");
    }
    const allLabels = [...dates, ...futureLabels];

    // Dữ liệu nối tiếp
    const historyDataPadded = [...series, ...new Array(chartState.horizon).fill(null)];
    const lastHistoricalVal = series[series.length - 1];

    const forecastMean = [...new Array(series.length - 1).fill(null), lastHistoricalVal, ...forecastResult.forecasts.map(f => f.forecast)];
    const upper80 = [...new Array(series.length - 1).fill(null), lastHistoricalVal, ...forecastResult.forecasts.map(f => f.upper80)];
    const lower80 = [...new Array(series.length - 1).fill(null), lastHistoricalVal, ...forecastResult.forecasts.map(f => f.lower80)];
    const upper95 = [...new Array(series.length - 1).fill(null), lastHistoricalVal, ...forecastResult.forecasts.map(f => f.upper95)];
    const lower95 = [...new Array(series.length - 1).fill(null), lastHistoricalVal, ...forecastResult.forecasts.map(f => f.lower95)];

    // Cập nhật Thẻ KPI dự báo T+14
    const targetForecast = forecastResult.forecasts[chartState.horizon - 1];
    const unitText = chartState.target === 'worldUsd' ? 'USD/oz' : 'Tr/Lượng';
    $("#card-forecast-target").html(`${targetForecast.forecast.toFixed(2)} <span class="kpi-unit">${unitText}</span>`);
    $("#card-forecast-range").text(`${targetForecast.lower95.toFixed(1)} - ${targetForecast.upper95.toFixed(1)}`);

    // Cập nhật Simulator
    updateSimulator(targetForecast);

    // Backtest
    const backtest = forecastEngine.runBacktest(chartState.target);
    if (backtest) {
      $("#val-mape, #val-mape-strip").text(backtest.mape + "%");
      $("#val-rmse").text(backtest.rmse + " " + (chartState.target === 'worldUsd' ? '$' : 'Tr'));
      $("#val-r2").text(backtest.r2);
      $("#val-direction").text(backtest.directionalAccuracy + "%");
    }

    // Chart.js Datasets
    const isDarkMode = $("body").hasClass("dark-mode");
    const ctx = document.getElementById("goldChart").getContext("2d");

    // Tạo gradient đổ bóng tinh tế dưới đường giá lịch sử
    const historyGradient = ctx.createLinearGradient(0, 0, 0, 400);
    if (isDarkMode) {
      historyGradient.addColorStop(0, "rgba(59, 130, 246, 0.25)");
      historyGradient.addColorStop(1, "rgba(59, 130, 246, 0.0)");
    } else {
      historyGradient.addColorStop(0, "rgba(37, 99, 235, 0.14)");
      historyGradient.addColorStop(1, "rgba(37, 99, 235, 0.0)");
    }

    const datasets = [
      {
        label: "Dữ liệu thực tế",
        data: historyDataPadded,
        borderColor: isDarkMode ? "#3b82f6" : "#2563eb",
        backgroundColor: historyGradient,
        borderWidth: 2,
        pointRadius: displayData.length > 30 ? 0 : 3,
        pointHoverRadius: 5,
        fill: true,
        tension: 0.15
      },
      {
        label: "Đường dự báo trọng tâm",
        data: forecastMean,
        borderColor: "#d97706",
        borderDash: [5, 4],
        borderWidth: 2.5,
        pointRadius: 3,
        pointHoverRadius: 6,
        fill: false,
        tension: 0.2
      }
    ];

    if (chartState.showConfidence) {
      datasets.push(
        {
          label: "Cận trên 95%",
          data: upper95,
          borderColor: "rgba(217, 119, 6, 0.25)",
          borderWidth: 1,
          pointRadius: 0,
          fill: false,
          tension: 0.2
        },
        {
          label: "Dải tin cậy 95%",
          data: lower95,
          borderColor: "rgba(217, 119, 6, 0.25)",
          backgroundColor: isDarkMode ? "rgba(217, 119, 6, 0.08)" : "rgba(217, 119, 6, 0.07)",
          borderWidth: 1,
          pointRadius: 0,
          fill: "-1",
          tension: 0.2
        },
        {
          label: "Cận trên 80%",
          data: upper80,
          borderColor: "rgba(217, 119, 6, 0.45)",
          borderWidth: 1,
          pointRadius: 0,
          fill: false,
          tension: 0.2
        },
        {
          label: "Dải tin cậy 80%",
          data: lower80,
          borderColor: "rgba(217, 119, 6, 0.45)",
          backgroundColor: isDarkMode ? "rgba(217, 119, 6, 0.15)" : "rgba(217, 119, 6, 0.12)",
          borderWidth: 1,
          pointRadius: 0,
          fill: "-1",
          tension: 0.2
        }
      );
    }

    if (chartState.showSma) {
      const smaPadded = [...indicators.sma, ...new Array(chartState.horizon).fill(null)];
      datasets.push({
        label: "SMA(14)",
        data: smaPadded,
        borderColor: "#9333ea",
        borderWidth: 1.2,
        pointRadius: 0,
        fill: false,
        tension: 0.2
      });
    }

    if (goldChart) {
      goldChart.destroy();
    }

    const gridColor = isDarkMode ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.04)";
    const textColor = isDarkMode ? "#64748b" : "#94a3b8";

    goldChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: allLabels,
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 400 },
        interaction: {
          mode: "index",
          intersect: false
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: isDarkMode ? "#171e30" : "#0f172a",
            titleColor: "#ffffff",
            bodyColor: "#e2e8f0",
            borderColor: isDarkMode ? "#2d3b55" : "#334155",
            borderWidth: 1,
            padding: 10,
            titleFont: { family: "'JetBrains Mono', monospace", size: 12 },
            bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
            callbacks: {
              label: function (context) {
                const label = context.dataset.label || "";
                const val = context.parsed.y;
                if (val === null || val === undefined) return null;
                const unit = chartState.target === "worldUsd" ? "$" : " Tr";
                return `${label}: ${val.toFixed(2)}${unit}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: gridColor },
            ticks: {
              color: textColor,
              maxTicksLimit: 10,
              font: { family: "'JetBrains Mono', monospace", size: 10.5 }
            }
          },
          y: {
            grid: { color: gridColor },
            ticks: {
              color: textColor,
              font: { family: "'JetBrains Mono', monospace", size: 10.5 },
              callback: function (val) {
                return chartState.target === "worldUsd" ? "$" + val : val + " Tr";
              }
            }
          }
        }
      }
    });
  }

  // 7. Đồng bộ Slider & Number Input trong Simulator
  function syncSimulatorInputs(qty, cost) {
    $("#sim-slider-qty").val(qty);
    $("#sim-input-qty").val(qty);
    $("#sim-qty-display").text(`${qty.toFixed(1)} Lượng`);

    $("#sim-slider-cost").val(cost);
    $("#sim-input-cost").val(cost);
    $("#sim-cost-display").text(`${cost.toFixed(2)} Tr`);

    const totalCapital = qty * cost * 1000000;
    $("#sim-total-capital").text(totalCapital.toLocaleString("vi-VN"));

    const targetForecast = {
      forecast: parseFloat($("#card-forecast-target").text()) || 106.15,
      upper95: parseFloat($("#card-forecast-range").text().split("-")[1]) || 108.1,
      lower95: parseFloat($("#card-forecast-range").text().split("-")[0]) || 104.2
    };

    updateSimulator(targetForecast);
  }

  function updateSimulator(targetForecast) {
    const qty = parseFloat($("#sim-input-qty").val()) || 5;
    const cost = parseFloat($("#sim-input-cost").val()) || 89.5;
    const totalCapital = qty * cost * 1000000;

    if (!targetForecast) return;

    const basePrice = targetForecast.forecast;
    const bullPrice = targetForecast.upper95;
    const bearPrice = targetForecast.lower95;

    $("#sim-card-base-target").text(`Giá: ${basePrice.toFixed(2)} Tr/Lượng`);
    $("#sim-card-bull-target").text(`Giá: ${bullPrice.toFixed(2)} Tr/Lượng`);
    $("#sim-card-bear-target").text(`Giá: ${bearPrice.toFixed(2)} Tr/Lượng`);

    function formatPnl(targetP) {
      const curValue = qty * targetP * 1000000;
      const pnlVnd = curValue - totalCapital;
      const pnlPct = ((pnlVnd / (totalCapital || 1)) * 100).toFixed(1);
      const sign = pnlVnd >= 0 ? "+" : "";
      return `${sign}${pnlVnd.toLocaleString('vi-VN')} VNĐ (${sign}${pnlPct}%)`;
    }

    $("#sim-pnl-base").text(formatPnl(basePrice));
    $("#sim-pnl-bull").text(formatPnl(bullPrice));
    $("#sim-pnl-bear").text(formatPnl(bearPrice));
  }

  // 8. Xuất và Nhập CSV
  function exportCsvFile() {
    let csvContent = "\uFEFF";
    csvContent += "Ngay,SJC_Mua_Tr,SJC_Ban_Tr,ChenhLech_MuaBan,Kitco_Spot_USD,TyGia_USDVND,TG_QuyDoi_Tr,ChenhLech_SJC_TG,BienDong_Pct\r\n";

    enrichedData.forEach(row => {
      csvContent += `${row.date},${row.sjcBuy},${row.sjcSell},${row.spreadDomestic},${row.worldUsd},${row.usdVnd},${row.worldVnd},${row.premiumWorld},${row.changePct}\r\n`;
    });

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `VangSo_Pro_Dataset_${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  function handleImportCsv(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (event) {
      const text = event.target.result;
      const lines = text.split(/\r?\n/).filter(line => line.trim() !== "");
      if (lines.length < 2) {
        alert("File CSV không hợp lệ hoặc rỗng.");
        return;
      }

      const imported = [];
      for (let i = 1; i < lines.length; i++) {
        const cols = lines[i].split(",").map(c => c.trim());
        if (cols.length >= 4) {
          const date = cols[0];
          const sjcBuy = parseFloat(cols[1]);
          const sjcSell = parseFloat(cols[2]);
          const worldUsd = parseFloat(cols[4] || cols[3]);
          const usdVnd = parseFloat(cols[5] || 25960);

          if (date && !isNaN(sjcBuy) && !isNaN(sjcSell)) {
            imported.push({
              date,
              sjcBuy,
              sjcSell,
              worldUsd: isNaN(worldUsd) ? 3300 : worldUsd,
              usdVnd: isNaN(usdVnd) ? 25960 : usdVnd
            });
          }
        }
      }

      if (imported.length < 5) {
        alert("Cần tối thiểu 5 phiên dữ liệu để chạy mô hình dự báo.");
        return;
      }

      imported.sort((a, b) => new Date(a.date) - new Date(b.date));
      enrichedData = window.GoldDatasetEngine.getEnrichedData(imported);
      forecastEngine.setDataset(enrichedData);

      updateTopKpis();
      renderDatasetGrid();
      updateChartAndForecasts();
      alert(`Đã nạp thành công ${imported.length} phiên giao dịch.`);
    };

    reader.readAsText(file, "UTF-8");
  }

  // 9. Lắng nghe các sự kiện UI
  // Timeframe pills
  $("#timeframe-pills .pill-btn").on("click", function () {
    $("#timeframe-pills .pill-btn").removeClass("active");
    $(this).addClass("active");
    chartState.timeframe = $(this).data("range");
    updateChartAndForecasts();
  });

  // Horizon pills
  $("#horizon-pills .pill-btn").on("click", function () {
    $("#horizon-pills .pill-btn").removeClass("active");
    $(this).addClass("active");
    chartState.horizon = parseInt($(this).data("horizon"), 10);
    updateChartAndForecasts();
  });

  // Target & Model select
  $("#select-target").on("change", function () {
    chartState.target = $(this).val();
    updateChartAndForecasts();
  });

  $("#select-model").on("change", function () {
    chartState.model = $(this).val();
    updateChartAndForecasts();
  });

  $("#chk-sma").on("change", function () {
    chartState.showSma = $(this).is(":checked");
    updateChartAndForecasts();
  });

  $("#chk-confidence").on("change", function () {
    chartState.showConfidence = $(this).is(":checked");
    updateChartAndForecasts();
  });

  // Tab switching
  $(".tab-nav-btn").on("click", function () {
    $(".tab-nav-btn").removeClass("active");
    $(this).addClass("active");
    const targetTab = $(this).data("tab");
    $(".tab-content").hide();
    $("#" + targetTab).show();
  });

  // Search dataset
  $("#table-search").on("input", function () {
    renderDatasetGrid();
  });

  // Simulator Events
  $("#sim-slider-qty").on("input", function () {
    const val = parseFloat($(this).val());
    syncSimulatorInputs(val, parseFloat($("#sim-input-cost").val()));
  });

  $("#sim-input-qty").on("input change", function () {
    const val = parseFloat($(this).val()) || 1;
    syncSimulatorInputs(val, parseFloat($("#sim-input-cost").val()));
  });

  $("#sim-slider-cost").on("input", function () {
    const val = parseFloat($(this).val());
    syncSimulatorInputs(parseFloat($("#sim-input-qty").val()), val);
  });

  $("#sim-input-cost").on("input change", function () {
    const val = parseFloat($(this).val()) || 80;
    syncSimulatorInputs(parseFloat($("#sim-input-qty").val()), val);
  });

  // Buttons
  $("#btn-export-csv").on("click", exportCsvFile);
  $("#input-import-csv").on("change", handleImportCsv);

  $("#btn-reset-dataset").on("click", function () {
    if (confirm("Khôi phục bộ dữ liệu thực tế mặc định?")) {
      rawData = window.GoldDatasetEngine.getRawData();
      enrichedData = window.GoldDatasetEngine.getEnrichedData(rawData);
      forecastEngine.setDataset(enrichedData);
      updateTopKpis();
      renderDatasetGrid();
      updateChartAndForecasts();
    }
  });

  $("#btn-refresh-data").on("click", function () {
    updateTopKpis();
    updateChartAndForecasts();
  });

  // Theme switch
  $("#btn-toggle-theme").on("click", function () {
    $("body").toggleClass("dark-mode");
    const isDark = $("body").hasClass("dark-mode");
    $(this).find("span").text(isDark ? "Terminal Light" : "Terminal Dark");
    updateChartAndForecasts();
  });

  // 10. Chạy khởi động
  renderBrandQuotes();
  updateTopKpis();
  renderDatasetGrid();
  updateChartAndForecasts();
  syncSimulatorInputs(5, 89.5);
});
