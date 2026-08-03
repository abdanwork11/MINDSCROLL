(function () {
  const canvas = document.getElementById("bgCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let W, H, particles = [];
  const COLORS = ["#0ea5e9", "#38bdf8", "#7dd3fc"];
  const COUNT = 55;
  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  function random(min, max) { return Math.random() * (max - min) + min; }
  function init() {
    particles = [];
    for (let i = 0; i < COUNT; i++) {
      particles.push({ x: random(0, W), y: random(0, H), r: random(1, 3.5), dx: random(-0.3, 0.3), dy: random(-0.4, -0.1), alpha: random(0.2, 0.6), color: COLORS[Math.floor(Math.random() * COLORS.length)] });
    }
  }
  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach((p) => {
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color; ctx.globalAlpha = p.alpha; ctx.fill();
      p.x += p.dx; p.y += p.dy;
      if (p.y < -10) { p.y = H + 10; p.x = random(0, W); }
      if (p.x < -10) p.x = W + 10;
      if (p.x > W + 10) p.x = -10;
    });
    ctx.globalAlpha = 1;
    requestAnimationFrame(draw);
  }
  resize(); init(); draw();
  window.addEventListener("resize", () => { resize(); init(); });
})();

document.querySelectorAll(".q-block").forEach((el, i) => {
  el.style.animationDelay = `${i * 0.06}s`;
});

(function () {
  const form = document.getElementById("mainForm");
  if (!form) return;
  const blocks = form.querySelectorAll(".q-block");
  const total = blocks.length;
  const doneCount = document.getElementById("doneCount");
  const fillEl = document.getElementById("progressFill");

  function countAnswered() {
    let done = 0;
    blocks.forEach((block) => {
      if (block.dataset.type === "menit") {
        const inp = block.querySelector(".menit-input");
        if (inp && inp.value && parseInt(inp.value) > 0) done++;
      } else {
        if (block.querySelector('input[type="radio"]:checked')) done++;
      }
    });
    return done;
  }

  function update() {
    const done = countAnswered();
    if (doneCount) doneCount.textContent = done;
    if (fillEl) fillEl.style.width = (done / total) * 100 + "%";
  }

  form.querySelectorAll('input[type="radio"]').forEach((r) => {
    r.addEventListener("change", () => {
      update();
      r.closest(".q-block")?.classList.add("answered");
    });
  });

  form.querySelectorAll(".menit-input").forEach((inp) => {
    inp.addEventListener("input", () => {
      update();
      if (inp.value && parseInt(inp.value) > 0) inp.closest(".q-block")?.classList.add("answered");
      else inp.closest(".q-block")?.classList.remove("answered");
    });
  });

  function showAlert() {
    const existing = document.getElementById("unanswered-alert");
    if (existing) return;
    const alertEl = document.createElement("div");
    alertEl.id = "unanswered-alert";
    alertEl.textContent = "Masih ada pertanyaan yang belum dijawab!";
    alertEl.style.cssText = "position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);background:#fee2e2;color:#b91c1c;border:1.5px solid #fca5a5;padding:0.85rem 1.5rem;border-radius:999px;font-size:0.9rem;font-weight:600;z-index:999;box-shadow:0 4px 20px rgba(0,0,0,0.1);white-space:nowrap;";
    document.body.appendChild(alertEl);
    setTimeout(() => alertEl.remove(), 3000);
  }

  function cekUnanswered() {
    for (const block of blocks) {
      let unanswered = false;
      if (block.dataset.type === "menit") {
        const inp = block.querySelector(".menit-input");
        if (!inp || !inp.value || parseInt(inp.value) <= 0) unanswered = true;
      } else {
        const radio = block.querySelector('input[type="radio"]');
        if (radio && !form.querySelector('input[name="' + radio.name + '"]:checked')) unanswered = true;
      }
      if (unanswered) {
        block.scrollIntoView({ behavior: "smooth", block: "center" });
        block.style.outline = "2px solid #ef4444";
        block.style.borderRadius = "8px";
        setTimeout(() => { block.style.outline = ""; }, 2000);
        showAlert();
        return true;
      }
    }
    return false;
  }

  const submitBtn = document.getElementById("submitBtn");
  if (submitBtn) {
    submitBtn.addEventListener("click", function (e) {
      if (cekUnanswered()) {
        e.preventDefault();
      }
    });
  }
})();

(function () {
  const fill = document.querySelector(".meter-fill");
  if (!fill) return;
  const target = fill.style.width;
  fill.style.width = "0%";
  requestAnimationFrame(() => {
    requestAnimationFrame(() => { fill.style.width = target; });
  });
})();
