/* galerie.js — Filtrage par catégorie et Lightbox */

// ── Filtrage par catégorie ────────────────────────────────────────
function filterCat(btn, cat) {
  document.querySelectorAll(".gal-filter").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  document.querySelectorAll(".gal-category").forEach(sec => {
    sec.style.display = (cat === "all" || sec.dataset.cat === cat) ? "" : "none";
  });
}

// ── Lightbox ─────────────────────────────────────────────────────
function openLb(el) {
  const img = el.querySelector("img");
  document.getElementById("lb-img").src       = img.src;
  document.getElementById("lb-caption").textContent = el.dataset.caption;
  document.getElementById("lightbox").classList.add("open");
  document.body.style.overflow = "hidden";
}

function closeLb() {
  document.getElementById("lightbox").classList.remove("open");
  document.body.style.overflow = "";
}

document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") closeLb();
});