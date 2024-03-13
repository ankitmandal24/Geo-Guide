
'''
# Team ID:			<1742>
# Author List:		<Ankit Mandal,Vikas Kumar,B Sai Sannidh Rayalu,Shashwat Bokhad>
# Filename:			<detection.py>
# Theme:            <GEOGUIDE>
# Functions:	    <`ViTForImageClassification`,`adjust_brightness_contrast(frame)`,`perform_prediction(model, frame, coordinates, class_names, threshold=0.45)`>
#Global_Variables:  <class_names>
###################################################################################################
'''
import cv2
import numpy as np
from PIL import Image
import torch
from torchvision.transforms import transforms
import torch.nn as nn
from transformers import ViTFeatureExtractor, ViTForImageClassification

class_names = ['Combat', 'Destroyed Buildings', 'Fire', 'Humanitarian Aid and Rehabilitation', 'Military Vehicles']


'''
* Function Name: ViTForImageClassification
* Input: num_labels (int) - number of labels for classification
* Output: None
* Logic:
Initializes a Vision Transformer (ViT) model for image classification with the specified number of output labels.
'''
class ViTForImageClassification(nn.Module):

    def __init__(self, num_labels=5):
        super(ViTForImageClassification, self).__init__()
        self.vit = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224-in21k')
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(self.vit.config.hidden_size, num_labels)
        self.num_labels = num_labels

    def forward(self, pixel_values):
        outputs = self.vit(pixel_values=pixel_values)
        output = self.dropout(outputs.last_hidden_state[:,0])
        logits = self.classifier(output)

        return logits


'''
* Function Name: adjust_brightness_contrast
* Input: image (numpy.ndarray) - input image, brightness (int) - brightness adjustment value, contrast (int) - contrast adjustment value
* Output: adjusted_image (numpy.ndarray) - image after brightness and contrast adjustment
* Logic:
Adjusts the brightness and contrast of the input image based on the provided values.
 Example Call:
    adjusted_image = adjust_brightness_contrast(image, brightness=10, contrast=20)
"""
'''
def adjust_brightness_contrast(image, brightness=-30, contrast=30):
    # Apply brightness adjustment

    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow

        # Apply brightness adjustment
        adjusted_image = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)
    else:
        adjusted_image = image.copy()

    # Apply contrast adjustment
    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)

        # Apply contrast adjustment
        adjusted_image = cv2.addWeighted(adjusted_image, alpha_c, adjusted_image, 0, gamma_c)

    return adjusted_image

"""
Function Name: perform_prediction
Input:
    model (ViTForImageClassification): ViT model for image classification
    frame (numpy array): Input image frame
    coordinates (list): Coordinates of the region of interest (ROI)
    class_names (list): List of class names
    threshold (float): Confidence threshold for prediction
Output:
    identified_labels (dict): Dictionary containing identified label and confidence
    hide_contour (bool): Flag to hide contour
    center_coordinates (tuple): Tuple containing center coordinates of the ROI
Logic:
    Performs prediction on the region of interest (ROI) in the input frame.

Example Call:
    identified_labels, hide_contour, center_coordinates = perform_prediction(model, frame, coordinates, class_names)
"""
def perform_prediction(model, frame, coordinates, class_names, threshold=0.45):

    identified_labels = {}

    # Calculate center coordinates based on the specified coordinates
    (x1, y1), (x2, y2) = coordinates
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    roi = frame[y1:y2, x1:x2] # region of interest for images inside the bounding box

    # Check if the ROI contains a valid image (not empty or too small)
    if roi.size == 0 or min(roi.shape[:2]) < 5:
        identified_labels['class'] = 'No Image'
        identified_labels['confidence'] = 0.0
        hide_contour = True
        return identified_labels, hide_contour, (center_x, center_y)

    pil_image = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    transform = transforms.Compose([
        transforms.Resize(size=(224, 224)),  # Adjust size for ViT model
        transforms.ToTensor(),
    ])
    input_data = transform(pil_image)
    input_data = input_data.unsqueeze(0)

    # Move the input tensor to the same device as the model
    input_data = input_data.to(device)

    with torch.no_grad():
        # Generate prediction
        logits = model(input_data)

        # Apply softmax to get probabilities
        probabilities = torch.nn.functional.softmax(logits, dim=1)[0]

        # Get predicted class index and confidence
        predicted_class_index = torch.argmax(probabilities).item()
        confidence = probabilities[predicted_class_index].item()

        # Map the index to your label
        predicted_class = class_names[predicted_class_index]

        identified_labels['class'] = predicted_class
        identified_labels['confidence'] = confidence

    # Hide contours if confidence is below the threshold
    hide_contour = confidence < threshold

    return identified_labels, hide_contour, (center_x, center_y)

if __name__ == "__main__":

    # Specify the contour coordinates,using for creating roi
    contour_coordinates = [((694, 922), (782,1003)),
                          ((1138,725), (1229, 809)),
                          ((1140, 528), (1234, 614)),
                          ((658, 537), (754, 625)),
                          ((665, 212), (761, 298))]

    #loading the model
    model=torch.load('odel1.pt')
    model.eval()

    # Move the model to the desired device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    identified_labels_dict = {}  # Initialize an empty list to store identified labels
    priority_list = ['fire', 'destroyed buildings', 'humanitarian aid and rehabilitation', 'military vehicles', 'combat']


    # Create a dictionary to store the identified labels in priority order
    priority_result_with_coordinates = {priority: [] for priority in priority_list}

    while True:
        ret, frame = cap.read()

        if not ret:
            print("End of video.")
            break

        frame = adjust_brightness_contrast(frame, brightness=-0, contrast=0)
        for i, coordinates in enumerate(contour_coordinates):
            # Check if coordinates are within bounds
            (x1, y1), (x2, y2) = coordinates
            if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
                print(f"Warning: Contour {i+1} coordinates are outside frame bounds.")
                continue

            # Perform prediction and check confidence
            prediction_result, hide_contour, center_coordinates = perform_prediction(model, frame, coordinates, class_names)

            # Display prediction information and hide contours if no image is placed
            if not hide_contour:
                identified_labels_dict[chr(65+i)] = f'{prediction_result["class"]}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f'{chr(65+i)}: {prediction_result["class"]}'
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


                if prediction_result['class'].lower() in priority_list:
                    priority_result_with_coordinates[prediction_result['class'].lower()].append({
                        'label': f'{chr(65+i)}:',
                        # 'confidence': prediction_result["confidence"],
                        'coordinates': center_coordinates
                    })

        # Resize the window
        frame_resized = cv2.resize(frame, (800, 800))

        cv2.imshow('Bounding Boxes with Predictions', frame_resized)
        cv2.waitKey(0)  # Change the waitKey value to control the frame rate

        # Break after processing the first frame
        break

        cap.release()
        cv2.destroyAllWindows()




    # Print the identified labels in the order of the priority list
    print("identified_labels =", identified_labels_dict)


    # Save the priority results with coordinates to a file (e.g., CSV)
    with open('priority_results_with_coordinate.txt', 'w') as f:
        for priority_label, result_info_list in priority_result_with_coordinates.items():
            for result_info in result_info_list:
                # Check if the label was not hidden
                if result_info['label'] != '':
                    label = result_info['label']
                    coordinates = result_info['coordinates']
                    f.write(f'{label} [{coordinates[0]}, {coordinates[1]}]\n')
