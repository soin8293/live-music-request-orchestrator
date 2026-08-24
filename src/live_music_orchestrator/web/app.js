"use strict";

const elements = {
  chip: document.querySelector("#connection-chip"),
  connection: document.querySelector("#connection-label"),
  art: document.querySelector("#now-art"),
  title: document.querySelector("#now-title"),
  artist: document.querySelector("#now-artist"),
  requester: document.querySelector("#now-requester"),
  time: document.querySelector("#now-time"),
  progress: document.querySelector("#now-progress"),
  queue: document.querySelector("#queue-list"),
  queueEmpty: document.querySelector("#queue-empty"),
  queueCount: document.querySelector("#queue-count"),
  revision: document.querySelector("#revision-label"),
  controls: document.querySelector("#controls"),
  requestForm: document.querySelector("#request-form"),
  skipButton: document.querySelector("#skip-button"),
  resetButton: document.querySelector("#reset-button"),
  status: document.querySelector("#control-status"),
};

let state = { revision: 0, current_track: null, queue: [] };
let connected = false;
let trackStartedAt = performance.now();

function setConnection(value) {
  connected = value;
  elements.chip.classList.toggle("is-online", connected);
  elements.connection.textContent = connected ? "CONNECTED" : "POLLING";
}

function formatTime(milliseconds) {
  const total = Math.max(0, Math.floor(milliseconds / 1000));
  const minutes = Math.floor(total / 60);
  return `${minutes}:${String(total % 60).padStart(2, "0")}`;
}

function setArtwork(element, item) {
  element.style.setProperty("--art-a", item?.color_start || "#8169ff");
  element.style.setProperty("--art-b", item?.color_end || "#ff4fa3");
}

function createQueueItem(item, position) {
  const row = document.createElement("li");
  row.className = "queue-item";

  const art = document.createElement("div");
  art.className = "queue-art";
  art.textContent = String(position + 1).padStart(2, "0");
  setArtwork(art, item);

  const copy = document.createElement("div");
  copy.className = "queue-copy";
  const title = document.createElement("strong");
  title.textContent = item.title || "Untitled request";
  const artist = document.createElement("span");
  artist.textContent = item.artist || "Demo Artist";
  copy.append(title, artist);

  const requester = document.createElement("span");
  requester.className = "queue-user";
  requester.textContent = `@${item.requester_name || item.requested_by || "viewer"}`;

  row.append(art, copy, requester);
  return row;
}

function render(nextState) {
  const previousTrack = state.current_track?.request_id;
  state = { ...state, ...nextState };
  if (state.current_track?.request_id !== previousTrack) {
    trackStartedAt = performance.now();
  }

  const track = state.current_track;
  if (track) {
    elements.title.textContent = track.title;
    elements.artist.textContent = track.artist;
    elements.requester.textContent = `Requested by ${track.requester_name || track.requested_by}`;
    setArtwork(elements.art, track);
  } else {
    elements.title.textContent = "Waiting for a request";
    elements.artist.textContent = "Synthetic catalog ready";
    elements.requester.textContent = "No requester yet";
    elements.time.textContent = "0:00";
    elements.progress.style.transform = "scaleX(0)";
    setArtwork(elements.art, null);
  }

  elements.queue.replaceChildren();
  (state.queue || []).slice(0, 9).forEach((item, index) => {
    elements.queue.append(createQueueItem(item, index));
  });
  elements.queueCount.textContent = String((state.queue || []).length);
  elements.queueEmpty.hidden = (state.queue || []).length > 0;
  elements.revision.textContent = `REV ${state.revision || 0}`;
}

async function refresh() {
  try {
    const response = await fetch("/api/state", { cache: "no-store" });
    if (!response.ok) throw new Error("state request failed");
    render(await response.json());
    if (!connected) elements.connection.textContent = "HTTP ONLINE";
  } catch (_error) {
    setConnection(false);
    elements.connection.textContent = "OFFLINE";
  }
}

async function mutate(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  });
  const result = await response.json();
  elements.status.textContent = result.reason || result.status || "done";
  await refresh();
}

function enableControls() {
  const show = new URLSearchParams(window.location.search).get("controls") === "1";
  elements.controls.hidden = !show;
  if (!show) return;

  elements.requestForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(elements.requestForm);
    await mutate("/ingest", {
      event_type: "CHAT_COMMAND",
      action: "request",
      username: form.get("user"),
      nickname: form.get("user"),
      command_params: form.get("song"),
      source: "browser_demo",
    });
  });
  elements.skipButton.addEventListener("click", () => mutate("/ingest", {
    event_type: "CHAT_COMMAND",
    action: "skip",
    username: "local_operator",
    source: "browser_demo",
  }));
  elements.resetButton.addEventListener("click", () => mutate("/api/reset", {}));
}

function updateProgress(timestamp) {
  const track = state.current_track;
  if (track) {
    const progress = Math.min(track.duration_ms, (track.progress_ms || 0) + timestamp - trackStartedAt);
    elements.time.textContent = `${formatTime(progress)} / ${formatTime(track.duration_ms)}`;
    elements.progress.style.transform = `scaleX(${progress / track.duration_ms})`;
  }
  window.requestAnimationFrame(updateProgress);
}

enableControls();
refresh();
window.setInterval(refresh, 5000);
window.requestAnimationFrame(updateProgress);

const eventStream = new EventSource("/events");
eventStream.addEventListener("open", () => setConnection(true));
eventStream.addEventListener("error", () => setConnection(false));
eventStream.addEventListener("state", (event) => render(JSON.parse(event.data)));
