/* Per-paper keys avoid overwriting another tab's updates to other papers. */
(() => {
  "use strict";
  const prefix = "arxiv-daily:read:v1:";
  const fallback = new Map();
  const unsaved = new Set();
  const baseId = (id) => String(id).replace(/v\d+$/, "");
  function warn() {
    for (const notice of document.querySelectorAll("[data-storage-notice]")) {
      notice.hidden = false;
      notice.textContent = "浏览器未能保存阅读状态；本次页面内仍可标记，刷新后可能丢失。";
    }
  }
  function isRead(id) {
    const key = prefix + baseId(id);
    if (unsaved.has(key)) return fallback.get(key);
    try {
      const value = localStorage.getItem(key) === "1";
      fallback.set(key, value);
      return value;
    } catch (_) {
      warn();
      return fallback.get(key) || false;
    }
  }
  function render() {
    for (const button of document.querySelectorAll("[data-read-toggle]")) {
      const read = isRead(button.dataset.readToggle);
      button.disabled = false;
      button.setAttribute("aria-pressed", String(read));
      button.textContent = read ? "已读 · 标为未读" : "未读 · 标为已读";
      const title = button.closest(".paper")?.querySelector("h2")?.textContent.trim() || document.title;
      button.setAttribute("aria-label", (read ? "标为未读：" : "标为已读：") + title);
    }
  }
  function refresh() {
    render();
    document.dispatchEvent(new Event("reading-state-change"));
  }
  document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-read-toggle]");
    if (!button) return;
    const id = baseId(button.dataset.readToggle);
    const key = prefix + id;
    const next = !isRead(id);
    fallback.set(key, next);
    try {
      localStorage.setItem(key, next ? "1" : "0");
      unsaved.delete(key);
    } catch (_) {
      unsaved.add(key);
      warn();
    }
    refresh();
  });
  window.addEventListener("storage", (event) => {
    if (event.key === null) {
      fallback.clear();
      unsaved.clear();
      refresh();
    } else if (event.key.startsWith(prefix)) {
      unsaved.delete(event.key);
      fallback.set(event.key, event.newValue === "1");
      refresh();
    }
  });
  window.addEventListener("pageshow", refresh);
  window.ArxivReading = Object.freeze({ isRead, baseId });
  render();
})();
