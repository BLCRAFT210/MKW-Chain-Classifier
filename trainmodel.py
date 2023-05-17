# Tensorflow 2.12 has errors, so downgrade to 2.9

import random
import os
import random

import einops
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import tensorflow as tf
import keras
from keras import layers

EPOCHS = 500
HEIGHT = 186
WIDTH = 122
ONEHOT = ['F', 'H', 'W', 'D']


def generator(folders):  # takes a list of folders of videos and yields a set of frames and the associated label
    def callable_generator():
        for folder in folders:
            result = []
            for i in range(25):
                frame = tf.keras.utils.load_img(
                    f'{folder}/{i}.png', grayscale=True)
                result.append(tf.keras.utils.img_to_array(frame))

            result = np.array(result)
            yield result, ONEHOT.index(folder[38])

    return callable_generator


BATCH_SIZE = 5
train_folders, val_folders, test_folders = [], [], []
randOrder = [*range(250)]
random.shuffle(randOrder)
for i in range(200):
    train_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/F/{randOrder[i]}')
    train_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/H/{randOrder[i]}')
    train_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/W/{randOrder[i]}')
    train_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/D/{randOrder[i]}')

for i in range(200, 225):
    val_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/F/{randOrder[i]}')
    val_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/H/{randOrder[i]}')
    val_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/W/{randOrder[i]}')
    val_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/D/{randOrder[i]}')

for i in range(225, 250):
    test_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/F/{randOrder[i]}')
    test_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/H/{randOrder[i]}')
    test_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/W/{randOrder[i]}')
    test_folders.append(
        f'/cluster/2023blai/TrainingDataReduced/D/{randOrder[i]}')

output_signature = (tf.TensorSpec(shape=(None, None, None, 1),
                    dtype=tf.float32), tf.TensorSpec(shape=(), dtype=tf.int16))

train_ds = tf.data.Dataset.from_generator(
    generator(train_folders), output_signature=output_signature)
train_ds = train_ds.batch(BATCH_SIZE)
val_ds = tf.data.Dataset.from_generator(
    generator(val_folders), output_signature=output_signature)
val_ds = val_ds.batch(BATCH_SIZE)
test_ds = tf.data.Dataset.from_generator(
    generator(test_folders), output_signature=output_signature)
test_ds = test_ds.batch(BATCH_SIZE)


class Conv2Plus1D(keras.layers.Layer):
    def __init__(self, filters, kernel_size, padding):
        """
          A sequence of convolutional layers that first apply the convolution operation over the
          spatial dimensions, and then the temporal dimension. 
        """
        super().__init__()
        self.seq = keras.Sequential([
            # Spatial decomposition
            layers.Conv3D(filters=filters,
                          kernel_size=(1, kernel_size[1], kernel_size[2]),
                          padding=padding),
            # Temporal decomposition
            layers.Conv3D(filters=filters,
                          kernel_size=(kernel_size[0], 1, 1),
                          padding=padding)
        ])

    def call(self, x):
        return self.seq(x)


class ResidualMain(keras.layers.Layer):
    """
      Residual block of the model with convolution, layer normalization, and the
      activation function, ReLU.
    """

    def __init__(self, filters, kernel_size):
        super().__init__()
        self.seq = keras.Sequential([
            Conv2Plus1D(filters=filters,
                        kernel_size=kernel_size,
                        padding='same'),
            layers.LayerNormalization(),
            layers.ReLU(),
            Conv2Plus1D(filters=filters,
                        kernel_size=kernel_size,
                        padding='same'),
            layers.LayerNormalization()
        ])

    def call(self, x):
        return self.seq(x)


class Project(keras.layers.Layer):
    """
      Project certain dimensions of the tensor as the data is passed through different
      sized filters and downsampled.
    """

    def __init__(self, units):
        super().__init__()
        self.seq = keras.Sequential([
            layers.Dense(units),
            layers.LayerNormalization()
        ])

    def call(self, x):
        return self.seq(x)


def add_residual_block(input, filters, kernel_size):
    """
      Add residual blocks to the model. If the last dimensions of the input data
      and filter size does not match, project it such that last dimension matches.
    """
    out = ResidualMain(filters,
                       kernel_size)(input)

    res = input
    # Using the Keras functional APIs, project the last dimension of the tensor to
    # match the new filter size
    if out.shape[-1] != input.shape[-1]:
        res = Project(out.shape[-1])(res)

    return layers.add([res, out])


