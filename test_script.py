#!/usr/bin/env python3
import sys
import os

print("Script starting...")
print("Python version:", sys.version)
print("Current directory:", os.getcwd())

# Check if files exist
issuer_list_path = "/home/syu2/Downloads/issuer_distribution_list.csv"
peer_data_path = "/usr/project/llm_webapp_voteproposal/df_peer_analysis_unfavorable_propsals.csv"
large_data_path = "/usr/project/llm_webapp_voteproposal/df_peer_analysis_large_dataset.csv"

print(f"Issuer list exists: {os.path.exists(issuer_list_path)}")
print(f"Peer data exists: {os.path.exists(peer_data_path)}")
print(f"Large data exists: {os.path.exists(large_data_path)}")

if os.path.exists(issuer_list_path):
    with open(issuer_list_path, 'r') as f:
        lines = f.readlines()
    print(f"Issuer list has {len(lines)} lines")
    print("First 3 issuers:", [line.strip() for line in lines[:3]])

try:
    import pandas as pd
    print("Pandas imported successfully")
    
    if os.path.exists(peer_data_path):
        peer_df = pd.read_csv(peer_data_path)
        print(f"Peer dataset loaded: {len(peer_df)} rows, {len(peer_df.columns)} columns")
        print("Peer columns:", list(peer_df.columns)[:5])
        
    if os.path.exists(large_data_path):
        print("Loading large dataset...")
        large_df = pd.read_csv(large_data_path)
        print(f"Large dataset loaded: {len(large_df)} rows, {len(large_df.columns)} columns")
        print("Large columns:", list(large_df.columns)[:5])
        
except Exception as e:
    print(f"Error: {e}")

print("Test script completed.")
