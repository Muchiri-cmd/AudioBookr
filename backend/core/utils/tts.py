import os, subprocess
from typing import Optional
import soundfile as sf
import numpy as np

#converts a chunk of text to WAV using Piper.
def synth_piper(text: str, model_filename: str, out_wav: str,
                piper_exe: str, piper_model_dir: str, length_scale: float=1.0) -> None:
    
    exe = piper_exe
    model_path = os.path.join(piper_model_dir, model_filename)
    
    if not os.path.exists(exe):
        raise FileNotFoundError(f"Piper executable not found at {exe}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Piper model not found at {model_path}")
    
    #ensure output directory exists
    os.makedirs(os.path.dirname(out_wav), exist_ok=True)
    
    #call piper via cmd
    try:
        result = subprocess.run(
            [exe, '-m', model_path, '-f', out_wav, '--length_scale', str(length_scale)],
            input=text, #send text to piper
            check=True, #raise error if Piper fails
            capture_output=True,    #capture stdout/stderr
            text=True,
            encoding='utf-8'
        )
        
        if not os.path.exists(out_wav):
            raise RuntimeError(f"Piper did not create output file: {out_wav}")
            
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Piper TTS failed: {e.stderr}")
    except Exception as e:
        raise RuntimeError(f"Piper TTS error: {str(e)}")

#merges multiple WAV chunks and converts to MP3
def concat_wavs_to_mp3(wav_paths, out_mp3_path):
    os.makedirs(os.path.dirname(out_mp3_path), exist_ok=True)
    
    # Create temporary files
    list_file = out_mp3_path.replace('.mp3', '_list.txt')
    temp_wav = out_mp3_path.replace('.mp3', '_temp.wav')
    
    try:
        # Create file list for ffmpeg
        with open(list_file, 'w', encoding='utf-8') as f:
            for wav_path in wav_paths:
                if os.path.exists(wav_path):
                    abs_path = os.path.abspath(wav_path).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")
        
        #concatenate all wav chunks into single temporary wav
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0', 
            '-i', list_file, '-c', 'copy', 
            temp_wav
        ], check=True, capture_output=True, text=True)
        
        #convert temporary wav to mp3
        subprocess.run([
            'ffmpeg', '-i', temp_wav,
            '-acodec', 'libmp3lame', '-ab', '128k', out_mp3_path
        ], check=True, capture_output=True, text=True)
        
    except subprocess.CalledProcessError as e:
        #if ffmpeg fails, log the error and return the first wav path if it exists
        print(f"FFmpeg error: {e.stderr}")
        if wav_paths and os.path.exists(wav_paths[0]):
            import shutil
            wav_output = out_mp3_path.replace('.mp3', '.wav')
            shutil.copy2(wav_paths[0], wav_output)
            return wav_output
        raise RuntimeError(f"Failed to create audio output: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Please install FFmpeg and add it to your PATH.")
    finally:
        # Always clean up temporary files
        try:
            if os.path.exists(list_file):
                os.remove(list_file)
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
        except Exception as e:
            print(f"Warning: Could not remove temporary files: {e}")

def get_audio_duration(wav_path: str) -> float:
    try:
        data, samplerate = sf.read(wav_path)
        return len(data) / samplerate
    except Exception:
        return 0.0