/*
  Renders the persistent chapter sidebar from assets/chapters-data.js.
  Mirrors the python-for-everyone navigation contract.
*/

(function () {
  function escapeHtml(str) {
    return str.replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  function isComplete(chapterId) {
    return !!(window.ACAFEProgress && window.ACAFEProgress.isComplete(chapterId));
  }

  function buildSidebarHtml(root, activeChapter) {
    const modules = window.ACAFE_MODULES || [];
    let html = `<a href="${root}index.html" class="sidebar-brand">AI Coding Agents for Everyone</a>`;
    html += `<span class="sidebar-subtitle">Visual, testable, engineering-first GenAI learning</span>`;

    modules.forEach((mod, index) => {
      const containsActive = mod.chapters.some((c) => c.id === activeChapter);
      const isOpen = containsActive || index === 0 ? "open" : "";
      const liveCount = mod.chapters.filter((c) => c.path).length;
      const totalCount = mod.chapters.length;
      html += `<details class="sidebar-module" ${isOpen}><summary><span>${escapeHtml(mod.title)}</span><em>${liveCount}/${totalCount}</em></summary>`;
      html += `<ul class="sidebar-chapter-list">`;
      mod.chapters.forEach((ch) => {
        const activeClass = ch.id === activeChapter ? "active" : "";
        if (ch.path) {
          const check = isComplete(ch.id) ? `<span class="sidebar-check">✓</span>` : `<span>${ch.num}.</span>`;
          html += `<li class="${activeClass} live"><a href="${root}${ch.path}">${check} <span>${escapeHtml(ch.title)}</span><em>Live</em></a>`;
          if (ch.subtopics && ch.subtopics.length) {
            html += `<ul class="sidebar-subtopic-list">`;
            ch.subtopics.forEach((sub) => {
              html += `<li><a href="${root}${ch.path}#${sub.id}">${escapeHtml(sub.title)}</a></li>`;
            });
            html += `</ul>`;
          }
          html += `</li>`;
        } else {
          html += `<li class="planned"><span class="soon"><span>${ch.num}. ${escapeHtml(ch.title)}</span><em>Soon</em></span></li>`;
        }
      });
      html += `</ul>`;
      if (mod.examPath) {
        html += `<a class="sidebar-exam-link" href="${root}${mod.examPath}">Module Written Exam</a>`;
      }
      html += `</details>`;
    });

    return html;
  }

  function wireMobileToggle() {
    const sidebar = document.getElementById("chapter-sidebar");
    const toggle = document.getElementById("sidebar-toggle");
    const scrim = document.getElementById("sidebar-scrim");
    if (!sidebar || !toggle || !scrim) return;

    function open() {
      sidebar.classList.add("open");
      scrim.classList.add("show");
      toggle.setAttribute("aria-expanded", "true");
    }

    function close() {
      sidebar.classList.remove("open");
      scrim.classList.remove("show");
      toggle.setAttribute("aria-expanded", "false");
    }

    toggle.addEventListener("click", () => {
      sidebar.classList.contains("open") ? close() : open();
    });
    scrim.addEventListener("click", close);
  }

  function init() {
    const sidebar = document.getElementById("chapter-sidebar");
    if (!sidebar) return;
    const root = sidebar.getAttribute("data-root") || "";
    const activeChapter = document.body.getAttribute("data-active-chapter") || "";
    sidebar.innerHTML = buildSidebarHtml(root, activeChapter);
    wireMobileToggle();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
