/**
 * StudentScore — Frontend Application Logic
 *
 * Quản lý toàn bộ tương tác UI:
 * - Upload file (drag & drop + click)
 * - Hiển thị Column Mapping UI
 * - Gửi request phân tích
 * - Render kết quả (stats cards, charts, tables, report)
 *
 * Dependencies: Plotly.js (loaded via CDN trong index.html)
 */

"use strict";

// -------------------------------------------------------------------------- //
//  DOM Elements
// -------------------------------------------------------------------------- //

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const uploadStatus = document.getElementById("upload-status");
const uploadFilename = document.getElementById("upload-filename");
const uploadInfo = document.getElementById("upload-info");
const btnSampleData = document.getElementById("btn-sample-data");

const sectionMapping = document.getElementById("section-mapping");
const selectScore = document.getElementById("select-score");
const selectLabel = document.getElementById("select-label");
const selectGroup = document.getElementById("select-group");
const previewContainer = document.getElementById("preview-container");
const previewTable = document.getElementById("preview-table");

const sectionConfig = document.getElementById("section-config");
const thresholdSlider = document.getElementById("threshold-slider");
const thresholdValue = document.getElementById("threshold-value");
const groupFilterContainer = document.getElementById("group-filter-container");
const selectGroupValue = document.getElementById("select-group-value");
const btnAnalyze = document.getElementById("btn-analyze");

const sectionResults = document.getElementById("section-results");
const statsCards = document.getElementById("stats-cards");
const distributionResults = document.getElementById("distribution-results");
const outlierTable = document.getElementById("outlier-table");
const reportContent = document.getElementById("report-content");


// -------------------------------------------------------------------------- //
//  State
// -------------------------------------------------------------------------- //

/** @type {{ column_stats: Object, preview: Array, row_count: number } | null} */
let uploadedMeta = null;


// -------------------------------------------------------------------------- //
//  Upload handlers
// -------------------------------------------------------------------------- //

/**
 * Xử lý file sau khi user chọn (qua drag-drop hoặc click).
 * Gửi POST /api/upload, nhận metadata cột, hiển thị mapping UI.
 *
 * @param {File} file - File object từ input hoặc drag event.
 * @returns {Promise<void>}
 */
async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData,
            // KHÔNG set Content-Type — browser tự set multipart/form-data + boundary
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || "Upload thất bại");
            if (data.details) console.warn("Schema errors:", data.details);
            return;
        }

        // Lưu metadata
        uploadedMeta = data;

        // Hiển thị upload status
        uploadFilename.textContent = file.name;
        uploadInfo.textContent = `${data.row_count} dòng · ${data.col_count} cột`;
        uploadStatus.removeAttribute("hidden");

        // Render preview table
        renderPreviewTable(data.preview);

        // Render column mapping dropdowns
        renderColumnMapping(data.column_stats);

        // Hiện các section tiếp theo
        sectionMapping.removeAttribute("hidden");
        sectionConfig.removeAttribute("hidden");
        btnAnalyze.disabled = false;

        sectionMapping.scrollIntoView({ behavior: "smooth" });

    } catch (err) {
        showError("Lỗi kết nối server: " + err.message);
    }
}

// --- Drag and drop ---
dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
});

// --- Click to select file ---
dropZone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) handleFileUpload(fileInput.files[0]);
});

// --- Sample data ---
btnSampleData.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/sample-data");
        if (!response.ok) {
            showError("Không thể tải dữ liệu mẫu từ server");
            return;
        }
        const blob = await response.blob();
        const file = new File([blob], "scores_sample.csv", { type: "text/csv" });
        handleFileUpload(file);
    } catch (err) {
        showError("Không thể tải dữ liệu mẫu: " + err.message);
    }
});


// -------------------------------------------------------------------------- //
//  Column Mapping UI
// -------------------------------------------------------------------------- //

/**
 * Render dropdown options cho Column Mapping dựa trên metadata cột.
 * Vì schema cố định, Exam_Score luôn là target nên auto-select.
 *
 * @param {{ target: Object, numeric_features: Array, categorical_features: Array }} meta
 */
function renderColumnMapping(meta) {
    // Clear options
    selectScore.innerHTML = "";
    selectLabel.innerHTML = '<option value="">— Không chọn —</option>';
    selectGroup.innerHTML = '<option value="">— Không chọn —</option>';

    // Score: target (Exam_Score) luôn đứng đầu, auto-selected
    const target = meta.target;
    selectScore.add(new Option(target.name, target.name, true, true));
    meta.numeric_features.forEach(col => {
        selectScore.add(new Option(col.name, col.name));
    });

    // Label: tất cả cột
    [target, ...meta.numeric_features, ...meta.categorical_features].forEach(col => {
        selectLabel.add(new Option(col.name, col.name));
    });

    // Group: chỉ categorical
    meta.categorical_features.forEach(col => {
        selectGroup.add(new Option(col.name, col.name));
    });
}

