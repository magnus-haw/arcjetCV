# plot feature map of first conv layer for given image
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.models import Model
from matplotlib import pyplot
from numpy import expand_dims


from keras.models import Input,load_model
from keras.layers import Dropout,concatenate,UpSampling2D
from keras.layers import Conv2D, MaxPooling2D

from keras_segmentation.predict import predict_multiple
from keras_segmentation.train import find_latest_checkpoint
import cv2
from glob import glob
import os

TRAIN = 0
LOAD = 1
APPLY = 1
if (APPLY == 1) and (TRAIN == 0):
    img = cv2.imread("tests/pika4.png")
    height = img.shape[0]
    width= img.shape[1]
    pix = max(width, height)- (max(width, height) % 4)
    input_height,input_width = pix, pix
    print(input_width)
    print(input_height)
else:
    input_height,input_width = 128, 128
n_classes = 3
epochs= 2
ckpath = "checkpoints_mosaic/mynet_arcjetCV"

##############################################################################
img_input = Input(shape=(input_height,input_width , 3 ))

conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(img_input)
conv1 = Dropout(0.2)(conv1)
conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(conv1)
pool1 = MaxPooling2D((2, 2))(conv1)

conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')(pool1)
conv2 = Dropout(0.2)(conv2)
conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')(conv2)
pool2 = MaxPooling2D((2, 2))(conv2)

conv3 = Conv2D(128, (3, 3), activation='relu', padding='same')(pool2)
conv3 = Dropout(0.2)(conv3)
conv3 = Conv2D(128, (3, 3), activation='relu', padding='same')(conv3)

up1 = concatenate([UpSampling2D((2, 2))(conv3), conv2], axis=-1)
conv4 = Conv2D(64, (3, 3), activation='relu', padding='same')(up1)
conv4 = Dropout(0.2)(conv4)
conv4 = Conv2D(64, (3, 3), activation='relu', padding='same')(conv4)

up2 = concatenate([UpSampling2D((2, 2))(conv4), conv1], axis=-1)
conv5 = Conv2D(32, (3, 3), activation='relu', padding='same')(up2)
conv5 = Dropout(0.2)(conv5)
conv5 = Conv2D(32, (3, 3), activation='relu', padding='same')(conv5)

out = Conv2D( n_classes, (1, 1) , padding='same')(conv5)
##############################################################################

from keras_segmentation.models.model_utils import get_segmentation_model
model = get_segmentation_model(img_input ,  out ) # this would build the segmentation model

if LOAD:
    latest_weights = find_latest_checkpoint(ckpath)
    model.load_weights(latest_weights)

if TRAIN:
    print("STARTED TRAINING\n")
    model.train(
        train_images =  "dataset/train_frames_mosaic/",
        train_annotations = "dataset/train_masks_mosaic/",
        checkpoints_path = ckpath , epochs=epochs,
        batch_size=32
    )
    print('FINISHED TRAINING')

##out = model.predict_segmentation(
##    inp="./val_frames/ms_8ply_0000_0_10.png",
##    out_fname="test_output.png"
##)

### Apply network to target imgs
if APPLY:
    inp_dir=""
    out_dir=""
    regex = "frame_0012.png" #inp_dir + "adept12ply_raw_????_?_?.png"
    imgpaths = sorted(glob(regex))

    for p in imgpaths:
        name, ext = os.path.splitext(p)
        out = model.predict_segmentation(
            inp = p,
            out_fname = "tests/pika4.png", #out_dir+name+ext,
            colors=[(0,0,255),(0,255,0),(255,0,0)]
        )
        lname = name.split('_')
        if lname[-1]=='0' and lname[-2]=='0':
            print(name)



# redefine model to output right after the first hidden layer
model = Model(inputs=model.inputs, outputs=model.layers[1].output)
model.summary()
# load the image with the required shape
img = load_img('tests/pika4.png', target_size=(224, 224))
# convert the image to an array
img = img_to_array(img)
# expand dimensions so that it represents a single 'sample'
img = expand_dims(img, axis=0)
# prepare the image (e.g. scale pixel values for the vgg)
img = preprocess_input(img)
# get feature map for first hidden layer
feature_maps = model.predict(img)
# plot all 64 maps in an 8x8 squares
haut = 6
long = 3

index = 1
for _ in range(haut):

	for _ in range(long):
		ax = pyplot.subplot(haut, long, index)
		ax.set_xticks([])
		ax.set_yticks([])
		pyplot.imshow(feature_maps[0, :, :, index-1], cmap='viridis')
		index += 1
# show the figure

pyplot.show()
