import mediapipe as mp
import time
from ultralytics import YOLO
import cv2
import numpy as np


bones = {
    0: ["Wrist", 0, 0],
    1: ["", 0, 0],
    2: ["TME", 0, 0],
    3: ["TPP", 0, 0],
    4: ["TDP", 0, 0],
    5: ["IME", 0, 0],
    6: ["IPP", 0, 0],
    7: ["IMP", 0, 0],
    8: ["IDP", 0, 0],
    9: ["MME", 0, 0],
    10: ["MPP", 0, 0],
    11: ["MMP", 0, 0],
    12: ["MDP", 0, 0],
    13: ["RME", 0, 0],
    14: ["RPP", 0, 0],
    15: ["RMP", 0, 0],
    16: ["RDP", 0, 0],
    17: ["PME", 0, 0],
    18: ["PPP", 0, 0],
    19: ["PMP", 0, 0],
    20: ["PDP", 0, 0],
}


SKELETON_LABEL = {
    "DP": "Distal Phalanx",
    "MP": "Middle Phalanx",
    "PP": "Proximal Phalanx",
    "ME": "Metacarpal",
}
FINGER_LABEL = {"T": "Thumb", "I": "Index", "M": "Middle", "R": "Ring", "P": "Pinky"}


def CLAHE(xray: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=3)
    clahe_image = clahe.apply(xray)
    xray_rgb = cv2.cvtColor(clahe_image, cv2.COLOR_GRAY2RGB)
    return xray_rgb


def detect(img):
    model = YOLO(f"models/detection.pt")
    pred = model(img)
    try:
        pred = pred[0].boxes.xyxy[0].tolist()
        bbox = [int(i) for i in pred]
        cropped_image = img[bbox[1] : bbox[3], bbox[0] : bbox[2]]
    except:
        cropped_image = img
    return cropped_image


def masking(img: np.ndarray) -> np.ndarray:
    H, W, _ = img.shape
    model = YOLO(f"models/segmentation.pt")
    results = model(img)
    if results[0].masks is None:
        masked_img = img
    else:
        for result in results:
            for j, mask_pred in enumerate(result.masks.data):
                mask_pred = (mask_pred.cpu().numpy() * 255).astype(np.uint8)
                mask_pred = cv2.resize(mask_pred, (W, H))

        mask_pred = cv2.cvtColor(mask_pred, cv2.COLOR_GRAY2BGR)
        masked_img = cv2.bitwise_and(img, mask_pred)
    return masked_img


def is_fist(hand_landmarks):
    fingers = []
    for i in [8, 12, 16, 20]:  # Index, Middle, Ring, Pinky tips
        if hand_landmarks.landmark[i].y < hand_landmarks.landmark[i - 2].y:
            fingers.append(1)  # Extended
        else:
            fingers.append(0)  # Folded
    return sum(fingers) == 0  # If all fingers are folded, it's a fist


def extract_name(bn: str) -> str:
    if bn == "Wrist":
        return "Wrist"
    elif bn == "":
        return ""
    else:
        return FINGER_LABEL[bn[0]] + " " + SKELETON_LABEL[bn[1:3]]


