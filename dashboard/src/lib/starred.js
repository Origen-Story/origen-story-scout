const STORAGE_KEY = "origen_story_scout_starred";

function canUseStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function loadStarred() {
  if (!canUseStorage()) return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const data = JSON.parse(raw);
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

function saveStarred(items) {
  if (!canUseStorage()) return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

export function getStarredArray() {
  return loadStarred();
}

export function isStarred(id) {
  return loadStarred().some((item) => item.id === id);
}

export function toggleStar(story) {
  const items = loadStarred();
  const index = items.findIndex((item) => item.id === story.id);
  if (index >= 0) {
    items.splice(index, 1);
  } else {
    items.unshift({
      id: story.id,
      title: story.title,
      url: story.url,
      source_name: story.source_name,
    });
  }
  saveStarred(items);
}

export function clearAllStarred() {
  if (!canUseStorage()) return;
  window.localStorage.removeItem(STORAGE_KEY);
}
