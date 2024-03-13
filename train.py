import os
import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase (replace with your credentials)
# cred = credentials.Certificate('path/to/firebase_credentials.json')
# firebase_admin.initialize_app(cred, {'storageBucket': 'your_storage_bucket'})
cred = credentials.Certificate("E:/my_studies/Majorproject/majorproject-550be-firebase-adminsdk-wzfdz-4b636ba1b9.json")
firebase_admin.initialize_app(cred,{
    'storageBucket':'majorproject-550be.appspot.com'
})
# Load LBPH recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Function to download images from Firebase Storage
def download_images_from_firebase(image_folder):
    bucket = storage.bucket()
    blobs = bucket.list_blobs(prefix=image_folder)
    for blob in blobs:
        filename = os.path.basename(blob.name)
        blob.download_to_filename(filename)

# Function to load images and labels
def load_images_and_labels(image_folder):
    images = []
    labels = []
    download_images_from_firebase(image_folder)
    for filename in os.listdir(image_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img_path = os.path.join(image_folder, filename)
            image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            label = int(os.path.basename(filename).split('.')[0])  # Assuming filenames are labeled with numbers
            images.append(image)
            labels.append(label)
    return images, labels

# Train the model
def train_model(image_folder):
    images, labels = load_images_and_labels(image_folder)
    recognizer.train(images, np.array(labels))
    recognizer.save("trained_model.yml")

# Example usage
if __name__ == '__main__':
    train_model("gs://majorproject-550be.appspot.com")
