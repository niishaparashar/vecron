
console.log("script.js loaded");
// -------------------- HELPERS --------------------
function getUserId() {
  return localStorage.getItem("user_id");
}

function setUserId(id) {
  localStorage.setItem("user_id", id);
}

function showError(msg) {
  alert(msg);
}

// -------------------- REGISTER --------------------
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

    // Now save everything
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("full_name", full_name);  // ← NAME SAVED

    alert("Registered successfully!");
    window.location.href = "profile.html";

  } catch (err) {
    showError("Server not reachable");
  }
}
// -------------------- LOGIN --------------------
async function loginUser() {
  event.preventDefault();
  const email = document.getElementById("login-email")?.value.trim();
  const password = document.getElementById("login-password")?.value;

  if (!email || !password) {
    alert("Please enter email and password");
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
      alert(data.detail || "Invalid email or password");
      return;
    }

    // Save login data
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("full_name", data.full_name || email.split("@")[0]);
    localStorage.setItem("user_email", email);
    localStorage.setItem("is_admin", data.is_admin);

    alert("Login successful!");
    // AFTER successful login
if (data.email === "vecr0n.adm1n@gmail.com") {
  window.location.href = "admin.html";
} else {
  window.location.href = "dashboard.html";
}



  } catch (err) {
    alert("Login failed. Check connection.");
    console.error(err);
  }
}
// -------------------- COMPLETE PROFILE --------------------
async function completeProfile() {
  const user_id = getUserId();

  if (!user_id) {
    showError("User not logged in");
    return;
  }

  const experience_level = document.getElementById("experience").value;
  const preferred_category = document.getElementById("category").value;
  const skills = document.getElementById("skills").value;
  const preferred_location = document.getElementById("location").value;
  const preferred_workplace = document.getElementById("workplace").value;

  try {
    const res = await fetch(`${API_BASE}/auth/complete-profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: Number(user_id),
        experience_level,
        preferred_category,
        skills,
        preferred_location,
        preferred_workplace
      })
    });
    

    const data = await res.json();

    if (!res.ok) {
      showError(data.detail || "Profile update failed");
      return;
    }

    window.location.href = "dashboard.html";

  } catch (err) {
    showError("Server error");
  }
}

// -------------------- LOAD RECOMMENDATIONS --------------------
async function loadRecommendations() {
  const user_id = getUserId();

  if (!user_id) {
    alert("Please login again");
    logout();
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/recommend/${user_id}`);
    const data = await res.json();

    const container = document.getElementById("recommendations");
    container.innerHTML = "";

    if (!data.recommendations || data.recommendations.length === 0) {
      container.innerHTML = "<p>No recommendations found.</p>";
      return;
    }

    data.recommendations.forEach(job => {
      const div = document.createElement("div");
      div.className = "job-card";
      div.style.border = "1px solid #ccc";
      div.style.margin = "10px";
      div.style.padding = "10px";

      div.innerHTML = `
        <h3>${job.title}</h3>
        <p><strong>${job.company_name}</strong></p>
        <p>${job.explanation || ""}</p>
        <small>Score: ${job.final_score.toFixed(2)}</small><br><br>

        <button onclick="logInteraction(${job.opportunity_id}, 'view')">👁 View</button>
        <button onclick="logInteraction(${job.opportunity_id}, 'save')">⭐ Save</button>
        <button onclick="logInteraction(${job.opportunity_id}, 'apply')">🚀 Apply</button>
      `;

      container.appendChild(div);
    });

  } catch (err) {
    alert("Failed to load recommendations");
  }
}
//-----------------LOGIN-INTERACTIONS-----
async function logInteraction(opportunity_id, interaction_type) {
  const user_id = getUserId();

  if (!user_id) {
    alert("Please login again");
    logout();
    return;
  }

  try {
    await fetch(`${API_BASE}/interactions/interact`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        
        opportunity_id: opportunity_id,
        interaction_type: interaction_type
      })
    });
    alert("Saved! Scores updating...");
    loadRecommendations();
  } catch (err) {
    console.error("Interaction failed", err);
  }
}

// -------------------- LOGOUT --------------------
function showLogoutModal() {
  document.getElementById("logout-modal").style.display = "flex";
}

function closeLogoutModal() {
  document.getElementById("logout-modal").style.display = "none";
}

function confirmLogout() {
  localStorage.clear();
  closeLogoutModal();
  window.location.href = "index.html";
}

