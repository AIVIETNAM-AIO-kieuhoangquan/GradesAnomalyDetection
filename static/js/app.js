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
let latestAnalysisData = null;
let currentOutliers = [];
let currentFilter = "all";


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
        showToast(`Upload thành công: ${data.row_count} dòng, ${data.col_count} cột`, "success");

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

    // Show loading spinner overlay
    sectionResults.removeAttribute("hidden");
    let overlay = document.getElementById("loading-overlay");
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.id = "loading-overlay";
        overlay.innerHTML = `
            <div style="text-align:center;padding:3rem;color:var(--text-muted)">
                <div class="spinner"></div>
                <p style="margin-top:1rem">Đang Phân Tích Dữ Liệu...</p>
            </div>
        `;
        sectionResults.appendChild(overlay);
    } else {
        overlay.style.display = "flex";
    }
    sectionResults.scrollIntoView({ behavior: "smooth" });

    // Thu thập methods đã chọn
    const methods = [];
    if (document.getElementById("method-iqr").checked) methods.push("iqr");
    if (document.getElementById("method-zscore").checked) methods.push("zscore");
    if (document.getElementById("method-mad").checked) methods.push("mad");
    if (document.getElementById("method-dbscan").checked) methods.push("dbscan");
    if (document.getElementById("method-percentile")?.checked) methods.push("percentile");

    const body = {
        methods: methods.length > 0 ? methods : ["iqr", "zscore", "percentile"],
        threshold: parseFloat(thresholdSlider.value),
        min_votes: 1,
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

        // Hide loading overlay
        const overlay = document.getElementById("loading-overlay");
        if (overlay) overlay.style.display = "none";

        renderResults(data);
        sectionResults.removeAttribute("hidden");
        sectionResults.scrollIntoView({ behavior: "smooth" });
        showToast("Phân tích thành công!", "success");

    } catch (err) {
        const overlay = document.getElementById("loading-overlay");
        if (overlay) overlay.style.display = "none";
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
    latestAnalysisData = data;
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
        { key: 'mean', label: 'Trung bình', icon: '📊', fmt: v => v.toFixed(2) },
        { key: 'median', label: 'Trung vị', icon: '📍', fmt: v => v.toFixed(2) },
        { key: 'std', label: 'Độ lệch chuẩn', icon: '📐', fmt: v => v.toFixed(2) },
        { key: 'min', label: 'Nhỏ nhất', icon: '⬇️', fmt: v => v.toFixed(1) },
        { key: 'max', label: 'Lớn nhất', icon: '⬆️', fmt: v => v.toFixed(1) },
        { key: 'q1', label: 'Q1 (25%)', icon: '◼️', fmt: v => v.toFixed(2) },
        { key: 'q3', label: 'Q3 (75%)', icon: '◼️', fmt: v => v.toFixed(2) },
        { key: 'iqr', label: 'IQR', icon: '↕️', fmt: v => v.toFixed(2) },
        { key: 'skewness', label: 'Độ lệch', icon: '〽️', fmt: v => v.toFixed(3) },
        { key: 'kurtosis', label: 'Độ nhọn', icon: '🔺', fmt: v => v.toFixed(3) },
        { key: 'count', label: 'Số mẫu', icon: '🔢', fmt: v => v.toLocaleString() },
        { key: 'missing', label: 'Thiếu dữ liệu', icon: '❓', fmt: v => v },
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
function renderDistribution(distribution) {
    document.getElementById('distribution-section');
    if (!distribution) return;

    const testsHtml = (distribution.tests || []).map(t => `
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
        <p style="margin-bottom:1rem">${distribution.conclusion}</p>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr><th>Kiểm định</th><th>Statistic</th><th>p-value</th><th>Kết quả</th></tr>
                </thead>
                <tbody>${testsHtml}</tbody>
            </table>
        </div>
        <p class="hint" style="margin-top:0.5rem">Phân phối fit tốt nhất: <strong>${distribution.best_fit}</strong></p>
    `;
}

/**
 * Render tất cả Plotly charts vào các container tương ứng.
 * Sử dụng Plotly.react() thay newPlot() để hiệu năng tốt hơn khi re-render.
 *
 * @param {Object} charts - Dict chart_name → Plotly JSON string.
 */
function renderCharts(charts) {
    if (!charts) return;

    const chartMap = {
        "histogram_kde": "chart-histogram",
        "box_plot":       "chart-boxplot",
        "violin_plot":    "chart-violin",
        "qq_plot":        "chart-qqplot",
        "scatter_outlier":"chart-scatter",
        "strip_plot":     "chart-strip",
    };

    const plotlyConfig = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ["lasso2d", "select2d"],
    };

    Object.entries(chartMap).forEach(([key, elementId]) => {
        const el = document.getElementById(elementId);
        if (!el) return;  // Element not in DOM — skip silently

        if (!charts[key]) {
            el.innerHTML = '<p class="chart-empty">Biểu đồ chưa sẵn sàng</p>';
            return;
        }

        try {
            const figData = JSON.parse(charts[key]);

            // Chỉ patch autosize — KHÔNG override layout gốc từ Plotly Python
            // Plotly Python đã serialize đúng axis ranges, dtype arrays, v.v.
            const layout = figData.layout || {};
            if (!('autosize' in layout)) layout.autosize = true;

            Plotly.newPlot(elementId, figData.data, layout, plotlyConfig);
        } catch (err) {
            console.error(`Lỗi render chart ${key}:`, err);
            el.innerHTML = '<p class="chart-error">Không thể tải biểu đồ</p>';
        }
    });

    // Sau khi DOM settle, resize tất cả charts để fill đúng container
    requestAnimationFrame(() => {
        Object.values(chartMap).forEach(id => {
            const el = document.getElementById(id);
            if (el && el._fullLayout) {
                Plotly.Plots.resize(el);
            }
        });
    });
}

/**
 * Render bảng outlier với highlighting, severity badges và bộ lọc.
 *
 * @param {Array<Object>} outliers - List OutlierRecord từ API.
 */
function renderOutliers(outliers) {
    currentOutliers = outliers || [];
    currentFilter = "all";

    const countTag = document.getElementById("outlier-count-tag");
    const actions = document.getElementById("outlier-actions");
    const filtersBar = document.getElementById("outlier-filters-bar");
    const searchInput = document.getElementById("outlier-search-input");
    if (searchInput) searchInput.value = "";

    // Reset filter chips
    document.querySelectorAll(".filter-chip").forEach(chip => {
        chip.classList.toggle("active", chip.dataset.filter === "all");
    });

    if (!outliers || outliers.length === 0) {
        if (countTag) {
            countTag.textContent = "0 phát hiện";
            countTag.removeAttribute("hidden");
        }
        if (actions) actions.setAttribute("hidden", "true");
        if (filtersBar) filtersBar.setAttribute("hidden", "true");
        outlierTable.innerHTML = `
            <tbody>
                <tr>
                    <td colspan="7" style="text-align:center;padding:2.5rem;color:var(--emerald);">
                        🎉 Không phát hiện giá trị ngoại lai nào với cấu hình hiện tại!
                    </td>
                </tr>
            </tbody>
        `;
        return;
    }

    if (countTag) {
        countTag.textContent = `${outliers.length} phát hiện`;
        countTag.removeAttribute("hidden");
    }
    if (actions) actions.removeAttribute("hidden");
    if (filtersBar) filtersBar.removeAttribute("hidden");

    renderOutlierRows(currentOutliers);
}

/**
 * Render các hàng trong bảng outlier.
 *
 * @param {Array<Object>} outliersList - Danh sách outliers cần hiển thị.
 */
function renderOutlierRows(outliersList) {
    if (!outliersList || outliersList.length === 0) {
        outlierTable.innerHTML = `
            <thead>
                <tr>
                    <th>Chỉ mục</th>
                    <th>Nhãn</th>
                    <th>Điểm số</th>
                    <th>Phương pháp</th>
                    <th>Z-Score</th>
                    <th>Mức độ</th>
                    <th>Giải thích</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="7" style="text-align:center;padding:2rem;color:var(--text3);">
                        Không tìm thấy bản ghi ngoại lai nào phù hợp với bộ lọc hiện tại.
                    </td>
                </tr>
            </tbody>
        `;
        return;
    }

    const rows = outliersList.map(o => {
        const isExtreme = Math.abs(o.z_score) > 3.5;
        const severityClass = isExtreme ? "severity-extreme" : "severity-moderate";
        const severityLabel = isExtreme ? "Cực đoan" : "Vừa phải";
        const methodsHtml = (o.methods_flagged || [])
            .map(m => `<span class="method-tag">${m.toUpperCase()}</span>`)
            .join("");

        return `
            <tr class="outlier-row ${isExtreme ? 'outlier-extreme' : 'outlier-moderate'}" data-index="${o.row_index}">
                <td><strong>#${o.row_index}</strong></td>
                <td>${o.label || '—'}</td>
                <td class="outlier-value">${o.value?.toFixed(2) ?? 'N/A'}</td>
                <td>${methodsHtml || '—'}</td>
                <td><strong>${o.z_score !== undefined ? o.z_score.toFixed(3) : 'N/A'}</strong></td>
                <td><span class="severity-pill ${severityClass}">${severityLabel}</span></td>
                <td class="explanation">${o.explanation ?? '—'}</td>
            </tr>
        `;
    }).join("");

    outlierTable.innerHTML = `
        <thead>
            <tr>
                <th>Chỉ mục</th>
                <th>Nhãn</th>
                <th>Điểm số</th>
                <th>Phương pháp</th>
                <th>Z-Score</th>
                <th>Mức độ</th>
                <th>Giải thích</th>
            </tr>
        </thead>
        <tbody>${rows}</tbody>
    `;
}

/**
 * Áp dụng bộ lọc và từ khóa tìm kiếm trên bảng outlier.
 */
function applyOutlierFilters() {
    const searchInput = document.getElementById("outlier-search-input");
    const query = searchInput ? searchInput.value.trim().toLowerCase() : "";

    const filtered = currentOutliers.filter(o => {
        const isExtreme = Math.abs(o.z_score) > 3.5;
        if (currentFilter === "extreme" && !isExtreme) return false;
        if (currentFilter === "moderate" && isExtreme) return false;

        if (query) {
            const idxMatch = String(o.row_index).includes(query);
            const labelMatch = o.label ? String(o.label).toLowerCase().includes(query) : false;
            const valMatch = String(o.value).includes(query);
            const expMatch = o.explanation ? o.explanation.toLowerCase().includes(query) : false;
            if (!idxMatch && !labelMatch && !valMatch && !expMatch) return false;
        }

        return true;
    });

    renderOutlierRows(filtered);
}

/**
 * Xuất danh sách Outliers sang file CSV.
 */
function exportOutliersCSV() {
    if (!currentOutliers || currentOutliers.length === 0) {
        showToast("Không có bản ghi ngoại lai nào để xuất!", "warning");
        return;
    }

    try {
        const headers = ["Index", "Label", "Score", "Methods_Flagged", "Z_Score", "Severity", "Explanation"];
        const rows = currentOutliers.map(o => {
            const z = o.z_score;
            const sev = Math.abs(z) > 3.5 ? "Cực đoan" : "Vừa phải";
            const methods = (o.methods_flagged || []).join("; ");
            const exp = `"${(o.explanation || '').replace(/"/g, '""')}"`;
            return [o.row_index, o.label || "", o.value, methods, z !== undefined ? z.toFixed(4) : "", sev, exp];
        });

        const csvContent = "\uFEFF" + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `outliers_report_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        showToast("Đã tải xuống file CSV outliers!", "success");
    } catch (e) {
        window.location.href = "/api/export/outliers";
    }
}

/**
 * Xuất toàn bộ báo cáo phân tích sang file JSON.
 */
function exportReportJSON() {
    if (!latestAnalysisData) {
        showToast("Chưa có kết quả phân tích để xuất!", "warning");
        return;
    }

    try {
        const payload = {
            exported_at: new Date().toISOString(),
            stats: latestAnalysisData.stats,
            distribution: latestAnalysisData.distribution,
            outliers: latestAnalysisData.outliers,
            report: latestAnalysisData.report,
        };
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `student_score_report_${new Date().toISOString().slice(0, 10)}.json`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        showToast("Đã tải xuống báo cáo JSON!", "success");
    } catch (e) {
        window.location.href = "/api/export/report";
    }
}

/**
 * Render báo cáo nhận xét vào report section.
 *
 * @param {Object} report - FullReport dict từ API.
 */
function renderReport(report) {
    if (!report) return;

    const reportActions = document.getElementById("report-actions");
    if (reportActions) reportActions.removeAttribute("hidden");

    const sections = [
        { icon: "📌", label: "Tóm tắt", text: report.summary },
        { icon: "📊", label: "Thống kê", text: report.statistics_comment },
        { icon: "📈", label: "Phân phối", text: report.distribution_comment },
        { icon: "🔴", label: "Outlier", text: report.outlier_comment },
    ];

    let html = '<div class="report-section" style="line-height:1.8">';

    // Only render sections that have content
    sections.forEach(s => {
        if (s.text && s.text.trim()) {
            html += `<p><strong>${s.icon} ${s.label}:</strong> ${s.text}</p>`;
        }
    });

    // Divider before recommendation
    html += '<hr style="border-color:rgba(255,255,255,0.1);margin:1rem 0">';

    // Recommendation section
    html += '<h4>💡 Đề xuất hành động:</h4>';
    html += `<div style="white-space:pre-line;margin-top:0.5rem">`;
    html += report.recommendation || "—";
    html += '</div>';

    // Copy button
    html += `
        <div style="display:flex;gap:.75rem;margin-top:1.5rem;flex-wrap:wrap">
            <button class="btn btn-secondary" onclick="copyReport()">
                📋 Sao chép báo cáo
            </button>
            <button class="btn btn-secondary" onclick="exportReportJSON()">
                📄 Tải file JSON
            </button>
        </div>
    `;

    html += '</div>';
    reportContent.innerHTML = html;
}

function copyReport() {
    const text = reportContent.innerText;
    navigator.clipboard.writeText(text).then(() => {
        showToast("Đã sao chép báo cáo!", "success");
    }).catch(() => {
        showToast("Không thể sao chép vào clipboard", "error");
    });
}



// -------------------------------------------------------------------------- //
//  Utilities
// -------------------------------------------------------------------------- //

/**
 * Hiển thị toast notification thay vì alert().
 *
 * @param {string} message - Nội dung thông báo.
 * @param {'success'|'error'|'warning'|'info'} type - Loại thông báo.
 * @param {number} duration - Thời gian hiển thị (ms).
 */
function showToast(message, type = 'info', duration = 4000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
        <span class="toast-msg">${message}</span>
        <button class="toast-close" aria-label="Đóng" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('toast-show'));

    setTimeout(() => {
        toast.classList.remove('toast-show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/** Wrapper ngắn gọn để dùng thay alert() */
function showError(message) {
    showToast(message, 'error');
}

// -------------------------------------------------------------------------- //
//  Export & Filter Event Listeners
// -------------------------------------------------------------------------- //

document.addEventListener("DOMContentLoaded", () => {
    const btnExportOutliers = document.getElementById("btn-export-outliers");
    if (btnExportOutliers) {
        btnExportOutliers.addEventListener("click", exportOutliersCSV);
    }

    const btnExportReport = document.getElementById("btn-export-report-json");
    if (btnExportReport) {
        btnExportReport.addEventListener("click", exportReportJSON);
    }

    const filterChips = document.querySelectorAll(".filter-chip");
    filterChips.forEach(chip => {
        chip.addEventListener("click", (e) => {
            filterChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            currentFilter = chip.dataset.filter || "all";
            applyOutlierFilters();
        });
    });

    const searchInput = document.getElementById("outlier-search-input");
    if (searchInput) {
        searchInput.addEventListener("input", applyOutlierFilters);
    }
});
