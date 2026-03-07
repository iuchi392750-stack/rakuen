'use strict';

// Clock
const clockTimeEl = document.getElementById('clock-time');
const clockDateEl = document.getElementById('clock-date');

const WEEKDAY_NAMES = ['日曜日', '月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日'];

function updateClock() {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, '0');
  const mm = String(now.getMinutes()).padStart(2, '0');
  const ss = String(now.getSeconds()).padStart(2, '0');
  clockTimeEl.textContent = `${hh}:${mm}:${ss}`;
  clockDateEl.textContent = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日 ${WEEKDAY_NAMES[now.getDay()]}`;
}

updateClock();
setInterval(updateClock, 1000);

const today = new Date();
let currentYear = today.getFullYear();
let currentMonth = today.getMonth(); // 0-indexed

const monthTitleEl = document.getElementById('month-title');
const calendarGridEl = document.getElementById('calendar-grid');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const todayBtn = document.getElementById('today-btn');

function render() {
  monthTitleEl.textContent = `${currentYear}年 ${currentMonth + 1}月`;

  calendarGridEl.innerHTML = '';

  const firstDay = new Date(currentYear, currentMonth, 1).getDay(); // 0=Sun
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

  // Previous month's trailing days
  const prevMonthDays = new Date(currentYear, currentMonth, 0).getDate();
  for (let i = firstDay - 1; i >= 0; i--) {
    const cell = createDayCell(prevMonthDays - i, 'other-month');
    calendarGridEl.appendChild(cell);
  }

  // Current month days
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(currentYear, currentMonth, day);
    const dow = date.getDay();
    const isToday =
      day === today.getDate() &&
      currentMonth === today.getMonth() &&
      currentYear === today.getFullYear();

    const classes = [];
    if (isToday) classes.push('today');
    if (dow === 0) classes.push('sunday');
    if (dow === 6) classes.push('saturday');

    const cell = createDayCell(day, ...classes);
    calendarGridEl.appendChild(cell);
  }

  // Next month's leading days to fill remaining cells
  const totalCells = calendarGridEl.children.length;
  const remaining = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7);
  for (let day = 1; day <= remaining; day++) {
    const cell = createDayCell(day, 'other-month');
    calendarGridEl.appendChild(cell);
  }
}

function createDayCell(day, ...classes) {
  const cell = document.createElement('div');
  cell.className = 'day-cell' + (classes.length ? ' ' + classes.join(' ') : '');

  const num = document.createElement('span');
  num.className = 'day-number';
  num.textContent = day;

  cell.appendChild(num);
  return cell;
}

prevBtn.addEventListener('click', () => {
  currentMonth--;
  if (currentMonth < 0) {
    currentMonth = 11;
    currentYear--;
  }
  render();
});

nextBtn.addEventListener('click', () => {
  currentMonth++;
  if (currentMonth > 11) {
    currentMonth = 0;
    currentYear++;
  }
  render();
});

todayBtn.addEventListener('click', () => {
  currentYear = today.getFullYear();
  currentMonth = today.getMonth();
  render();
});

render();
