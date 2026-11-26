(() => {
  "use strict";
  const $ = (s) => document.querySelector(s);

  // Build elements with textContent only, so user or server text can never inject HTML.
  function el(tag, text, cls) {
    const e = document.createElement(tag);
    if (text) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  }
  const list = (items) => {
    const ul = el("ul");
    items.forEach((i) => ul.appendChild(el("li", String(i))));
    return ul;
  };
  const block = (title, child) => {
    const d = el("div", null, "ablock");
    d.appendChild(el("h4", title));
    d.appendChild(child);
    return d;
  };

  // Mobile menu
  const toggle = $("#navToggle"), nav = $("#nav");
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  nav.addEventListener("click", (e) => {
    if (e.target.tagName === "A") {
      nav.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });

  const out = $("#answer"), input = $("#question");

  function urgentBanner() {
    const b = el("div", null, "banner");
    b.setAttribute("role", "alert");
    b.appendChild(el("div", "If you or someone else is in danger, call 112 now."));
    const p = el("div");
    [["Women helpline", "181"], ["CHILDLINE", "1098"], ["Cyber fraud", "1930"]].forEach(([n, t], i) => {
      if (i) p.appendChild(document.createTextNode(" · "));
      p.appendChild(document.createTextNode(n + " "));
      const a = el("a", t);
      a.href = "tel:" + t;
      p.appendChild(a);
    });
    b.appendChild(p);
    return b;
  }

  function sourceLinks(sources) {
    const ul = el("ul");
    (sources || []).forEach((s) => {
      if (typeof s.url !== "string" || !s.url.startsWith("https://")) return;
      const li = el("li");
      const a = el("a", s.label);
      a.href = s.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      li.appendChild(a);
      ul.appendChild(li);
    });
    return ul;
  }

  function badge(d) {
    const m = el("div", null, "meta");
    m.appendChild(el("span", d.mode, "tag" + (d.mode === "Live AI" ? " live" : "")));
    if (d.category) m.appendChild(el("span", d.category, "tag"));
    if (d.confidence) m.appendChild(el("span", "Confidence: " + d.confidence, "tag"));
    return m;
  }

  function render(d) {
    out.replaceChildren();
    if (d.urgent) out.appendChild(urgentBanner());
    const card = el("article", null, d.matched ? "answer" : "answer plain");
    card.appendChild(badge(d));
    if (!d.matched) {
      card.appendChild(el("h3", "No good match found"));
      card.appendChild(el("p", d.message));
      card.appendChild(block("Free help", sourceLinks(d.sources)));
    } else {
      card.appendChild(el("h3", d.title));
      card.appendChild(el("p", d.explanation));
      card.appendChild(block("Your rights", list(d.rights)));
      card.appendChild(block("Possible next steps", list(d.next_steps)));
      card.appendChild(block("When to get a professional", el("p", d.professional)));
      card.appendChild(block("Official sources", sourceLinks(d.sources)));
    }
    card.appendChild(el("p", d.disclaimer, "small"));
    out.appendChild(card);
    out.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function ask(q) {
    q = q.trim();
    if (q.length < 3) { input.focus(); return; }
    input.value = q;
    out.replaceChildren(el("p", "Looking for guidance…"));
    out.setAttribute("aria-busy", "true");
    try {
      const r = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      if (!r.ok) throw new Error("bad response");
      render(await r.json());
    } catch (e) {
      out.replaceChildren(el("p", "Something went wrong. Please try again, or call NALSA on 15100.", "error"));
    }
    out.removeAttribute("aria-busy");
  }

  $("#chatForm").addEventListener("submit", (e) => { e.preventDefault(); ask(input.value); });
  $("#homeForm").addEventListener("submit", (e) => { e.preventDefault(); ask($("#homeQ").value); });
  document.querySelectorAll("[data-q]").forEach((b) =>
    b.addEventListener("click", () => ask(b.dataset.q)));
})();
