/*
  Renders the home-page chapter map from the same data used by the sidebar.
  This keeps the landing page, roadmap, and sidebar aligned as the course grows.
*/

(function () {
  const moduleAccents = [
    "module-1",
    "module-2",
    "module-3",
    "module-4",
    "module-5",
    "module-6",
    "module-7",
    "module-8",
  ];

  function escapeHtml(str) {
    return String(str || "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    }[c]));
  }

  function isComplete(chapterId) {
    return !!(window.ACAFEProgress && window.ACAFEProgress.isComplete(chapterId));
  }

  function chapterDescription(chapter, moduleTitle) {
    if (chapter.description) return chapter.description;
    if (chapter.path) {
      return "Live now with lesson, quiz, production exercises, practice bank, interview prep, and project work.";
    }
    return `Planned chapter in ${moduleTitle.replace(/^Module \d+ — /, "")}.`;
  }

  function chapterCta(chapter) {
    if (chapter.path) return "Start learning";
    return "Coming soon";
  }

  function renderChapter(chapter, moduleTitle, accentClass) {
    const root = window.MFE_HOME_ROOT || "";
    const href = chapter.path ? `${root}${chapter.path}` : `${root}docs/curriculum/index.html`;
    const status = chapter.path ? "Live" : "Planned";
    const completeClass = isComplete(chapter.id) ? " chapter-complete" : "";
    const soonClass = chapter.path ? "" : " chapter-card-planned";

    return `
      <a class="chapter-card ${accentClass}${completeClass}${soonClass}" data-chapter-link="${escapeHtml(chapter.id)}" href="${href}">
        <div class="chapter-card-top">
          <span class="chapter-number-orb">${chapter.num}</span>
          <span class="chapter-card-status">${status}</span>
        </div>
        <span class="chapter-card-num">Chapter ${chapter.num}</span>
        <h3>${escapeHtml(chapter.title)}</h3>
        <p>${escapeHtml(chapterDescription(chapter, moduleTitle))}</p>
        <span class="chapter-card-cta"><span>${chapterCta(chapter)}</span></span>
      </a>
    `;
  }

  function renderModule(mod, index) {
    const accentClass = moduleAccents[index] || "module-1";
    const liveCount = mod.chapters.filter((chapter) => chapter.path).length;
    const totalCount = mod.chapters.length;

    return `
      <section class="module-section ${accentClass}">
        <div class="module-section-header">
          <div>
            <span class="module-kicker"><span class="module-dot"></span>Module ${index + 1}</span>
            <h3>${escapeHtml(mod.title.replace(/^Module \d+ — /, ""))}</h3>
            <p>${escapeHtml(mod.summary || "A focused path in the MCP engineering journey.")}</p>
          </div>
          <span class="module-status">${liveCount}/${totalCount} live</span>
        </div>
        <div class="chapter-grid">
          ${mod.chapters.map((chapter) => renderChapter(chapter, mod.title, accentClass)).join("")}
        </div>
      </section>
    `;
  }

  function init() {
    const mount = document.getElementById("chapter-map");
    if (!mount) return;

    const modules = window.ACAFE_MODULES || [];
    mount.innerHTML = modules.map(renderModule).join("");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
