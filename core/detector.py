from models import ClassificationEnum
from core.audio_utils import load_audio_features
import joblib
import numpy as np
import os

MODEL_PATH = "model.pkl"

def classify_voice(base64_audio: str, language: str):
    """
    Main classification function.
    
    Args:
        base64_audio: Base64-encoded MP3
        language: One of [Tamil, English, Hindi, Malayalam, Telugu]
    
    Returns:
        {
            "classification": "HUMAN" or "AI_GENERATED",
            "confidenceScore": float (0.0-1.0),
            "explanation": str
        }
    """
    try:
        # Load model
        if not os.path.exists(MODEL_PATH):
            # Fallback if model missing (should run train_model.py)
            raise FileNotFoundError("Model file missing")
            
        clf = joblib.load(MODEL_PATH)
        
        # Extract features (Now returns correct dict keys matching new audio_utils)
        features_dict = load_audio_features(base64_audio)
        
        # Feature vector in correct order for model
        feature_vector = np.array([[
            features_dict["zero_crossing_rate"],
            features_dict["spectral_flatness"],
            features_dict["pitch_std"],
            features_dict["silence_ratio"],
            features_dict["duration"]
        ]])

        # Predict
        prediction_label = clf.predict(feature_vector)[0]
        
        # Get confidence
        probs = clf.predict_proba(feature_vector)[0]
        class_idx = list(clf.classes_).index(prediction_label)
        confidence = probs[class_idx]
        
        # Interpretation Logic
        explanation_map = {
            "HUMAN": {
                "high_pitch": features_dict["pitch_std"] > 20,
                "natural_silence": features_dict["silence_ratio"] > 0.1,
                "spectral_variance": features_dict["spectral_flatness"] > 0.02
            },
            "AI_GENERATED": {
                "flat_pitch": features_dict["pitch_std"] < 15,
                "continuous_stream": features_dict["silence_ratio"] < 0.08,
                "clean_spectrum": features_dict["spectral_flatness"] < 0.015
            }
        }
        
        reasons = []
        if prediction_label == "HUMAN":
            if explanation_map["HUMAN"]["high_pitch"]:
                reasons.append("Natural pitch variability")
            if explanation_map["HUMAN"]["natural_silence"]:
                reasons.append("Human breathing patterns")
            if explanation_map["HUMAN"]["spectral_variance"]:
                reasons.append("Complex spectral characteristics")
            explanation = " and ".join(reasons) if reasons else "Natural speech patterns detected"
        else:
            if explanation_map["AI_GENERATED"]["flat_pitch"]:
                reasons.append("Monotonic pitch")
            if explanation_map["AI_GENERATED"]["continuous_stream"]:
                reasons.append("No natural pauses")
            if explanation_map["AI_GENERATED"]["clean_spectrum"]:
                reasons.append("Overly clean audio")
            explanation = " and ".join(reasons) if reasons else "AI-like speech patterns detected"
            
        classification = ClassificationEnum(prediction_label)

        return {
            "classification": classification,
            "confidenceScore": round(float(confidence), 2),
            "explanation": explanation
        }

    except Exception as e:
        print(f"Detector Error: {e}")
        # Graceful fallback for demo/error purposes
        return {
            "classification": ClassificationEnum.HUMAN,
            "confidenceScore": 0.5,
            "explanation": f"Analysis uncertain due to processing error: {str(e)}"
        }
