let replay = null;
let eventCursor = 0;

const fileInput = document.getElementById("fileInput");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const eventSlider = document.getElementById("eventSlider");
const eventIndex = document.getElementById("eventIndex");
const summary = document.getElementById("summary");
const players = document.getElementById("players");
const eventDetails = document.getElementById("eventDetails");
const market = document.getElementById("market");

fileInput.addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  replay = JSON.parse(await file.text());
  eventCursor = 0;
  resetTimeline();
});

prevBtn.addEventListener("click", () => {
  if (!replay) return;
  eventCursor = Math.max(0, eventCursor - 1);
  eventSlider.value = eventCursor;
  render();
});

nextBtn.addEventListener("click", () => {
  if (!replay) return;
  eventCursor = Math.min(replay.events.length - 1, eventCursor + 1);
  eventSlider.value = eventCursor;
  render();
});

eventSlider.addEventListener("input", () => {
  eventCursor = Number(eventSlider.value);
  render();
});

function render() {
  if (!replay) {
    summary.innerHTML = "";
    players.innerHTML = "";
    market.innerHTML = "";
    eventDetails.textContent = "";
    return;
  }
  const event = replay.events[eventCursor] || null;
  const snapshot = event?.snapshot || replay;
  eventIndex.textContent = `${eventCursor + 1} / ${replay.events.length}`;
  summary.innerHTML = [
    metric("Seed", replay.seed),
    metric("Winner", snapshot.winner ?? "None"),
    metric("Turn", snapshot.turn_number ?? replay.turn_number),
    metric("Deck", snapshot.deck_count),
    metric("Discard", snapshot.discard_count),
  ].join("");
  eventDetails.textContent = event ? JSON.stringify(event, null, 2) : "No events";
  players.innerHTML = snapshot.players.map(renderPlayer).join("");
  market.innerHTML = snapshot.market.map(renderMarketCard).join("");
}

async function loadReplayFromQuery() {
  const replayPath = new URLSearchParams(window.location.search).get("replay");
  if (!replayPath) return;
  const response = await fetch(replayPath);
  replay = await response.json();
  eventCursor = 0;
  resetTimeline();
}

function resetTimeline() {
  eventSlider.max = Math.max(0, replay.events.length - 1);
  eventSlider.value = 0;
  render();
}

function metric(label, value) {
  return `<div class="metric"><strong>${escapeHtml(label)}</strong><div>${escapeHtml(String(value))}</div></div>`;
}

function renderPlayer(player) {
  const board = boardCells(player);
  const cells = board.cells.map((placed) => renderPlacedCard(player, placed)).join("");
  return `
    <article class="player">
      <div class="playerHeader">
        <strong>Player ${player.player_id}</strong>
        <span>${player.coins} coins | ${player.victory_points} VP</span>
      </div>
      <div class="zoo" style="--zoo-cols: ${board.cols}">${cells}</div>
    </article>
  `;
}

function renderPlacedCard(player, placed) {
  if (!placed) {
    return `<div class="cell empty"></div>`;
  }
  const card = replay.card_catalog[placed.card_id];
  const hasPawn = player.pawn[0] === placed.position[0] && player.pawn[1] === placed.position[1];
  const image = card.image ? `<img class="cardImage" src="${escapeHtml(card.image)}" alt="${escapeHtml(card.name)}">` : "";
  return `
    <div class="cell ${hasPawn ? "pawn" : ""}">
      ${image}
      <div class="cardOverlay">
        <div class="cardName">${escapeHtml(card.name)}</div>
        <div class="cardMeta">${escapeHtml(card.kind)} | ${placed.position.join(", ")}</div>
      </div>
      ${placed.tokens ? `<div class="cardMeta">${placed.tokens} token(s)</div>` : ""}
    </div>
  `;
}

function renderMarketCard(cardId) {
  const card = replay.card_catalog[cardId];
  const image = card.image ? `<img class="cardImage" src="${escapeHtml(card.image)}" alt="${escapeHtml(card.name)}">` : "";
  return `
    <div class="cell marketCell">
      ${image}
      <div class="cardOverlay">
        <div class="cardName">${escapeHtml(card.name)}</div>
        <div class="cardMeta">${card.cost} coins | ${card.victory_points} VP</div>
      </div>
    </div>
  `;
}

function boardCells(player) {
  const byPosition = new Map(player.zoo.map((placed) => [placed.position.join(","), placed]));
  const xs = player.zoo.map((placed) => placed.position[0]);
  const ys = player.zoo.map((placed) => placed.position[1]);
  const minX = Math.min(-2, ...xs);
  const maxX = Math.max(2, ...xs);
  const minY = Math.min(-2, ...ys);
  const maxY = Math.max(2, ...ys);
  const cells = [];
  for (let y = minY; y <= maxY; y += 1) {
    for (let x = minX; x <= maxX; x += 1) {
      cells.push(byPosition.get(`${x},${y}`) || null);
    }
  }
  return { cells, cols: maxX - minX + 1 };
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[char]));
}

loadReplayFromQuery().catch((error) => {
  eventDetails.textContent = `Failed to load replay: ${error.message}`;
});
