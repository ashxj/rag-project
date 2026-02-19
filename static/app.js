const categorySelect = document.getElementById("category");
const form = document.getElementById("search-form");
const queryInput = document.getElementById("query");
const statusNode = document.getElementById("status");
const resultsNode = document.getElementById("results");
const TOKEN_RE = /[\p{L}\p{N}_]+/gu;
const LV_CHAR_GROUPS = {
  a: "[aā]",
  ā: "[aā]",
  c: "[cč]",
  č: "[cč]",
  e: "[eē]",
  ē: "[eē]",
  g: "[gģ]",
  ģ: "[gģ]",
  i: "[iī]",
  ī: "[iī]",
  k: "[kķ]",
  ķ: "[kķ]",
  l: "[lļ]",
  ļ: "[lļ]",
  n: "[nņ]",
  ņ: "[nņ]",
  s: "[sš]",
  š: "[sš]",
  u: "[uū]",
  ū: "[uū]",
  z: "[zž]",
  ž: "[zž]",
};

async function loadCategories() {
  const response = await fetch("/api/categories");
  const payload = await response.json();
  const categories = payload.categories || [];

  const allOption = document.createElement("option");
  allOption.value = "";
  allOption.textContent = "Visas kategorijas";
  categorySelect.appendChild(allOption);

  for (const category of categories) {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    categorySelect.appendChild(option);
  }
}

function renderResults(items) {
  resultsNode.innerHTML = "";

  if (!items.length) {
    statusNode.textContent = "Nekas netika atrasts.";
    return;
  }

  statusNode.textContent = `Atrasto rezultātu skaits: ${items.length}`;

  for (const item of items) {
    const card = document.createElement("article");
    card.className = "card";

    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = `Kategorija: ${item.category} | Fails: ${item.source} | Rezultāts: ${item.score}`;

    const snippet = document.createElement("div");
    snippet.className = "snippet";
    snippet.innerHTML = highlightText(item.chunk, currentQueryTokens);

    card.appendChild(meta);
    card.appendChild(snippet);
    resultsNode.appendChild(card);
  }
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeRegex(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function queryToTokens(query) {
  const matches = query.toLowerCase().match(TOKEN_RE) || [];
  return [...new Set(matches)];
}

function tokenToLatvianFlexiblePattern(token) {
  let pattern = "";
  for (const char of token.toLowerCase()) {
    pattern += LV_CHAR_GROUPS[char] || escapeRegex(char);
  }
  return pattern;
}

function highlightText(text, tokens) {
  const safeText = escapeHtml(text);
  if (!tokens.length) return safeText;

  const alternation = tokens.map((token) => tokenToLatvianFlexiblePattern(token)).join("|");
  if (!alternation) return safeText;

  const pattern = new RegExp(`(${alternation})`, "giu");
  return safeText.replace(pattern, '<mark class="hit">$1</mark>');
}

let currentQueryTokens = [];

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();
  if (!query) return;
  currentQueryTokens = queryToTokens(query);

  statusNode.textContent = "Notiek meklēšana pa teksta daļām...";
  resultsNode.innerHTML = "";

  const response = await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      category: categorySelect.value || null,
      top_k: 5,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    statusNode.textContent = `Kļūda: ${error.detail || "neizdevās veikt meklēšanu"}`;
    return;
  }

  const payload = await response.json();
  renderResults(payload.results || []);
});

loadCategories().catch((error) => {
  statusNode.textContent = `Kategoriju ielādes kļūda: ${error.message}`;
});
