console.log("script.js loaded");

// ================= HELPERS =================

function getUserId() {
  return localStorage.getItem("user_id");
}

function getToken() {
  return localStorage.getItem("access_token");
}

function showError(msg) {
  alert(msg);
}

// ================= REGISTER =================

async function registerUser() {

  const full_name = document.getElementById("full_name")?.value.trim();
  const email = document.getElementById("email")?.value.trim();
  const password = document.getElementById("password")?.value;

  if (!full_name || !email || !password) {
    showError("All fields are required");
    return;
  }

  try {

    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name, email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.detail || "Registration failed");
      return;
    }

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("full_name", full_name);

    alert("Registered successfully!");
    window.location.href = "profile.html";

  } catch {
    showError("Server not reachable");
  }
}

// ================= LOGIN =================

async function loginUser(event) {

  event.preventDefault();

  const email = document.getElementById("login-email")?.value.trim();
  const password = document.getElementById("login-password")?.value;

  if (!email || !password) {
    alert("Enter email and password");
    return;
  }

  try {

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.detail || "Invalid login");
      return;
    }

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_id", data.user_id);
    const savedName = localStorage.getItem("full_name");

    localStorage.setItem(
      "full_name",
       data.full_name || savedName || ""
    );

    localStorage.setItem("user_email", email);
    localStorage.setItem("is_admin", data.is_admin);

    alert("Login successful!");

    if (email === "vecr0n.adm1n@gmail.com") {
      window.location.href = "admin.html";
    } else {
      window.location.href = "dashboard.html";
    }

  } catch (err) {
    console.error(err);
    alert("Login failed");
  }
}

// ================= PROFILE =================

async function loadProfile() {

  const user_id = getUserId();
  const token = getToken();

  if (!user_id || !token) return;

  try {

    const res = await fetch(`${API_BASE}/auth/me/${user_id}`, {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!res.ok) throw new Error("Profile failed");

    const data = await res.json();

    // View mode
    document.getElementById("pv-name").textContent = data.full_name || "Not set";
    document.getElementById("pv-email").textContent = data.email || "Not set";
    document.getElementById("pv-exp").textContent = data.experience_level || "-";

    document.getElementById("pv-skills").innerHTML =
      (data.skills || "")
        .split(",")
        .map(s => `<span class="tag">${s.trim()}</span>`)
        .join("");

    // Edit mode
    document.getElementById("experience_level").value =
      data.experience_level || "Beginner";

    document.getElementById("skills").value =
      data.skills || "";

    document.getElementById("preferred_workplace").value =
      data.preferred_workplace || "Remote";

  } catch (err) {
    console.error("Profile error:", err);
    alert("Failed to load profile");
  }
}

// ================= UPDATE PROFILE =================

async function saveProfile() {

  const token = getToken();

  const payload = {
    user_id: getUserId(),
    experience_level: experience_level.value,
    skills: skills.value,
    preferred_workplace: preferred_workplace.value
  };

  try {

    const res = await fetch(`${API_BASE}/auth/update-profile`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error();

    alert("Profile updated!");

    loadProfile();
    loadRecommendations();

    disableEdit();

  } catch {
    alert("Profile update failed");
  }
}

// ================= RECOMMENDATIONS =================

async function loadRecommendations() {

  const user_id = getUserId();
  const token = getToken();

  if (!user_id || !token) {
    confirmLogout();
    return;
  }

  try {

    const res = await fetch(
      `${API_BASE}/recommend/${user_id}?top_n=20`,
      {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      }
    );

    if (!res.ok) throw new Error();

    const data = await res.json();

    const container = document.getElementById("recommendations");
    container.innerHTML = "";

    const recs = data.recommendations || [];

    if (recs.length === 0) {
      container.innerHTML = "<p>No recommendations yet.</p>";
      return;
    }

    recs.forEach(job => {

      const card = document.createElement("div");
      card.className = "job-card";

      card.innerHTML = `
        <div class="match-badge">Matched</div>

        <div class="job-title">${job.title}</div>
        <div class="company">${job.company_name}</div>

        <div class="meta">
          <span>${job.location || "Remote"}</span>
          <span>${job.experience_level || "Beginner"}</span>
        </div>

        <div class="actions">
          <button class="action-btn view-btn"
            onclick="logInteraction(${job.opportunity_id},'view')">
            View
          </button>

          <button class="action-btn save-btn"
            onclick="logInteraction(${job.opportunity_id},'save')">
            Save
          </button>

          <button class="action-btn apply-btn"
            onclick="logInteraction(${job.opportunity_id},'apply')">
            Apply
          </button>
        </div>
      `;

      container.appendChild(card);

    });

  } catch (err) {
    console.error("Recommendation error:", err);
    document.getElementById("recommendations").innerHTML =
      "<p>Failed to load recommendations</p>";
  }
}

// ================= INTERACTIONS =================

async function logInteraction(id, type) {

  const token = getToken();

  try {

    await fetch(`${API_BASE}/interactions/interact`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        opportunity_id: id,
        interaction_type: type
      })
    });

  } catch (err) {
    console.error("Interaction failed", err);
  }
}

