(() => {
  "use strict";
  const tags = [...document.querySelectorAll("[data-tag]")];
  const states = [...document.querySelectorAll("[data-read-filter]")];
  const papers = [...document.querySelectorAll(".paper")];
  const available = new Set(tags.map((control) => control.dataset.tag));
  const count = document.querySelector("#result-count");
  const empty = document.querySelector("#no-results");
  function apply() {
    const params = new URLSearchParams(location.search);
    const tag = available.has(params.get("tag")) ? params.get("tag") : "";
    const requested = params.get("status");
    const status = ["read", "unread"].includes(requested) ? requested : "all";
    const topicDetails = document.querySelector('.topic-filters');
    if (topicDetails && tag && tags.some((control) =>
      control.dataset.tag === tag && topicDetails.contains(control))) topicDetails.open = true;
    let visible = 0;
    let readCount = 0;
    for (const paper of papers) {
      const read = window.ArxivReading.isRead(paper.dataset.paperId);
      const topicMatches = !tag || JSON.parse(paper.dataset.tags).includes(tag);
      const statusMatches = status === "all" || (status === "read" ? read : !read);
      paper.hidden = !topicMatches || !statusMatches;
      if (read) readCount += 1;
      if (!paper.hidden) visible += 1;
    }
    for (const control of tags) {
      const active = control.dataset.tag === tag;
      control.classList.toggle("is-active", active);
      if (active) control.setAttribute("aria-current", "true");
      else control.removeAttribute("aria-current");
      const url = new URL(location.href);
      if (control.dataset.tag) url.searchParams.set("tag", control.dataset.tag);
      else url.searchParams.delete("tag");
      control.href = url.pathname + url.search;
    }
    const totals = { all: papers.length, read: readCount, unread: papers.length - readCount };
    for (const control of states) {
      control.disabled = false;
      control.setAttribute("aria-pressed", String(control.dataset.readFilter === status));
      control.textContent = `${control.dataset.label} ${totals[control.dataset.readFilter]}`;
    }
    if (count) count.textContent = `${tag ? tag + " · " : ""}显示 ${visible} / ${papers.length} 篇`;
    if (empty) empty.hidden = visible !== 0;
  }
  function navigate(key, value) {
    const url = new URL(location.href);
    if (value) url.searchParams.set(key, value);
    else url.searchParams.delete(key);
    if (url.href !== location.href) history.pushState(null, "", url);
    apply();
  }
  for (const control of tags) control.addEventListener("click", (event) => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    navigate("tag", control.dataset.tag);
  });
  for (const control of states) control.addEventListener("click", () => {
    navigate("status", control.dataset.readFilter === "all" ? "" : control.dataset.readFilter);
  });
  window.addEventListener("popstate", apply);
  window.addEventListener("pageshow", apply);
  document.addEventListener("reading-state-change", apply);
  apply();
})();
