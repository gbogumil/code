import os

base_dir = '/lib/code/data'

image_names = list(f for f in os.listdir(base_dir) if f[-4:].lower() == '.bmp')

print(image_names[:10])

print('total images: ', len(image_names))

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

rows = 4
cols = 5

pic_index = 0

fig = plt.gcf()
fig.set_size_inches(cols*4, rows*4)

#pic_index += 8

#next_image = [os.path.join(base_dir, fname)
#              for fname in image_names[pic_index-8:pic_index]]

#for i, img_path in enumerate(next_image):
#    sp = plt.subplot(rows, cols, i+1)
#    sp.axis('Off')#
#
#    img = mpimg.imread(img_path)
#    plt.imshow(img)
#
#plt.show()


from tensorflow.keras import layers
from tensorflow.keras import Model

img_input = layers.Input(shape=(150,150,1))

x = layers.Conv2D(16,1, activation='relu')(img_input)
x = layers.MaxPooling2D(2)(x)

x = layers.Conv2D(32,1,activation='relu')(x)
x = layers.MaxPooling2D(2)(x)

x = layers.Conv2D(64, 1, activation='relu')(x)
x = layers.MaxPooling2D(2)(x)

x = layers.Flatten()(x)

x = layers.Dense(512, activation='relu')(x)

output = layers.Dense(1, activation='sigmoid')(x)

model = Model(img_input, output)

model.summary()

from tensorflow.keras.optimizers import RMSprop

model.compile(loss='binary_crossentropy',
              optimizer=RMSprop(lr=0.001),
              metrics=['acc'])


from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(rescale=1./255)
val_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory