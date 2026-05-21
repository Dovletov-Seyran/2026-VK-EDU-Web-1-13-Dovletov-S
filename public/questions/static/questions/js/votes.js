document.addEventListener("DOMContentLoaded", function () {

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie("csrftoken");
    const voteButtons = document.querySelectorAll(".vote-btn");

    voteButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const voteBox = this.closest(".vote-box");
            const type = voteBox.dataset.type;
            const id = parseInt(voteBox.dataset.id);
            const vote = parseInt(this.dataset.vote);

            if (this.classList.contains("active")) {
                return;
            }

            let url;
            let body;
            if (type === "question") {
                url = "/question/vote/";
                body = { question_id: id, vote: vote };
            } else {
                url = "/answer/vote/";
                body = { answer_id: id, vote: vote };
            }

            fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                },
                body: JSON.stringify(body),
            })
                .then(function (response) {
                    if (response.status === 403) {
                        window.location.href = "/login/";
                        return;
                    }
                    return response.json();
                })
                .then(function (data) {
                    if (!data) return;

                    if (data.error) {
                        alert(data.error);
                        return;
                    }

                    const counter = voteBox.querySelector(".vote-count");
                    counter.textContent = data.rating;

                    const allButtons = voteBox.querySelectorAll(".vote-btn");
                    allButtons.forEach(function (btn) {
                        btn.classList.remove("active");
                    });

                    if (data.user_vote !== 0) {
                        const activeBtn = voteBox.querySelector(
                            '.vote-btn[data-vote="' + data.user_vote + '"]'
                        );
                        if (activeBtn) {
                            activeBtn.classList.add("active");
                        }
                    }
                })
                .catch(function (error) {
                    console.error("Ошибка:", error);
                    alert("Произошла ошибка при голосовании");
                });
        });
    });
    const checkboxes = document.querySelectorAll(".correct-checkbox:not([disabled])");

    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener("change", function () {
            const answerId = parseInt(this.dataset.answerId);

            fetch("/answer/accept/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                },
                body: JSON.stringify({ answer_id: answerId }),
            })
                .then(function (response) {
                    if (response.status === 403) {
                        window.location.href = "/login/";
                        return;
                    }
                    return response.json();
                })
                .then(function (data) {
                    if (!data) return;

                    if (data.error) {
                        alert(data.error);
                        checkbox.checked = !checkbox.checked;
                        return;
                    }

                    document.querySelectorAll(".correct-label").forEach(function (label) {
                        label.classList.remove("is-correct");
                    });

                    document.querySelectorAll(".correct-checkbox:not([disabled])").forEach(function (cb) {
                        cb.checked = false;
                    });

                    if (data.accepted) {
                        checkbox.checked = true;
                        checkbox.closest(".correct-label").classList.add("is-correct");
                    }
                })
                .catch(function (error) {
                    console.error("Ошибка:", error);
                    alert("Произошла ошибка");
                    checkbox.checked = !checkbox.checked;
                });
        });
    });
});