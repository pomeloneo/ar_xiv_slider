(() => {
  "use strict";
  const slides = [...document.querySelectorAll(".slide")];
  const controls = document.querySelector(".slide-controls");
  const previous = document.querySelector("#previous");
  const next = document.querySelector("#next");
  const select = document.querySelector("#page-select");
  let page = 1;
  function show(focus = false) {
    const requested = Number(location.hash.replace("#slide-", ""));
    page = Number.isInteger(requested) && requested >= 1 && requested <= slides.length ? requested : 1;
    slides.forEach((slide, i) => { slide.hidden = i + 1 !== page; });
    previous.disabled = page === 1;
    next.disabled = page === slides.length;
    select.value = String(page);
    if (focus) slides[page - 1].querySelector("h1").focus({ preventScroll: true });
  }
  function go(number) {
    if (number < 1 || number > slides.length) return;
    history.replaceState(null, "", "#slide-" + number);
    show(true);
    window.scrollTo({ top: 0 });
  }
  previous.addEventListener("click", () => go(page - 1));
  next.addEventListener("click", () => go(page + 1));
  select.addEventListener("change", () => go(Number(select.value)));
  document.addEventListener("keydown", (event) => {
    if (event.target.closest("button,a,input,select,textarea,[contenteditable],[data-mermaid-output]")) return;
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
      event.preventDefault();
      go(page + (event.key === "ArrowRight" ? 1 : -1));
    }
  });
  window.addEventListener("hashchange", () => show(true));
  controls.hidden = false;
  show();
})();
