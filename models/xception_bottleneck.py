from keras import models
from keras import layers
import matplotlib.pyplot as plt
import numpy as np
from keras.applications import Xception
from keras import regularizers
import os
import helpers

BATCH_SIZE = 16
NUM_EPOCHS = 25

# Get the image generator for 'adjusting' the images
train_datagen = helpers.fit_train_image_generator()
test_datagen = helpers.fit_test_image_generator()

train_generator = train_datagen.flow_from_directory(
        directory='../../sculpture_data/model_data/classes_12/train',
        target_size=helpers.IMG_DIMENSIONS,
        batch_size=BATCH_SIZE,
        color_mode="rgb",
        seed=42,
        shuffle=True,
        class_mode="categorical")

validation_generator = test_datagen.flow_from_directory(
        directory='../../sculpture_data/model_data/classes_12/validation',
        target_size=helpers.IMG_DIMENSIONS,
        batch_size=BATCH_SIZE,
        color_mode="rgb",
        seed=42,
        class_mode="categorical")


base_model = Xception(include_top=False, weights='imagenet')

# Freeze all layers!!!!!!!!!!!!!!!
for layer in base_model.layers:
    layer.trainable = False

# Add Custom FC
x = base_model.output
x = layers.Dense(128,
                 activation='relu',
                 kernel_regularizer=regularizers.l2(0.0075)
                 )(x)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.5)(x)
predictions = layers.Dense(helpers.CLASSES, activation='softmax')(x)

model = models.Model(inputs=base_model.input, outputs=predictions)

model.compile(loss="categorical_crossentropy", optimizer='rmsprop', metrics=["accuracy"])
cnn_model = model.fit_generator(
                train_generator,
                epochs=NUM_EPOCHS,
                steps_per_epoch=helpers.TRAIN_IMAGES // BATCH_SIZE,
                validation_data=validation_generator,
                validation_steps=helpers.VALIDATION_IMAGES // BATCH_SIZE,
                )

file_name = "xception_bottleneck_12_reg_0075"
print("Saving CNN as '{}'...".format(file_name + "h5"))
model.save(file_name + ".h5")

# plot the training loss and accuracy
N = NUM_EPOCHS
plt.style.use("ggplot")

# Accuracy
plt.figure()
plt.plot(np.arange(0, N), cnn_model.history["acc"], label="train_acc")
plt.plot(np.arange(0, N), cnn_model.history["val_acc"], label="val_acc")
plt.title("Training Accuracy on Dataset")
plt.xlabel("Epoch #")
plt.ylabel("Accuracy")
plt.legend(loc="lower left")
plt.savefig(f"{file_name}_acc_plot.png")

# Loss
plt.figure()
plt.plot(np.arange(0, N), cnn_model.history["loss"], label="train_loss")
plt.plot(np.arange(0, N), cnn_model.history["val_loss"], label="val_loss")
plt.title("Training Loss on Dataset")
plt.xlabel("Epoch #")
plt.ylabel("Loss")
plt.legend(loc="lower left")
plt.savefig(f"{file_name}_loss_plot.png")
