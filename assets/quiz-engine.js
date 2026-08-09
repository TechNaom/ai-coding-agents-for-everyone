/*
  Quiz engine for AI Coding Agents for Everyone.
  Same page contract as python-for-everyone: fill-in-the-blank rows and
  multiple-choice questions, with progress completion on perfect score.
*/

(function () {
  function normalize(value) {
    return value.trim().toLowerCase();
  }

  function isCorrect(input) {
    const accepted = (input.dataset.answers || "")
      .split(",")
      .map(normalize)
      .filter(Boolean);
    return accepted.includes(normalize(input.value));
  }

  function checkOne(row) {
    const input = row.querySelector(".fib-blank");
    const feedback = row.querySelector(".fib-feedback");
    if (!input) return null;

    const correct = isCorrect(input);
    input.classList.remove("correct", "incorrect");
    input.classList.add(correct ? "correct" : "incorrect");
    input.setAttribute("aria-invalid", correct ? "false" : "true");

    if (feedback) {
      feedback.textContent = correct ? "Correct" : "Try again";
      feedback.classList.remove("correct", "incorrect");
      feedback.classList.add(correct ? "correct" : "incorrect");
    }
    return correct;
  }

  function answerMcq(question, chosenOption) {
    if (question.classList.contains("answered")) return;
    const options = question.querySelectorAll(".mcq-option");
    const feedback = question.querySelector(".mcq-feedback");
    const chosenCorrect = chosenOption.dataset.correct === "true";

    options.forEach((option) => {
      option.disabled = true;
      if (option === chosenOption) {
        option.classList.add(chosenCorrect ? "correct" : "incorrect");
      } else if (option.dataset.correct === "true" && !chosenCorrect) {
        option.classList.add("reveal-correct");
      }
    });

    question.classList.add("answered", chosenCorrect ? "correct" : "incorrect");
    if (feedback) {
      feedback.textContent = chosenCorrect ? "Correct" : "Not quite - correct answer highlighted above";
      feedback.classList.add(chosenCorrect ? "correct" : "incorrect");
    }
  }

  function updateScore() {
    const scoreEl = document.getElementById("quiz-score");
    const fillEl = document.getElementById("quiz-progress-fill");
    const celebrationEl = document.getElementById("quiz-celebration");
    const fibRows = document.querySelectorAll(".fib-row");
    const mcqQuestions = document.querySelectorAll(".mcq-question");
    const total = fibRows.length + mcqQuestions.length;
    let correctCount = 0;

    fibRows.forEach((row) => {
      const input = row.querySelector(".fib-blank");
      if (input && input.classList.contains("correct")) correctCount += 1;
    });

    mcqQuestions.forEach((question) => {
      if (question.classList.contains("correct")) correctCount += 1;
    });

    if (scoreEl) scoreEl.textContent = `Score: ${correctCount} / ${total}`;
    if (fillEl) fillEl.style.width = `${total ? Math.round((correctCount / total) * 100) : 0}%`;

    const perfectScore = total > 0 && correctCount === total;
    if (celebrationEl) celebrationEl.classList.toggle("show", perfectScore);
    if (perfectScore && window.ACAFEProgress) {
      window.ACAFEProgress.markComplete(document.body.dataset.chapterId);
    }
  }

  function wireUp() {
    document.querySelectorAll(".fib-row").forEach((row) => {
      const input = row.querySelector(".fib-blank");
      const button = row.querySelector(".check-btn");
      if (!input || !button) return;

      button.addEventListener("click", () => {
        checkOne(row);
        updateScore();
      });

      input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          checkOne(row);
          updateScore();
        }
      });
    });

    document.querySelectorAll(".mcq-question").forEach((question) => {
      question.querySelectorAll(".mcq-option").forEach((option) => {
        option.addEventListener("click", () => {
          answerMcq(question, option);
          updateScore();
        });
      });
    });

    const checkAllBtn = document.getElementById("check-all-btn");
    if (checkAllBtn) {
      checkAllBtn.addEventListener("click", () => {
        document.querySelectorAll(".fib-row").forEach(checkOne);
        updateScore();
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wireUp);
  } else {
    wireUp();
  }
})();

