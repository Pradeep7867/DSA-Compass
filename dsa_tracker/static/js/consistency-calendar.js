document.addEventListener("DOMContentLoaded", () => {
    initializeConsistencyCalendar();
});

function initializeConsistencyCalendar() {
    const heatmapData = window.heatmapData;
    if (!heatmapData || heatmapData.length == 0 ) return;
    renderMonths(heatmapData);
    renderHeatmap(heatmapData);
}
// ── Month Labels ─────────────────────────────────────────────────
function renderMonths(heatmapData) {
    const monthContainer = document.getElementById("heatmap-months");
    monthContainer.innerHTML = "";

    // Find padding offset so first week aligns to Monday
    const firstDate      = new Date(heatmapData[0].date);
    const firstDayOfWeek = (firstDate.getDay() + 6) % 7; // Mon=0 … Sun=6

    // Total week columns = padding + data days, rounded up
    const totalWeeks = Math.ceil((heatmapData.length + firstDayOfWeek) / 7);

    let previousMonth = "";

    for (let w = 0; w < totalWeeks; w++) {
        // Index into heatmapData accounting for the padding offset
        const dataIndex = w * 7 - firstDayOfWeek;
        const label     = document.createElement("span");

        if (dataIndex >= 0 && dataIndex < heatmapData.length) {
            const month = new Date(heatmapData[dataIndex].date)
                .toLocaleString("default", { month: "short" });

            if (month !== previousMonth) {
                label.textContent = month;
                previousMonth     = month;
            } else {
                label.textContent = "";
            }
        }

        monthContainer.appendChild(label);
    }
}

// ── Heatmap Grid ─────────────────────────────────────────────────
function renderHeatmap(heatmapData) {
    const container = document.getElementById("consistency-heatmap");
    container.innerHTML = "";

    // Pad first week so Jan 1 falls on the correct weekday (Mon = top)
    const firstDate      = new Date(heatmapData[0].date);
    const firstDayOfWeek = (firstDate.getDay() + 6) % 7; // Mon=0 … Sun=6

    // --- First (possibly partial) week ---
    const firstWeek = document.createElement("div");
    firstWeek.className = "week-column";

    // Invisible padding cells above the first real day
    for (let pad = 0; pad < firstDayOfWeek; pad++) {
        const empty = document.createElement("div");
        empty.className      = "heatmap-cell";
        empty.style.visibility = "hidden";
        firstWeek.appendChild(empty);
    }

    // Real days in the first partial week
    const firstWeekDays = heatmapData.slice(0, 7 - firstDayOfWeek);
    firstWeekDays.forEach(day => firstWeek.appendChild(createDayCell(day)));
    container.appendChild(firstWeek);

    // --- Remaining full weeks ---
    for (
        let weekStart = 7 - firstDayOfWeek;
        weekStart < heatmapData.length;
        weekStart += 7
    ) {
        const weekData = heatmapData.slice(weekStart, weekStart + 7);
        container.appendChild(createWeekColumn(weekData));
    }
}

function createWeekColumn(weekData) {
    const column = document.createElement("div");
    column.className = "week-column";
    weekData.forEach(day => column.appendChild(createDayCell(day)));
    return column;
}

function createDayCell(day) {
    const cell       = document.createElement("div");
    cell.className   = "heatmap-cell";

    // Priority: revision > focus_met > studied
    if      (day.revision)   cell.classList.add("revision");
    else if (day.focus_met)  cell.classList.add("focus");
    else if (day.studied)    cell.classList.add("studied");

    cell.dataset.date = day.date;

    const status =
        day.revision  ? "Revision"  :
        day.focus_met ? "Focus Met" :
        day.studied   ? "Studied"   : "Not Studied";

    cell.title = `${day.date} — ${status}`;
    return cell;
}
