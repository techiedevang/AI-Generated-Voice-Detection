import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

MODEL_PATH = "model.pkl"

def generate_synthetic_data(n_samples=2000):
    """
    Generates synthetic audio features mimicking ASVspoof data.
    Features: [zcr, flatness, pitch_std, silence_ratio, duration]
    
    Human Voice Characteristics:
    - High pitch variability (pitch_std > 20)
    - Natural silence (silence_ratio > 0.1)
    - Higher ZCR noise (natural breath)
    
    AI Voice Characteristics:
    - Flat pitch (pitch_std < 15)
    - Very low spectral flatness (clean, < 0.01)
    - Low silence (continuous stream)
    """
    X = []
    y = []

    for _ in range(n_samples // 2):
        # HUMAN Class (Label 1)
        zcr = np.random.uniform(0.04, 0.15)
        flatness = np.random.uniform(0.02, 0.08)
        pitch_std = np.random.uniform(25.0, 80.0) # Highly dynamic
        silence = np.random.uniform(0.1, 0.4)
        duration = np.random.uniform(3.0, 10.0)
        
        X.append([zcr, flatness, pitch_std, silence, duration])
        y.append("HUMAN")

    for _ in range(n_samples // 2):
        # AI_GENERATED Class (Label 0)
        zcr = np.random.uniform(0.01, 0.06)
        flatness = np.random.uniform(0.001, 0.015) # Very clean
        pitch_std = np.random.uniform(0.5, 18.0) # Monotonic
        silence = np.random.uniform(0.0, 0.08) # Continuous
        duration = np.random.uniform(3.0, 10.0)

        X.append([zcr, flatness, pitch_std, silence, duration])
        y.append("AI_GENERATED")

    return np.array(X), np.array(y)

import os
import glob
import librosa

def load_real_data(dataset_dir="dataset"):
    """
    Attempts to load real ASVspoof data from the directory.
    Expected structure: dataset/LA/ASVspoof2019_LA_train/flac/*.flac
    And protocol: dataset/LA/ASVspoof2019_LA_cm_protocols/ASVspoof2019.LA.cm.train.trn.txt
    """
    protocol_path = os.path.join(dataset_dir, "LA", "ASVspoof2019_LA_cm_protocols", "ASVspoof2019.LA.cm.train.trn.txt")
    audio_dir = os.path.join(dataset_dir, "LA", "ASVspoof2019_LA_train", "flac")
    
    if not os.path.exists(protocol_path):
        print(f"Real dataset not found at {protocol_path}. Using synthetic data.")
        return None, None

    print(f"Loading real data from {dataset_dir}...")
    X = []
    y = []
    
    # Read labels
    # Format: SPEAKER_ID AUDIO_FILE_NAME SYSTEM_ID KEY(bonafide/spoof)
    file_labels = {}
    with open(protocol_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                filename = parts[1]
                label = "HUMAN" if parts[4] == "bonafide" else "AI_GENERATED"
                file_labels[filename] = label

    # Process files (Limit to 200 for demo speed if many exist)
    count = 0
    limit = 200 
    
    files = glob.glob(os.path.join(audio_dir, "*.flac"))
    print(f"Found {len(files)} audio files. Processing first {limit}...")
    
    for file_path in files[:limit]:
        filename = os.path.basename(file_path).replace(".flac", "")
        if filename in file_labels:
            try:
                # Load audio
                y_signal, sr = librosa.load(file_path, sr=22050)
                
                # Extract features (Same as audio_utils logic)
                zcr = np.mean(librosa.feature.zero_crossing_rate(y=y_signal))
                flatness = np.mean(librosa.feature.spectral_flatness(y=y_signal))
                pitches, magnitudes = librosa.piptrack(y=y_signal, sr=sr)
                pitch_values = pitches[magnitudes > np.median(magnitudes)]
                pitch_std = np.std(pitch_values) if len(pitch_values) > 0 else 0
                
                non_silent_intervals = librosa.effects.split(y_signal, top_db=20)
                non_silent_duration = sum([(end - start) for start, end in non_silent_intervals]) / sr
                total_duration = librosa.get_duration(y=y_signal, sr=sr)
                silence_ratio = 1.0 - (non_silent_duration / total_duration)

                X.append([zcr, flatness, pitch_std, silence_ratio, total_duration])
                y.append(file_labels[filename])
                count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print(f"Processed {count} real samples.")
    return np.array(X), np.array(y)

def train_and_save():
    print("Checking for real dataset...")
    X, y = load_real_data()
    
    if X is None or len(X) == 0:
        print("Generating synthetic dataset (Fallback)...")
        X, y = generate_synthetic_data()
    
    print(f"Dataset shape: {X.shape}")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train
    print("Training Random Forest Classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Evaluate
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Model Accuracy: {acc * 100:.2f}%")
    print(classification_report(y_test, preds))
    
    # Save
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_and_save()
