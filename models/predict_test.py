"""
Run evaluation of the test set
"""
from keras import models
from keras import layers
from keras.applications import Xception
from keras.preprocessing.image import ImageDataGenerator
from keras import regularizers
from keras import optimizers
import numpy as np


# Batch = 1 to cover every test image
BATCH_SIZE = 1
img_dimensions = (299, 299)
NUM_EPOCHS = 50
CLASSES = 12

train_images = 2387
test_images = 804


test_datagen = ImageDataGenerator(
    rescale=1./255
)

test_generator = test_datagen.flow_from_directory(
        directory='../../sculpture_data/model_data/classes_12/test',
        #directory=r"C:\Users\Jack\Desktop\harry\sculpture_data\model_data\classes_12\test",
        target_size=img_dimensions,
        color_mode="rgb",
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False,
        seed=42)


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

    model.compile(loss="categorical_crossentropy",
                  optimizer=optimizers.SGD(lr=1e-4, momentum=0.9),
                  metrics=["accuracy"])

    return model


def total_eval(model):
    """
    Get total accuracy & loss
    
    :param model: Cnn
    
    :return None
    """
    test_loss, test_acc = model.evaluate_generator(test_generator, steps=test_images // BATCH_SIZE, verbose=True)
    print('test acc:', test_acc)
    print("test loss:", test_loss)


def get_ind_preds(model):
    """
    Get individual predictions
    
    :param model: Cnn
    
    :return: Matrix of preds vs. True
    """
    predictions = model.predict_generator(test_generator, steps=test_images // BATCH_SIZE, verbose=1)
    test_preds = np.argmax(predictions, axis=1)
    test_trues = test_generator.classes

    # Save Preds
    test_predictions = []
    for foo, bar in zip(test_preds, test_trues):
        test_predictions.append([foo, bar])
    np.savetxt('test_preds.txt', np.array(test_predictions), fmt='%d')


if __name__ == "__main__":
    cnn_model = create_model()
    total_eval(cnn_model)

    # Must reset first!!!! Otherwise the results won't make sense
    test_generator.reset()
    get_ind_preds(cnn_model)


