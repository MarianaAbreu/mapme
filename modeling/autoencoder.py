
from keras.layers import Input, Dense
from keras.models import Model

import pickle


def autoencoder_params(encoding_dim_, input_len, list_layers, a_fun, optimizer, loss,
                       x_train, y_train, x_test, y_test, label, epochs):
    """
    This function creates and trains an autoencoder with the specified characteristics.
    This autoencoder includes the encoding part and the decoding part. Both are returned for future analysis.
    :param encoding_dim_: shortest number of nodes
    :param input_len: Length of the samples
    :param list_layers: List with the number of nodes in each layer (where first value is the first layer and
    the last value is the bottleneck
    :param a_fun: Activation function - https://keras.io/api/layers/activations/#available-activations
    :param optimizer: Optimizer - https://keras.io/api/optimizers/#available-optimizers
    :param loss: Loss function that can be selected from this list https://keras.io/api/losses/#available-losses
    :param x_train: Training samples
    :param y_train: Output of each training sample, usually is equal to x_train
    :param x_test: Validation samples
    :param y_test: Output of validation samples, usually is equal to x_test
    :param label: Label name to save the models
    :param epochs: Number of epochs to run
    :return: decoder and encoder models after training
    """
    # this is the size of our encoded representations
    encoding_dim = encoding_dim_  # 32 floats -> compression of factor 32, assuming the input is 1024 floats

    # confirmation
    if sorted(list_layers, key=int, reverse=True) != list_layers:
        print('\nList should be in order!\n')

    input_sig = Input(shape=(input_len,))
    # encoder creation
    encoded = Dense(list_layers[0], activation=a_fun)(input_sig)
    for nt in list_layers[1:]:
        encoded = Dense(nt, activation=a_fun)(encoded)
    # "decoded" is the lossy reconstruction of the input
    inverse_layers = list_layers[::-1][1:] + [input_len]
    decoded = Dense(inverse_layers[0], activation=a_fun)(encoded)
    for ll in inverse_layers[1:]:
        decoded = Dense(ll, activation=a_fun)(decoded)

    autoencoder = Model(input_sig, decoded)

    # Let's also create a separate encoder model as well as the decoder model:
    encoder = Model(input_sig, encoded)
    encoded_input = Input(shape=(encoding_dim,))
    dec_layers = autoencoder.layers[len(list_layers)+1:]
    decoder_output = dec_layers[0](encoded_input)
    for dl in dec_layers[1:]:
        decoder_output = dl(decoder_output)
    decoder = Model(encoded_input, decoder_output)

    # First, we'll configure our model
    autoencoder.compile(optimizer=optimizer, loss=loss)

    print('\nAutoencoder Created:')
    print('Layers: ' + str(list_layers))
    print('Input Length: ' + str(input_len))
    print('Compression: ' + str(encoding_dim))
    print('Activation: ' + str(a_fun))
    print('Optimizer: ' + str(optimizer))
    print('Loss: ' + str(loss) + '\n')

    autoencoder.fit(x_train, y_train,
                    epochs=epochs,
                    batch_size=100,
                    shuffle=True,
                    validation_data=(x_test, y_test))

    pickle.dump(decoder, open(label+'_decoder', 'wb'))
    pickle.dump(encoder, open(label+'_encoder', 'wb'))

    return decoder, encoder


def create_autoencoder(x_train, y_train, x_test, y_test, label, loss='cosine_proximity',
                       activ='tanh', opt='adam', nodes=None, epochs=100):
    if nodes is None:
        print('Please Give the List of Layers - Ex [500, 200, 100]')

    decoder, encoder = autoencoder_params(nodes[-1], x_train.shape[1], nodes, activ, opt, loss,
                                          x_train, y_train, x_test, y_test, label, epochs)
    return decoder, encoder
