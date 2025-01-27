// Global Constants
const fetchButton = document.getElementById("fetch-emails-button");
const resultsContainer = document.getElementById("results");
const loadingState = document.getElementById("loading-state");
const loadingMessage = document.getElementById("loading-message");
const modal = document.getElementById("task-modal");
const closeButton = document.querySelector(".close-button");

// Utility Functions
const setLoadingState = (isLoading, messages) => {
    if (isLoading) {
        fetchButton.disabled = true;
        fetchButton.textContent = "Fetching...";
        resultsContainer.innerHTML = "";
        loadingState.classList.remove("hidden");

        let messageIndex = 0;
        return setInterval(() => {
            loadingMessage.textContent = messages[messageIndex];
            messageIndex = (messageIndex + 1) % messages.length;
        }, 1500);
    } else {
        fetchButton.disabled = false;
        fetchButton.textContent = "Fetch Emails";
        loadingState.classList.add("hidden");
    }
};

const showError = (message) => {
    resultsContainer.innerHTML = `<p class="error">Error: ${message}</p>`;
};

const createTaskElement = (task, index) => {
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
        <button class="view-details-button">View Details</button>
    `;

    // Add event listener for "View Details" button
    const viewDetailsButton = taskDiv.querySelector(".view-details-button");
    viewDetailsButton.addEventListener("click", () => showModal({
        from: task.from || "Unknown sender",
        subject: task.subject || "No subject",
        detailed_tasks: task.detailed_tasks || "No additional details."
    }));

    return taskDiv;
};

const setupTaskCheckboxes = () => {
    document.querySelectorAll(".task-checkbox").forEach(checkbox => {
        checkbox.addEventListener("change", (e) => {
            const taskDiv = e.target.closest(".task");
            const summary = taskDiv.querySelector(".summary");
            taskDiv.classList.toggle("completed", e.target.checked);
            summary.classList.toggle("crossed", e.target.checked);
        });
    });
};

const showModal = (task) => {
    document.getElementById("modal-from").textContent = task.from;
    document.getElementById("modal-subject").textContent = task.subject;
    document.getElementById("modal-detailed-tasks").textContent = task.detailed_tasks;
    modal.classList.remove("hidden");
};

const closeModal = () => {
    modal.classList.add("hidden");
};

// Event Listeners
fetchButton.addEventListener("click", async () => {
    const messages = ["Fetching emails...", "Analyzing content...", "Preparing tasks..."];
    const messageInterval = setLoadingState(true, messages);

    try {
        const response = await fetch("/fetch-emails", { method: "POST" });
        const data = await response.json();

        clearInterval(messageInterval);
        setLoadingState(false);

        if (response.ok) {
            resultsContainer.innerHTML = "";
            data.tasks.forEach((task, index) => {
                const taskElement = createTaskElement(task, index);
                resultsContainer.appendChild(taskElement);
            });
            setupTaskCheckboxes();
        } else {
            showError(data.error);
        }
    } catch (error) {
        clearInterval(messageInterval);
        setLoadingState(false);
        showError(error.message);
    }
});

closeButton.addEventListener("click", closeModal);

window.addEventListener("click", (event) => {
    if (event.target === modal) {
        closeModal();
    }
});
