import os
from core.utils.parser import extract_text, clean_text, to_chunks
from core.utils.tts import synth_piper, concat_wavs_to_mp3

# -----------------------------
# 1. File to test
# -----------------------------
test_file = "Hey.docx"   # replace with your file path
output_dir = "test_output"
os.makedirs(output_dir, exist_ok=True)

# -----------------------------
# 2. Read and clean text
# -----------------------------
text = extract_text(test_file)
text = clean_text(text)
print(f"Extracted {len(text)} characters")

# -----------------------------
# 3. Chunk text
# -----------------------------
chunks = to_chunks(text, target_chars=1000)  # smaller chunks for testing
print(f"Created {len(chunks)} chunks")

# -----------------------------
# 4. Generate WAVs for each chunk
# -----------------------------
wav_paths = []
voice_model = "en_US-ryan-low.onnx"  # replace with your Piper model
for i, chunk in enumerate(chunks):
    wav_path = os.path.join(output_dir, f"chunk_{i:03d}.wav")
    synth_piper(chunk, voice_model, wav_path)
    wav_paths.append(wav_path)
    print(f"Chunk {i} saved to {wav_path}")

# -----------------------------
# 5. Concatenate WAVs to MP3
# -----------------------------
out_mp3 = os.path.join(output_dir, "final_output.mp3")
concat_wavs_to_mp3(wav_paths, out_mp3)
print(f"Final MP3 saved to {out_mp3}")
