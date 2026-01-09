<script>
  import { onMount } from "svelte";
  import "./app.css";
  import { isStarred, toggleStar, getStarredArray, clearAllStarred } from "./lib/starred.js";

  let report = { stories: [], generated_at: null };
  let loading = true;
  let error = null;
  let starredStories = [];
  let showStarredPanel = false;
  let activeFilter = null; // Active trending term filter

  function refreshStarred() {
    starredStories = getStarredArray();
  }

  function handleToggleStar(story) {
    toggleStar(story);
    refreshStarred();
    // Force reactivity for the main list
    report = { ...report };
  }

  function handleClearStarred() {
    if (confirm("Remove all starred stories?")) {
      clearAllStarred();
      refreshStarred();
      report = { ...report };
    }
  }

  function toggleFilter(term) {
    activeFilter = activeFilter === term ? null : term;
  }

  function storyMatchesTerm(story, term) {
    const searchText = `${story.title} ${story.content || ''}`.toLowerCase();
    const termLower = term.toLowerCase();
    return searchText.includes(termLower);
  }

  // Reactive filtered stories based on active filter
  $: filteredStories = activeFilter
    ? report.stories.filter(s => storyMatchesTerm(s, activeFilter))
    : report.stories;

  async function loadReport() {
    try {
      const resp = await fetch("/data/latest_report.json");
      if (!resp.ok) throw new Error("Report not found. Run the scout first.");
      report = await resp.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function formatDate(dateStr) {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  }

  onMount(() => {
    loadReport();
    refreshStarred();
  });
</script>

<div class="premium-container">
  <header>
    <div class="header-left">
      <div class="logo-area">
        <svg
          id="origen-logo"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 296 298"
          width="120"
          height="120"
        >
          <style>
            .st0 {
              fill: var(--sage);
            }
          </style>
          <path
            class="st0"
            d="M230.93,72.56c-8-.78-16.75-1.53-20.61-1.51-67.65.34-81.04,29-82.92,34.24l43.12-.17.04.06c10.93-.02,20.07,1.51,28.82,5.11,20.52,8.43,36.69,24.4,49.82,28.18,3.3.95,6.64,1.06,9.81.69-1.91-24.7-11.85-48.11-28.07-66.59h-.02,0Z"
          />
          <path
            class="st0"
            d="M218.28,60.2c-3.23-2.72-6.62-5.26-10.2-7.61-13.5,5.76-18.86,8.8-24.21,11.56,7.87-2.37,20.98-4.18,34.41-3.95Z"
          />
          <path
            class="st0"
            d="M225.5,139.11c-6.02-6.1-11.9-11.02-17.53-14.96-12.74-3.21-22.55-2.52-25.68,1.16l14.01,24-.02.02c15.93,26.37,14.21,43.51,10.26,84.66-.37,3.82.15,6.88,1.23,9.42,20.55-13.45,36.93-33.59,45.47-58.64.2-.59.37-1.18.56-1.77-3.02-6.58-6.17-13.22-7.87-16.19-4.59-8.02-11.6-18.73-20.44-27.7h0Z"
          />
          <path
            class="st0"
            d="M198.49,229.76c-.19.65-.41,1.32-.65,2.01-.17.54-.37,1.08-.56,1.64-.11.35-.24.71-.37,1.06-.24.65-.5,1.27-.73,1.92-.52,1.32-1.08,2.67-1.66,4.05-.26.6-.52,1.23-.8,1.85-.69,1.55-1.44,3.15-2.24,4.74-.39.8-.78,1.6-1.21,2.41-.41.8-.84,1.6-1.27,2.41-.34.65-.69,1.25-1.03,1.9,3.36-1.34,6.64-2.87,9.85-4.53,1.4-12.18,1.49-17.85,1.72-23.37-.15.63-.3,1.27-.5,1.94-.17.65-.35,1.29-.56,1.96h0Z"
          />
          <path
            class="st0"
            d="M170.89,193.74h-.11c-5.5,9.46-11.4,16.62-18.93,22.42-17.57,13.52-39.52,19.49-49.37,28.95-2.05,1.98-3.6,4.29-4.81,6.73,3.43,1.55,6.96,2.95,10.61,4.2,20.98,7.16,42.58,7.83,62.67,3.15,3.94-5.58,7.76-11.1,9.38-13.93,33.7-58.81,15.46-84.75,11.94-88.91l-21.39,37.38h0Z"
          />
          <path
            class="st0"
            d="M32.05,131.99c-.6,4.05-.95,8.11-1.08,12.14,10.84,8.13,15.95,11.17,20.83,14.29-5.73-5.41-13.41-15.24-19.75-26.43h0Z"
          />
          <path
            class="st0"
            d="M135.56,216.61c9.18-9.4,13.5-18.24,11.88-22.79l-27.7.11-.02-.02c-30.81.56-44.8-9.49-78.45-33.5-3.58-2.57-6.94-3.62-10.03-3.73,2.05,26.32,13.19,51.16,31.33,70.15,6.92.65,13.78,1.21,17.07,1.23,9.23.04,22.01-.63,34.19-3.79,8.3-2.13,15.5-4.76,21.73-7.65h0Z"
          />
          <path
            class="st0"
            d="M105.61,129.34l13.26-23.13h-.04c14.98-27.7,30.59-34.77,68.6-52.17,4.68-2.16,7.42-5.04,8.97-8.17-4.61-2.31-9.42-4.35-14.42-6.06-12.2-4.16-24.6-6.12-36.8-6.12-7.89,0-15.72.82-23.33,2.41-4.74,6.64-9.94,14.01-11.92,17.4-4.66,7.98-10.46,19.38-13.84,31.52-2.29,8.26-3.62,15.8-4.25,22.64,3.56,12.65,9.03,20.83,13.78,21.69h0Z"
          />
          <path
            class="st0"
            d="M115.64,186.93l-21.67-37.19.06-.13c-5.48-9.49-8.71-18.2-9.96-27.62-2.91-21.97,2.91-43.96-.37-57.24-.91-3.71-2.78-6.94-5-9.72-9.38,6.68-17.81,14.83-24.9,24.23-7.07,9.4-12.81,20.07-16.79,31.82-.37,1.06-.69,2.11-.99,3.15,3.21,7.11,6.73,14.62,8.6,17.83,34.08,58.68,65.69,55.82,71.02,54.87h0Z"
          />
          <path
            class="st0"
            d="M163.84,193.76l-8.9.04c-1.64,4.4-3.28,10.78-6.75,16.49,8.43-5.48,12.87-11.32,15.65-16.54h0Z"
          />
          <path
            class="st0"
            d="M101.9,135.85c-3-3.62-7.72-8.26-10.91-14.12.52,10.07,3.36,16.84,6.47,21.86l4.44-7.74Z"
          />
          <path
            class="st0"
            d="M174.06,111.15l4.48,7.7c4.61-.8,10.97-2.59,17.64-2.44-8.95-4.55-16.23-5.45-22.12-5.26Z"
          />
        </svg>
        <div class="title-group">
          <h1 class="page-title">
            <span class="title-origen">Origen Story</span>
            <span class="title-scout">Scout</span>
          </h1>
        </div>
      </div>
    </div>
    <div class="header-right">
      <button
        class="starred-toggle"
        class:has-starred={starredStories.length > 0}
        onclick={() => showStarredPanel = !showStarredPanel}
        title="View starred stories"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill={starredStories.length > 0 ? "currentColor" : "none"} stroke="currentColor" stroke-width="2">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        {#if starredStories.length > 0}
          <span class="starred-count">{starredStories.length}</span>
        {/if}
      </button>
      <div class="header-date">
        <p class="date-label">Last updated</p>
        <p class="date-value">
          {report.generated_at ? formatDate(report.generated_at) : "---"}
        </p>
      </div>
    </div>
  </header>

  <!-- Starred Stories Panel -->
  {#if showStarredPanel}
    <div class="starred-panel">
      <div class="starred-header">
        <h2>Starred Stories</h2>
        {#if starredStories.length > 0}
          <button class="clear-btn" onclick={handleClearStarred}>Clear All</button>
        {/if}
      </div>
      {#if starredStories.length === 0}
        <p class="starred-empty">No starred stories yet. Click the star icon on any story to save it for later.</p>
      {:else}
        <div class="starred-list">
          {#each starredStories as story}
            <div class="starred-item">
              <div class="starred-item-content">
                <a href={story.url} target="_blank" class="starred-title">{story.title}</a>
                <span class="starred-source">{story.source_name}</span>
              </div>
              <button class="unstar-btn" onclick={() => handleToggleStar(story)} title="Remove from starred">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}

  <!-- Trending Terms Bar -->
  {#if !loading && !error && report.trending_terms && report.trending_terms.length > 0}
    <div class="topic-stats-bar">
      <span class="bar-label">Trending:</span>
      {#each report.trending_terms as term}
        <button
          class="topic-chip"
          class:active={activeFilter === term.term}
          title="{term.count} sources: {term.sources.join(', ')}"
          onclick={() => toggleFilter(term.term)}
        >
          <span class="topic-name">{term.term}</span>
          <span class="topic-count">{term.count}</span>
        </button>
      {/each}
      {#if activeFilter}
        <button class="clear-filter-btn" onclick={() => activeFilter = null}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
          Clear filter
        </button>
      {/if}
    </div>
  {/if}

  <!-- Cross-Source Coverage Section -->
  {#if !loading && !error && report.cross_source_stories && report.cross_source_stories.length > 0}
    <div class="cross-source-section">
      <div class="cross-source-header">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" class="fire-icon">
          <path d="M12 2c-5.33 4.55-8 8.48-8 11.8 0 4.98 3.8 8.2 8 8.2s8-3.22 8-8.2c0-3.32-2.67-7.25-8-11.8z"/>
        </svg>
        <h3>Cross-Source Coverage</h3>
        <span class="cross-source-subtitle">Same story, multiple sources</span>
      </div>
      <div class="cross-source-list">
        {#each report.cross_source_stories as cluster}
          {@const clusterStories = report.stories.filter(s => cluster.story_ids.includes(s.id))}
          <div class="cross-source-item">
            <div class="cluster-topic">{cluster.topic}</div>
            <div class="cluster-sources">
              {#each clusterStories as story, i}
                <a href={story.url} target="_blank" class="source-link" title={story.title}>
                  {story.source_name}
                </a>{#if i < clusterStories.length - 1}<span class="source-separator">•</span>{/if}
              {/each}
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  {#if loading}
    <div class="empty-state">
      <h2>Scouting the network...</h2>
    </div>
  {:else if error}
    <div class="empty-state">
      <h2 style="color: #ff6b6b">Offline</h2>
      <p>{error}</p>
    </div>
  {:else if report.stories.length === 0}
    <div class="empty-state">
      <h2>Quiet morning...</h2>
      <p>No new relevant stories found in your feeds yet.</p>
    </div>
  {:else if filteredStories.length === 0}
    <div class="empty-state">
      <h2>No matches for "{activeFilter}"</h2>
      <p>Try selecting a different term or <button class="inline-btn" onclick={() => activeFilter = null}>clear the filter</button>.</p>
    </div>
  {:else}
    <!-- Top 9 Story Grid -->
    <div class="story-grid">
      {#each filteredStories.slice(0, 9) as story}
        <article class="story-card">
          <div class="card-badges">
            <div
              class="provenance-badge"
              title="Provenance: {story.provenance_rating}"
            >
              <div class="status-pin">?</div>
            </div>
          </div>

          <div class="source-row">
            <p class="source-tag">{story.source_name}</p>
          </div>

          <h2 class="story-title">{story.title}</h2>

          {#if story.summary && story.summary !== "Summary unavailable."}
            <div class="summary-block">
              <span class="summary-label">Summary:</span>
              <ul class="summary-list">
                {#each story.summary
                  .split("\n")
                  .filter((l) => l.trim() && l.trim().length > 10 && !l.includes("2-3 concise bullet points") && !l.includes("summary of the article")) as line}
                  <li class="summary-item">{line.replace(/^[*-]\s*/, "")}</li>
                {/each}
              </ul>
            </div>
          {/if}

          <div class="card-footer">
            <a href={story.url} target="_blank" class="story-link">
              <span>Read Original</span>
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M7 17L17 7M17 7H7M17 7V17" />
              </svg>
            </a>
            <div class="card-actions">
              {#if story.trending}
                <span class="trending-indicator" title="Trending: covered by multiple sources">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2c-5.33 4.55-8 8.48-8 11.8 0 4.98 3.8 8.2 8 8.2s8-3.22 8-8.2c0-3.32-2.67-7.25-8-11.8z"/>
                  </svg>
                </span>
              {/if}
              <button
                class="star-btn"
                class:starred={isStarred(story.id)}
                onclick={() => handleToggleStar(story)}
                title={isStarred(story.id) ? "Remove from starred" : "Star this story"}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill={isStarred(story.id) ? "currentColor" : "none"} stroke="currentColor" stroke-width="2">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </button>
              <span class="card-score" class:high={story.relevance_score >= 0.7}>
                {Math.round(story.relevance_score * 100)}%
              </span>
            </div>
          </div>
        </article>
      {/each}
    </div>

    <!-- Secondary Headlines List -->
    {#if filteredStories.length > 9}
      <section class="secondary-section">
        <h2 class="section-title">{activeFilter ? `More "${activeFilter}" Stories` : 'Additional Stories'}</h2>
        <div class="headline-list">
          {#each filteredStories.slice(9) as story}
            <div class="headline-item">
              <a href={story.url} target="_blank" class="headline-link">
                <span class="headline-title">
                  {#if story.trending}
                    <svg class="trending-icon-inline" width="12" height="12" viewBox="0 0 24 24" fill="var(--sage)">
                      <path d="M12 2c-5.33 4.55-8 8.48-8 11.8 0 4.98 3.8 8.2 8 8.2s8-3.22 8-8.2c0-3.32-2.67-7.25-8-11.8z"/>
                    </svg>
                  {/if}
                  {story.title}
                </span>
              </a>
              <div class="headline-meta">
                <span class="source-tag">{story.source_name}</span>
                <button
                  class="star-btn-small"
                  class:starred={isStarred(story.id)}
                  onclick={(e) => { e.preventDefault(); e.stopPropagation(); handleToggleStar(story); }}
                  title={isStarred(story.id) ? "Remove from starred" : "Star this story"}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill={isStarred(story.id) ? "currentColor" : "none"} stroke="currentColor" stroke-width="2">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                </button>
                <span
                  class="item-score"
                  class:high={story.relevance_score >= 0.7}
                  >{Math.round(story.relevance_score * 100)}%</span
                >
              </div>
            </div>
          {/each}
        </div>
      </section>
    {/if}
  {/if}
</div>

<style>
  /* Local styles if needed, but using app.css for core design */
</style>
