const USERS = {
  student1: { password: "pass123", role: "student" },
  student2: { password: "pass123", role: "student" },
  faculty1: { password: "pass123", role: "faculty" },
  hod1:     { password: "pass123", role: "hod"     }
};

const FACULTY_LIMIT = 3;
const HOD_LIMIT = 10;
const INITIAL_BALANCE = 20;

// ---------- persistence ----------
function loadState() {
  const raw = localStorage.getItem("clp_state");
  if (raw) return JSON.parse(raw);
  const fresh = { leaves: [], nextId: 1, session: null };
  localStorage.setItem("clp_state", JSON.stringify(fresh));
  return fresh;
}
function saveState(s) { localStorage.setItem("clp_state", JSON.stringify(s)); }
let state = loadState();

// ---------- helpers ----------
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function calculateDays(startStr, endStr) {
  const start = new Date(startStr);
  const end = new Date(endStr);
  if (isNaN(start.getTime()) || isNaN(end.getTime())) throw new Error("Invalid date");
  if (end < start) throw new Error("End date cannot be before start date");
  return Math.floor((end - start) / 86400000) + 1;   // inclusive
}
function validateLeave(startStr, endStr, reason) {
  if (!startStr || !endStr) throw new Error("Start and end dates are required");
  if (!reason || !reason.trim()) throw new Error("Reason is required");
  if (reason.trim().length < 5) throw new Error("Reason must be at least 5 characters");
  calculateDays(startStr, endStr);   // throws if invalid range
  return true;
}
function canApprove(role, days) {
  if (role === "faculty") return days <= FACULTY_LIMIT;
  if (role === "hod")     return days <= HOD_LIMIT;
  return false;
}
function getBalance(username) {
  const used = state.leaves
    .filter(l => l.student === username && l.status === "Approved")
    .reduce((s, l) => s + l.days, 0);
  return Math.max(0, INITIAL_BALANCE - used);
}

// ---------- business logic ----------
function login(username, password) {
  const u = USERS[username];
  if (!u || u.password !== password) throw new Error("Invalid username or password");
  state.session = { username, role: u.role };
  saveState(state);
}
function logout() {
  state.session = null;
  saveState(state);
}
function applyLeave(username, startStr, endStr, reason) {
  validateLeave(startStr, endStr, reason);
  const days = calculateDays(startStr, endStr);
  const leave = {
    id: state.nextId++, student: username,
    startDate: startStr, endDate: endStr,
    reason: reason.trim(), days,
    status: "Pending", remark: "", decidedBy: "",
    createdAt: new Date().toISOString()
  };
  state.leaves.push(leave);
  saveState(state);
  return leave;
}
function cancelLeave(id, username) {
  const l = state.leaves.find(x => x.id === id && x.student === username);
  if (!l) throw new Error("Leave not found");
  if (l.status !== "Pending") throw new Error("Only pending leaves can be cancelled");
  l.status = "Cancelled";
  saveState(state);
}
function decideLeave(id, role, username, decision, remark) {
  const l = state.leaves.find(x => x.id === id);
  if (!l) throw new Error("Leave not found");
  if (l.status !== "Pending") throw new Error("Only pending leaves can be decided");
  if (decision === "Approved" && !canApprove(role, l.days))
    throw new Error(`Your role cannot approve ${l.days} days`);
  if (decision === "Rejected" && !remark.trim())
    throw new Error("Rejection remark is required");
  l.status = decision;
  l.remark = remark.trim();
  l.decidedBy = username;
  saveState(state);
}

// ---------- rendering ----------
function render() {
  const session = state.session;
  document.getElementById("loginSection").classList.toggle("hidden", !!session);
  document.getElementById("logoutBtn").classList.toggle("hidden", !session);
  document.getElementById("studentDashboard").classList.add("hidden");
  document.getElementById("approverDashboard").classList.add("hidden");
  if (!session) return;
  if (session.role === "student") renderStudent(session.username);
  else renderApprover(session.role, session.username);
}

