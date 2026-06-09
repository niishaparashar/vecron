console.log("auth.js loaded");

async function login() {
  const email = document.getElementById("login-email")?.value.trim();
  const password = document.getElementById("login-password")?.value;

  try {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_email", email);
    localStorage.setItem("is_admin", data.is_admin ? "true" : "false");
    // after successful login
    if (data.is_admin) {
      window.location.href = "admin.html";
    } else {
      window.location.href = "dashboard.html";
}

  } catch (err) {
    alert(err.message);
  }
}

async function registerUser() {
  const full_name = document.getElementById("register-full-name")?.value.trim();
  const email = document.getElementById("register-email")?.value.trim();
  const password = document.getElementById("register-password")?.value;

  try {
    await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ full_name, email, password }),
    });

    alert("Registered successfully. Please login.");
    window.location.href = "index.html";
  } catch (err) {
    alert(err.message);
  }
}

async function completeProfile() {
  const payload = {
    experience_level: document.getElementById("experience").value,
    preferred_category: document.getElementById("category").value,
    skills: document.getElementById("skills").value,
    preferred_location: document.getElementById("location").value,
    preferred_workplace: document.getElementById("workplace").value,
  };

  try {
    await apiFetch("/auth/complete-profile", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    window.location.href = "profile.html";
  } catch (err) {
    alert(err.message);
  }
}

function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}
