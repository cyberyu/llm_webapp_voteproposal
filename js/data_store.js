// Data persistence utility for LLM WebApp
const DataStore = {
    // Save data to localStorage
    save: function(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (e) {
            console.error('Error saving data to localStorage:', e);
            return false;
        }
    },
    
    // Load data from localStorage
    load: function(key, defaultValue = null) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : defaultValue;
        } catch (e) {
            console.error('Error loading data from localStorage:', e);
            return defaultValue;
        }
    },
    
    // Clear specific data
    clear: function(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('Error clearing data from localStorage:', e);
            return false;
        }
    },
    
    // Clear all data
    clearAll: function() {
        try {
            localStorage.clear();
            return true;
        } catch (e) {
            console.error('Error clearing all data from localStorage:', e);
            return false;
        }
    },
    
    // Keys for different data types
    keys: {
        ISSUERS: 'llm_webapp_issuers',
        PERFORMANCE_RESULTS: 'llm_webapp_performance_results',
        ACTIVE_PAGE: 'llm_webapp_active_page',
        PEERANALYSIS_CSV_DATA: 'llm_webapp_peeranalysis_csv_data',
        PEERANALYSIS_LARGE_CSV_DATA: 'llm_webapp_peeranalysis_large_csv_data',
        PEERANALYSIS_SELECTED_CATEGORY: 'llm_webapp_peeranalysis_selected_category',
        PEERANALYSIS_SELECTED_ISSUER: 'llm_webapp_peeranalysis_selected_issuer',
        PEERANALYSIS_COMPARISON_SORT: 'llm_webapp_peeranalysis_comparison_sort',
        // Keys used by peeranalysis_storage.js
        PEER_ANALYSIS: 'llm_webapp_peer_analysis',
        PEER_FILTERED_DATA: 'llm_webapp_peer_filtered_data',
        PEER_SELECTED_CATEGORY: 'llm_webapp_peer_selected_category',
        PEER_SELECTED_ISSUER: 'llm_webapp_peer_selected_issuer',
        PEER_COMPARISON_SORT: 'llm_webapp_peer_comparison_sort',
        LARGE_CSV_DATA: 'llm_webapp_large_csv_data'
    }
};
