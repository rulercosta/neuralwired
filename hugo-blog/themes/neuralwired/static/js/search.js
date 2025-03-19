let searchIndex;
let searchResults = [];
const searchInput = document.getElementById('search-input');
const searchResultsContainer = document.getElementById('search-results');

// Initialize lunr with loaded data
async function initializeSearch() {
    try {
        const response = await fetch('/index.json');
        const data = await response.json();
        
        searchIndex = lunr(function() {
            this.field('title', { boost: 10 });
            this.field('content');
            this.field('summary', { boost: 5 });
            this.ref('permalink');

            data.posts.forEach(post => {
                this.add(post);
            });
        });

        // Store the raw data for displaying results
        searchResults = data.posts;
    } catch (error) {
        console.error('Error initializing search:', error);
    }
}

function performSearch(query) {
    if (!query || !searchIndex) return;

    try {
        const results = searchIndex.search(query);
        displayResults(results);
    } catch (error) {
        console.error('Search error:', error);
    }
}

function displayResults(results) {
    if (!searchResultsContainer) return;

    if (results.length === 0) {
        searchResultsContainer.innerHTML = '<p>No results found</p>';
        return;
    }

    const html = results.map(result => {
        const post = searchResults.find(p => p.permalink === result.ref);
        if (!post) return '';
        
        return `
        <article class="search-result">
            <h3><a href="${post.permalink}">${post.title}</a></h3>
            <div class="post-meta">
                <span class="post-date">${post.date}</span>
            </div>
            <div class="post-excerpt">${post.summary}</div>
        </article>`;
    }).join('');

    searchResultsContainer.innerHTML = html;
}

// Initialize search when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeSearch);

// Setup search input handler
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value;
        if (query.length >= 2) {
            performSearch(query);
            searchResultsContainer.style.display = 'block';
        } else {
            searchResultsContainer.style.display = 'none';
        }
    });
}

// Close search results when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-container')) {
        searchResultsContainer.style.display = 'none';
    }
});