// ================= UI =================

function openProfile() {

  document.getElementById("profile-drawer").classList.remove("hidden");
  document.getElementById("profile-overlay").classList.remove("hidden");

  document.getElementById("profile-edit").classList.add("hidden");
  document.getElementById("profile-view").classList.remove("hidden");

  loadProfile();
}

function closeProfile() {
  document.getElementById("profile-drawer").classList.add("hidden");
  document.getElementById("profile-overlay").classList.add("hidden");
}

function enableEdit() {
  document.getElementById("profile-view").classList.add("hidden");
  document.getElementById("profile-edit").classList.remove("hidden");
}

function disableEdit() {
  document.getElementById("profile-edit").classList.add("hidden");
  document.getElementById("profile-view").classList.remove("hidden");
}

// ================= LOGOUT =================

function showLogoutModal() {
  document.getElementById("logout-modal").style.display = "flex";
}

function closeLogoutModal() {
  document.getElementById("logout-modal").style.display = "none";
}

function confirmLogout() {
  localStorage.clear();
  window.location.href = "index.html";
}

// ================= HEADER =================

function updateHeader() {

  if (location.pathname.includes("index.html")) return;

  const old = document.getElementById("logout-btn");
  if (old) old.remove();

  const email = localStorage.getItem("user_email");

  if (email === "vecr0n.adm1n@gmail.com") {

    let btn = document.getElementById("admin-btn");

    if (!btn) {

      btn = document.createElement("button");
      btn.id = "admin-btn";
      btn.textContent = "Admin";

      btn.style.cssText =
        "padding:10px 20px;background:#6366f1;color:white;border-radius:30px";

      btn.onclick = () => location.href = "admin.html";

      document.querySelector(".auth-controls").appendChild(btn);
    }
  }
}

function updateNavigation() {
  const navContainer = document.getElementById("nav-buttons");
  if (!navContainer) return;

  // Clear existing items but keep the logic consistent
  navContainer.innerHTML = '<div class="nav-indicator"></div>';
  const indicator = navContainer.querySelector(".nav-indicator");

  const navItems = [
    { name: "Home", file: "index.html" },
    { name: "Dashboard", file: "dashboard.html" },
    { name: "Explore", file: "explore.html" }
  ];

  // Handle root path as index.html
  let currentPage = window.location.pathname.split("/").pop();
  if (currentPage === "" || currentPage === "/") currentPage = "index.html";

  navItems.forEach(item => {
    const a = document.createElement("a");
    a.href = item.file;
    a.textContent = item.name;
    a.classList.add("nav-btn");
    if (currentPage === item.file) a.classList.add("active");
    navContainer.appendChild(a);
  });

  // Calculate position after the browser has a chance to layout the buttons
  requestAnimationFrame(() => {
    const activeBtn = navContainer.querySelector(".nav-btn.active");
    if (activeBtn) {
      indicator.style.width = `${activeBtn.offsetWidth}px`;
      indicator.style.left = `${activeBtn.offsetLeft}px`;
      indicator.style.opacity = "1";
    }
  });
}


// ================= INIT =================

document.addEventListener("DOMContentLoaded", () => {

  updateHeader();
  updateNavigation();

  if (location.pathname.includes("dashboard")) {
    loadRecommendations();
  }

});
