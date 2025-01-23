document.getElementById("fetch-emails-button").addEventListener("click", async () => {
    const fetchButton = document.getElementById("fetch-emails-button");
    const resultsContainer = document.getElementById("results");
    const loadingState = document.getElementById("loading-state");
    const loadingMessage = document.getElementById("loading-message");

    fetchButton.disabled = true;
    fetchButton.textContent = "Fetching...";
    resultsContainer.innerHTML = "";
    loadingState.classList.remove("hidden");

    const messages = ["Fetching emails...", "Analyzing content...", "Preparing tasks..."];
    let messageIndex = 0;

    const messageInterval = setInterval(() => {
        loadingMessage.textContent = messages[messageIndex];
        messageIndex = (messageIndex + 1) % messages.length;
    }, 1500);

    try {
        const response = await fetch("/fetch-emails", { method: "POST" });
        const data = await response.json();

        clearInterval(messageInterval);
        loadingState.classList.add("hidden");
        fetchButton.disabled = false;
        fetchButton.textContent = "Fetch Emails";

        if (response.ok) {
            resultsContainer.innerHTML = ``;

            data.tasks.forEach((task, index) => {
                const deadline = task.deadline && /^\d{4}-\d{2}-\d{2}$/.test(task.deadline)
                    ? task.deadline
                    : "No deadline";

                const taskDiv = document.createElement("div");
                taskDiv.classList.add("task");
                taskDiv.setAttribute("data-index", index);
                taskDiv.innerHTML = `
                    <label>
                        <input type="checkbox" class="task-checkbox" />
                        <div>
                            <p class="deadline">${deadline}</p>
                            <p class="summary">${task.summary}</p>
                        </div>
                    </label>
                   
                `;
                resultsContainer.appendChild(taskDiv);

            });

            // Checkbox functionality
            document.querySelectorAll(".task-checkbox").forEach(checkbox => {
                checkbox.addEventListener("change", (e) => {
                    const taskDiv = e.target.closest(".task");
                    const summary = taskDiv.querySelector(".summary");
                    if (e.target.checked) {
                        taskDiv.classList.add("completed");
                        summary.classList.add("crossed");
                    } else {
                        taskDiv.classList.remove("completed");
                        summary.classList.remove("crossed");
                    }
                });
            });
        } else {
            resultsContainer.innerHTML = `<p class="error">Error: ${data.error}</p>`;
        }
    } catch (error) {
        clearInterval(messageInterval);
        loadingState.classList.add("hidden");
        fetchButton.disabled = false;
        fetchButton.textContent = "Fetch Emails";
        resultsContainer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
});

// Modal functionality
const modal = document.getElementById("task-modal");
const closeButton = document.querySelector(".close-button");

const showModal = (task) => {
    document.getElementById("modal-from").textContent = task.from;
    document.getElementById("modal-subject").textContent = task.subject;
    document.getElementById("modal-detailed-tasks").textContent = task.detailed_tasks;
    modal.classList.remove("hidden");
};

closeButton.addEventListener("click", () => {
    modal.classList.add("hidden");
});

window.addEventListener("click", (event) => {
    if (event.target === modal) {
        modal.classList.add("hidden");
    }
});
