"""
convolutional neural network architectures
partly adapted from pytorch tutorial

References:
[Sainath 2015] - Tara N. Sainath and Carolina Parada. Convolutional neural networks for small-footprint key-word spotting. InINTERSPEECH, 2015
"""

import numpy as np

import torch
import torch.nn as nn


class ConvBasics():
  """
  Convolutional Networks base class with useful functions
  """

  def __init__(self, n_classes, data_size):

    # arguments
    self.n_classes = n_classes
    self.data_size = data_size

    # extract input size [channel x features x frames]
    self.n_channels, self.n_features, self.n_frames = self.data_size


  def get_conv_layer_dimensions(self, input_dim, kernel_sizes, strides, padding):
    """
    get convolutional layer dimensions upon kernel sizes, strides and padding
    input_dim; (height, width) or (n_features, n_frames) for mfcc or (n_time_steps,) for raw input
    """

    # layer dimensions
    conv_layer_dim = []

    # first dimension
    conv_layer_dim.append(input_dim)

    # for all convolutional layers
    for i, (k, s, p) in enumerate(zip(kernel_sizes, strides, padding)):

      # init layer dim
      layer_dim = None

      # for all dimensions
      for d, (k_d, s_d, p_d) in enumerate(zip(k, s, p)):

        # dimension
        dim = int((conv_layer_dim[i][d] + 2 * p_d - k_d) / s_d + 1)

        # new dim
        layer_dim = layer_dim + (dim,) if layer_dim is not None else (dim,)

      # append to dimensions
      conv_layer_dim.append(layer_dim)

    return conv_layer_dim


  def transfer_params(self, model):
    """
    transfer parameters from other models
    """

    with torch.no_grad():

      # go through all parameters
      for param_name in model.state_dict():

        #print("param_tensor: ", param_name)

        # encoders
        if param_name == 'conv_layer0.weight': self.state_dict()['conv_layer0.weight'][:] = model.state_dict()[param_name]
        elif param_name == 'conv_layer1.weight': self.state_dict()['conv_layer1.weight'][:] = model.state_dict()[param_name]

        # decoders
        elif param_name == 'deconv_layer0.weight': self.state_dict()['conv_layer1.weight'][:] = model.state_dict()[param_name]
        elif param_name == 'deconv_layer1.weight': self.state_dict()['conv_layer0.weight'][:] = model.state_dict()[param_name]


  def transfer_params_label_models(self, models, n=8):
    """
    transfer of parameters for adv-label models with n feature maps each
    """

    with torch.no_grad():

      # regard every conv encoder
      for i, model in enumerate(models):

        #print("stat: ", model.state_dict().keys())

        # go through all parameters
        for param_name in model.state_dict():

          # encoders
          if param_name == 'conv_layer0.weight': self.state_dict()[param_name][i*n:(i+1)*n] = model.state_dict()[param_name]
          elif param_name == 'conv_layer1.weight': self.state_dict()[param_name][:, i*n:(i+1)*n] = model.state_dict()[param_name]

          # decoders
          elif param_name == 'deconv_layer0.weight': self.state_dict()[param_name][:, i*n:(i+1)*n] = model.state_dict()[param_name]
          elif param_name == 'deconv_layer1.weight': self.state_dict()[param_name][i*n:(i+1)*n] = model.state_dict()[param_name]



