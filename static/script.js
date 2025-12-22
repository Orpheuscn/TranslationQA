// 全局变量
let csvData = '';

// DOM元素
const sourceTextEl = document.getElementById('sourceText');
const targetTextEl = document.getElementById('targetText');
const similarityThresholdEl = document.getElementById('similarityThreshold');
const forceSplitThresholdEl = document.getElementById('forceSplitThreshold');
const checkBtn = document.getElementById('checkBtn');
const btnText = document.getElementById('btnText');
const btnLoading = document.getElementById('btnLoading');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const summaryEl = document.getElementById('summary');
const csvTableEl = document.getElementById('csvTable');
const errorMessageEl = document.getElementById('errorMessage');
const downloadCsvBtn = document.getElementById('downloadCsvBtn');
const copyTableBtn = document.getElementById('copyTableBtn');

// 高级设置元素
const toggleAdvancedBtn = document.getElementById('toggleAdvanced');
const toggleIcon = document.getElementById('toggleIcon');
const advancedPanel = document.getElementById('advancedPanel');
const maxAlignEl = document.getElementById('maxAlign');
const topKEl = document.getElementById('topK');
const skipEl = document.getElementById('skip');
const winEl = document.getElementById('win');
const scoreThresholdEl = document.getElementById('scoreThreshold');
const useMinSimilarityEl = document.getElementById('useMinSimilarity');

// 高级设置展开/隐藏
toggleAdvancedBtn.addEventListener('click', () => {
    const isHidden = advancedPanel.style.display === 'none';
    advancedPanel.style.display = isHidden ? 'block' : 'none';
    toggleIcon.textContent = isHidden ? '▼' : '▶';
});

// 检测按钮点击事件
checkBtn.addEventListener('click', async () => {
    const sourceText = sourceTextEl.value.trim();
    const targetText = targetTextEl.value.trim();
    
    if (!sourceText || !targetText) {
        alert('请输入原文和译文！');
        return;
    }
    
    // 显示加载状态
    checkBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    try {
        // 发送请求
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source_text: sourceText,
                target_text: targetText,
                similarity_threshold: parseFloat(similarityThresholdEl.value),
                force_split_threshold: parseFloat(forceSplitThresholdEl.value),
                // 高级参数
                max_align: parseInt(maxAlignEl.value),
                top_k: parseInt(topKEl.value),
                skip: parseFloat(skipEl.value),
                win: parseInt(winEl.value),
                score_threshold: parseFloat(scoreThresholdEl.value),
                use_min_similarity: useMinSimilarityEl.checked
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 显示结果
            displayResults(result.data);
        } else {
            // 显示错误
            displayError(result.error);
        }
    } catch (error) {
        displayError(`网络错误: ${error.message}`);
    } finally {
        // 恢复按钮状态
        checkBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
});

// 显示结果
function displayResults(data) {
    csvData = data.csv;
    
    // 显示摘要
    const summary = data.summary;
    const issues = data.issues;
    
    const omissionsCount = issues.omissions.length;
    const additionsCount = issues.additions.length;
    const lowSimilarityCount = issues.low_similarity.length;
    const totalIssues = omissionsCount + additionsCount + lowSimilarityCount;
    
    summaryEl.innerHTML = `
        <h3>📊 统计信息</h3>
        <div class="summary-grid">
            <div class="summary-item">
                <strong>源文本句子数</strong>
                <span>${summary.src_count}</span>
            </div>
            <div class="summary-item">
                <strong>目标文本句子数</strong>
                <span>${summary.tgt_count}</span>
            </div>
            <div class="summary-item">
                <strong>对齐组数</strong>
                <span>${summary.alignment_count}</span>
            </div>
            <div class="summary-item">
                <strong>相似度阈值</strong>
                <span>${summary.similarity_threshold}</span>
            </div>
        </div>
        
        <h3 style="margin-top: 20px;">⚠️ 发现的问题 (总计: ${totalIssues}处)</h3>
        <div class="issues-grid">
            <div class="issue-item">
                <div class="issue-count ${omissionsCount > 0 ? 'error' : 'ok'}">${omissionsCount}</div>
                <div>缺失 (Omission)</div>
            </div>
            <div class="issue-item">
                <div class="issue-count ${additionsCount > 0 ? 'error' : 'ok'}">${additionsCount}</div>
                <div>增添 (Addition)</div>
            </div>
            <div class="issue-item">
                <div class="issue-count ${lowSimilarityCount > 0 ? 'warning' : 'ok'}">${lowSimilarityCount}</div>
                <div>相似度低</div>
            </div>
        </div>
        
        ${data.force_split_count > 0 ? `
            <div style="margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 6px;">
                <strong>⚡ 强制拆散对齐组:</strong> ${data.force_split_count}个 (相似度 < ${forceSplitThresholdEl.value})
            </div>
        ` : ''}
    `;
    
    // 显示CSV表格
    displayCsvTable(data.csv);
    
    // 显示结果区域
    resultSection.style.display = 'block';
    errorSection.style.display = 'none';
    
    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 显示CSV表格
function displayCsvTable(csv) {
    const lines = csv.trim().split('\n');
    const headers = parseCSVLine(lines[0]);

    let tableHTML = '<table><thead><tr>';
    headers.forEach(header => {
        tableHTML += `<th>${header}</th>`;
    });
    tableHTML += '</tr></thead><tbody>';

    for (let i = 1; i < lines.length; i++) {
        const cells = parseCSVLine(lines[i]);
        tableHTML += '<tr>';
        cells.forEach((cell, index) => {
            let className = '';
            // 最后一列是异常情况
            if (index === cells.length - 1) {
                if (cell === 'OK') {
                    className = 'exception-ok';
                } else if (cell.includes('缺失') || cell.includes('增添')) {
                    className = 'exception-error';
                } else if (cell.includes('相似度低')) {
                    className = 'exception-warning';
                }
            }
            tableHTML += `<td class="${className}">${cell}</td>`;
        });
        tableHTML += '</tr>';
    }

    tableHTML += '</tbody></table>';
    csvTableEl.innerHTML = tableHTML;
}

// 解析CSV行（处理引号）
function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];

        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current);
            current = '';
        } else {
            current += char;
        }
    }

    result.push(current);
    return result;
}

// 显示错误
function displayError(errorMsg) {
    errorMessageEl.textContent = errorMsg;
    errorSection.style.display = 'block';
    resultSection.style.display = 'none';
}

// 下载CSV
downloadCsvBtn.addEventListener('click', () => {
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', 'translation_qa_report.csv');
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

// 复制表格
copyTableBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(csvData).then(() => {
        const originalText = copyTableBtn.textContent;
        copyTableBtn.textContent = '✅ 已复制！';
        setTimeout(() => {
            copyTableBtn.textContent = originalText;
        }, 2000);
    }).catch(err => {
        alert('复制失败: ' + err.message);
    });
});

