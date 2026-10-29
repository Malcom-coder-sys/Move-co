/* dashboard.js — Graphes Chart.js du tableau de bord admin
   Les données sont injectées depuis Django via json_script (#chart-data) */

document.addEventListener("DOMContentLoaded", function () {

  const data = JSON.parse(document.getElementById("chart-data").textContent);
  const CHART_LABELS    = data.labels;
  const CHART_VALUES    = data.values;
  const SERVICES_LABELS = data.services_labels;
  const SERVICES_VALUES = data.services_values;

  // ── Graphe évolution (courbe 30 jours) ───────────────────────────
  const ctxLine = document.getElementById("chartEvolution");
  if (ctxLine) {
    const ctx = ctxLine.getContext("2d");
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, "rgba(255,107,26,0.35)");
    gradient.addColorStop(1, "rgba(255,107,26,0)");

    new Chart(ctx, {
      type: "line",
      data: {
        labels: CHART_LABELS,
        datasets: [{
          label: "Demandes",
          data: CHART_VALUES,
          borderColor: "#ff6b1a",
          backgroundColor: gradient,
          borderWidth: 2.5,
          pointRadius: 3,
          pointBackgroundColor: "#ff6b1a",
          pointHoverRadius: 6,
          tension: 0.4,
          fill: true,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#0d1526",
            borderColor: "rgba(255,107,26,0.3)",
            borderWidth: 1,
            titleColor: "#f0f4ff",
            bodyColor: "#ff6b1a",
            callbacks: { label: ctx => ` ${ctx.parsed.y} demande(s)` }
          }
        },
        scales: {
          x: {
            ticks: { color: "#8a97b0", font: { size: 10 }, maxTicksLimit: 8 },
            grid:  { color: "rgba(255,255,255,0.04)" }
          },
          y: {
            beginAtZero: true,
            ticks: { color: "#8a97b0", font: { size: 11 }, stepSize: 1 },
            grid:  { color: "rgba(255,255,255,0.04)" }
          }
        }
      }
    });
  }

  // ── Graphe répartition par service (donut) ────────────────────────
  const ctxDoughnut = document.getElementById("chartServices");
  if (ctxDoughnut) {
    new Chart(ctxDoughnut.getContext("2d"), {
      type: "doughnut",
      data: {
        labels: SERVICES_LABELS.length ? SERVICES_LABELS : ["Aucune donnée"],
        datasets: [{
          data: SERVICES_VALUES.length ? SERVICES_VALUES : [1],
          backgroundColor: ["#ff6b1a", "#f59e0b", "#10b981", "#3b82f6"],
          borderColor: "#0d1526",
          borderWidth: 3,
          hoverOffset: 8,
        }]
      },
      options: {
        responsive: true,
        cutout: "65%",
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: "#8a97b0", font: { size: 11 }, padding: 14, boxWidth: 12 }
          },
          tooltip: {
            backgroundColor: "#0d1526",
            borderColor: "rgba(255,107,26,0.3)",
            borderWidth: 1,
            titleColor: "#f0f4ff",
            bodyColor: "#ff6b1a",
          }
        }
      }
    });
  }

});