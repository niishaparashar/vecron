console.log("api.js loaded");

const API_BASE = "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("access_token");
}

async function apiFetch(endpoint, options = {}) {
  const token = getToken();

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
    throw new Error(data.detail || "Request failed");
  }

  return data;
}