class ConvNetTrad(nn.Module, ConvBasics):
  """
  Traditional CNN adapted from [Sainath 2015] - cnn-trad-fpool3
  """

  def __init__(self, n_classes, data_size):

    # parent init
    super().__init__()
    ConvBasics.__init__(self, n_classes, data_size)

    # params
    self.n_feature_maps = [64, 64]

    # original settings for 39x32
    #self.kernel_sizes = [(8, 20), (4, 1), (4, 10)]
    #self.strides = [(1, 1), (4, 1), (1, 1)]

    # for 13x32
    self.kernel_sizes = [(4, 20), (2, 4), (2, 4)]
    self.strides = [(1, 1), (2, 4), (1, 1)]
    self.padding = [(0, 0), (0, 0), (0, 0)]

    # get layer dimensions
    self.conv_layer_dim = self.get_conv_layer_dimensions(input_dim=(self.n_features, self.n_frames), kernel_sizes=self.kernel_sizes, strides=self.strides, padding=self.padding)

    # 1. conv layer
    self.conv1 = nn.Conv2d(self.n_channels, self.n_feature_maps[0], kernel_size=self.kernel_sizes[0], stride=self.strides[0])

    # max pool layer
    self.pool = nn.MaxPool2d(kernel_size=self.kernel_sizes[1], stride=self.strides[1])

    # 2. conv layer
    self.conv2 = nn.Conv2d(64, 64, kernel_size=self.kernel_sizes[2], stride=self.strides[2])

    # fully connected layers with affine transformations: y = Wx + b
    self.fc1 = nn.Linear(np.prod(self.conv_layer_dim[-1]) * self.n_feature_maps[-1], 32)
    self.fc2 = nn.Linear(32, 128)
    self.fc3 = nn.Linear(128, n_classes)

    # dropout layer
    self.dropout_layer1 = nn.Dropout(p=0.2)
    self.dropout_layer2 = nn.Dropout(p=0.5)

    # softmax layer
    self.softmax = nn.Softmax(dim=1)


  def forward(self, x):
    """
    forward pass
    """

    # 1. conv layer [1 x 64 x 32 x 13]
    x = torch.relu(self.conv1(x))

    # max pooling layer [1 x 64 x 8 x 13]
    x = self.pool(x)

    # 2. conv layer [1 x 64 x 5 x 4]
    x = torch.relu(self.conv2(x))

    # flatten output from 2. conv layer [1 x 1280]
    x = x.view(-1, np.product(x.shape[1:]))

    # 1. fully connected layers [1 x 32]
    x = self.fc1(x)
    x = self.dropout_layer1(x)

    # 2. fully connected layers [1 x 128]
    x = torch.relu(self.fc2(x))
    x = self.dropout_layer2(x)

    # Softmax layer [1 x n_classes]
    x = self.softmax(self.fc3(x))

    return x



class ConvNetFstride4(nn.Module, ConvBasics):
  """
  CNN architecture with limited multipliers adapted from [Sainath 2015] - cnn-one-fstride4
  """

  def __init__(self, n_classes, data_size):

    # parent init
    super().__init__()
    ConvBasics.__init__(self, n_classes, data_size)

    # params
    self.n_feature_maps = [54]
    self.kernel_sizes = [(8, self.n_frames)]
    self.strides = [(4, 1)]
    self.padding = [(0, 0)]

    # get layer dimensions
    self.conv_layer_dim = self.get_conv_layer_dimensions(input_dim=(self.n_features, self.n_frames), kernel_sizes=self.kernel_sizes, strides=self.strides, padding=self.padding)

    # conv layer
    self.conv = nn.Conv2d(self.n_channels, self.n_feature_maps[0], kernel_size=self.kernel_sizes[0], stride=self.strides[0])

    # fully connected layers with affine transformations: y = Wx + b
    self.fc1 = nn.Linear(np.prod(self.conv_layer_dim[-1]) * self.n_feature_maps[-1], 32)
    self.fc2 = nn.Linear(32, 128)
    self.fc3 = nn.Linear(128, 128)
    self.fc4 = nn.Linear(128, self.n_classes)

    # dropout layer
    self.dropout_layer1 = nn.Dropout(p=0.2)
    self.dropout_layer2 = nn.Dropout(p=0.5)

    # softmax layer
    self.softmax = nn.Softmax(dim=1)


  def forward(self, x):
    """
    forward pass
    """

    # 1. conv layer [1 x 54 x 8 x 1]
    x = torch.relu(self.conv(x))

    # flatten output from conv layer [1 x 432]
    x = x.view(-1, np.product(x.shape[1:]))

    # 1. fully connected layers [1 x 32]
    x = self.fc1(x)
    x = self.dropout_layer1(x)

    # 2. fully connected layers [1 x 128]
    x = torch.relu(self.fc2(x))
    x = self.dropout_layer2(x)

    # 3. fully connected layers [1 x 128]
    x = torch.relu(self.fc3(x))
    x = self.dropout_layer2(x)

    # Softmax layer [1 x n_classes]
    x = self.softmax(self.fc4(x))

    return x



