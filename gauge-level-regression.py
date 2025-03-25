import tensorflow as tf
import pandas as pd
import numpy as np
from PIL import Image, ImageFilter
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# Paths to images and labels
IMAGES_PATH = 'images/generated/gauges/'
LABELS_CSV = 'images/generated/labels.csv'

# Image parameters
IMG_HEIGHT = 224
IMG_WIDTH = 224
CHANNELS = 1

# Read labels CSV
labels_df = pd.read_csv(LABELS_CSV)
labels_df['filename'] = labels_df['filename'].apply(lambda x: os.path.join(IMAGES_PATH, x))


# Prepare images and labels
def load_image(image_path):
    image = Image.open(image_path)
    image = image.convert("L")  # Convert to grayscale
    image = image.filter(ImageFilter.FIND_EDGES)
    image = image.resize((IMG_WIDTH, IMG_HEIGHT))
    image = np.array(image, dtype=np.float32) / 255.0  # Normalize
    return image


images = np.array([load_image(img_path) for img_path in labels_df['filename']])
labels = labels_df['regression_label'].values.reshape(-1, 1)  # Make sure labels are 2D

# Scale labels to [0, 1] range
scaler = MinMaxScaler()
labels = scaler.fit_transform(labels)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, CHANNELS)),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Conv2D(256, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),

    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),

    tf.keras.layers.Dense(1)  # Single output neuron for regression
])

model.compile(optimizer='adam',
              loss='mean_squared_error',
              metrics=['mae'])  # Mean Absolute Error as additional metric


# Print the model summary
model.summary()

# Train the model
EPOCHS = 10
BATCH_SIZE = 32

history = model.fit(X_train, y_train,
                               epochs=EPOCHS,
                               batch_size=BATCH_SIZE,
                               validation_data=(X_test, y_test))

# Evaluate the model
test_loss, test_mae = model.evaluate(X_test, y_test)
print(f"Test MAE: {test_mae}")