def main():
    #  === X-ray image Processing  ===
    xray_img = cv2.imread("Input/x-ray.png", cv2.IMREAD_UNCHANGED)
    xray_rgb = CLAHE(xray_img)
    cropped_img = detect(xray_rgb)
    masked_img = masking(cropped_img)

    #  === Real Hand Detection and Tracking ===
    mp_hands = mp.solutions.hands
    # which detect only one hand and set confidence to 0.5
    hands = mp_hands.Hands(
        static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5
    )

    # === Variables ===
    opacity = 0.6  # default opacity of the X-ray image
    torelance_x = 40  # pixel
    torelance_y = 60  # pixel

    # open Webcam
    webcam = cv2.VideoCapture(0)

    while webcam.isOpened():
        success, frame = webcam.read()  # read the frame
        if not success:
            break

        # Flip the frame horizontally for a mirror effect"
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Convert BGR to RGB for MediaPipe processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process hand detection
        result = hands.process(rgb_frame)
        # Reset every frame
        xray_enabled = True
        left_hand = None
        right_hand = None

        # Hand Tracking if can detect then process next step, if not do nothing
        if result.multi_hand_landmarks:
            # separate object for each hand
            for i, hand_landmarks in enumerate(result.multi_hand_landmarks):
                hand_label = result.multi_handedness[i].classification[0].label
                if hand_label == "Left":
                    left_hand = hand_landmarks
                elif hand_label == "Right":
                    right_hand = hand_landmarks

            # check the hand if right hand and fist then disable x-ray
            if right_hand and is_fist(right_hand):
                xray_enabled = False
            else:
                xray_enabled = True

            if xray_enabled and right_hand is not None:

                # === 1. Overlay X-ray Image Using Right Hand ===
                # right_hand_landmarks = hand_positions["Right"]
                x_min, y_min = w, h
                x_max, y_max = 0, 0

                # Get bounding box of the right hand
                for i, landmark in enumerate(right_hand.landmark):
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    x_min, y_min = min(x_min, x), min(y_min, y)
                    x_max, y_max = max(x_max, x), max(y_max, y)

                    # # Draw a circle on the index fingertip
                    # cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)

                    # # Optional: Draw landmarks and connections
                    # mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    # save the landmark position for each bone
                    bones[i][1] = x
                    bones[i][2] = y

                # Expand the bounding box slightly
                padding = 50
                x_min, y_min = max(0, x_min - padding), max(0, y_min - padding)
                x_max, y_max = min(w, x_max + padding), min(h, y_max + padding)
                # cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), thickness=4)

                hand_width = x_max - x_min
                hand_height = y_max - y_min

                xray_resized = cv2.resize(masked_img, (hand_width, hand_height))

                # Extract Region of Interest from the frame which is the real hand and overlay by the x-ray image
                roi = frame[y_min:y_max, x_min:x_max]

                # create 2D alpha mask
                alpha = (
                    np.ones(
                        (xray_resized.shape[0], xray_resized.shape[1]), dtype=np.float32
                    )
                    * opacity
                )  # Default alpha
                # Convert alpha to 3-channel for blending
                alpha = np.expand_dims(alpha, axis=-1)  # Shape (h, w, 1)
                # Blend the images using alpha transparency
                roi = (
                    (1 - alpha) * roi.astype(np.float32)
                    + alpha * xray_resized.astype(np.float32)
                ).astype(np.uint8)

                # Replace the overlay region into the frame
                frame[y_min:y_max, x_min:x_max] = roi

                # === 2. Adjust Opacity Using Left Hand ===
                if left_hand:
                    # The screen start top-left corner is (0, 0)
                    # The hand landmarks are normalized to the range [0, 1]
                    # So, the higher the y value mean low position of the hand
                    index_finger_tip_y = left_hand.landmark[8].y
                    index_finger_pip_y = left_hand.landmark[6].y
                    middle_finger_tip_y = left_hand.landmark[12].y
                    middle_finger_pip_y = left_hand.landmark[10].y
                    ring_finger_tip_y = left_hand.landmark[16].y
                    ring_finger_pip_y = left_hand.landmark[14].y
                    pinky_finger_tip_y = left_hand.landmark[20].y
                    pinky_finger_pip_y = left_hand.landmark[18].y

                    # 3 fingure to increase opacity
                    if (
                        index_finger_tip_y < index_finger_pip_y
                        and middle_finger_tip_y < middle_finger_pip_y
                        and ring_finger_tip_y < ring_finger_pip_y
                        and pinky_finger_tip_y > pinky_finger_pip_y
                    ):
                        opacity = min(1.0, opacity + 0.005)
                    # 2 fingure to decrease opacity
                    elif (
                        index_finger_tip_y < index_finger_pip_y
                        and middle_finger_tip_y < middle_finger_pip_y
                        and ring_finger_tip_y > ring_finger_pip_y
                        and pinky_finger_tip_y > pinky_finger_pip_y
                    ):
                        opacity = max(0.0, opacity - 0.005)
                    # 1 figure to show tip for each bone
                    elif (
                        index_finger_tip_y < index_finger_pip_y
                        and middle_finger_tip_y > middle_finger_pip_y
                        and ring_finger_tip_y > ring_finger_pip_y
                        and pinky_finger_tip_y > pinky_finger_pip_y
                    ):  # condition
                        index_finger_tip_x = left_hand.landmark[8].x * w
                        index_finger_tip_y = left_hand.landmark[8].y * h
                        for i in range(0, 21):
                            if abs(
                                bones[i][1] - torelance_x
                            ) < index_finger_tip_x < abs(
                                bones[i][1] + torelance_x
                            ) and abs(
                                bones[i][2] - torelance_y
                            ) < index_finger_tip_y < abs(
                                bones[i][2] + torelance_y
                            ):
                                name = extract_name(bones[i][0])
                                cv2.putText(
                                    frame,
                                    name,
                                    (int(index_finger_tip_x), int(index_finger_tip_y)),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1,
                                    (0, 255, 0),
                                    4,
                                )
                                break

        cv2.imshow("X-ARay", frame)

        key = cv2.waitKey(1) & 0xFF  # Get the key input

        if key == ord("q"):  # Press 'q' to quit
            break
        elif key == ord(
            "c"
        ):  # Press 'c' to capture the overlay image for doctors to analyze
            timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")
            cv2.imwrite(f"Outputs/Overlay_{timestamp}.png", roi)

    webcam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
