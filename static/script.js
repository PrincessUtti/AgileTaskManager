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
    
    //const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
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
    //document.querySelector(".container").classList.add("open-popup");
}

function closePopup() {
    //document.querySelector(".container").classList.remove("open-popup");
    popup.classList.remove("open-popup");
}

function openEditForm(taskId){
    const form = document.getElementById("editForm");
    form.action = `/update_task/${taskId}`;
    openPopup();
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
    if (!timetable) {
        console.error("Timetable element not found.");
        return;
    }

    let draggedItem = null;
    document.querySelectorAll(".task").forEach(task => {
        task.addEventListener("dragstart", (event) => {
            draggedItem = task;
            event.dataTransfer.setData("text/plain", task.id);
        });

        task.addEventListener("dragend", () => {
            draggedItem = null;
        });
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
                //formData.append("end_time", slot.dataset.endTime);

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
                }
            }
        }
    });

    /*
    timetable.addEventListener("drop", async (event) => {
        const slot = event.target.closest(".timeslot");
        if (slot && draggedItem) {
            event.preventDefault();
            slot.classList.remove("drag-over");
            const taskId = draggedItem.id;
            const startTime = slot.dataset.time;
            const endTime = slot.dataset.endTime;
        }
    });
    */
}

/*
timelineCells.addEventListener("drop", async (event) => {
    const taskId = event.dataTransfer.getData("text/plain");
    const startTime = event.target.dataset.time;
    const endTime = event.target.dataset.endTime;

    await fetch(`/update_task_time/${taskId}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({start_time: startTime, end_time: endTime})
    });
});

function calculatedEndTime(startTime, duration) {
    const [hours, minutes] = startTime.split(':').map(Number);
    const startDate = new Date(0, 0, 0, hours, minutes);
    startDate.setMinutes(startDate.getMinutes() + duration);
    const endHours = String(startDate.getHours()).padStart(2, '0');
    const endMinutes = String(startDate.getMinutes()).padStart(2, '0');
    return `${endHours}:${endMinutes}`;
}
*/
/*
timelineCells.addEventListener("drop", async (event) => {
    event.preventDefault();
    const taskId = event.dataTransfer.getData("text/plain");
    const targetCell = event.target.closest(".timeslot");
    const targetDate = targetCell.getAttribute("data-date");

    try {
        const response = await fetch(`/move_task/${taskId}?date=${targetDate}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error("Failed to move task");
        }

        updateCalendar();
    } catch (error) {
        console.error("Error moving task:", error);
    }
});
*/