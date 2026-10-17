const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]") ? document.querySelector("[name=csrfmiddlewaretoken]").value : "";

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            ...(options.headers || {})
        },
        credentials: "same-origin"
    });
    let data = null;
    if (response.status !== 204) {
        data = await response.json().catch(() => null);
    }
    if (!response.ok) {
        let errorText = "Ошибка выполнения запроса";
        if (data) {
            errorText = typeof data === 'object' ? JSON.stringify(data) : data;
        }
        throw new Error(errorText);
    }
    return data;
}

const categorySelect = document.getElementById("category");
const form = document.getElementById("ticket-form");
const titleInput = document.getElementById("title");
const message = document.getElementById("message");
const list = document.getElementById("tickets-list");
const loading = document.getElementById("loading");
const filter = document.getElementById("status-filter");

function showMessage(text, isError = false) {
    message.textContent = text;
    message.className = "alert " + (isError ? "alert-danger" : "alert-success") + " mb-3";
}

async function loadCategories() {
    const categories = await apiRequest("/tickets/api/categories/");
    categorySelect.replaceChildren();
    for (const category of categories) {
        const option = document.createElement("option");
        option.value = category.id;
        option.textContent = category.name;
        categorySelect.append(option);
    }
}

async function loadTickets() {
    if (!loading) return;
    loading.hidden = false;
    const params = new URLSearchParams();
    if (filter.value) params.set("status", filter.value);

    const url = "/tickets/api/tickets/" + (params.toString() ? "?" + params.toString() : "");
    try {
        const tickets = await apiRequest(url);
        list.replaceChildren();
        if (tickets.length === 0) {
            list.innerHTML = "<p class='text-muted'>Заявки не найдены</p>";
            return;
        }
        for (const ticket of tickets) {
            const row = document.createElement("div");
            row.className = "d-flex justify-content-between align-items-center border-bottom py-3 gap-3";

            const info = document.createElement("div");
            info.innerHTML = `<strong>${ticket.title}</strong> <span class="text-muted">(${ticket.category_name})</span>`;

            const controls = document.createElement("div");
            controls.className = "d-flex gap-2 align-items-center";

            const statusBadge = document.createElement("span");
            statusBadge.className = "badge bg-blue-lt";
            statusBadge.textContent = ticket.status;
            controls.append(statusBadge);

            // Кнопка перехода к следующему статусу
            if (ticket.status === "new") {
                const btn = document.createElement("button");
                btn.className = "btn btn-sm btn-outline-warning";
                btn.textContent = "В работу";
                btn.onclick = () => changeStatus(ticket.id, "progress");
                controls.append(btn);
            } else if (ticket.status === "progress") {
                const btn = document.createElement("button");
                btn.className = "btn btn-sm btn-outline-success";
                btn.textContent = "Завершить";
                btn.onclick = () => changeStatus(ticket.id, "done");
                controls.append(btn);
            }

            // Кнопка удаления
            const deleteBtn = document.createElement("button");
            deleteBtn.className = "btn btn-sm btn-outline-danger";
            deleteBtn.textContent = "Удалить";
            deleteBtn.onclick = () => deleteTicket(ticket.id, ticket.title);
            controls.append(deleteBtn);

            row.append(info, controls);
            list.append(row);
        }
    } catch (error) {
        showMessage("Ошибка загрузки заявок: " + error.message, true);
    } finally {
        loading.hidden = true;
    }
}

async function changeStatus(ticketId, newStatus) {
    try {
        await apiRequest(`/tickets/api/tickets/${ticketId}/`, {
            method: "PATCH",
            body: JSON.stringify({ status: newStatus })
        });
        showMessage("Статус обновлен");
        await loadTickets();
    } catch (error) {
        showMessage("Ошибка изменения статуса: " + error.message, true);
    }
}

async function deleteTicket(ticketId, ticketTitle) {
    if (!confirm(`Удалить заявку «${ticketTitle}»?`)) return;
    try {
        await apiRequest(`/tickets/api/tickets/${ticketId}/`, { method: "DELETE" });
        showMessage("Заявка удалена");
        await loadTickets();
    } catch (error) {
        showMessage("Ошибка удаления: " + error.message, true);
    }
}

if (form) {
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            await apiRequest("/tickets/api/tickets/", {
                method: "POST",
                body: JSON.stringify({
                    title: titleInput.value,
                    category: Number(categorySelect.value)
                })
            });
            titleInput.value = "";
            showMessage("Заявка успешно создана");
            await loadTickets();
        } catch (error) {
            showMessage("Ошибка создания: " + error.message, true);
        }
    });
}

if (filter) filter.addEventListener("change", loadTickets);

async function init() {
    try {
        await loadCategories();
        await loadTickets();
    } catch (e) {
        console.error(e);
    }
}

init();