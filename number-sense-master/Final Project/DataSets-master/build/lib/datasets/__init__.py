""" Save machine learning data sets to a common location, and load them without
    having to specify a path.

    All datasets will be saved to `datasets.path`. By default, this will be point to
    ~/datasets. You can update this path via `datasets.set_path`.
"""

from pathlib import Path
import numpy as np

from .toydata import ToyData

__all__ = ["load_cifar10",
           "load_mnist",
           "load_fashion_mnist",
           "download_cifar10",
           "download_fashion_mnist",
           "download_mnist",
           "ToyData"]


_config_file = Path.home()/".datasets"


def get_path(verbose=False):
    if _config_file.is_file():
        with _config_file.open("r") as f:
            header, path = f.readlines()
        path = Path(path)
    else:
        path = Path.home() / "datasets"
        path.mkdir(exist_ok=True)
    if verbose:
        print("`datasets module: datasets will be loaded from '{}'".format(path))
    return path


get_path(verbose=True)


def set_path(new_path, mkdir=False):
    """
    Specify the path to which datasets will be saved. This path is saved to
    a config file saved at: ~/.datasets

    Parameters
    ----------
    new_path : PathLike
        The path to the directory to which all datasets will be saved.

    mkdir : bool, optional (default=False)
        If `True` the specified directory will be created if it doesn't already exist.
    """
    new_path = Path(new_path)
    if mkdir:
        new_path.mkdir(exist_ok=True)
    with _config_file.open(mode="w") as f:
        f.write("# The python pacakge `datasets` will write data to the following directory:\n")
        f.write(str(new_path.absolute()))
    get_path(verbose=True)


def restore_default_path(are_you_sure):
    """
    Deletes ~/.datasets config file and restores the path to '~/datasets

    Parameters
    ----------
    are_you_sure : bool
        Users must explicitly specify `True` to reset the path.
    """
    global path
    import os
    if are_you_sure is not True:
        print("You must expliticly specify `restore_default_path(True)` to reset the path.")
        return

    if _config_file.is_file():
        os.remove(_config_file)
    path = get_path(verbose=False)


def download_cifar10():
    """ Download the cifar-10 dataset and save it as a .npz archive.
        md5 check-sum verification is performed.

        path = <path_to_datasets>/cifar-10-python.npz """
    from datasets.download_utils import _download_cifar10
    import shutil
    tmp_dir = get_path() / "_tmp_dir_"
    if tmp_dir.exists():
        print("Directory: {} already exists - an intermediate directory needs to be constructed here".format(tmp_dir))
        print("move/delete that directory and try again.")
        return None

    try:
        _download_cifar10(get_path(), tmp_dir)
    finally:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)


def load_cifar10(fname='cifar-10-python.npz'):
    """ The CIFAR-10 dataset consists of 60000x3x32x32 uint-8 color images in 10
        classes, with 6000 images per class. There are 50000 training images 
        and 10000 test images.

        The labels are integers in [0, 9]

        https://www.cs.toronto.edu/~kriz/cifar.html

        Parameters
        ----------
        fname : str, optional (default="mnist.npz")
            The filename of the .npz archive storing the cifar-10 data

        Returns
        -------
        Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray]
            training-data, training-labels, test-data, test-labels

        Notes
        -----
        A tuple of the categories corresponding to the data's integer labels are bound as an
        attribute of this function:

            `dataset.load_cifar10.labels`
        """

    path = get_path()
    if not (path / fname).exists():
        msg = """ Data not found! Please download the data (cifar-10-python.npz) using 
                 `datasets.download_cifar10()`"""
        raise FileNotFoundError(msg)

    with np.load(str(path / fname)) as data:
        xtr, ytr, xte, yte = tuple(data[key] for key in ['x_train', 'y_train', 'x_test', 'y_test'])
    print("cifar-10 loaded")
    return xtr, ytr, xte, yte


load_cifar10.labels = ("airplane",
                       "automobile",
                       "bird",
                       "cat",
                       "deer",
                       "dog",
                       "frog",
                       "horse",
                       "ship",
                       "truck")


