console.log("admin.js loaded");

async function loadAdminAnalytics() {
  try {
    const res = await fetch("/admin/analytics");
    const data = await res.json();

    const totalUsers = document.getElementById("total-users");
    const todayUsers = document.getElementById("today-users");
    const totalInteractions = document.getElementById("total-interactions");
    const topSkill = document.getElementById("top-skill");

    if (totalUsers) totalUsers.textContent = data.total_users || 0;
    if (todayUsers) todayUsers.textContent = data.registered_today || 0;
    if (totalInteractions) totalInteractions.textContent = data.total_interactions || 0;
    if (topSkill) topSkill.textContent = (data.top_skills || []).map(s => s.skill).join(", ") || "-";
  } catch (err) {
    console.error("Admin analytics failed:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadAdminAnalytics();
  // Keep admin stats fresh so new registrations appear without manual reload.
  setInterval(loadAdminAnalytics, 60000);
});
