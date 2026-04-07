/**
 * BioAttend - Main JavaScript
 * Handles dark mode, sidebar, toasts, and UI utilities
 */

// ---- Dark Mode ----
(function() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
})();

document.addEventListener('DOMContentLoaded', () => {
  const toggleBtns = document.querySelectorAll('.theme-toggle, #themeToggle');
  toggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    });
  });

  // ---- Sidebar toggle (mobile) ----
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.getElementById('sidebar');
  const sidebarClose = document.getElementById('sidebarClose');

  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', () => sidebar.classList.add('open'));
  }
  if (sidebarClose && sidebar) {
    sidebarClose.addEventListener('click', () => sidebar.classList.remove('open'));
  }

  // Close sidebar on overlay click
  document.addEventListener('click', (e) => {
    if (sidebar && sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) && e.target !== menuToggle) {
      sidebar.classList.remove('open');
    }
  });

  // ---- Auto-dismiss flash messages ----
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(100%)';
      alert.style.transition = 'all 0.4s';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });
});

// ---- Toast Notification ----
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  const colors = {
    success: '#dcfce7',
    danger: '#fee2e2',
    warning: '#fef3c7',
    info: '#e0f2fe'
  };
  const textColors = {
    success: '#15803d',
    danger: '#b91c1c',
    warning: '#92400e',
    info: '#0369a1'
  };
  toast.className = 'toast';
  toast.style.background = colors[type] || colors.info;
  toast.style.color = textColors[type] || textColors.info;
  toast.style.borderColor = colors[type];
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(20px)';
    toast.style.transition = 'all 0.4s';
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

// ---- Confirm Delete ----
function confirmDelete(msg) {
  return confirm(msg || 'Are you sure you want to delete this?');
}

// ---- Format date display ----
function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
  });
}

// ---- Make top bar show current date ----
document.addEventListener('DOMContentLoaded', () => {
  const dateEl = document.querySelector('.date-display');
  if (dateEl && !dateEl.textContent.trim()) {
    dateEl.textContent = new Date().toLocaleDateString('en-US', {
      weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
    });
  }
});

// ---- Make top bar show current time ----
setInterval(() => {
  const timeEl = document.querySelector('.time-display');
  if (timeEl && !timeEl.textContent.trim()) {
    timeEl.textContent = new Date().toLocaleTimeString('en-US', {
      hour: 'numeric', minute: 'numeric', hour12: true
    });
  }
}, 1000);
const menuToggle=document.getElementById("menuToggle")
const sidebar=document.getElementById("sidebar")
const sidebarClose=document.getElementById("sidebarClose")

menuToggle.onclick=function(){
sidebar.classList.add("active")
}

sidebarClose.onclick=function(){
sidebar.classList.remove("active")
}
document.addEventListener("DOMContentLoaded", function () {

const menuToggle = document.getElementById("menuToggle");
const sidebar = document.getElementById("sidebar");
const sidebarClose = document.getElementById("sidebarClose");

/* OPEN SIDEBAR */
if(menuToggle){
menuToggle.addEventListener("click", function(){
sidebar.classList.toggle("active");
});
}

/* CLOSE SIDEBAR */
if(sidebarClose){
sidebarClose.addEventListener("click", function(){
sidebar.classList.remove("active");
});
}

/* CLOSE SIDEBAR WHEN CLICK OUTSIDE */
document.addEventListener("click", function(e){
if(
sidebar.classList.contains("active") &&
!sidebar.contains(e.target) &&
!menuToggle.contains(e.target)
){
sidebar.classList.remove("active");
}
});

});

function loadNews(){
fetch("/api/news")
.then(r=>r.json())
.then(data=>{
const box=document.getElementById("newsBox");

box.innerHTML=data.map(n=>`
<div class="news-item">
<a href="${n.url}" target="_blank">${n.title}</a>
</div>
`).join("");
});
}

loadNews();
