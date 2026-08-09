/*
  Client-side progress tracker for AI Coding Agents for Everyone.
  Same contract as python-for-everyone: no backend, no accounts, localStorage
  only. A chapter is complete when its quiz reaches a perfect score.
*/

window.ACAFEProgress = (function () {
  const STORAGE_KEY = "acafe-progress-v1";

  function load() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch (e) {
      return {};
    }
  }

  function save(data) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
      /* localStorage unavailable; fail silently */
    }
  }

  function markComplete(chapterId) {
    if (!chapterId) return;
    const data = load();
    data[chapterId] = true;
    save(data);
  }

  function isComplete(chapterId) {
    return !!load()[chapterId];
  }

  function renderBadges() {
    document.querySelectorAll("[data-chapter-link]").forEach((el) => {
      const id = el.getAttribute("data-chapter-link");
      if (isComplete(id) && !el.querySelector(".complete-badge")) {
        el.classList.add("chapter-complete");
        const badge = document.createElement("span");
        badge.className = "complete-badge";
        badge.textContent = "Completed";
        el.appendChild(badge);
      }
    });
  }

  return { markComplete, isComplete, renderBadges };
})();

document.addEventListener("DOMContentLoaded", function () {
  if (window.ACAFEProgress) window.ACAFEProgress.renderBadges();
});

