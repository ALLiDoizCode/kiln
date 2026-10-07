// Quiz component shared by every lesson.
//
// Markup:
//   <section class="quiz" data-lesson="0001">
//     <div class="q">
//       <p>Question text</p>
//       <div class="options">
//         <button class="option">Wrong answer</button>
//         <button class="option" data-correct>Right answer</button>
//       </div>
//       <p class="why">Shown after answering.</p>
//     </div>
//     <div class="result"></div>
//   </section>
//
// Options are shuffled on load, the first click on a question is the answer that
// counts, and the result block offers the outcome as text to paste to the teacher.
(function () {
  function shuffle(parent) {
    const items = Array.from(parent.children);
    for (let i = items.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [items[i], items[j]] = [items[j], items[i]];
    }
    items.forEach((item) => parent.appendChild(item));
  }

  document.querySelectorAll(".quiz").forEach((quiz) => {
    const questions = Array.from(quiz.querySelectorAll(".q"));
    const result = quiz.querySelector(".result");
    const outcome = [];

    questions.forEach((q, index) => {
      const options = q.querySelector(".options");
      shuffle(options);
      options.querySelectorAll("button.option").forEach((button) => {
        button.addEventListener("click", () => {
          if (q.classList.contains("answered")) return;
          const correct = button.hasAttribute("data-correct");
          q.classList.add("answered");
          button.classList.add(correct ? "right" : "wrong");
          options.querySelectorAll("button.option").forEach((other) => {
            other.disabled = true;
            if (other.hasAttribute("data-correct")) other.classList.add("right");
          });
          outcome[index] = { correct, chosen: button.textContent.trim() };
          if (outcome.filter(Boolean).length === questions.length) finish();
        });
      });
    });

    function finish() {
      const score = outcome.filter((o) => o.correct).length;
      const lines = outcome.map(
        (o, i) => `Q${i + 1}: ${o.correct ? "right" : "wrong"} (chose "${o.chosen}")`
      );
      const text = `Lesson ${quiz.dataset.lesson} quiz: ${score}/${questions.length}\n${lines.join("\n")}`;
      result.innerHTML = "";
      const summary = document.createElement("p");
      summary.textContent = `${score} of ${questions.length} on the first try. Paste the result to your teacher so the next lesson starts in the right place.`;
      const copy = document.createElement("button");
      copy.textContent = "Copy result";
      copy.addEventListener("click", () => {
        navigator.clipboard.writeText(text).then(
          () => (copy.textContent = "Copied"),
          () => (copy.textContent = "Copy failed: select the text below")
        );
      });
      const pre = document.createElement("pre");
      pre.textContent = text;
      result.append(summary, copy, pre);
      result.classList.add("shown");
    }
  });
})();
