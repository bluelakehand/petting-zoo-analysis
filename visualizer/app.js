let replay = null;
let tournament = null;
let tournamentBaseUrl = null;
let gameCursor = 0;
let eventCursor = 0;

const fileInput = document.getElementById("fileInput");
const tournamentFileInput = document.getElementById("tournamentFileInput");
const tournamentControls = document.getElementById("tournamentControls");
const prevGameBtn = document.getElementById("prevGameBtn");
const nextGameBtn = document.getElementById("nextGameBtn");
const gameSelect = document.getElementById("gameSelect");
const gameSummary = document.getElementById("gameSummary");
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
  tournament = null;
  tournamentBaseUrl = null;
  tournamentControls.hidden = true;
  setReplay(JSON.parse(await file.text()));
});

tournamentFileInput.addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  tournamentBaseUrl = null;
  await setTournament(JSON.parse(await file.text()));
});

prevGameBtn.addEventListener("click", async () => {
  if (!tournament) return;
  gameCursor = Math.max(0, gameCursor - 1);
  await loadTournamentGame(gameCursor);
});

nextGameBtn.addEventListener("click", async () => {
  if (!tournament) return;
  gameCursor = Math.min(tournament.games.length - 1, gameCursor + 1);
  await loadTournamentGame(gameCursor);
});

gameSelect.addEventListener("change", async () => {
  gameCursor = Number(gameSelect.value);
  await loadTournamentGame(gameCursor);
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
  players.innerHTML = snapshot.players.map((player) => renderPlayer(player, event)).join("");
  market.innerHTML = (snapshot.supply || snapshot.market || replay.supply || replay.market || []).map(renderMarketCard).join("");
}

async function loadReplayFromQuery() {
  const params = new URLSearchParams(window.location.search);
  const tournamentPath = params.get("tournament");
  if (tournamentPath) {
    const tournamentUrl = new URL(tournamentPath, window.location.href);
    const response = await fetch(tournamentUrl);
    tournamentBaseUrl = tournamentUrl;
    await setTournament(await response.json());
    return;
  }
  const replayPath = params.get("replay");
  if (!replayPath) return;
  const response = await fetch(replayPath);
  setReplay(await response.json());
}

function setReplay(nextReplay) {
  replay = nextReplay;
  window.replay = replay;
  eventCursor = 0;
  resetTimeline();
}

async function setTournament(nextTournament) {
  tournament = nextTournament;
  gameCursor = 0;
  renderTournamentControls();
  await loadTournamentGame(0);
}

async function loadTournamentGame(index) {
  const entry = tournament.games[index];
  if (!entry) return;
  gameCursor = index;
  gameSelect.value = String(index);
  if (entry.replay_payload) {
    setReplay(entry.replay_payload);
  } else if (entry.replay) {
    const replayUrl = tournamentBaseUrl ? new URL(entry.replay, tournamentBaseUrl) : entry.replay;
    const response = await fetch(replayUrl);
    setReplay(await response.json());
  } else {
    throw new Error(`Tournament game ${entry.game_id} has no replay data.`);
  }
  renderTournamentControls();
}

function renderTournamentControls() {
  if (!tournament) {
    tournamentControls.hidden = true;
    return;
  }
  tournamentControls.hidden = false;
  gameSelect.innerHTML = tournament.games.map((game, index) => {
    const label = `Game ${game.game_id} | ${game.winner_policy} wins | turn ${game.turn_number}`;
    return `<option value="${index}">${escapeHtml(label)}</option>`;
  }).join("");
  gameSelect.value = String(gameCursor);
  const game = tournament.games[gameCursor];
  gameSummary.textContent = game
    ? `${gameCursor + 1} / ${tournament.games.length} | seed ${game.seed} | P${game.winner_id} ${game.winner_policy}`
    : "";
}

function resetTimeline() {
  eventSlider.max = Math.max(0, replay.events.length - 1);
  eventSlider.value = 0;
  render();
}

function metric(label, value) {
  return `<div class="metric"><strong>${escapeHtml(label)}</strong><div>${escapeHtml(String(value))}</div></div>`;
}

function renderPlayer(player, event) {
  const board = boardCells(player);
  const cells = board.cells.map((placed) => renderPlacedCard(player, placed, event)).join("");
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

function renderPlacedCard(player, placed, event) {
  if (!placed) {
    return `<div class="cell empty"></div>`;
  }
  const card = replay.card_catalog[placed.card_id];
  const hasPawn = player.pawn[0] === placed.position[0] && player.pawn[1] === placed.position[1];
  const isVisitedMove = hasPawn && event?.kind === "move" && event?.player_id === player.player_id;
  const image = card.image ? `<img class="cardImage" src="${escapeHtml(card.image)}" alt="${escapeHtml(card.name)}">` : "";
  return `
    <div class="cell ${hasPawn ? "pawn" : ""} ${isVisitedMove ? "visitedMove" : ""}">
      ${image}
      ${hasPawn ? `<div class="pawnToken" title="Player ${player.player_id} pawn">P${player.player_id}</div>` : ""}
      <div class="cardOverlay">
        <div class="cardName">${escapeHtml(card.name)}</div>
        <div class="cardMeta">${escapeHtml(card.kind)} | ${placed.position.join(", ")}</div>
      </div>
      ${placed.tokens ? `<div class="cardMeta">${placed.tokens} token(s)</div>` : ""}
    </div>
  `;
}

function renderMarketCard(entry) {
  const cardId = typeof entry === "string" ? entry : entry.card_id;
  const count = typeof entry === "string" ? "" : `<div class="stackCount">${entry.count} left</div>`;
  const card = replay.card_catalog[cardId];
  const image = card.image ? `<img class="cardImage" src="${escapeHtml(card.image)}" alt="${escapeHtml(card.name)}">` : "";
  return `
    <div class="cell marketCell">
      ${image}
      ${count}
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
