import mermaid from "mermaid";

// The diagram source stays in the page so reading does not depend on rendering.
// Render once, explicitly, rather than letting Mermaid scan the entire document.
const FONT = 'system-ui, "Noto Sans SC", "Microsoft YaHei", sans-serif';
const MIN_ZOOM = 0.5;
const MAX_ZOOM = 4;
const MIN_FIT_SCALE = 0.9;

function addZoomControls(figure, output, svg) {
  const box = svg.viewBox.baseVal;
  if (!(box.width > 0 && box.height > 0)) {
    throw new Error("The diagram did not provide a usable SVG viewBox");
  }
  const naturalWidth = box.width;
  const aspectRatio = box.height / box.width;
  let zoom = 1;
  let appliedWidth = 0;
  const controls = document.createElement("div");
  controls.className = "arxiv-mermaid-controls";
  controls.setAttribute("role", "group");
  controls.setAttribute("aria-label", "关系图缩放");
  const size = document.createElement("span");
  size.setAttribute("role", "status");
  size.setAttribute("aria-live", "polite");
  const makeButton = (label, action) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", action);
    return button;
  };
  const resize = () => {
    // A hidden slide has width zero. ResizeObserver reruns when it is revealed.
    const available = output.clientWidth || naturalWidth;
    // A wide overview should scroll inside its frame rather than shrink Chinese
    // labels into unreadable marks on a phone. Zoom-out remains an explicit choice.
    const fittedWidth = Math.max(naturalWidth * MIN_FIT_SCALE, Math.min(naturalWidth, available));
    const width = fittedWidth * zoom;
    if (Math.abs(width - appliedWidth) > 0.1) {
      svg.style.width = `${width}px`;
      svg.style.height = `${width * aspectRatio}px`;
      appliedWidth = width;
    }
  };
  const update = () => {
    size.textContent = `${Math.round(zoom * 100)}%`;
    smaller.disabled = zoom <= MIN_ZOOM;
    larger.disabled = zoom >= MAX_ZOOM;
    resize();
  };
  const smaller = makeButton("缩小", () => {
    zoom = Math.max(MIN_ZOOM, zoom - 0.25);
    update();
  });
  const larger = makeButton("放大", () => {
    zoom = Math.min(MAX_ZOOM, zoom + 0.25);
    update();
  });
  const reset = makeButton("重置", () => {
    zoom = 1;
    update();
    output.scrollLeft = 0;
  });
  controls.append(smaller, larger, reset, size);
  output.before(controls);
  output.tabIndex = 0;
  output.setAttribute("role", "region");
  output.setAttribute("aria-label", "关系图；放大后可用左右方向键滚动，Home 和 End 移到两端");
  output.addEventListener("keydown", (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    // Keep the slide deck's document-level navigation from stealing graph keys.
    event.preventDefault();
    event.stopPropagation();
    if (event.key === "Home") output.scrollLeft = 0;
    else if (event.key === "End") output.scrollLeft = output.scrollWidth;
    else output.scrollLeft += event.key === "ArrowRight" ? 80 : -80;
  });
  svg.removeAttribute("width");
  svg.removeAttribute("height");
  svg.style.maxWidth = "none";
  svg.style.display = "block";
  update();
  if (typeof ResizeObserver === "function") {
    const observer = new ResizeObserver(resize);
    observer.observe(output);
  } else {
    window.addEventListener("resize", resize);
    const observer = new MutationObserver(resize);
    for (let ancestor = figure; ancestor; ancestor = ancestor.parentElement) {
      observer.observe(ancestor, { attributes: true, attributeFilter: ["hidden", "style", "class"] });
    }
  }
  // Static pages keep each figure and its layout observer for their lifetime.
  figure.dataset.mermaidZoom = "ready";
}

