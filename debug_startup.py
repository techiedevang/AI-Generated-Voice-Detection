print("Starting imports...")
try:
    import torch
    print("Torch imported.")
    import torchaudio
    print("Torchaudio imported.")
    import speechbrain
    print("Speechbrain imported.")
    from core.lid import get_detector
    print("Core.lid imported.")
    
    # Initialize detector (trigger download)
    detector = get_detector()
    print("Detector initialized.")
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
