// The front end of menpowidgets.tools.CameraWidget (an anywidget module).
// It streams the webcam in a <video> and, when `take_snapshot` changes, copies
// the current frame to a canvas and sends it to Python as a PNG data URL.

function showError(el, error) {
  const message = document.createElement("div");
  message.style.width = "300px";
  message.style.textAlign = "center";
  message.textContent =
    "The webcam could not be opened (the browser needs a secure context such " +
    "as https or localhost, and the permission to use the camera): " + error;
  el.append(message);
}

async function render({ model, el }) {
  const video = document.createElement("video");
  video.autoplay = true;
  video.muted = true;
  video.playsInline = true;
  const canvas = document.createElement("canvas");
  canvas.style.display = "none";
  el.append(video, canvas);

  let width = model.get("canvas_width");
  let height = 0;
  let stream = null;
  let closed = false;

  function resize() {
    if (!video.videoWidth) return;
    width = model.get("canvas_width");
    height = Math.round(video.videoHeight / (video.videoWidth / width));
    for (const node of [video, canvas]) {
      node.setAttribute("width", width);
      node.setAttribute("height", height);
    }
    model.set("canvas_height", height);
    model.save_changes();
  }

  function takeSnapshot() {
    if (!height) return;
    canvas.getContext("2d").drawImage(video, 0, 0, width, height);
    model.set("imageurl", canvas.toDataURL("image/png"));
    model.save_changes();
  }

  model.on("change:canvas_width", resize);
  model.on("change:take_snapshot", takeSnapshot);
  video.addEventListener("loadedmetadata", resize);

  try {
    // hd asks for 1280x720 or better, but accepts what the camera has
    const constraints = {
      video: model.get("hd")
        ? { width: { ideal: 1280 }, height: { ideal: 720 } }
        : true,
      audio: false,
    };
    stream = await navigator.mediaDevices.getUserMedia(constraints);
  } catch (error) {
    console.log("CameraView ERROR: " + error);
    showError(el, error);
    return;
  }
  if (closed) {
    stream.getTracks().forEach((track) => track.stop());
    return;
  }
  video.srcObject = stream;
  await video.play().catch(() => {});

  // Stop the camera when the widget is removed from the page
  return () => {
    closed = true;
    if (stream) stream.getTracks().forEach((track) => track.stop());
    video.srcObject = null;
  };
}

export default { render };
