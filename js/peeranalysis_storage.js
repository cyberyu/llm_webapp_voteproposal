/**
 * PeerAnalysisStorage - Utility for saving/loading peer analysis data
 */
const PeerAnalysisStorage = {
    keys: {
        CSV_DATA: 'peeranalysis_csv_data',
        LARGE_CSV_DATA: 'peeranalysis_large_csv_data',
        SELECTED_CATEGORY: 'peeranalysis_selected_category',
        SELECTED_ISSUER: 'peeranalysis_selected_issuer',
        COMPARISON_SORT_BY: 'peeranalysis_comparison_sort_by'
    },

    /**
     * Save CSV data to localStorage
     * Note: Due to localStorage size limits, we'll only save up to 1000 rows
     */
    saveCSVData: function(data) {
        if (!data || !data.length) return;
        
        try {
            // Only save up to 1000 rows to avoid exceeding localStorage limits
            const limitedData = data.slice(0, 1000);
            DataStore.set(this.keys.CSV_DATA, JSON.stringify(limitedData));
        } catch (error) {
            console.error("Error saving CSV data:", error);
        }
    },

    /**
     * Get CSV data from localStorage
     */
    getCSVData: function() {
        try {
            const data = DataStore.get(this.keys.CSV_DATA);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error("Error getting CSV data:", error);
            return null;
        }
    },

    /**
     * Save large CSV data to localStorage
     * Note: Due to localStorage size limits, we'll only save up to 500 rows
     */
    saveLargeCSVData: function(data) {
        if (!data || !data.length) return;
        
        try {
            // Only save up to 500 rows to avoid exceeding localStorage limits
            const limitedData = data.slice(0, 500);
            DataStore.set(this.keys.LARGE_CSV_DATA, JSON.stringify(limitedData));
        } catch (error) {
            console.error("Error saving large CSV data:", error);
        }
    },

    /**
     * Get large CSV data from localStorage
     */
    getLargeCSVData: function() {
        try {
            const data = DataStore.get(this.keys.LARGE_CSV_DATA);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error("Error getting large CSV data:", error);
            return null;
        }
    },

    /**
     * Save selected category
     */
    saveSelectedCategory: function(category) {
        DataStore.set(this.keys.SELECTED_CATEGORY, category || '');
    },

    /**
     * Get selected category
     */
    getSelectedCategory: function() {
        return DataStore.get(this.keys.SELECTED_CATEGORY) || '';
    },

    /**
     * Save selected issuer
     */
    saveSelectedIssuer: function(issuer) {
        DataStore.set(this.keys.SELECTED_ISSUER, issuer || '');
    },

    /**
     * Get selected issuer
     */
    getSelectedIssuer: function() {
        return DataStore.get(this.keys.SELECTED_ISSUER) || '';
    },

    /**
     * Save comparison sort by
     */
    saveComparisonSortBy: function(sortBy) {
        DataStore.set(this.keys.COMPARISON_SORT_BY, sortBy || 'total');
    },

    /**
     * Get comparison sort by
     */
    getComparisonSortBy: function() {
        return DataStore.get(this.keys.COMPARISON_SORT_BY) || 'total';
    }
};
