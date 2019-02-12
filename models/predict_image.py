"""
Code to predict a single image
"""
from keras import models
from keras import layers
from keras.applications import Xception
from keras import regularizers
import numpy as np
from keras.preprocessing import image


def load(filename):
    """
    Load the file to predict
    """
    img = image.load_img(filename, target_size=(299, 299))
    np_image = image.img_to_array(img)
    np_image = np.array(np_image).astype('float32')/255

    # Make to a rank 4 (1, 299, 299, 3) -> 1 is for the batch size
    np_image = np.expand_dims(np_image, axis=0)

    return np_image


def create_model():
    """
    Create our fine-tuned model & load the weights
    """
    base_model = Xception(include_top=False, weights=None)

    # Add Custom FC
    x = base_model.output
    x = layers.Dense(128,
                     activation='relu',
                     kernel_regularizer=regularizers.l2(0.0075))(x)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.5)(x)
    predictions = layers.Dense(12, activation='softmax')(x)

    # Turn into model & load the weights
    model = models.Model(inputs=base_model.input, outputs=predictions)
    model.load_weights("../models/xception_finetune_12_reg_75_block4.h5")

    return model


def predict_image():
    """
    Predict & print the class probabilities for some image

    Images to use:
    1. David - Michaelangelo -> /train/HIGH RENAISSANCE/HIGH RENAISSANCE061.jpg
    """
    classes = ["BAROQUE", "EARLY RENAISSANCE", "HIGH RENAISSANCE", "IMPRESSIONISM", "MANNERISM",
               "MEDIEVAL", "MINIMALISM", "NEOCLASSICISM",  "REALISM", "ROCOCO",
               "ROMANTICISM", "SURREALISM"
               ]
    pic = load("../../sculpture_data/model_data/classes_12/train/HIGH RENAISSANCE/HIGH RENAISSANCE061.jpg")
    model = create_model()
    preds = model.predict(pic)

    for index in range(0, 12):
        print(classes[index], "->", "{}%".format(round(preds[0][index]*100, 2)))


if __name__ == "__main__":
    predict_image()