function renderStudent(username) {
  document.getElementById("studentDashboard").classList.remove("hidden");
  document.getElementById("leaveBalance").textContent = getBalance(username);
  const list = document.getElementById("leaveList");
  const mine = state.leaves.filter(l => l.student === username).sort((a,b) => b.id - a.id);
  list.innerHTML = mine.length ? "" : "<li>No leave requests yet.</li>";
  mine.forEach(l => {
    const li = document.createElement("li");
    li.className = "leave-item status-" + l.status.toLowerCase();
    li.innerHTML = `
      <div><strong>#${l.id}</strong> ${l.startDate} → ${l.endDate} (${l.days} day${l.days>1?"s":""})</div>
      <div>Reason: ${escapeHtml(l.reason)}</div>
      <div>Status: <strong>${l.status}</strong>${l.remark ? " — " + escapeHtml(l.remark) : ""}</div>
      ${l.status === "Pending" ? `<button data-action="cancel" data-id="${l.id}">Cancel</button>` : ""}
    `;
    list.appendChild(li);
  });
}

function renderApprover(role, username) {
  document.getElementById("approverDashboard").classList.remove("hidden");
  document.getElementById("approverRole").textContent = role.toUpperCase();
  const list = document.getElementById("pendingList");
  const pending = state.leaves.filter(l => l.status === "Pending").sort((a,b) => a.id - b.id);
  list.innerHTML = pending.length ? "" : "<li>No pending requests.</li>";
  pending.forEach(l => {
    const within = canApprove(role, l.days);
    const li = document.createElement("li");
    li.className = "leave-item";
    li.innerHTML = `
      <div><strong>#${l.id}</strong> ${l.student}: ${l.startDate} → ${l.endDate} (${l.days} day${l.days>1?"s":""})</div>
      <div>Reason: ${escapeHtml(l.reason)}</div>
      <div class="hint">${within ? "Within your approval limit" : "Exceeds your approval limit"}</div>
      <input class="remark" data-id="${l.id}" placeholder="Rejection remark (required to reject)">
      <button data-action="approve" data-id="${l.id}" ${within ? "" : "disabled"}>Approve</button>
      <button data-action="reject"  data-id="${l.id}">Reject</button>
    `;
    list.appendChild(li);
  });
}

// ---------- event wiring ----------
document.getElementById("loginBtn").addEventListener("click", () => {
  const u = document.getElementById("username").value.trim();
  const p = document.getElementById("password").value;
  const err = document.getElementById("loginError");
  err.textContent = "";
  try {
    login(u, p);
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
    render();
  } catch (e) { err.textContent = e.message; }
});

document.getElementById("logoutBtn").addEventListener("click", () => {
  logout(); render();
});

document.getElementById("applyLeaveForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const err = document.getElementById("applyError");
  err.textContent = "";
  try {
    applyLeave(
      state.session.username,
      document.getElementById("startDate").value,
      document.getElementById("endDate").value,
      document.getElementById("reason").value
    );
    document.getElementById("applyLeaveForm").reset();
    renderStudent(state.session.username);
  } catch (ex) { err.textContent = ex.message; }
});

document.getElementById("leaveList").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-action='cancel']");
  if (!btn) return;
  try {
    cancelLeave(Number(btn.dataset.id), state.session.username);
    renderStudent(state.session.username);
  } catch (ex) { alert(ex.message); }
});

document.getElementById("pendingList").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;
  const id = Number(btn.dataset.id);
  const remarkEl = document.querySelector(`.remark[data-id="${id}"]`);
  const remark = remarkEl ? remarkEl.value : "";
  const decision = btn.dataset.action === "approve" ? "Approved" : "Rejected";
  try {
    decideLeave(id, state.session.role, state.session.username, decision, remark);
    renderApprover(state.session.role, state.session.username);
  } catch (ex) { alert(ex.message); }
});

render();