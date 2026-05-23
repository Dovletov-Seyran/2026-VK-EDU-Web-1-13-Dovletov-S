document.addEventListener("DOMContentLoaded", function () {
    const match = window.location.pathname.match(/\/question\/(\d+)\//);
    if (!match) return;

    const questionId = match[1];
    const channel = "questions:question_" + questionId;

    const urlParams = new URLSearchParams(window.location.search);
    const currentPage = parseInt(urlParams.get("page")) || 1;

    // 1. Получаем JWT-токен от Django
    fetch("/centrifugo/token/")
        .then((response) => response.json())
        .then((data) => {
            // 2. Подключаемся к Centrifugo
            const centrifuge = new Centrifuge(CENTRIFUGO_WS_URL, {
                token: data.token,
            });

            // 3. Подписываемся на канал этого вопроса
            const sub = centrifuge.newSubscription(channel);

            // 4. Когда приходит новое сообщение (новый ответ)
            sub.on("publication", function (ctx) {
                const answer = ctx.data;

                if (currentPage === 1) {
                    insertAnswer(answer);
                } else {
                    alert("Появился новый ответ! Перейдите на первую страницу, чтобы увидеть его.");
                }
            });

            sub.subscribe();
            centrifuge.connect();
        });

    function insertAnswer(answer) {
        const answersSection = document.getElementById("answers");
        if (!answersSection) return;

        const emptyMessage = answersSection.nextElementSibling;
        if (emptyMessage && emptyMessage.tagName === "P" && emptyMessage.textContent.includes("Пока нет")) {
            emptyMessage.remove();
        }

        // Создаём HTML нового ответа
        const answerHTML = `
      <div class="white-card" id="answer-${answer.answer_id}">
        <div class="d-flex gap-3 align-items-start">
          <div class="vote-box flex-shrink-0" data-type="answer" data-id="${answer.answer_id}">
            <button disabled>▲</button>
            <span class="vote-count">0</span>
            <button disabled>▼</button>
          </div>
          <div class="q-avatar flex-shrink-0">
            <img src="${answer.avatar_url}" width="24" height="24"
              style="border-radius: 4px; object-fit: cover;">
          </div>
          <div class="flex-grow-1">
            <p class="answer-text">${answer.text}</p>
            <span class="q-time">answered just now</span>
          </div>
        </div>
      </div>
    `;

        answersSection.insertAdjacentHTML("afterend", answerHTML);
    }
});