/**
 * Render bảng preview dữ liệu (5 dòng đầu).
 *
 * @param {Array<Object>} rows - Mảng objects, mỗi object là 1 dòng.
 */
function renderPreviewTable(rows) {
    if (!rows || rows.length === 0) return;

    const headers = Object.keys(rows[0]);

    let html = "<thead><tr>";
    headers.forEach(h => html += `<th>${h}</th>`);
    html += "</tr></thead><tbody>";

    rows.forEach(row => {
        html += "<tr>";
        headers.forEach(h => {
            const val = row[h] ?? "";
            html += `<td>${val}</td>`;
        });
        html += "</tr>";
    });
    html += "</tbody>";

    previewTable.innerHTML = html;
    previewContainer.removeAttribute("hidden");
}


// -------------------------------------------------------------------------- //
//  Analysis
// -------------------------------------------------------------------------- //

/**
 * Thu thập config từ UI và gửi POST /api/analyze.
 * Render kết quả lên dashboard.
 */
async function runAnalysis() {
    btnAnalyze.disabled = true;
    btnAnalyze.textContent = "⌛ Đang phân tích...";

    // Thu thập methods đã chọn
    const methods = [];
    if (document.getElementById("method-iqr").checked) methods.push("iqr");
    if (document.getElementById("method-zscore").checked) methods.push("zscore");
    if (document.getElementById("method-mad").checked) methods.push("mad");
    if (document.getElementById("method-dbscan").checked) methods.push("dbscan");

    const body = {
        methods: methods.length > 0 ? methods : ["iqr", "zscore"],
        threshold: parseFloat(thresholdSlider.value),
    };

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || "Phân tích thất bại");
            return;
        }

        renderResults(data);
        sectionResults.removeAttribute("hidden");
        sectionResults.scrollIntoView({ behavior: "smooth" });

    } catch (err) {
        showError("Lỗi phân tích: " + err.message);
    } finally {
        btnAnalyze.disabled = false;
        btnAnalyze.textContent = "🔍 Phân tích";
    }
}

btnAnalyze.addEventListener("click", runAnalysis);

thresholdSlider.addEventListener("input", () => {
    thresholdValue.textContent = parseFloat(thresholdSlider.value).toFixed(1);
});


// -------------------------------------------------------------------------- //
//  Render Results
// -------------------------------------------------------------------------- //

/**
 * Dispatcher: gọi tất cả các hàm render sau khi nhận response từ API.
 */
function renderResults(data) {
    renderStats(data.stats);
    renderDistribution(data.distribution);
    renderCharts(data.charts);
    renderOutliers(data.outliers);
    renderReport(data.report);
}

/**
 * Render statistics cards (mean, median, std, ...) vào stats-grid.
 *
 * @param {Object} stats - DescriptiveStats dict từ API.
 */
function renderStats(stats) {
  const container = document.getElementById('stats-cards');
  if (!container) return;

  const cardDefs = [
    { key: 'mean',     label: 'Trung bình',   icon: '📊', fmt: v => v.toFixed(2) },
    { key: 'median',   label: 'Trung vị',     icon: '📍', fmt: v => v.toFixed(2) },
    { key: 'std',      label: 'Độ lệch chuẩn',icon: '📐', fmt: v => v.toFixed(2) },
    { key: 'min',      label: 'Nhỏ nhất',     icon: '⬇️', fmt: v => v.toFixed(1) },
    { key: 'max',      label: 'Lớn nhất',     icon: '⬆️', fmt: v => v.toFixed(1) },
    { key: 'q1',       label: 'Q1 (25%)',     icon: '◼️', fmt: v => v.toFixed(2) },
    { key: 'q3',       label: 'Q3 (75%)',     icon: '◼️', fmt: v => v.toFixed(2) },
    { key: 'iqr',      label: 'IQR',          icon: '↕️', fmt: v => v.toFixed(2) },
    { key: 'skewness', label: 'Độ lệch',      icon: '〽️', fmt: v => v.toFixed(3) },
    { key: 'kurtosis', label: 'Độ nhọn',      icon: '🔺', fmt: v => v.toFixed(3) },
    { key: 'count',    label: 'Số mẫu',       icon: '🔢', fmt: v => v.toLocaleString() },
    { key: 'missing',  label: 'Thiếu dữ liệu',icon: '❓', fmt: v => v },
  ];

  container.innerHTML = cardDefs.map(({ key, label, icon, fmt }) => `
    <div class="stat-card" id="stat-${key}">
      <div class="stat-icon">${icon}</div>
      <div class="stat-label">${label}</div>
      <div class="stat-value">${stats[key] !== undefined ? fmt(stats[key]) : 'N/A'}</div>
    </div>
  `).join('');
}