def download_fashion_mnist():
    """ Function for downloading fashion-mnist and saves fashion-mnist as a
        numpy compressed-archive. md5 check-sum verficiation is performed.

        Parameters
        ----------
        path : Optional[pathlib.Path, str]
            Path to containing .npz file. If `None`, the path to the DataSets module is used."""
    from datasets.download_utils import _md5_check, _download_mnist

    path = get_path() / "fashion_mnist.npz"
    tmp_file = get_path() / "__mnist.bin"

    if path.is_file():
        print("File already exists:\n\t{}".format(path))
        return None

    if path.is_dir():
        print("`path` specifies a directory. It should specify the file-destination, including the file-name.")
        return None

    server_url = "http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/"

    check_sums = {"train-images-idx3-ubyte.gz": "8d4fb7e6c68d591d4c3dfef9ec88bf0d",
                  "train-labels-idx1-ubyte.gz": "25c81989df183df01b3e8a0aad5dffbe",
                  "t10k-images-idx3-ubyte.gz": "bef4ecab320f06d8554ea6380940ec79",
                  "t10k-labels-idx1-ubyte.gz": "bb300cfdad3c16e7a12a480ee83cd310"}
    _download_mnist(path, server_url=server_url, tmp_file=tmp_file, check_sums=check_sums)


def load_fashion_mnist(fname="fashion_mnist.npz"):
    """ Loads the fashion-mnist dataset (including train & test, along with their labels).

        The data set is loaded as Nx1x28x28 uint8 numpy arrays. N is the size of the
        data set - N=60,000 for the training set, and N=10,000 for the test set.

        The labels are integers in [0, 9]

        Additional information regarding the fashion-mnist data set can be found here:
            - https://github.com/zalandoresearch/fashion-mnist

        Parameters
        ----------
        fname : str, optional (default="fashion_mnist.npz")
            The filename of the .npz file to be loaded

        Returns
        -------
        Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray]
            training-data, training-labels, test-data, test-labels

        Notes
        -----
        A tuple of the categories corresponding to the data's integer labels are bound as an
        attribute of this function:

            `dataset.load_fashion_mnist.labels`
        """

    path = get_path()

    if not (path / fname).exists():
        import inspect
        msg = """ Data not found! Please download the data (fashion_mnist.npz) using 
                 `datasets.download_fashion_mnist()`"""
        raise FileNotFoundError(inspect.cleandoc(msg))

    with np.load(str(path / fname)) as data:
        out = [data[key] for key in ['x_train', 'y_train', 'x_test', 'y_test']]

    print("fashion-mnist loaded")
    return tuple(out)


load_fashion_mnist.labels = ('T-shirt/top',
                             'Trouser',
                             'Pullover',
                             'Dress',
                             'Coat',
                             'Sandal',
                             'Shirt',
                             'Sneaker',
                             'Bag',
                             'Ankle boot')


def download_mnist():
    """ Function for downloading mnist and saves fashion-mnist as a
        numpy compressed-archive. file-size verificiation is performed."""

    from datasets.download_utils import _md5_check, _download_mnist

    path = get_path() / "mnist.npz"
    tmp_file = get_path() / "__mnist.bin"

    if path.is_file():
        print("File already exists:\n\t{}".format(path))
        return None

    if path.is_dir():
        print("`path` specifies a directory. It should specify the file-destination, including the file-name.")
        return None

    server_url = "http://yann.lecun.com/exdb/mnist/"

    check_file_sizes = {"train-images-idx3-ubyte.gz": 9912422,
                        "train-labels-idx1-ubyte.gz": 28881,
                        "t10k-images-idx3-ubyte.gz": 28881,
                        "t10k-labels-idx1-ubyte.gz": 4542}
    _download_mnist(path, server_url=server_url, tmp_file=tmp_file, check_sums=check_file_sizes)


def load_mnist(fname="mnist.npz"):
    """ The MNIST database of handwritten digits, has a training set of 60,000 examples, and a test set of
        10,000 examples. It is a subset of a larger set available from NIST. The digits have been
        size-normalized and centered in a fixed-size image.

        The data set is loaded as Nx1x28x28 uint8 numpy arrays. N is the size of the
        data set - N=60,000 for the training set, and N=10,000 for the test set.

        The labels are integers in [0, 9]

        http://yann.lecun.com/exdb/mnist/

        Parameters
        ----------
        fname : str, optional (default="mnist.npz")
            The filename of the .npz archive storing the mnist data

        Returns
        -------
        Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray]
            training-data, training-labels, test-data, test-labels"""
    path = get_path()
    with np.load(path / fname) as data:
        out = tuple(data[str(key)] for key in ['x_train', 'y_train', 'x_test', 'y_test'])
    print("mnist loaded")
    return out


load_mnist.labels = tuple(str(i) for i in range(10))
