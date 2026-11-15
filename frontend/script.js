console.log("script.js loaded");

// ================= HELPERS =================

function getUserId() {
  return localStorage.getItem("user_id");
}

function getToken() {
  return localStorage.getItem("access_token");
}

function showError(msg) {
  const activeModal = document.querySelector(".modal.active .form-error");
  if (activeModal) {
    activeModal.textContent = msg;
    return;
  }
  alert(msg);
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isAdminUser() {
  const adminValue = localStorage.getItem("is_admin");
  return adminValue === "true" || adminValue === "1";
}

function clearAuthErrors(prefix) {
  const formError = document.getElementById(`${prefix}-form-error`);
  if (formError) formError.textContent = "";

  ["full-name", "email", "password"].forEach((field) => {
    const fieldError = document.getElementById(`${prefix}-${field}-error`);
    if (fieldError) fieldError.textContent = "";
  });
}

function setFieldError(prefix, field, message) {
  const fieldError = document.getElementById(`${prefix}-${field}-error`);
  if (fieldError) fieldError.textContent = message;
}

function setFormError(prefix, message) {
  const formError = document.getElementById(`${prefix}-form-error`);
  if (formError) {
    formError.textContent = message;
    return;
  }
  alert(message);
}

const opportunityCache = {};

function ensureCenterLoader() {
  if (document.getElementById("center-loader-overlay")) return;

  const style = document.createElement("style");
  style.id = "center-loader-style";
  style.textContent = `
    #center-loader-overlay {
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      background: rgba(10, 14, 22, 0.72);
      z-index: 3000;
      flex-direction: column;
      gap: 12px;
    }
    #center-loader-spinner {
      width: 54px;
      height: 54px;
      border-radius: 50%;
      border: 5px solid rgba(255, 255, 255, 0.2);
      border-top-color: #10b981;
      animation: centerSpin 0.85s linear infinite;
    }
    #center-loader-text {
      color: #e5e7eb;
      font-size: 14px;
      letter-spacing: 0.3px;
    }
    @keyframes centerSpin {
      to { transform: rotate(360deg); }
    }
  `;

  const overlay = document.createElement("div");
  overlay.id = "center-loader-overlay";
  overlay.innerHTML = `
    <div id="center-loader-spinner"></div>
    <div id="center-loader-text">Signing you in...</div>
  `;

  document.head.appendChild(style);
  document.body.appendChild(overlay);
}

function showCenterLoader(text = "Signing you in...") {
  ensureCenterLoader();
  const overlay = document.getElementById("center-loader-overlay");
  const label = document.getElementById("center-loader-text");
  if (label) label.textContent = text;
  if (overlay) overlay.style.display = "flex";
}

function hideCenterLoader() {
  const overlay = document.getElementById("center-loader-overlay");
  if (overlay) overlay.style.display = "none";
}

function sanitizeJobDescription(value) {
  const rawDescription = String(value || "").trim();
  if (!rawDescription) return "No detailed description provided for this role yet.";

  const allowedTags = new Set([
    "A", "B", "BR", "CODE", "EM", "H2", "H3", "H4", "I", "LI", "OL", "P",
    "PRE", "STRONG", "UL",
  ]);
  const parser = new DOMParser();
  const source = parser.parseFromString(rawDescription, "text/html").body;
  const output = document.createDocumentFragment();

  function appendSafe(node, parent) {
    if (node.nodeType === Node.TEXT_NODE) {
      parent.appendChild(document.createTextNode(node.textContent || ""));
      return;
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return;

    const element = node;
    const tagName = element.tagName.toUpperCase();
    if (!allowedTags.has(tagName)) {
      element.childNodes.forEach(child => appendSafe(child, parent));
      return;
    }

    const safeElement = document.createElement(tagName.toLowerCase());
    if (tagName === "A") {
      const href = element.getAttribute("href") || "";
      if (/^https?:\/\//i.test(href)) {
        safeElement.href = href;
        safeElement.target = "_blank";
        safeElement.rel = "noopener noreferrer";
      }
    }
    element.childNodes.forEach(child => appendSafe(child, safeElement));
    parent.appendChild(safeElement);
  }

  source.childNodes.forEach(node => appendSafe(node, output));
  return output;
}

function ensureOpportunityModal() {
  if (document.getElementById("job-detail-modal")) return;

  const modal = document.createElement("div");
  modal.id = "job-detail-modal";
  modal.style.cssText = "display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);z-index:2000;align-items:center;justify-content:center;padding:20px;";

  modal.innerHTML = `
    <div style="width:min(840px, 96vw);max-height:92vh;overflow:auto;background:#111827;border:1px solid #2a3142;border-radius:14px;padding:24px;position:relative;">
      <button id="job-detail-close" style="position:absolute;top:14px;right:14px;background:transparent;color:#9ca3af;border:none;font-size:24px;cursor:pointer;">x</button>
      <h2 id="job-detail-title" style="margin:0 0 8px 0;color:#f3f4f6;"></h2>
      <div id="job-detail-company" style="color:#10b981;font-weight:600;margin-bottom:14px;"></div>
      <div id="job-detail-meta" style="color:#9ca3af;font-size:14px;margin-bottom:16px;"></div>
      <div style="margin-bottom:16px;">
        <h3 style="margin:0 0 8px 0;color:#e5e7eb;font-size:16px;">Complete Skills</h3>
        <div id="job-detail-skills" style="color:#d1d5db;line-height:1.5;"></div>
      </div>
      <div style="margin-bottom:20px;">
        <h3 style="margin:0 0 8px 0;color:#e5e7eb;font-size:16px;">Job Description</h3>
        <div id="job-detail-description" style="color:#d1d5db;line-height:1.6;"></div>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <button id="job-detail-view" style="padding:10px 16px;background:#374151;color:#f3f4f6;border:none;border-radius:8px;cursor:pointer;">View Details</button>
        <button id="job-detail-save" style="padding:10px 16px;background:#0ea5e9;color:#fff;border:none;border-radius:8px;cursor:pointer;">Save</button>
        <button id="job-detail-apply" style="padding:10px 16px;background:#10b981;color:#062b1f;border:none;border-radius:8px;cursor:pointer;font-weight:700;">Apply</button>
        <a id="job-detail-career" target="_blank" rel="noopener noreferrer" style="padding:10px 16px;background:#1f2937;color:#d1d5db;border-radius:8px;text-decoration:none;">Company Careers</a>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  document.getElementById("job-detail-close").addEventListener("click", closeOpportunityModal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeOpportunityModal();
  });
}

function closeOpportunityModal() {
  const modal = document.getElementById("job-detail-modal");
  if (modal) modal.style.display = "none";
}

async function fetchOpportunityDetails(opportunityId) {
  if (opportunityCache[opportunityId]) return opportunityCache[opportunityId];
  const response = await fetch(`${API_BASE}/opportunities/${opportunityId}`);
  if (!response.ok) throw new Error("Failed to fetch opportunity");
  const details = await response.json();
  opportunityCache[opportunityId] = details;
  return details;
}

async function openJobDetails(opportunityId) {
  ensureOpportunityModal();
  try {
    const details = await fetchOpportunityDetails(opportunityId);

    document.getElementById("job-detail-title").textContent = details.title || "Opportunity";
    document.getElementById("job-detail-company").textContent = details.company_name || "";
    document.getElementById("job-detail-meta").textContent =
      `${details.location || "Remote"} | ${details.employment_type || "Full-time"} | ${details.experience_level || "Any"} | ${details.workplace_type || "On-site"}`;
    document.getElementById("job-detail-skills").textContent = details.skills_required || "Not specified";
    const description = document.getElementById("job-detail-description");
    description.replaceChildren(sanitizeJobDescription(details.job_description));

    const careerUrl = details.career_page_url || "";
    const applyUrl = details.apply_url || details.career_page_url || "#";
    const saveButton = document.getElementById("job-detail-save");
    saveButton.dataset.opportunityId = String(opportunityId);
    saveButton.textContent = "Save";
    saveButton.classList.remove("saved");
    saveButton.disabled = false;

    const careerLink = document.getElementById("job-detail-career");
    if (careerUrl) {
      careerLink.href = careerUrl;
      careerLink.style.pointerEvents = "auto";
      careerLink.style.opacity = "1";
      careerLink.textContent = careerUrl.includes("google.com/search?q=") ? "Find Careers" : "Company Careers";
    } else {
      careerLink.href = "#";
      careerLink.style.pointerEvents = "none";
      careerLink.style.opacity = "0.5";
      careerLink.textContent = "Career page unavailable";
    }

    document.getElementById("job-detail-view").onclick = () => logInteraction(opportunityId, "view");
    saveButton.onclick = () => saveJob(opportunityId);
    document.getElementById("job-detail-apply").onclick = () => applyForJob(opportunityId, applyUrl);

    document.getElementById("job-detail-modal").style.display = "flex";
    await logInteraction(opportunityId, "view");
  } catch (error) {
    console.error(error);
    alert("Unable to load job details");
  }
}

async function saveJob(opportunityId) {
  const ok = await logInteraction(opportunityId, "save");
  if (!ok) return;
  setSaveButtonState(opportunityId);
  if (document.getElementById("saved-jobs")) {
    await loadSavedJobs();
  }
}

function setSaveButtonState(opportunityId) {
  document.querySelectorAll(`[data-save-job="${opportunityId}"]`).forEach(button => {
    button.textContent = "Saved";
    button.classList.add("saved");
    button.disabled = true;
  });
  const detailButton = document.getElementById("job-detail-save");
  if (detailButton && detailButton.dataset.opportunityId === String(opportunityId)) {
    detailButton.textContent = "Saved";
    detailButton.classList.add("saved");
    detailButton.disabled = true;
  }
}

async function loadSavedJobs() {
  const container = document.getElementById("saved-jobs");
  if (!container) return;

  try {
    const data = await apiFetch("/interactions/saved");
    const jobs = data.saved_jobs || [];
    container.innerHTML = jobs.length
      ? jobs.map(job => renderJobCard(job, true)).join("")
      : '<p class="empty-state">You have not saved any jobs yet.</p>';
    jobs.forEach(job => setSaveButtonState(job.opportunity_id));
  } catch (error) {
    console.error("Saved jobs error:", error);
    container.innerHTML = '<p class="empty-state">Unable to load saved jobs.</p>';
  }
}

function renderJobCard(job, saved = false) {
  const saveLabel = saved ? "Saved" : "Save";
  const saveClass = saved ? " saved" : "";
  return `
    <div class="job-card">
      <div class="job-title">${job.title}</div>
      <div class="company">${job.company_name}</div>
      <div class="meta">
        <span>📍 ${job.location || "Remote"}</span>
        <span>🎓 ${job.experience_level || "Any"}</span>
      </div>
      <div class="tags">
        ${(job.skills_required || "").split(",").slice(0, 5).map(skill => `<span class="tag">${skill.trim()}</span>`).join("")}
      </div>
      <div class="actions">
        <button class="action-btn view-btn" onclick="openJobDetails(${job.opportunity_id})">View Details</button>
        <button class="action-btn save-btn${saveClass}" data-save-job="${job.opportunity_id}" onclick="saveJob(${job.opportunity_id})" ${saved ? "disabled" : ""}>${saveLabel}</button>
        <button class="action-btn apply-btn" onclick="applyForJob(${job.opportunity_id}, '${job.apply_url || job.career_page_url || ""}')">Apply</button>
      </div>
    </div>
  `;
}

async function applyForJob(opportunityId, url) {
  const ok = await logInteraction(opportunityId, "apply");
  if (!ok) return;
  let targetUrl = url;

  if (!targetUrl || targetUrl === "#") {
    try {
      const details = await fetchOpportunityDetails(opportunityId);
      targetUrl = details.apply_url || details.career_page_url || "";
    } catch (error) {
      console.error(error);
    }
  }

  if (targetUrl && targetUrl !== "#") {
    window.open(targetUrl, "_blank", "noopener");
  } else {
    alert("Application URL is not available for this role yet.");
  }
}

// ================= REGISTER =================

async function registerUser() {
  const prefix = "register";
  clearAuthErrors(prefix);

  const full_name = document.getElementById("register-full-name")?.value.trim();
  const email = document.getElementById("register-email")?.value.trim();
  const password = document.getElementById("register-password")?.value;

  let hasError = false;

  if (!full_name) {
    setFieldError(prefix, "full-name", "Full name is required");
    hasError = true;
  }
  if (!email) {
    setFieldError(prefix, "email", "Email is required");
    hasError = true;
  } else if (!isValidEmail(email)) {
    setFieldError(prefix, "email", "Enter a valid email address");
    hasError = true;
  }
  if (!password) {
    setFieldError(prefix, "password", "Password is required");
    hasError = true;
  } else if (password.length < 6) {
    setFieldError(prefix, "password", "Password must be at least 6 characters");
    hasError = true;
  }

  if (hasError) return;

  try {

    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name, email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      setFormError(prefix, data.detail || "Registration failed");
      return;
    }

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("full_name", full_name);
    localStorage.setItem("user_email", email);
    localStorage.setItem("is_admin", data.is_admin ? "true" : "false");
    localStorage.setItem("profile_completed", data.profile_completed ? "1" : "0");

    alert("Registered successfully!");
    window.location.href = "profile.html";

  } catch {
    setFormError(prefix, "Server not reachable");
  }
}

// ================= LOGIN =================

async function loginUser(event) {

  if (event) event.preventDefault();

  const prefix = "login";
  clearAuthErrors(prefix);

  const email = document.getElementById("login-email")?.value.trim();
  const password = document.getElementById("login-password")?.value;

  let hasError = false;

  if (!email) {
    setFieldError(prefix, "email", "Email is required");
    hasError = true;
  } else if (!isValidEmail(email)) {
    setFieldError(prefix, "email", "Enter a valid email address");
    hasError = true;
  }
  if (!password) {
    setFieldError(prefix, "password", "Password is required");
    hasError = true;
  }

  if (hasError) return;

  showCenterLoader("Signing you in...");

  try {

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      hideCenterLoader();
      setFormError(prefix, data.detail || "Invalid login");
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
    localStorage.setItem("is_admin", data.is_admin ? "true" : "false");

    if (data.is_admin) {
      window.location.href = "admin.html";
    } else {
      window.location.href = "dashboard.html";
    }

  } catch (err) {
    hideCenterLoader();
    console.error(err);
    setFormError(prefix, "Login failed");
  }
}

// ================= PROFILE =================

const PROFILE_SKILLS = [
  "Python", "JavaScript", "TypeScript", "Java", "C++", "C#",
  "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js",
  "SQL", "PostgreSQL", "MongoDB", "Git", "Docker", "AWS",
  "Machine Learning", "Data Analysis", "Pandas", "Power BI",
  "UI/UX Design", "Figma", "Communication", "Project Management"
];
let selectedProfileSkills = new Set();

function renderProfileSkillPicker(filter = "") {
  const options = document.getElementById("skill-options");
  const selected = document.getElementById("selected-skills");
  if (!options || !selected) return;

  const normalizedFilter = filter.trim().toLowerCase();
  options.innerHTML = PROFILE_SKILLS
    .filter(skill => !selectedProfileSkills.has(skill))
    .filter(skill => !normalizedFilter || skill.toLowerCase().includes(normalizedFilter))
    .map(skill => `<button type="button" class="skill-option" data-skill="${skill}">${skill}</button>`)
    .join("");

  selected.innerHTML = Array.from(selectedProfileSkills)
    .map(skill => `<button type="button" class="selected-skill" data-skill="${skill}" aria-label="Remove ${skill}">${skill} ×</button>`)
    .join("");

  options.querySelectorAll("[data-skill]").forEach(button => {
    button.addEventListener("click", () => {
      selectedProfileSkills.add(button.dataset.skill);
      renderProfileSkillPicker(document.getElementById("skill-search").value);
    });
  });
  selected.querySelectorAll("[data-skill]").forEach(button => {
    button.addEventListener("click", () => {
      selectedProfileSkills.delete(button.dataset.skill);
      renderProfileSkillPicker(document.getElementById("skill-search").value);
    });
  });
}

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
    document.getElementById("pv-location").textContent = data.preferred_location || "Anywhere";

    document.getElementById("pv-skills").innerHTML =
      (data.skills || "")
        .split(",")
        .map(s => `<span class="tag">${s.trim()}</span>`)
        .join("");

    // Edit mode
    document.getElementById("experience_level").value =
      data.experience_level || "Beginner";

    selectedProfileSkills = new Set(
      (data.skills || "").split(",").map(skill => skill.trim()).filter(Boolean)
    );
    renderProfileSkillPicker();
    document.getElementById("preferred_location").value =
      data.preferred_location || "";

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
    skills: Array.from(selectedProfileSkills).join(", "),
    preferred_location: preferred_location.value.trim() || "Anywhere",
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

  document.addEventListener("DOMContentLoaded", () => {
    const skillSearch = document.getElementById("skill-search");
    if (skillSearch) {
      skillSearch.addEventListener("input", () => renderProfileSkillPicker(skillSearch.value));
      renderProfileSkillPicker();
    }
  });
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
            onclick="openJobDetails(${job.opportunity_id})">
            View
          </button>

          <button class="action-btn save-btn"
            onclick="saveJob(${job.opportunity_id})">
            Save
          </button>

          <button class="action-btn apply-btn"
            onclick="applyForJob(${job.opportunity_id})">
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
  const userId = getUserId();

  if (!token || !userId) {
    alert("Please login to save interactions.");
    return false;
  }

  try {

    const response = await fetch(`${API_BASE}/interactions/interact`, {
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

    if (!response.ok) {
      if (response.status === 401) {
        alert("Session expired. Please login again.");
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_id");
        localStorage.removeItem("user_email");
        window.location.href = "index.html";
        return false;
      }
      throw new Error("Interaction logging failed");
    }

    return true;

  } catch (err) {
    console.error("Interaction failed", err);
    return false;
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

  if (isAdminUser()) {

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
    { name: "Explore", file: "explore.html" },
    { name: "Saved Jobs", file: "dashboard.html#saved-jobs" }
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

  ensureCenterLoader();
  ensureOpportunityModal();
  updateHeader();
  updateNavigation();

  if (location.pathname.includes("dashboard")) {
    loadRecommendations();
    if (window.location.hash === "#saved-jobs") {
      document.getElementById("saved-jobs")?.scrollIntoView({ behavior: "smooth" });
    }
  }

});
