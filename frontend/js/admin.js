console.log("admin.js loaded");

async function loadAdminData() {
  try {
    const res = await fetch("/admin/analytics");
    const data = await res.json();

    document.getElementById("total-users").textContent = data.total_users;
    document.getElementById("active-today").textContent = data.registered_today;
    document.getElementById("total-interactions").textContent = data.total_interactions;
  } catch (err) {
    console.error("Admin analytics failed:", err);
  }
}

document.addEventListener("DOMContentLoaded", loadAdminData);
