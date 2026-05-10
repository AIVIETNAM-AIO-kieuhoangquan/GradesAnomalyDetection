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

/** @type {{ columns: Array, preview: Array, row_count: number } | null} */
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
    const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
        // DO NOT set Content-Type header — browser auto-sets multipart/form-data
        // with the correct boundary
    });
    const data = await response.json();
    if (!response.ok) {
        showError(data.error || "Upload failed");
        return;
    }
    uploadedMeta = data;
    uploadFilename.textContent = file.name;
    uploadInfo.textContent = data.row_count + " rows, " + data.col_count + " cols";
    uploadStatus.classList.remove("hidden");

    // STEP 7: Render preview table
    renderPreviewTable(data.preview);

    // STEP 8: Show next sections
    sectionMapping.classList.remove("hidden");
    sectionConfig.classList.remove("hidden");
}
// Drag and drop
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

// Click to select file
dropZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) handleFileUpload(fileInput.files[0]);
});


// TODO: Implement
// 1. Tạo FormData, append file
// 2. fetch POST /api/upload
// 3. Parse response JSON
// 4. Lưu vào uploadedMeta
// 5. Gọi renderColumnMapping(response)
// 6. Hiển thị upload status (filename, row count)
// 7. Show section-mapping & section-config

// TODO: Implement event listeners
// - dropZone: dragover, dragleave, drop → gọi handleFileUpload
// - dropZone: click → trigger fileInput.click()
// - fileInput: change → handleFileUpload(files[0])
// - btnSampleData: click → fetch /api/sample-data, rồi upload nó


// -------------------------------------------------------------------------- //
//  Column Mapping UI
// -------------------------------------------------------------------------- //

/**
 * Render dropdown options cho Column Mapping dựa trên metadata cột.
 * - select-score: chỉ hiển thị cột numeric
 * - select-label: hiển thị tất cả cột
 * - select-group: hiển thị cột categorical
 *
 * @param {{ columns: Array<{name: string, category: string}> }} meta
 */
function renderColumnMapping(meta) {
    // TODO: Implement
    // 1. Clear existing options
    // 2. Populate select-score với numeric columns
    // 3. Populate select-label với all columns + "— Không chọn —"
    // 4. Populate select-group với categorical columns + "— Không chọn —"
    // 5. Enable btn-analyze
}

/**
 * Render bảng preview dữ liệu (5 dòng đầu).
 *
 * @param {Array<Object>} rows - Mảng objects, mỗi object là 1 dòng.
 */
function renderPreviewTable(rows) {
    // TODO: Implement
    // 1. Tạo thead từ Object.keys(rows[0])
    // 2. Tạo tbody từ rows
    // 3. Gán vào previewTable.innerHTML
    // 4. Show previewContainer
}


// -------------------------------------------------------------------------- //
//  Analysis
// -------------------------------------------------------------------------- //

/**
 * Thu thập config từ UI và gửi POST /api/analyze.
 * Render kết quả lên dashboard.
 *
 * @returns {Promise<void>}
 */
async function runAnalysis() {
    // TODO: Implement
    // 1. Build column_mapping từ select values
    // 2. Build methods array từ checked checkboxes
    // 3. Get threshold từ slider
    // 4. Get group_value (nếu có)
    // 5. fetch POST /api/analyze với JSON body
    // 6. Parse response
    // 7. Gọi renderStats, renderCharts, renderOutliers, renderReport
    // 8. Show section-results, scroll to it
}

// TODO: btnAnalyze.addEventListener("click", runAnalysis)
// TODO: thresholdSlider.addEventListener("input", updateThresholdDisplay)


// -------------------------------------------------------------------------- //
//  Render Results
// -------------------------------------------------------------------------- //

/**
 * Render statistics cards (mean, median, std, ...) vào stats-grid.
 *
 * @param {Object} stats - DescriptiveStats dict từ API.
 */
function renderStats(stats) {
    // TODO: Implement
    // 1. Định nghĩa danh sách metrics cần hiển thị (key, label, icon)
    // 2. Tạo HTML card cho mỗi metric
    // 3. Gán vào statsCards.innerHTML
}

/**
 * Render tất cả Plotly charts vào các container tương ứng.
 *
 * @param {Object} charts - Dict chart_name → Plotly JSON string.
 */
function renderCharts(charts) {
    // TODO: Implement
    // 1. Với mỗi chart: parse JSON, gọi Plotly.newPlot(containerId, data, layout)
    // 2. Map: histogram_kde → chart-histogram, box_plot → chart-boxplot, v.v.
}

/**
 * Render bảng outlier với highlighting.
 *
 * @param {Array<Object>} outliers - List OutlierRecord từ API.
 */
function renderOutliers(outliers) {
    // TODO: Implement
    // 1. Tạo thead (Row #, Label, Value, Phương pháp, Giải thích)
    // 2. Tạo tbody, mỗi row có class "outlier-row"
    // 3. Nếu rỗng, hiển thị "Không phát hiện outlier"
}

/**
 * Render báo cáo nhận xét vào report section.
 *
 * @param {Object} report - FullReport dict từ API.
 */
function renderReport(report) {
    // TODO: Implement
    // 1. Build HTML từ report.summary, statistics_comment, v.v.
    // 2. Gán vào reportContent.innerHTML
}


// -------------------------------------------------------------------------- //
//  Utilities
// -------------------------------------------------------------------------- //

/**
 * Cập nhật hiển thị giá trị threshold khi kéo slider.
 */
function updateThresholdDisplay() {
    // TODO: thresholdValue.textContent = thresholdSlider.value
}

/**
 * Hiển thị lỗi cho user (toast hoặc alert).
 *
 * @param {string} message - Thông báo lỗi.
 */
function showError(message) {
    // TODO: Implement — toast notification hoặc alert
}
