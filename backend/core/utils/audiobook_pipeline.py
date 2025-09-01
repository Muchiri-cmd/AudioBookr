import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.utils.parser import extract_text, clean_text, to_chunks
from core.utils.tts import synth_piper, concat_wavs_to_mp3

def process_file_to_mp3(file_path, output_dir, voice_model, piper_exe, piper_model_dir,
                        chunk_size=300, max_workers=4):
    """Convert any document file into a single MP3 audiobook."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    #  Read and clean
    raw_text = extract_text(file_path)
    text = clean_text(raw_text)
    
    # Chunk text
    chunks = to_chunks(text, target_chars=chunk_size)
    
    #  Generate WAVs in parallel
    wav_paths = []
    def process_chunk(chunk_text, idx):
        wav_path = os.path.join(output_dir, f'chunk_{idx:03d}.wav')
        synth_piper(chunk_text, voice_model, wav_path, piper_exe, piper_model_dir)
        return wav_path
    
    #convert chunks to WAVS in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_chunk, chunk, i): i for i, chunk in enumerate(chunks)}
        for future in as_completed(futures):
            wav_paths.append(future.result())
    
    # Concatenate WAVs → MP3
    out_mp3 = os.path.join(output_dir, "final_output.mp3")
    concat_wavs_to_mp3(wav_paths, out_mp3)
    
    # Clean up temporary WAV chunks after creating final MP3
    cleanup_chunks(output_dir)
    
    return out_mp3

def cleanup_chunks(output_dir):
    """Remove all chunk WAV files after processing."""
    try:
        chunk_pattern = os.path.join(output_dir, "chunk_*.wav")
        chunk_files = glob.glob(chunk_pattern)
        for chunk_file in chunk_files:
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
                print(f"Cleaned up: {os.path.basename(chunk_file)}")
        print(f"Cleanup completed. Kept final MP3 in: {output_dir}")
    except Exception as e:
        print(f"Warning: Error during cleanup: {str(e)}")