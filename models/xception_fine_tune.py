import pandas as pd
from keras import models
from keras import layers
from keras import optimizers
from keras.applications import Xception
from keras.preprocessing.image import ImageDataGenerator
from keras import regularizers

BATCH_SIZE = 16
img_dimensions = (299, 299)
NUM_EPOCHS = 50
CLASSES = 12

train_images = 2387
validation_images = 802
test_images = 802


# Train & Test Data Generators
train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)
# We just rescale the test ones
test_datagen = ImageDataGenerator(
    rescale=1./255
)

train_generator = train_datagen.flow_from_directory(
        directory='../../sculpture_data/model_data/classes_12/train',
        target_size=img_dimensions,
        batch_size=BATCH_SIZE,
        color_mode="rgb",
        seed=42,
        shuffle=True,
        class_mode="categorical")

validation_generator = test_datagen.flow_from_directory(
        directory='../../sculpture_data/model_data/classes_12/validation',
        target_size=img_dimensions,
        batch_size=BATCH_SIZE,
        color_mode="rgb",
        seed=42,
        class_mode="categorical")


# Create and load weights
base_model = Xception(include_top=False, weights=None)

# Add Custom FC
x = base_model.output
x = layers.Dense(128,
                 activation='relu',
                 kernel_regularizer=regularizers.l2(0.0075))(x)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.5)(x)
predictions = layers.Dense(CLASSES, activation='softmax')(x)

# Freeze Layers
# Block 14 starts at index 126
# Block 13 starts at index 116
# Block 12 starts at index 106
# Block 11 starts at index  96
# Block 10 starts at index  86
# Block  9 starts at index  76
# Block  8 starts at index  66
# Block  7 starts at index  56
# Block  6 starts at index  46
# Block  5 starts at index  36
# Block  4 starts at index  26
# Block  3 starts at index  16

blocks = {"block14": 126, "block12": 106, "block10": 86, "block8": 66, "block6": 46, "block4": 26}

for block in blocks:
    file_name = f"xception_finetune_12_reg_75_{block}"

    for layer in range(len(base_model.layers)):
        if layer < 26:
            base_model.layers[layer].trainable = False
        else:
            base_model.layers[layer].trainable = True

    # Combine the base and layer
    # Load all weights from previously trained bottleneck
    model = models.Model(inputs=base_model.input, outputs=predictions)
    model.load_weights("xception_bottleneck_12_reg_0075.h5")

    # Compile and fit
    # Look at the optimizer
    model.compile(loss="categorical_crossentropy",
                  optimizer=optimizers.SGD(lr=1e-4, momentum=0.9),
                  metrics=["accuracy"])

    cnn_model = model.fit_generator(
                    train_generator,
                    epochs=NUM_EPOCHS,
                    steps_per_epoch=train_images // BATCH_SIZE,
                    validation_data=validation_generator,
                    validation_steps=validation_images // BATCH_SIZE,
                    )

    # Save the file
    print("Saving CNN as '{}'...".format(file_name))
    model.save(file_name + ".h5")

    # Save training/validation accuracy/loss
    val_loss_df = pd.DataFrame({
        'train_acc': cnn_model.history["acc"],
        'train_loss': cnn_model.history["loss"],
        "val_acc": cnn_model.history["val_acc"],
        "val_loss": cnn_model.history["val_loss"]
    })
    val_loss_df.to_csv(file_name + "val_loss.csv", sep=',')

