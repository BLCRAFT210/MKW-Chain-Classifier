import numpy as np
import tensorflow as tf
import keras
from keras import layers

ONEHOT = ['F', 'H', 'W', 'D']
BATCH_SIZE = 5


def generator(folders):  # takes a list of folders of videos and yields a set of frames and the associated label
    def callable_generator():
        for folder in folders:
            result = []
            for i in range(25):
                frame = tf.keras.utils.load_img(
                    f'{folder}/{i}.png', grayscale=True)
                result.append(tf.keras.utils.img_to_array(frame))

            result = np.array(result)
            yield result, ONEHOT.index(folder[30])

    return callable_generator


test_folders = []
for i in range(250, 275):
    test_folders.append(f'/cluster/2023blai/TestingData/F/{i}')
    test_folders.append(f'/cluster/2023blai/TestingData/H/{i}')
    test_folders.append(f'/cluster/2023blai/TestingData/W/{i}')
    test_folders.append(f'/cluster/2023blai/TestingData/D/{i}')

output_signature = (tf.TensorSpec(shape=(None, None, None, 1),
                    dtype=tf.float32), tf.TensorSpec(shape=(), dtype=tf.int16))
test_ds = tf.data.Dataset.from_generator(
    generator(test_folders), output_signature=output_signature)
test_ds = test_ds.batch(BATCH_SIZE)

model = tf.keras.models.load_model('saved_model/model')
model.evaluate(test_ds, return_dict=True)

'''
result = []
for i in range(25):
    frame = tf.keras.utils.load_img(f'/cluster/2023blai/TrainingDataReduced/D/214/{i}.png', grayscale=True)
    result.append(tf.keras.utils.img_to_array(frame))
print(model.predict(np.array([result])))
'''