// -------------------- UPDATE HEADER --------------------
function updateHeader() {
  if (window.location.pathname === "/" || window.location.pathname.includes("index.html")) {
    return;
  }
  const token = localStorage.getItem("access_token");
  const email = localStorage.getItem("user_email");
  const isAdmin = email === "vecr0n.adm1n@gmail.com";

  let logoutBtn = document.getElementById("logout-btn");

  if (token) {
    if (!logoutBtn) {
      logoutBtn = document.createElement("button");
      logoutBtn.id = "logout-btn";
      logoutBtn.textContent = "Logout";
      logoutBtn.style.cssText = `
        padding: 10px 20px;
        background: #ef4444;
        color: white;
        border: none;
        border-radius: 30px;
        cursor: pointer;
        font-weight: bold;
        margin-left: 20px;
      `;
      logoutBtn.onclick = showLogoutModal;  // ← CALL MODAL, NOT DIRECT LOGOUT

      const header = document.querySelector(".header") || document.body;
      header.appendChild(logoutBtn);
    }
  } else if (logoutBtn) {
    logoutBtn.remove();
  }
  if (token && isAdmin) {
    // Add Admin Panel button
    let adminBtn = document.getElementById("admin-btn");
    if (!adminBtn) {
      adminBtn = document.createElement("button");
      adminBtn.id = "admin-btn";
      adminBtn.textContent = "Admin Panel";
      adminBtn.style.cssText = "padding: 10px 20px; background: #6366f1; color: white; border: none; border-radius: 30px; font-weight: bold; margin-left: 20px;";
      adminBtn.onclick = () => window.location.href = "admin.html";
      document.querySelector(".auth-controls").appendChild(adminBtn);
    }
  }
}
function updateNavigation() {
  const token = localStorage.getItem("access_token");
  const navContainer = document.getElementById("nav-buttons");

  if (token && navContainer) {
    navContainer.innerHTML = `
      <a href="index.html" class="nav-btn">Home</a>
      <a href="explore.html" class="nav-btn">Explore</a>
    `;
  }
}

//-----------uodate-info-------------------
async function updateProfile() {
  const user_id = localStorage.getItem("user_id");

  const payload = {
    user_id: Number(user_id),
    experience_level: document.getElementById("experience_level").value,
    preferred_category: document.getElementById("preferred_category").value,
    skills: document.getElementById("skills").value,
    preferred_location: document.getElementById("preferred_location").value,
    preferred_workplace: document.getElementById("preferred_workplace").value,
    
  };

  const res = await fetch(`${API_BASE}/auth/update-profile`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.detail || "Update failed");
    return;
  }

  alert("Profile updated!");
  loadRecommendations();
}

async function loadProfile() {
  const user_id = localStorage.getItem("user_id");

  const res = await fetch(`${API_BASE}/auth/me/${user_id}`);
  const data = await res.json();

  document.getElementById("full_name").value = data.full_name;
  document.getElementById("email").value = data.email;
  document.getElementById("experience_level").value = data.experience_level || "Junior";
  document.getElementById("skills").value = data.skills || "";
  document.getElementById("preferred_category").value = data.preferred_category || "Software";
  document.getElementById("preferred_workplace").value = data.preferred_workplace || "Remote";
  document.getElementById("preferred_location").value = data.preferred_location || "";
}


document.addEventListener("DOMContentLoaded", loadProfile);

function openProfile() {
  document.getElementById("profile-drawer").classList.remove("hidden");
  document.getElementById("profile-overlay").classList.remove("hidden");

  // FORCE correct state every time
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


async function loadProfile() {
  const user_id = localStorage.getItem("user_id");
  const res = await fetch(`/auth/me/${user_id}`);
  const data = await res.json();

  document.getElementById("pv-name").textContent = data.full_name || "Not set";
  document.getElementById("pv-email").textContent = data.email;
  document.getElementById("pv-exp").textContent = data.experience_level;
  document.getElementById("pv-skills").innerHTML =
  (data.skills || "").split(",").map(
    s => `<span>${s.trim()}</span>`
  ).join("");

  

  document.getElementById("experience_level").value = data.experience_level;
  document.getElementById("skills").value = data.skills;
  document.getElementById("preferred_workplace").value = data.preferred_workplace;
}

async function saveProfile() {
  const payload = {
    user_id: localStorage.getItem("user_id"),
    experience_level: experience_level.value,
    skills: skills.value,
    preferred_workplace: preferred_workplace.value
  };

  await fetch("/auth/update-profile", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  document.getElementById("profile-edit").classList.add("hidden");
  document.getElementById("profile-view").classList.remove("hidden");
 

  loadProfile();
  if (!localStorage.getItem("is_admin")) {
  loadRecommendations();
}

  disableEdit();
}

// Call it on load
document.addEventListener("DOMContentLoaded", () => {
  updateHeader();
  updateNavigation();  
  loadTheme();
  
});