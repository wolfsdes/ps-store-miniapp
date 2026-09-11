const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function getGames(params = {}) {
  const qs = new URLSearchParams();
  if (params.search) qs.set("search", params.search);
  if (params.platform && params.platform !== "all") qs.set("platform", params.platform);
  const res = await fetch(`${API}/games?${qs}`);
  if (!res.ok) throw new Error("Не удалось загрузить каталог");
  return res.json();
}

export async function getSettings() {
  const res = await fetch(`${API}/settings`);
  if (!res.ok) throw new Error("Не удалось загрузить настройки");
  return res.json();
}

export async function createOrder(payload) {
  const res = await fetch(`${API}/orders`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Не удалось создать заказ");
  }
  return res.json();
}
