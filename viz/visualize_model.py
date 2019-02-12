from keras import models
from keras import layers
from keras.applications import Xception
from keras import regularizers
from keras.utils.vis_utils import plot_model

# Create and load weights
base_model = Xception(include_top=False, weights=None)

# Add Custom FC
x = base_model.output
x = layers.Dense(128,
                 activation='relu',
                 # TODO: Look!!!!!!!!!!!!!!
                 kernel_regularizer=regularizers.l2(0.0075))(x)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.5)(x)
predictions = layers.Dense(12, activation='softmax')(x)

model = models.Model(inputs=base_model.input, outputs=predictions)
model.load_weights("../models/xception_bottleneck_12_reg_0075.h5")

plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)



