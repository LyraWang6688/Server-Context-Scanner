const els = {
  scanSummaryBtn: document.querySelector("#scanSummaryBtn"),
  scanFullBtn: document.querySelector("#scanFullBtn"),
  copyBtn: document.querySelector("#copyBtn"),
  clearBtn: document.querySelector("#clearBtn"),
  downloadLink: document.querySelector("#downloadLink"),
  reportOutput: document.querySelector("#reportOutput"),
  statusText: document.querySelector("#statusText"),
  modeText: document.querySelector("#modeText"),
  lineCountText: document.querySelector("#lineCountText"),
  charCountText: document.querySelector("#charCountText"),
  generatedAtText: document.querySelector("#generatedAtText"),
  tokenInput: document.querySelector("#tokenInput"),
  saveTokenBtn: document.querySelector("#saveTokenBtn"),
};

const tokenStorageKey = "server-context-scanner-token";

function getToken() {
  return localStorage.getItem(tokenStorageKey) || "";
}

function setBusy(isBusy) {
  els.scanSummaryBtn.disabled = isBusy;
  els.scanFullBtn.disabled = isBusy;
  els.copyBtn.disabled = isBusy;
  els.clearBtn.disabled = isBusy;
  els.statusText.textContent = isBusy ? "扫描中..." : els.statusText.textContent;
  document.body.classList.toggle("is-busy", isBusy);
}

function updateStatus(text, type = "neutral") {
  els.statusText.textContent = text;
  els.statusText.dataset.type = type;
}

function updateReport(data) {
  els.reportOutput.value = data.report || "";
  els.modeText.textContent = data.mode || "-";
  els.lineCountText.textContent = String(data.lineCount || 0);
  els.charCountText.textContent = String(data.charCount || 0);
  els.generatedAtText.textContent = data.generatedAt ? `生成于 ${data.generatedAt}` : "尚未生成";
}

function authHeaders() {
  const token = getToken();
  return token ? { "X-Scanner-Token": token } : {};
}

async function scan(mode) {
  setBusy(true);
  updateStatus(mode === "full" ? "正在生成完整报告..." : "正在生成精简报告...", "working");

  try {
    const response = await fetch("/api/scan", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify({ mode }),
    });
    const data = await response.json();
    if (!response.ok || !data.ok) {
      throw new Error(data.error || "扫描失败");
    }

    updateReport(data);
    updateStatus("扫描完成", "success");
  } catch (error) {
    updateStatus(error.message || "扫描失败", "error");
  } finally {
    setBusy(false);
  }
}

async function copyReport() {
  const content = els.reportOutput.value;
  if (!content) {
    updateStatus("没有可复制的报告", "error");
    return;
  }

  try {
    await navigator.clipboard.writeText(content);
    updateStatus("已复制", "success");
    els.copyBtn.classList.add("copied");
    els.copyBtn.textContent = "已复制";
    window.setTimeout(() => {
      els.copyBtn.classList.remove("copied");
      els.copyBtn.textContent = "复制报告";
    }, 1600);
  } catch {
    els.reportOutput.focus();
    els.reportOutput.select();
    updateStatus("浏览器限制自动复制，请手动 Ctrl/Cmd+C", "error");
  }
}

function clearReport() {
  els.reportOutput.value = "";
  els.modeText.textContent = "-";
  els.lineCountText.textContent = "0";
  els.charCountText.textContent = "0";
  els.generatedAtText.textContent = "尚未生成";
  updateStatus("已清空", "neutral");
}

function updateDownloadLink() {
  const token = getToken();
  els.downloadLink.href = token ? `/download/latest?token=${encodeURIComponent(token)}` : "/download/latest";
}

function initTokenPanel() {
  if (!els.tokenInput || !els.saveTokenBtn) {
    return;
  }

  els.tokenInput.value = getToken();
  updateDownloadLink();
  els.saveTokenBtn.addEventListener("click", () => {
    localStorage.setItem(tokenStorageKey, els.tokenInput.value.trim());
    updateDownloadLink();
    updateStatus("Token 已保存到本浏览器", "success");
  });
}

els.scanSummaryBtn.addEventListener("click", () => scan("summary"));
els.scanFullBtn.addEventListener("click", () => scan("full"));
els.copyBtn.addEventListener("click", copyReport);
els.clearBtn.addEventListener("click", clearReport);

initTokenPanel();
updateDownloadLink();