class ConvNetExperimental(nn.Module, ConvBasics):
  """
  CNN experimental
  """

  def __init__(self, n_classes, data_size):

    # parent init
    super().__init__()
    ConvBasics.__init__(self, n_classes, data_size)

    # conv params
    self.n_feature_maps = [(self.n_channels, 4), (4, 8), (8, 5)]
    self.kernel_sizes = [(self.n_features, 20), (1, 6), (1, 9)]
    self.strides = [(1, 1), (1, 3), (1, 1)]
    self.padding = [(0, 0), (0, 0), (0, 0)]

    # relu params (be carefull, last layer should be false)
    self.relu_active = [True, True, False]
    self.dropout_active = [False, True, False]

    # get layer dimensions
    self.conv_layer_dim = self.get_conv_layer_dimensions(input_dim=(self.n_features, self.n_frames), kernel_sizes=self.kernel_sizes, strides=self.strides, padding=self.padding)

    # conv layer
    self.conv_layers = torch.nn.ModuleList()
    for f, k, s in zip(self.n_feature_maps, self.kernel_sizes, self.strides): self.conv_layers.append(nn.Conv2d(f[0], f[1], kernel_size=k, stride=s))

    # dimensions
    self.conv_in_dim = self.data_size
    self.conv_out_dim = ((self.n_feature_maps[-1][1],) + self.conv_layer_dim[-1])

    # softmax layer
    self.softmax = nn.Softmax(dim=1)


  def forward(self, x):
    """
    forward pass
    """

    # convolutional layers
    for conv, r, d in zip(self.conv_layers, self.relu_active, self.dropout_active):
      x = conv(x)
      if r: x = torch.relu(x)
      if d: x = self.dropout_layer2(x)

    # flatten
    x = x.view(-1, np.product(x.shape[1:]))

    # Softmax layer
    x = self.softmax(x)

    return x



class ClassifierNetFc1(nn.Module):
  """
  classifier network with one fully connected layer
  """

  def __init__(self, input_dim, output_dim):

    # parent init
    super().__init__()

    # structure
    self.fc1, self.softmax = nn.Linear(input_dim, output_dim), nn.Softmax(dim=1)


  def forward(self, x):
    """
    forward pass
    """
    return self.softmax(self.fc1(x))



class ClassifierNetFc3(nn.Module):
  """
  classifier network with three fully connected layers
  """

  def __init__(self, input_dim, output_dim):

    # parent init
    super().__init__()

    # structure
    self.fc1, self.fc2, self.fc3, self.dropout_layer, self.softmax = nn.Linear(input_dim, 64), nn.Linear(64, 32), nn.Linear(32, output_dim), nn.Dropout(p=0.5), nn.Softmax(dim=1)


  def forward(self, x):
    """
    forward pass
    """
    return self.softmax(self.fc3(self.dropout_layer(torch.relu(self.fc2(torch.relu(self.fc1(x)))))))



class ConvJim(nn.Module, ConvBasics):
  """
  CNN encoder with fc3
  """

  def __init__(self, n_classes, data_size):

    # parent init
    super().__init__()
    ConvBasics.__init__(self, n_classes, data_size)

    # conv params
    self.n_feature_maps = [(self.n_channels, 8 * 6), (8 * 6, 8)]
    self.kernel_sizes = [(self.n_features, 20), (1, 5)]
    self.strides = [(1, 1), (1, 1)]
    self.padding = [(0, 0), (0, 0)]

    # get conv layer dimensions
    self.conv_layer_dim = self.get_conv_layer_dimensions((self.n_features, self.n_frames), self.kernel_sizes, self.strides, self.padding)
    self.conv_in_dim = self.data_size
    self.conv_out_dim = ((self.n_feature_maps[-1][1],) + self.conv_layer_dim[-1])

    # conv layer
    self.conv_layer0 = nn.Conv2d(self.n_feature_maps[0][0], self.n_feature_maps[0][1], kernel_size=self.kernel_sizes[0], stride=self.strides[0], bias=False)
    self.conv_layer1 = nn.Conv2d(self.n_feature_maps[1][0], self.n_feature_maps[1][1], kernel_size=self.kernel_sizes[1], stride=self.strides[1], bias=False)

    # classifier net
    self.classifier_net = ClassifierNetFc3(np.prod(self.conv_out_dim), n_classes)


  def forward(self, x):
    """
    forward pass
    """

    # conv layers
    x = torch.relu(self.conv_layer0(x))
    x = torch.relu(self.conv_layer1(x))

    # flatten
    x = x.view(-1, np.product(x.shape[1:]))

    # classifier net
    x = self.classifier_net(x)

    return x



if __name__ == '__main__':
  """
  main function
  """

  # generate random sample
  x = torch.randn((1, 1, 13, 50))

  # create net
  #net = ConvNetFstride4(n_classes=5, data_size=x.shape[1:])
  #net = ConvNetTrad(n_classes=5, data_size=x.shape[1:])
  net = ConvJim(n_classes=5, data_size=x.shape[1:])

  # test net
  o = net(x)

  # print some infos
  print("\nx: ", x.shape), print("Net: ", net), print("o: ", o)