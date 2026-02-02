console.log("app.js loaded");

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

// add row in the table
async function updateObjects() {
  try {
    const objects = await getObjects();
    console.log(objects);
    renderObjects(objects);

  } catch (err) {
    console.error("Update failed:", err);
  }
}


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
        </tr>`;   

    }


}

// poll every 300 ms (≈ 3 times/sec)
setInterval(updateObjects, 300);

// optional: first immediate call
updateObjects();
