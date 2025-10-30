const BASE_URL = "http://localhost:8000"; // Change this when deploying

function getBaseURL() { return BASE_URL; }

const TOKEN_KEY = "cpl_admin_token";

// save the token:
function saveToken(token) { 
  console.log("saveToken", token);
  localStorage.setItem(TOKEN_KEY, token); }


function getToken() { return localStorage.getItem(TOKEN_KEY); }
function clearToken() { localStorage.removeItem(TOKEN_KEY); }

async function apiFetch(endpoint, opts = {}) {
  console.log("key_save_1");
  const baseUrl = getBaseURL();
  console.log("key_save_2");
  const headers = opts.headers || {};
  console.log("key_save_3");
  const token = getToken();
  console.log("key_save_4");
  if(token) headers["Authorization"] = "Bearer " + token;
  console.log("key_save_5");
  opts.headers = headers;
  console.log("key_save_6");
  const res = await fetch(baseUrl + endpoint, opts);
  console.log("key_save_7");
  console.log(res);
  if(res.status===401) { clearToken(); window.location = "login.html"; }
  return res;
}
