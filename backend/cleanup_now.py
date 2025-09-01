#!/usr/bin/env python3
"""
Quick cleanup script to remove existing chunk WAV files.
"""

import os
import glob

def cleanup_existing_chunks():
    """Remove all existing chunk WAV files."""
    
    outputs_dir = "media/outputs"
    
    if not os.path.exists(outputs_dir):
        print(f"Directory {outputs_dir} not found!")
        return
    
    print(f"Cleaning up existing chunk files in {outputs_dir}...")
    
    # Find and remove all chunk WAV files
    chunk_pattern = os.path.join(outputs_dir, "chunk_*.wav")
    chunk_files = glob.glob(chunk_pattern)
    
    if chunk_files:
        print(f"Found {len(chunk_files)} chunk files to remove...")
        removed_count = 0
        
        for chunk_file in chunk_files:
            try:
                os.remove(chunk_file)
                removed_count += 1
                if removed_count % 10 == 0:  # Show progress every 10 files
                    print(f"  Removed {removed_count} files...")
            except Exception as e:
                print(f"  Error removing {chunk_file}: {e}")
        
        print(f"Successfully removed {removed_count} chunk files!")
    else:
        print("No chunk files found.")
    
    # Show remaining files
    print(f"\nRemaining files in {outputs_dir}:")
    remaining = os.listdir(outputs_dir)
    for file in remaining:
        if os.path.isfile(os.path.join(outputs_dir, file)):
            size = os.path.getsize(os.path.join(outputs_dir, file))
            print(f"  - {file} ({size} bytes)")
    
    print("\nCleanup completed!")

if __name__ == "__main__":
    cleanup_existing_chunks()
