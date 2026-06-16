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
  eventIndex.textContent = `${eventCursor + 1} / ${replay.events.length}`;
  summary.innerHTML = [
    metric("Seed", replay.seed),
    metric("Winner", replay.winner ?? "None"),
    metric("Turn", event ? event.turn : replay.turn_number),
    metric("Deck", replay.deck_count),
    metric("Discard", replay.discard_count),
  ].join("");
  eventDetails.textContent = event ? JSON.stringify(event, null, 2) : "No events";
  players.innerHTML = replay.players.map(renderPlayer).join("");
  market.innerHTML = replay.market.map(renderMarketCard).join("");
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
  const cells = player.zoo
    .slice()
    .sort((a, b) => a.position[1] - b.position[1] || a.position[0] - b.position[0])
    .map((placed) => renderPlacedCard(player, placed))
    .join("");
  return `
    <article class="player">
      <div class="playerHeader">
        <strong>Player ${player.player_id}</strong>
        <span>${player.coins} coins | ${player.victory_points} VP</span>
      </div>
      <div class="zoo">${cells}</div>
    </article>
  `;
}

function renderPlacedCard(player, placed) {
  const card = replay.card_catalog[placed.card_id];
  const hasPawn = player.pawn[0] === placed.position[0] && player.pawn[1] === placed.position[1];
  return `
    <div class="cell ${hasPawn ? "pawn" : ""}">
      <div class="cardName">${escapeHtml(card.name)}</div>
      <div class="cardMeta">${escapeHtml(card.kind)} | ${placed.position.join(", ")}</div>
      ${placed.tokens ? `<div class="cardMeta">${placed.tokens} token(s)</div>` : ""}
    </div>
  `;
}

function renderMarketCard(cardId) {
  const card = replay.card_catalog[cardId];
  return `<div class="cell"><div class="cardName">${escapeHtml(card.name)}</div><div class="cardMeta">${card.cost} coins | ${card.victory_points} VP</div></div>`;
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
