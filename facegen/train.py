"""
facegen/train.py
"""

import os

from keras.callbacks import Callback, EarlyStopping, ModelCheckpoint

import numpy as np
import scipy.misc

from .instance import Emotion, RaFDInstances
from .model import build_model


class GenerateIntermediate(Callback):
    """ Callback to generate intermediate images after each epoch. """

    def __init__(self, output_dir, num_identities, batch_size=32):
        """
        Constructor for a GenerateIntermediate object.

        Args:
            output_dir (str): Directory to save intermediate results in.
            num_identities (int): Number of identites in the training set.
        Args: (optional)
            batch_size (int): Batch size to use when generating images.
        """
        super(Callback, self).__init__()

        self.output_dir = os.path.join(output_dir, 'intermediate')
        self.num_identities = num_identities
        self.batch_size = batch_size

        self.parameters = dict()

        # Sweep through identities
        self.parameters['identity'] = np.eye(num_identities)

        # Make all have neutral expressions, front-facing
        self.parameters['emotion'] = np.empty((num_identities, Emotion.length()))
        self.parameters['orientation'] = np.zeros((num_identities, 2))
        for i in range(0, num_identities):
            self.parameters['emotion'][i,:] = Emotion.neutral
            self.parameters['orientation'][i,1] = 1


    def on_train_begin(self, logs={}):
        """ Create directories. """

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)


    def on_epoch_end(self, epoch, logs={}):
        """ Generate and save results to the output directory. """

        dest_dir = os.path.join(self.output_dir, 'e{:04}'.format(epoch))
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        gen = self.model.predict(self.parameters, batch_size=self.batch_size)

        for i in range(0, gen.shape[0]):
            image = np.empty(gen.shape[2:]+(3,))
            for x in range(0, 3):
                image[:,:,x] = gen[i,x,:,:]
            image = np.array(255*np.clip(image,0,1), dtype=np.uint8)
            file_path = os.path.join(dest_dir, '{:02}.jpg'.format(i))
            scipy.misc.imsave(file_path, image)


def train_model(data_dir, output_dir, batch_size=32, num_epochs=100,
        deconv_layers=5, generate_intermediate=False, verbose=False):
    """
    Trains the model on the data, generating intermediate results every epoch.

    Args:
        model (keras.Model): Model to train.
        data_dir (str): Directory where the data lives.
        output_dir (str): Directory where outputs should be saved.
    Args (optional):
        batch_size (int): Size of the batch to use.
        num_epochs (int): Number of epochs to train for.
        deconv_layers (int): The number of deconvolution layers to use.
        generate_intermediate (bool): Whether or not to generate intermediate results.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    instances = RaFDInstances(data_dir)

    if verbose:
        print("Found {} instances with {} identities".format(
            instances.num_instances, instances.num_identities))


    # Create FaceGen model to use

    model = build_model(
        identity_len = instances.num_identities,
        deconv_layers = deconv_layers)

    if verbose:
        print("Built model with {} deconvolution layers and output size {}"
                .format(deconv_layers, model.output_shape[2:]))


    # Create training callbacks

    callbacks = list()

    if generate_intermediate:
        callbacks.append( GenerateIntermediate(output_dir, instances.num_identities) )

    model_name = 'FaceGen.model.d{:02}.{{epoch:03d}}.h5'.format(deconv_layers)

    callbacks.append(
        ModelCheckpoint(
            os.path.join(output_dir, model_name),
            monitor='loss', verbose=0, save_best_only=True,
        )
    )
    callbacks.append(
        EarlyStopping(monitor='loss', patience=5)
    )

    # Load data and begin training

    if verbose:
        print("Loading data...")

    inputs, outputs = instances.load_data(model.output_shape[2:], verbose=verbose)

    if verbose:
        print("Training...")

    model.fit(inputs, outputs, batch_size=batch_size, nb_epoch=num_epochs,
            callbacks=callbacks, shuffle=True, verbose=1)

    if verbose:
        print("Done!")
