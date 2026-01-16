/**
 * Starred stories management using localStorage.
 * Allows saving stories for later use in social posts and newsletters.
 * Supports tagging: Read Later, Share on Social, Newsletter
 */

const STORAGE_KEY = 'origen_starred_stories';

// Available tags for categorizing starred stories
export const TAGS = {
  READ_LATER: 'read_later',
  SHARE_SOCIAL: 'share_social',
  NEWSLETTER: 'newsletter'
};

export const TAG_LABELS = {
  [TAGS.READ_LATER]: 'Read Later',
  [TAGS.SHARE_SOCIAL]: 'Share on Social',
  [TAGS.NEWSLETTER]: 'Newsletter'
};

/**
 * Get all starred stories from localStorage
 * @returns {Object} Map of story ID to starred story data
 */
export function getStarredStories() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch (e) {
    console.error('Error reading starred stories:', e);
    return {};
  }
}

/**
 * Check if a story is starred
 * @param {string} storyId
 * @returns {boolean}
 */
export function isStarred(storyId) {
  const starred = getStarredStories();
  return storyId in starred;
}

/**
 * Star a story (save for later)
 * @param {Object} story - The story object to star
 * @param {Array} tags - Optional initial tags to apply
 */
export function starStory(story, tags = []) {
  const starred = getStarredStories();
  starred[story.id] = {
    id: story.id,
    title: story.title,
    url: story.url,
    source_name: story.source_name,
    summary: story.summary,
    relevance_score: story.relevance_score,
    starred_at: new Date().toISOString(),
    tags: tags
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(starred));
}

/**
 * Unstar a story (remove from saved)
 * @param {string} storyId
 */
export function unstarStory(storyId) {
  const starred = getStarredStories();
  delete starred[storyId];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(starred));
}

/**
 * Toggle star status for a story
 * @param {Object} story
 * @returns {boolean} New starred status
 */
export function toggleStar(story) {
  if (isStarred(story.id)) {
    unstarStory(story.id);
    return false;
  } else {
    starStory(story);
    return true;
  }
}

/**
 * Get count of starred stories
 * @returns {number}
 */
export function getStarredCount() {
  return Object.keys(getStarredStories()).length;
}

/**
 * Get all starred stories as an array, sorted by starred_at (newest first)
 * @returns {Array}
 */
export function getStarredArray() {
  const starred = getStarredStories();
  return Object.values(starred).sort((a, b) =>
    new Date(b.starred_at) - new Date(a.starred_at)
  );
}

/**
 * Clear all starred stories
 */
export function clearAllStarred() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({}));
}

/**
 * Get tags for a starred story
 * @param {string} storyId
 * @returns {Array} Array of tag strings
 */
export function getStoryTags(storyId) {
  const starred = getStarredStories();
  return starred[storyId]?.tags || [];
}

/**
 * Add a tag to a starred story
 * @param {string} storyId
 * @param {string} tag - One of TAGS values
 */
export function addTag(storyId, tag) {
  const starred = getStarredStories();
  if (starred[storyId]) {
    const tags = starred[storyId].tags || [];
    if (!tags.includes(tag)) {
      starred[storyId].tags = [...tags, tag];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(starred));
    }
  }
}

/**
 * Remove a tag from a starred story
 * @param {string} storyId
 * @param {string} tag - One of TAGS values
 */
export function removeTag(storyId, tag) {
  const starred = getStarredStories();
  if (starred[storyId] && starred[storyId].tags) {
    starred[storyId].tags = starred[storyId].tags.filter(t => t !== tag);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(starred));
  }
}

/**
 * Toggle a tag on a starred story
 * @param {string} storyId
 * @param {string} tag - One of TAGS values
 * @returns {boolean} New tag state (true if added, false if removed)
 */
export function toggleTag(storyId, tag) {
  const tags = getStoryTags(storyId);
  if (tags.includes(tag)) {
    removeTag(storyId, tag);
    return false;
  } else {
    addTag(storyId, tag);
    return true;
  }
}

/**
 * Check if a story has a specific tag
 * @param {string} storyId
 * @param {string} tag
 * @returns {boolean}
 */
export function hasTag(storyId, tag) {
  return getStoryTags(storyId).includes(tag);
}

/**
 * Get starred stories filtered by tag
 * @param {string} tag - One of TAGS values, or null for all
 * @returns {Array} Array of starred stories with the specified tag
 */
export function getStoriesByTag(tag) {
  const stories = getStarredArray();
  if (!tag) return stories;
  return stories.filter(story => (story.tags || []).includes(tag));
}

/**
 * Get count of stories with a specific tag
 * @param {string} tag
 * @returns {number}
 */
export function getTagCount(tag) {
  return getStoriesByTag(tag).length;
}

/**
 * Get all tag counts
 * @returns {Object} Map of tag to count
 */
export function getAllTagCounts() {
  const stories = getStarredArray();
  const counts = {
    [TAGS.READ_LATER]: 0,
    [TAGS.SHARE_SOCIAL]: 0,
    [TAGS.NEWSLETTER]: 0
  };

  stories.forEach(story => {
    (story.tags || []).forEach(tag => {
      if (counts[tag] !== undefined) {
        counts[tag]++;
      }
    });
  });

  return counts;
}

/**
 * Export newsletter-tagged stories as formatted text
 * @returns {string} Formatted newsletter content
 */
export function exportNewsletterContent() {
  const stories = getStoriesByTag(TAGS.NEWSLETTER);
  if (stories.length === 0) {
    return 'No stories tagged for newsletter.';
  }

  return stories.map(story => {
    const summary = story.summary && story.summary !== 'Summary unavailable.'
      ? story.summary.split('\n')[0].replace(/^[•\-\*]\s*/, '').trim()
      : '';
    const summaryLine = summary ? `\n${summary}` : '';
    return `**${story.title}**${summaryLine}\n${story.url}`;
  }).join('\n\n---\n\n');
}
