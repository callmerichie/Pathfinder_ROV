// Socket.IO connection
const socket = io();

socket.on("connect", () => {
  console.log("Socket connected:", socket.id);
});

// Manual movement state
const keys = { w: false, a: false, s: false, d: false };

// object tracked
let objectTracked = false;
//let manualOverrideSent = false;


// Keyboard handling
document.addEventListener("keydown", (e) => {
  if (e.key in keys) {
    keys[e.key] = true;
    e.preventDefault();
  }
});

document.addEventListener("keyup", (e) => {
  if (e.key in keys) {
    keys[e.key] = false;
    e.preventDefault();
  }
});



// checks if any key is pressed
 function anyKeyPressed(){
   return Object.values(keys).some(v => v);
 }


// Send commands at fixed rate
setInterval(() => {
  if(objectTracked === false){
    socket.emit("manual_movement", keys);
  }

  if(anyKeyPressed() && objectTracked === true){
    alert("Tracking active: stop tracking for manual driving!");
  }
}, 50);

// Safety stop: in case of switch pages or crashing, the vehicle stops while in manual
window.addEventListener("blur", () => {
  Object.keys(keys).forEach(k => keys[k] = false);
  socket.emit("manual_movement", keys);
});



socket.emit("manual_movement", keys, (reply) => {
  console.log("Server reply:", reply);
});



// get the object_list for Flask
async function getObjects() {
  const response = await fetch("/get_list_objects", {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }

  return response.json();
}

// add row in the table -> possible update: change the row tables only if something changed 
// (compare timestamp or hash/ sort by object id)
async function showListObjects() {
  try {
    const objects = await getObjects();
    //console.log(objects);
    renderObjects(objects);

  } catch (err) {
    console.error("Update failed:", err);
  }
}

// creates the row
function renderObjects(objects_list){
    let row = document.getElementById("objects_list");

    row.innerHTML = ""; // clear row

    for (let i = 0; i < objects_list.objects.length; i++){
        let object = objects_list.objects[i]

        row.innerHTML +=
        `<tr id="rowIndex${i}">
            <td>${objects_list.fps}</td>
            <td>${object.object_id ?? ""}</td>
            <td>${object.class_id}</td>
            <td>${object.class_name}</td>
            <td>${object.confidence}</td>
            <td>
              <button id="rowTracking${i}" class="btn btn-warning" 
                  onclick='trackObjectROV(${JSON.stringify(object.object_id)}, ${JSON.stringify(object.class_name)})'>
                  TRACK OBJECT
              </button>
            </td>
            <td>
              <button id="rowStopROV${i}" class="btn btn-danger"
                  onclick='stopROV(${JSON.stringify(object.object_id)}, ${JSON.stringify(object.class_name)})'>
                  STOP OBJECT TRACKING
              </button>
            </td>
        </tr>`;   

    }


}


// send the object choesen to flask
async function trackObjectROV(objectId, className) {

  objectTracked = true;
  //manualOverrideSent = false;

  const res = await fetch("/tracking_object", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ object_id: objectId, class_name: className })
  });
  console.log(await res.json()); // print the reponse from flask
}


// send a stop request to flask to stop the tracking and the rov
async function stopROV(objectId, className) {

  objectTracked = false;
  //manualOverrideSent = false;

  const res = await fetch("/stop_tracking_rov", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ object_id: objectId, class_name: className })
  });
  console.log(await res.json()); // print the reponse from flask
}



// poll every 1000 ms (≈ 10 times/sec)
setInterval(showListObjects, 1000);

// optional: first immediate call
showListObjects();
