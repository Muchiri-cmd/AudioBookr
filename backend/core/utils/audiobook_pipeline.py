import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from parser import extract_text, clean_text, to_chunks
from tts import synth_piper, concat_wavs_to_mp3

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
    
    return out_mp3