class ResizeVideo(keras.layers.Layer):
    def __init__(self, height, width):
        super().__init__()
        self.height = height
        self.width = width
        self.resizing_layer = layers.Resizing(self.height, self.width)

    def call(self, video):
        """
          Use the einops library to resize the tensor.  

          Args:
            video: Tensor representation of the video, in the form of a set of frames.

          Return:
            A downsampled size of the video according to the new height and width it should be resized to.
        """
        # b stands for batch size, t stands for time, h stands for height,
        # w stands for width, and c stands for the number of channels.
        old_shape = einops.parse_shape(video, 'b t h w c')
        images = einops.rearrange(video, 'b t h w c -> (b t) h w c')
        images = self.resizing_layer(images)
        videos = einops.rearrange(
            images, '(b t) h w c -> b t h w c',
            t=old_shape['t'])
        return videos


input_shape = (None, 25, HEIGHT, WIDTH, 1)
input = layers.Input(shape=(input_shape[1:]))
x = input

x = Conv2Plus1D(filters=16, kernel_size=(3, 7, 7), padding='same')(x)
x = layers.BatchNormalization()(x)
x = layers.ReLU()(x)
x = ResizeVideo(HEIGHT // 2, WIDTH // 2)(x)

# Block 1
x = add_residual_block(x, 16, (3, 3, 3))
x = ResizeVideo(HEIGHT // 4, WIDTH // 4)(x)

# Block 2
x = add_residual_block(x, 32, (3, 3, 3))
x = ResizeVideo(HEIGHT // 8, WIDTH // 8)(x)

# Block 3
x = add_residual_block(x, 64, (3, 3, 3))
x = ResizeVideo(HEIGHT // 16, WIDTH // 16)(x)

# Block 4
x = add_residual_block(x, 128, (3, 3, 3))

x = layers.GlobalAveragePooling3D()(x)
x = layers.Flatten()(x)
x = layers.Dense(4, 'softmax')(x)

model = keras.Model(input, x)

frames, label = next(iter(train_ds))
model.build(frames)

# Visualize the model
keras.utils.plot_model(model, to_file='model.png',
                       expand_nested=True, dpi=60, show_shapes=True)

model.compile(loss=keras.losses.SparseCategoricalCrossentropy(from_logits=False),
              optimizer=keras.optimizers.Adam(learning_rate=0.0001),
              metrics=['accuracy'])

callback = tf.keras.callbacks.EarlyStopping(
    monitor='loss', min_delta=0.0005, patience=10)

history = model.fit(x=train_ds,
                    epochs=EPOCHS,
                    validation_data=val_ds,
                    callbacks=[callback])


def plot_history(history):
    """
      Plotting training and validation learning curves.

      Args:
        history: model history with all the metric measures
    """
    fig, (ax1, ax2) = plt.subplots(2)

    fig.set_size_inches(18.5, 10.5)

    # Plot loss
    ax1.set_title('Loss')
    ax1.plot(history.history['loss'], label='train')
    ax1.plot(history.history['val_loss'], label='test')
    ax1.set_ylabel('Loss')

    # Determine upper bound of y-axis
    max_loss = max(history.history['loss'] + history.history['val_loss'])

    ax1.set_ylim([0, np.ceil(max_loss)])
    ax1.set_xlabel('Epoch')
    ax1.legend(['Train', 'Validation'])

    # Plot accuracy
    ax2.set_title('Accuracy')
    ax2.plot(history.history['accuracy'],  label='train')
    ax2.plot(history.history['val_accuracy'], label='test')
    ax2.set_ylabel('Accuracy')
    ax2.set_ylim([0, 1])
    ax2.set_xlabel('Epoch')
    ax2.legend(['Train', 'Validation'])

    plt.savefig('history.png')


plot_history(history)

print('Evaluating model')
model.evaluate(test_ds, return_dict=True)

try:
    os.mkdir('/cluster/2023blai/saved_model')
except:
    pass
model.save('/cluster/2023blai/saved_model/model')
