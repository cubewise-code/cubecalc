import os
from base64 import b64decode


def set_current_directory():
    abspath = os.path.abspath(__file__)
    directory = os.path.dirname(abspath)
    # set current directory
    os.chdir(directory)
    return directory


def decrypt_password(encrypted_password):
    """ b64 decoding

    :param encrypted_password: encrypted password with b64
    :return: password in plain text
    """
    return b64decode(encrypted_password).decode("UTF-8")