async function drawFigure(figure, index) {
  const output = figure.querySelector("[data-mermaid-output]");
  const source = figure.querySelector("[data-mermaid-source]");
  const status = figure.querySelector("[data-mermaid-status]");
  if (!output || !source || !status || figure.dataset.mermaidState) return;
  figure.dataset.mermaidState = "loading";
  const staging = document.createElement("div");
  // SVG measurement requires layout even when the destination slide is hidden.
  staging.style.cssText = "position:fixed;left:-100000px;top:0;width:1024px;visibility:hidden;pointer-events:none";
  staging.setAttribute("aria-hidden", "true");
  document.body.append(staging);
  try {
    const text = source.textContent.trim();
    if (!text) throw new Error("The diagram source is empty");
    const id = `arxiv-mermaid-${index}`;
    const { svg } = await mermaid.render(id, text, staging);
    // Mermaid produces and sanitizes this SVG under securityLevel: strict.
    // Never evaluate source code or bind diagram click directives.
    output.innerHTML = svg;
    const diagram = output.querySelector("svg");
    if (!diagram) throw new Error("No SVG was produced");
    addZoomControls(figure, output, diagram);
    status.textContent = "关系图已绘制；宽图可左右滑动，也可缩放查看或展开源码。";
    figure.dataset.mermaidState = "ready";
  } catch (error) {
    output.replaceChildren();
    status.textContent = "关系图未能绘制，请展开下方源码，结合图注继续阅读。";
    figure.dataset.mermaidState = "error";
    const details = source.closest("details");
    if (details) details.open = true;
    console.warn("A learning diagram could not be rendered:", error);
  } finally {
    staging.remove();
  }
}

async function start() {
  const figures = [...document.querySelectorAll("[data-mermaid]")];
  if (!figures.length) return;
  const style = document.createElement("style");
  style.textContent = `
    [data-mermaid] { min-width: 0; max-width: 100%; }
    [data-mermaid-output] { width: 100%; max-width: 100%; min-width: 0; overflow-x: auto; }
    [data-mermaid-source] { max-width: 100%; overflow-x: auto; }
    .arxiv-mermaid-controls { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 12px 0; }
    .arxiv-mermaid-controls button { min-width: 54px; min-height: 44px; padding: 7px 12px; border: 1px solid #879aa3; border-radius: 7px; background: #fff; color: #173a47; font: inherit; cursor: pointer; }
    .arxiv-mermaid-controls button:disabled { opacity: .45; cursor: default; }
    .arxiv-mermaid-controls button:focus-visible, [data-mermaid-output]:focus-visible { outline: 3px solid #a95317; outline-offset: 3px; }
    .arxiv-mermaid-controls span { font-variant-numeric: tabular-nums; }
    [data-mermaid-state="error"] [data-mermaid-status] { color: #9b361f; }
    @media print { .arxiv-mermaid-controls { display: none; } [data-mermaid-output] svg { max-width: 100% !important; height: auto !important; } }
  `;
  document.head.append(style);
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "strict",
    suppressErrorRendering: true,
    fontFamily: FONT,
    theme: "neutral",
    layout: "dagre",
    htmlLabels: false,
    flowchart: { htmlLabels: false, useMaxWidth: false },
  });
  // Fonts must be ready before Mermaid measures Chinese labels.
  await document.fonts.ready;
  for (const [index, figure] of figures.entries()) await drawFigure(figure, index);
}

if (!globalThis.__arxivMermaidRendererStarted) {
  globalThis.__arxivMermaidRendererStarted = true;
  const run = () => start().catch((error) => {
    for (const figure of document.querySelectorAll("[data-mermaid]")) {
      if (figure.dataset.mermaidState === "ready") continue;
      figure.dataset.mermaidState = "error";
      const status = figure.querySelector("[data-mermaid-status]");
      if (status) status.textContent = "关系图未能初始化，请查看下方源码和图注。";
    }
    console.warn("The learning diagram renderer could not initialize:", error);
  });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run, { once: true });
  else run();
}
