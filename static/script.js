function initCalendar() {
    const monthYearElement = document.getElementById("monthYear");
    const datesElement = document.getElementById("dates");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");

    let currentDate = new Date();

    const updateCalendar = () => {
        const month = currentDate.getMonth();
        const year = currentDate.getFullYear();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startDay = (firstDay.getDay() + 6) % 7; //firstdayindex // === 0 ? 6 : firstDay.getDay() - 1; // Adjust for Monday start
        const endDay = (lastDay.getDay() + 6) % 7; //lastdayindex// === 0 ? 6 : lastDay.getDay() - 1; // Adjust for Monday start
    
        const monthYearString = currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });
        monthYearElement.textContent = monthYearString;

        let datesHTML = "";
        
        for (let i=0; i < startDay; i++) {
            const prevDate = new Date(year, month, -i);
            datesHTML += `<div class="date inactive">${prevDate.getDate()}</div>`;
        //datesHTML += `<div class="date prev-date">${prevDate.getDate()}</div>`;
        }
    
        for (let i = 1; i <= daysInMonth; i++) {
            const date = new Date(year, month, i);
            //const isToday = date.toDateString() === new Date().toDateString() ? "active" : "";
            const isToday = date.toDateString() === new Date().toDateString();
            datesHTML += `<div class="date ${isToday ? 'today' : ''}" data-date="${year}-${month+1}-${i}">${i}</div>`;
        }
        
        for (let i = 1; i <= 6 - endDay; i++) {
            const nextDate = new Date(year, month + 1, i);
            datesHTML += `<div class="date inactive">${nextDate.getDate()}</div>`;
            //datesHTML += `<div class="date next-date">${nextDate.getDate()}</div>`;
        }

        datesElement.innerHTML = datesHTML;

        document.querySelectorAll(".date").forEach(d => {
            const date = d.getAttribute("data-date");

            if (date){
                fetch(`/tasks_by_date?date=${date}`)
                .then(response => response.json())
                .then(data => {
                    if (data.tasks && data.tasks.length > 0){
                        d.classList.add("has-task")
                    }
                })
            }
            
            
            d.addEventListener("click", () => {
                const date = d.getAttribute("data-date");

                /*openPopup();*/

                fetch(`/tasks_by_date?date=${date}`)
                .then(response => response.json())
                .then(data => {
                    const box = document.getElementById("taskBox");
                    box.innerHTML = "";
                    
                    //handles the case where no task exists
                    if (!data.tasks || data.tasks.length ===0) {
                        box.innerHTML = "";
                        return;
            
                    }

                    box.innerHTML = `<h3> Tasks for ${date} </h3>`;
                    data.tasks.forEach (t => {
                        box.innerHTML += `<p>${t.title} - ${t.description} <button class="editBtn" data-id="${t.id}">EDIT TASK</button></p>`;
                    });

                    document.querySelectorAll(".editBtn").forEach(btn =>{
                        btn.addEventListener("click", () => {
                            const id = btn.getAttribute("data-id");
                            openEditForm(id);
                        });
                    });
                });
            })
        });
    };

    prevBtn.addEventListener("click", () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        updateCalendar();
    })

    nextBtn.addEventListener("click", () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        updateCalendar();
    })

    updateCalendar();
}

let popup = document.getElementById("popup");

function openPopup() {
    popup.classList.add("open-popup");
}

function closePopup() {
    popup.classList.remove("open-popup");
}

function openEditForm(taskId){
    const form = document.getElementById("editForm");
    form.action = `/update_task/${taskId}`;
    const editPopup = document.getElementById("editPopup");
    if (editPopup) {
        editPopup.classList.add("open-popup");
    } else {
        openPopup();
    }
}

function closeEditPopup() {
    const editPopup = document.getElementById("editPopup");
    if (editPopup) {
        editPopup.classList.remove("open-popup");
    } else {
        closePopup();
    }
}

function navBar(containerId){
    fetch("/nav")
    .then(response => response.text())
    .then(html => {
        document.getElementById(containerId).innerHTML=html;

        const menuIcon = document.getElementById("menu-icon");
        const overlayMenu = document.getElementById("overlay-menu");

        menuIcon.addEventListener("click", () => {
            overlayMenu.style.display = "block";
        });

        overlayMenu.addEventListener("mouseleave", () => {
            overlayMenu.style.display = "none";
        });
    })

    .catch(err => console.error("Navbar failed to load: ", err));
}

function initDragAndDrop() {
    const timetable = document.getElementById("timetable");
    const unscheduledContainer = document.getElementById("unscheduledTasks");

    if (!timetable) {
        console.error("Timetable element not found.");
        return;
    }

    let draggedItem = null;

    document.addEventListener("dragstart", (event) => {
        const task = event.target.closest(".task, .subtask");
        if (task) {
            draggedItem = task;
            event.dataTransfer.setData("text/plain", task.id);
        }
    });

    document.addEventListener("dragend", (event) => {
        if (event.target.closest(".task, .subtask")) {
            draggedItem = null;
        }
    });

    timetable.addEventListener("dragover", (event) => {
        const slot = event.target.closest(".timeslot"); /*every timeline cell could change to timeslot*/ 
        if (slot) {
            event.preventDefault();
            slot.classList.add("drag-over");
        }
    });

    timetable.addEventListener("dragleave", (event) => {
        const slot = event.target.closest(".timeslot");
        if (slot) {
            slot.classList.remove("drag-over");
        }
    });

    timetable.addEventListener("drop", async e => {
        const slot = e.target.closest(".timeslot");
        if (slot) {
            e.preventDefault();
            slot.classList.remove("drag-over");

            const taskId = e.dataTransfer.getData("text/plain");
            const dragged = document.getElementById(taskId) || draggedItem;

            if (dragged) {
                slot.appendChild(dragged);

                const formData = new FormData();
                formData.append("start_time", slot.dataset.time);

                if (slot.dataset.date) {
                    formData.append("due_date", slot.dataset.date);
                }

                const response = await fetch(`/update_task_time/${taskId}`, {
                    method: "POST",
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();

                    const startEl = dragged.querySelector(".task-start");
                    const endEl = dragged.querySelector(".task-end");
                    const dueEl = dragged.querySelector(".task-due");

                    if (startEl && data.start_time) {
                        startEl.textContent = `Start Time: ${data.start_time}`;
                    }
                    if (endEl && data.end_time) {
                        endEl.textContent = `End Time: ${data.end_time}`;
                    }
                    if (dueEl && data.due_date) {
                        dueEl.textContent = `Due Date: ${data.due_date}`;
                    }

                    const totalMinutes = (data.tokens || 1) * (data.token_duration || 10);
                    dragged.style.height = `${(totalMinutes/30)*40}px`
                }
            }
        }
    });

    if (unscheduledContainer) {
        unscheduledContainer.addEventListener("dragover", (event) => event.preventDefault());

        unscheduledContainer.addEventListener("drop", async (event) => {
            event.preventDefault();

            const taskId = event.dataTransfer.getData("text/plain");
            const dragged = document.getElementById(taskId) || draggedItem;

            if (dragged) {
                unscheduledContainer.appendChild(dragged);

                dragged.style.height = "auto";
                
                // Post empty payload to update backend database fields to NULL
                await fetch(`/update_task_time/${taskId}`, {
                    method: "POST",
                    body: new FormData()
                });
            }
        });
    }
}

