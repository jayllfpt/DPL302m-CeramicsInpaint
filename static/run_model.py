import numpy as np
import cv2
import cv2 as cv
from static.options.test_options import TestOptions
from static.model.net import InpaintingModel_DFBM
from static.util.utils import generate_rect_mask
from time import sleep

# path temp files
path_pre_image = r"static/temp0.png"
path_hsv_result = r"static/temp1.png"

def m3_preprocessing_image(path:str):
    image = cv.imread(path)
    image = cv.resize(image, (256, 256))
    image = cv.GaussianBlur(image, (7, 7), 0)
    image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    cv2.imwrite(path_pre_image, image)    
    return image

def gaussian_kernel(size, sigma):
    kernel = np.fromfunction(lambda x, y: (1 / (2 * np.pi * sigma**2)) * np.exp(-((x - size//2)**2 + (y - size//2)**2) / (2 * sigma**2)), (size, size))
    return kernel

def convert_image_org(image):
    kernel = gaussian_kernel(7, 1.0)
    reverse_kernel = np.flipud(np.fliplr(kernel))
    image = cv.filter2D(image, -1, reverse_kernel)
    image = cv.cvtColor(image, cv.COLOR_HSV2BGR)
    return image

def load_image(path:str):
  m3_preprocessing_image(path)
  image = cv2.imread(path_pre_image)
  image = np.transpose(image, [2, 0, 1])
  image = np.expand_dims(image, axis=0)
  return image

def predict(model, image, mask):
  result = model.evaluate(image, mask)
  result = np.transpose(result[0][::-1, :, :], [1, 2, 0])
  result = result[:, :, ::-1]
  # result = convert_image_org(result)
  cv2.imwrite(path_hsv_result, result)

def convert_final_result(path, h = 256, w = 256):
  image = cv2.imread(path_hsv_result)
  image = convert_image_org(image)
  image = cv2.resize(image, (w, h))
  cv2.imwrite(path, image)

_path_model = "static/50_net_DFBN.pth"
_path_org_image = "uploads/image_107.PNG"
_path_masked = "uploads/masked.png"
_path_result = "uploads/inpainted_result.png"

def run(path_model = _path_model, path_org_image = _path_org_image,path_masked = _path_masked, path_result = _path_result):
  # load model
  config = config = TestOptions().parse()
  ourModel = InpaintingModel_DFBM(opt=config)
  ourModel.load_networks(path_model)

  # generate mask & image
  mask, _ = generate_rect_mask(config.img_shapes, config.mask_shapes, config.random_mask)
  image = load_image(path_org_image)
  
  # save image with mask
  _image = cv2.imread(path_org_image)
  h, w = _image.shape[:2]
  if h >= config.img_shapes[0] and w >= config.img_shapes[1]:
      h_start = (h - config.img_shapes[0]) // 2
      w_start = (w - config.img_shapes[1]) // 2
      _image = _image[h_start: h_start + config.img_shapes[0], w_start: w_start + config.img_shapes[1], :]
  else:
      t = min(h, w)
      _image = _image[(h - t) // 2:(h - t) // 2 + t, (w - t) // 2:(w - t) // 2 + t, :]
      _image = cv2.resize(_image, (config.img_shapes[1], config.img_shapes[0]))
  _image = np.transpose(_image, [2, 0, 1])
  _image = np.expand_dims(_image, axis=0)
  image_vis = _image * (1 - mask) + 255 * mask
  image_vis = np.transpose(image_vis[0][::, :, :], [1, 2, 0])
  cv2.imwrite(path_masked,  image_vis.astype(np.uint8))

  # predict
  predict(ourModel, image, mask)
  convert_final_result(path_result, h, w)

# main()
