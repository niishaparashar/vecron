console.log("api.js loaded");

const API_BASE = window.location.origin;




function getToken() {
  return localStorage.getItem("access_token");
}

async function apiFetch(endpoint, options = {}) {
  const token = getToken();
  const normalizedEndpoint = endpoint.split("?")[0];

  const headers = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };

  const response = await fetch(API_BASE + endpoint, {
    ...options,
    headers,
  });

  const data = await response.json();

  if (!response.ok) {
    const isAuthEndpoint =
      normalizedEndpoint.startsWith("/auth/login") ||
      normalizedEndpoint.startsWith("/auth/register");

    if (response.status === 401 && !isAuthEndpoint) {
      localStorage.clear();
      window.location.href = "index.html";
    }
    throw new Error(data.detail || "Request failed");
  }

  return data;
}
