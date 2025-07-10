import pandas as pd

def filter_csv_data():
    """
    Filter the 2025_error_proposals.csv file based on the criteria:
    - mgmt_rec equals 'F'
    - proposal_type equals 'MG'
    Use ForRatioAmongVoted_true as the SOLE rule for approval/rejection:
      - Approved: ForRatioAmongVoted_true >= 0.5
      - Rejected: ForRatioAmongVoted_true < 0.5
    Also create a full dataset for analysis that includes all proposals for proper approval rate calculation
    """
    
    # Load the CSV file from the Downloads directory
    csv_file_path = '/home/syu2/Downloads/2025_Predictions_All_Issuers_v9.csv'
    
    try:
        # Read the CSV file
        print("Loading CSV file...")
        df = pd.read_csv(csv_file_path)
        print(f"Original dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 5 rows of the original data:")
        print(df.head())
        print(f"\nUnique values in mgmt_rec: {df['mgmt_rec'].unique()}")
        print(f"Unique values in proposal_type: {df['proposal_type'].unique()}")
        # Convert ForRatioAmongVoted_true to numeric for filtering
        def convert_for_ratio(value):
            if pd.isna(value):
                return 0.0
            try:
                if isinstance(value, str) and value.endswith('%'):
                    return float(value.rstrip('%')) / 100.0
                else:
                    return float(value)
            except (ValueError, TypeError):
                return 0.0
        # Only keep proposals with mgmt_rec='F' and proposal_type='MG'
        base_df = df[(df['mgmt_rec'] == 'F') & (df['proposal_type'] == 'MG')].copy()
        base_df['ForRatio_numeric'] = base_df['ForRatioAmongVoted_true'].apply(convert_for_ratio)
        # Determine approval status solely from ForRatioAmongVoted_true
        base_df['approval_by_ratio'] = base_df['ForRatio_numeric'] >= 0.5
        # Full analysis dataset: all proposals with mgmt_rec='F' and proposal_type='MG'
        full_analysis_df = base_df.copy()
        # Filtered dataset: only rejected proposals (ForRatioAmongVoted_true < 0.5)
        filtered_df = base_df[base_df['ForRatio_numeric'] < 0.5].copy()
        print(f"\nFull analysis dataset shape: {full_analysis_df.shape}")
        print(f"Filtered dataset shape: {filtered_df.shape}")
        print(f"Rows removed: {df.shape[0] - filtered_df.shape[0]}")
        # Remove specified columns from filtered dataset
        columns_to_remove = ['director_master_skey', 'final_key', 'director_number', 'director_name']
        columns_to_remove_filtered = [col for col in columns_to_remove if col in filtered_df.columns]
        columns_to_remove_full = [col for col in columns_to_remove if col in full_analysis_df.columns]
        if columns_to_remove_filtered:
            filtered_df = filtered_df.drop(columns=columns_to_remove_filtered)
            print(f"\nRemoved columns from filtered dataset: {columns_to_remove_filtered}")
            print(f"Filtered dataset shape after removing columns: {filtered_df.shape}")
        if columns_to_remove_full:
            full_analysis_df = full_analysis_df.drop(columns=columns_to_remove_full)
            print(f"Removed columns from full analysis dataset: {columns_to_remove_full}")
            print(f"Full analysis dataset shape after removing columns: {full_analysis_df.shape}")
        # Display filtered data summary
        print("\nFiltered data summary:")
        print(filtered_df.head())
        # Save both datasets
        output_file = '/usr/project/llm_webapp_voteproposal/filtered_proposals.csv'
        filtered_df.to_csv(output_file, index=False)
        print(f"\nFiltered data saved to: {output_file}")
        full_output_file = '/usr/project/llm_webapp_voteproposal/full_analysis_proposals.csv'
        full_analysis_df.to_csv(full_output_file, index=False)
        print(f"Full analysis data saved to: {full_output_file}")
        # Display some statistics
        print(f"\nData statistics:")
        print(f"Total proposals in filtered data: {len(filtered_df)}")
        print(f"Total proposals in full analysis data: {len(full_analysis_df)}")
        print(f"Unique issuers in filtered data: {filtered_df['issuer_name'].nunique() if 'issuer_name' in filtered_df.columns else 'N/A'}")
        print(f"Unique issuers in full analysis data: {full_analysis_df['issuer_name'].nunique() if 'issuer_name' in full_analysis_df.columns else 'N/A'}")
        print(f"Approved proposals (by ForRatioAmongVoted_true >= 0.5): {full_analysis_df['approval_by_ratio'].sum()}")
        print(f"Rejected proposals (by ForRatioAmongVoted_true < 0.5): {(~full_analysis_df['approval_by_ratio']).sum()}")
        return filtered_df, full_analysis_df
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
        return None, None
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")
        return None, None

if __name__ == "__main__":
    filtered_data, full_data = filter_csv_data()