/**
 * Render kết quả kiểm định phân phối.
 *
 * @param {Object} dist - DistributionResult dict từ API.
 */
function renderDistribution(dist) {
    if (!dist) return;

    const testsHtml = (dist.tests || []).map(t => `
        <tr>
            <td>${t.test_name}</td>
            <td>${t.statistic?.toFixed(4) ?? "—"}</td>
            <td>${t.p_value?.toFixed(4) ?? "N/A"}</td>
            <td>${t.is_normal
                ? '<span style="color:#4CAF50">✔ Chuẩn</span>'
                : '<span style="color:#FF4B4B">✘ Không chuẩn</span>'}</td>
        </tr>
    `).join("");

    distributionResults.innerHTML = `
        <h3>📉 Kiểm định phân phối</h3>
        <p style="margin-bottom:1rem">${dist.conclusion}</p>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr><th>Kiểm định</th><th>Statistic</th><th>p-value</th><th>Kết quả</th></tr>
                </thead>
                <tbody>${testsHtml}</tbody>
            </table>
        </div>
        <p class="hint" style="margin-top:0.5rem">Phân phối fit tốt nhất: <strong>${dist.best_fit}</strong></p>
    `;
}

/**
 * Render tất cả Plotly charts vào các container tương ứng.
 *
 * @param {Object} charts - Dict chart_name → Plotly JSON string.
 */
function renderCharts(charts) {
    if (!charts) return;

    const config = { responsive: true, displayModeBar: false };

    const chartMap = {
        "histogram_kde":   "chart-histogram",
        "box_plot":        "chart-boxplot",
        "violin_plot":     "chart-violin",
        "qq_plot":         "chart-qqplot",
        "scatter_outlier": "chart-scatter",
    };

    Object.entries(chartMap).forEach(([key, containerId]) => {
        if (charts[key]) {
            try {
                const parsed = JSON.parse(charts[key]);
                Plotly.newPlot(containerId, parsed.data, parsed.layout, config);
            } catch (e) {
                console.warn(`Lỗi render chart ${key}:`, e);
            }
        }
    });
}

/**
 * Render bảng outlier với highlighting.
 *
 * @param {Array<Object>} outliers - List OutlierRecord từ API.
 */
function renderOutliers(outliers) {
    if (!outliers || outliers.length === 0) {
        outlierTable.innerHTML = '<p style="color:#4CAF50">🎉 Không phát hiện giá trị ngoại lai nào!</p>';
        return;
    }

    const rows = outliers.map(o => `
        <tr class="outlier-row">
            <td><strong>${o.label ?? "—"}</strong></td>
            <td>${o.value}</td>
            <td>${(o.z_score ?? 0).toFixed(2)}</td>
            <td><small>${(o.methods_flagged || []).join(", ")}</small></td>
            <td><small>${o.explanation ?? ""}</small></td>
        </tr>
    `).join("");

    outlierTable.innerHTML = `
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Nhãn</th>
                        <th>Giá trị</th>
                        <th>Z-Score</th>
                        <th>Phương pháp</th>
                        <th>Giải thích</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        </div>
    `;
}

/**
 * Render báo cáo nhận xét vào report section.
 *
 * @param {Object} report - FullReport dict từ API.
 */
function renderReport(report) {
    if (!report) return;

    reportContent.innerHTML = `
        <div class="report-section" style="line-height:1.8">
            <p><strong>📌 Tóm tắt:</strong> ${report.summary}</p>
            <hr style="border-color:rgba(255,255,255,0.1);margin:1rem 0">
            <p><strong>📊 Thống kê:</strong> ${report.statistics_comment}</p>
            <p><strong>📈 Phân phối:</strong> ${report.distribution_comment}</p>
            <p><strong>🔴 Outlier:</strong> ${report.outlier_comment}</p>
            <hr style="border-color:rgba(255,255,255,0.1);margin:1rem 0">
            <h4>💡 Đề xuất hành động:</h4>
            <div style="white-space:pre-line;margin-top:0.5rem">${report.recommendation}</div>
        </div>
    `;
}


// -------------------------------------------------------------------------- //
//  Utilities
// -------------------------------------------------------------------------- //

/**
 * Hiển thị thông báo lỗi cho user.
 *
 * @param {string} message - Thông báo lỗi.
 */
function showError(message) {
    // Dùng alert đơn giản — Week 2 sẽ thay bằng toast notification
    alert("⚠️ " + message);
}
