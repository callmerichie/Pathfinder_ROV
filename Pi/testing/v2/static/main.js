// Socket.IO connection
const socket = io();

socket.on("connect", () => {
  console.log("Socket connected");
});


// ── Manual driving ────────────────────────────────────────────────────────────

const keys = { w: false, a: false, s: false, d: false };
let objectTracked = false;
let objectDetails = [];

document.addEventListener("keydown", (e) => {
  if (e.key in keys) { keys[e.key] = true;  e.preventDefault(); }
});
document.addEventListener("keyup", (e) => {
  if (e.key in keys) { keys[e.key] = false; e.preventDefault(); }
});

function anyKeyPressed() {
  return Object.values(keys).some(v => v);
}

// Send movement commands at fixed rate
setInterval(() => {
  if (!objectTracked) {
    socket.emit("manual_movement", keys);
  }
  if (anyKeyPressed() && objectTracked) {
    console.log("Key pressed during tracking — disabling tracking");
    stopROV(objectDetails[0], objectDetails[1]);
  }
}, 50);

// Safety stop on tab/window blur
window.addEventListener("blur", () => {
  Object.keys(keys).forEach(k => keys[k] = false);
  socket.emit("manual_movement", keys);
});

socket.emit("manual_movement", keys, (reply) => {
  console.log("Server reply:", reply);
});


// ── Distance sensors ──────────────────────────────────────────────────────────

const OBSTACLE_MM = 50;   // must match Arduino #define
const MAX_MM      = 2000; // VL53L0X practical max

socket.on("sensor_update", (data) => {
  updateSensorBar("s1", data.s1);
  updateSensorBar("s2", data.s2);

  const tooClose = isBlocking(data.s1) || isBlocking(data.s2);
  document.getElementById("obstacle-alert").classList.toggle("d-none", !tooClose);
});

function isBlocking(value) {
  return value !== -1 && value <= OBSTACLE_MM;
}

function updateSensorBar(id, value) {
  const bar  = document.getElementById(`bar-${id}`);
  const text = document.getElementById(`text-${id}`);

  if (value === -1) {
    text.textContent = "---";
    text.className = "sensor-value text-muted";
    bar.style.width = "0%";
    bar.className = "progress-bar bg-secondary";
    return;
  }

  const pct = Math.min((value / MAX_MM) * 100, 100).toFixed(1);
  bar.style.width = `${pct}%`;
  text.textContent = `${value} mm`;

  if (value <= OBSTACLE_MM) {
    bar.className = "progress-bar bg-danger";
    text.className = "sensor-value text-danger fw-bold";
  } else if (value <= 100) {
    bar.className = "progress-bar bg-warning";
    text.className = "sensor-value text-warning fw-bold";
  } else if (value <= 200) {
    bar.className = "progress-bar bg-info";
    text.className = "sensor-value text-info";
  } else {
    bar.className = "progress-bar bg-success";
    text.className = "sensor-value text-success";
  }
}


// ── Object detection table ────────────────────────────────────────────────────

async function getObjects() {
  const response = await fetch("/get_list_objects", { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP error ${response.status}`);
  return response.json();
}

async function showListObjects() {
  try {
    renderObjects(await getObjects());
  } catch (err) {
    console.error("Update failed:", err);
  }
}

function renderObjects(objects_list) {
  const tbody = document.getElementById("objects_list");
  tbody.innerHTML = "";

  for (let i = 0; i < objects_list.objects.length; i++) {
    const obj = objects_list.objects[i];
    tbody.innerHTML +=
      `<tr>
        <td>${objects_list.fps !== null ? parseFloat(objects_list.fps).toFixed(1) : "---"}</td>
        <td>${obj.object_id ?? ""}</td>
        <td>${obj.class_id}</td>
        <td>${obj.class_name}</td>
        <td>${parseFloat(obj.confidence).toFixed(2)}</td>
        <td>
          <button class="btn btn-warning btn-sm"
              onclick='trackObjectROV(${JSON.stringify(obj.object_id)}, ${JSON.stringify(obj.class_name)})'>
            Track
          </button>
        </td>
        <td>
          <button class="btn btn-danger btn-sm"
              onclick='stopROV(${JSON.stringify(obj.object_id)}, ${JSON.stringify(obj.class_name)})'>
            Stop tracking
          </button>
        </td>
      </tr>`;
  }
}

async function trackObjectROV(objectId, className) {
  objectTracked = true;
  objectDetails = [objectId, className];
  const res = await fetch("/tracking_object", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ object_id: objectId, class_name: className })
  });
  console.log(await res.json());
}

async function stopROV(objectId, className) {
  objectTracked = false;
  const res = await fetch("/stop_tracking_rov", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ object_id: objectId, class_name: className })
  });
  console.log(await res.json());
}

setInterval(showListObjects, 1000);
showListObjects();