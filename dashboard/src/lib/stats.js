/**
 * Publication usage statistics tracking.
 * Tracks stars, clicks, and shares per source for creator compensation allocation.
 */

const STORAGE_KEY = 'origen_publication_stats';

/**
 * Get all publication stats from localStorage
 * @returns {Object} Map of source_name to stats object
 */
export function getPublicationStats() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch (e) {
    console.error('Error reading publication stats:', e);
    return {};
  }
}

/**
 * Save stats to localStorage
 * @param {Object} stats
 */
function saveStats(stats) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(stats));
}

/**
 * Initialize or get stats for a source
 * @param {Object} stats - Current stats object
 * @param {string} sourceName
 * @returns {Object} The source's stats object
 */
function ensureSource(stats, sourceName) {
  if (!stats[sourceName]) {
    stats[sourceName] = {
      stars: 0,
      clicks: 0,
      shares: 0,
      newsletter_uses: 0,
      first_seen: new Date().toISOString(),
      last_activity: new Date().toISOString()
    };
  }
  return stats[sourceName];
}

/**
 * Record a star event for a source
 * @param {string} sourceName
 */
export function recordStar(sourceName) {
  const stats = getPublicationStats();
  const source = ensureSource(stats, sourceName);
  source.stars++;
  source.last_activity = new Date().toISOString();
  saveStats(stats);
}

/**
 * Record an unstar event (decrement stars)
 * @param {string} sourceName
 */
export function recordUnstar(sourceName) {
  const stats = getPublicationStats();
  if (stats[sourceName] && stats[sourceName].stars > 0) {
    stats[sourceName].stars--;
    stats[sourceName].last_activity = new Date().toISOString();
    saveStats(stats);
  }
}

/**
 * Record a click event for a source
 * @param {string} sourceName
 */
export function recordClick(sourceName) {
  const stats = getPublicationStats();
  const source = ensureSource(stats, sourceName);
  source.clicks++;
  source.last_activity = new Date().toISOString();
  saveStats(stats);
}

/**
 * Record a share event for a source
 * @param {string} sourceName
 */
export function recordShare(sourceName) {
  const stats = getPublicationStats();
  const source = ensureSource(stats, sourceName);
  source.shares++;
  source.last_activity = new Date().toISOString();
  saveStats(stats);
}

/**
 * Record a newsletter use for a source
 * @param {string} sourceName
 */
export function recordNewsletterUse(sourceName) {
  const stats = getPublicationStats();
  const source = ensureSource(stats, sourceName);
  source.newsletter_uses++;
  source.last_activity = new Date().toISOString();
  saveStats(stats);
}

/**
 * Calculate weighted score for a source
 * Weights: stars=3, clicks=1, shares=5, newsletter=10
 * @param {Object} sourceStats
 * @returns {number}
 */
export function calculateScore(sourceStats) {
  return (
    (sourceStats.stars || 0) * 3 +
    (sourceStats.clicks || 0) * 1 +
    (sourceStats.shares || 0) * 5 +
    (sourceStats.newsletter_uses || 0) * 10
  );
}

/**
 * Get ranked publications by usage score
 * @returns {Array} Array of {name, stats, score, percentage} sorted by score desc
 */
export function getRankedPublications() {
  const stats = getPublicationStats();
  const entries = Object.entries(stats);

  if (entries.length === 0) {
    return [];
  }

  // Calculate scores
  const scored = entries.map(([name, sourceStats]) => ({
    name,
    stats: sourceStats,
    score: calculateScore(sourceStats)
  }));

  // Sort by score descending
  scored.sort((a, b) => b.score - a.score);

  // Calculate total score and percentages
  const totalScore = scored.reduce((sum, s) => sum + s.score, 0);

  return scored.map(s => ({
    ...s,
    percentage: totalScore > 0 ? (s.score / totalScore) * 100 : 0
  }));
}

/**
 * Calculate budget allocation based on usage
 * @param {number} monthlyBudget - Total monthly budget in dollars
 * @returns {Array} Array of {name, score, percentage, allocation} sorted by allocation desc
 */
export function calculateBudgetAllocation(monthlyBudget = 50) {
  const ranked = getRankedPublications();

  return ranked.map(pub => ({
    ...pub,
    allocation: (pub.percentage / 100) * monthlyBudget
  }));
}

/**
 * Get total usage counts across all sources
 * @returns {Object} {totalStars, totalClicks, totalShares, totalNewsletterUses, totalSources}
 */
export function getTotalStats() {
  const stats = getPublicationStats();
  const entries = Object.values(stats);

  return {
    totalStars: entries.reduce((sum, s) => sum + (s.stars || 0), 0),
    totalClicks: entries.reduce((sum, s) => sum + (s.clicks || 0), 0),
    totalShares: entries.reduce((sum, s) => sum + (s.shares || 0), 0),
    totalNewsletterUses: entries.reduce((sum, s) => sum + (s.newsletter_uses || 0), 0),
    totalSources: entries.length
  };
}

/**
 * Clear all publication stats
 */
export function clearAllStats() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({}));
}

/**
 * Export stats as JSON for backup
 * @returns {string}
 */
export function exportStats() {
  return JSON.stringify(getPublicationStats(), null, 2);
}
