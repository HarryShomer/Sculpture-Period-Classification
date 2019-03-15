"""
Code to predict a single image
"""
from keras import models
from keras import layers
from keras.applications import Xception
from keras import regularizers
import numpy as np
from keras.preprocessing import image
import os
import sys
import warnings


def load(filename):
    """
    Load the file to predict
    """
    img = image.load_img(filename, target_size=(299, 299))
    np_image = image.img_to_array(img)
    np_image = np.array(np_image).astype('float32')/255

    # Make to a rank 4 tensor (1, 299, 299, 3) -> 1 is for the batch size
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


def predict_image(pic_style):
    """
    Predict & print the class probabilities for some image

    Images to use:
    1. David - Michaelangelo -> ../../sculpture_data/model_data/classes_12/train/HIGH RENAISSANCE/HIGH RENAISSANCE061.jpg
    2. Clodion -> ../../sculpture_data/model_data/classes_12/train/ROCOiCO/ROCOCO090.jpg

    :param pic_style: style the pic belongs to

    :return None
    """
    classes = ["BAROQUE", "EARLY-RENAISSANCE", "HIGH-RENAISSANCE", "IMPRESSIONISM", "MANNERISM",
               "MEDIEVAL", "MINIMALISM", "NEOCLASSICISM",  "REALISM", "ROCOCO",
               "ROMANTICISM", "SURREALISM"
               ]

    if pic_style.upper() in classes:
        pic = load(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../", "examples", pic_style + ".jpg") )
        model = create_model()
        preds = model.predict(pic)
    else:
        print("Input is not a style")
        return

    # Match up pred with class & sort
    preds = [(classes[i], preds[0][i]) for i in range(len(preds[0]))]
    preds =  sorted(preds, key=lambda x: x[1], reverse=True)

    # Print the output nicely
    print("\n")
    print('{:18s} {:8}'.format("Style", "Probability%"))
    print("-------------------------------")
    for pred in preds:
        print('{:17s} | {:7.2f}%'.format(pred[0], pred[1]*100, 2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please supply a command line argument in the form of one of the styles")
    else:
        predict_image(sys.argv[1])

