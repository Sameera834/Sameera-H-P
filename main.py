# ============================================================
# REAL-TIME OBJECT DETECTION SYSTEM (20 OBJECTS)
# YOLOv8 – FULL PIPELINE – FINAL FIXED VERSION
# ============================================================

import os
import sys
import cv2
import shutil
from ultralytics import YOLO

# ============================================================
# START CONFIRMATION
# ============================================================
print("🔥 main.py started successfully", flush=True)

# ============================================================
# CONFIGURATION
# ============================================================
DATASET_ROOT = r"dataset"        # must contain train/ and test/
YOLO_DATASET = r"yolo_dataset"
EPOCHS = 20                      # increase later if needed
IMG_SIZE = 640

CLASSES = [
    "person","plant","laptop","mobile","book",
    "chair","table","bottle","cup","bag",
    "pen","keyboard","mouse","monitor","television",
    "car","bicycle","dog","cat","clock"
]

# ============================================================
# STEP 0: VALIDATE DATASET PATHS
# ============================================================
def validate_paths():
    print("🔍 Validating dataset paths...", flush=True)

    if not os.path.exists(DATASET_ROOT):
        print(f"❌ Dataset root not found: {DATASET_ROOT}")
        sys.exit(1)

    for split in ["train", "test"]:
        path = os.path.join(DATASET_ROOT, split)
        if not os.path.exists(path):
            print(f"❌ Missing folder: {path}")
            sys.exit(1)

    print("✅ Dataset structure verified\n", flush=True)

# ============================================================
# STEP 1: CONVERT DATASET TO YOLO FORMAT
# ============================================================
def convert_dataset():
    print("🔄 Converting dataset to YOLO format...", flush=True)

    for split in ["train", "test"]:
        img_out = os.path.join(YOLO_DATASET, "images", split)
        lbl_out = os.path.join(YOLO_DATASET, "labels", split)
        os.makedirs(img_out, exist_ok=True)
        os.makedirs(lbl_out, exist_ok=True)

        for cls in CLASSES:
            src_dir = os.path.join(DATASET_ROOT, split, cls)
            if not os.path.exists(src_dir):
                continue

            class_id = CLASSES.index(cls)

            for img in os.listdir(src_dir):
                if not img.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue

                src_img = os.path.join(src_dir, img)
                new_name = f"{cls}_{img}"
                dst_img = os.path.join(img_out, new_name)

                shutil.copy(src_img, dst_img)

                label_path = os.path.join(
                    lbl_out, new_name.rsplit(".", 1)[0] + ".txt"
                )

                # Full-image bounding box (academic-safe)
                with open(label_path, "w") as f:
                    f.write(f"{class_id} 0.5 0.5 1.0 1.0\n")

    print("✅ Dataset conversion completed\n", flush=True)

# ============================================================
# STEP 2: CREATE dataset.yaml
# ============================================================
def create_yaml():
    print("📄 Creating dataset.yaml...", flush=True)

    yaml_text = f"""path: {YOLO_DATASET}
train: images/train
val: images/test

nc: {len(CLASSES)}
names:
"""
    for c in CLASSES:
        yaml_text += f"  - {c}\n"

    with open("dataset.yaml", "w") as f:
        f.write(yaml_text)

    print("✅ dataset.yaml created\n", flush=True)

# ============================================================
# STEP 3: TRAIN YOLOv8 MODEL
# ============================================================
def train_model():
    print("🚀 Training YOLOv8 model...", flush=True)

    model = YOLO("yolov8n.pt")

    model.train(
        data="dataset.yaml",
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=8,
        verbose=True,
        device="cpu"   # change to "cuda" only if GPU is confirmed
    )

    print("✅ Training completed\n", flush=True)

# ============================================================
# STEP 4: EVALUATE MODEL (✅ FIXED METRICS)
# ============================================================
def evaluate_model():
    print("📊 Evaluating model...", flush=True)

    model = YOLO("runs/detect/train/weights/best.pt")
    metrics = model.val()

    # Correct YOLOv8 metric access
    precision = metrics.box.mp
    recall = metrics.box.mr

    if (precision + recall) > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0

    print("\n====== EVALUATION METRICS ======")
    print(f"Precision (mean): {precision:.4f}")
    print(f"Recall (mean)   : {recall:.4f}")
    print(f"F1-Score        : {f1:.4f}")
    print(f"mAP@50          : {metrics.box.map50:.4f}")
    print(f"mAP@50-95       : {metrics.box.map:.4f}")
    print("================================\n", flush=True)

# ============================================================
# STEP 5: REAL-TIME WEBCAM DETECTION
# ============================================================
def realtime_detection():
    print("🎥 Starting real-time webcam detection", flush=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Webcam not accessible", flush=True)
        return

    model = YOLO("runs/detect/train/weights/best.pt")

    print("🟢 Press ESC to exit webcam\n", flush=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame", flush=True)
            break

        results = model(frame, conf=0.4)
        annotated = results[0].plot()

        cv2.imshow("Real-Time Object Detection", annotated)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🛑 Webcam closed", flush=True)

# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    validate_paths()
    convert_dataset()
    create_yaml()
    train_model()
    evaluate_model()
    realtime_detection()

    print("\n🎉 PROGRAM COMPLETED SUCCESSFULLY", flush=True)
