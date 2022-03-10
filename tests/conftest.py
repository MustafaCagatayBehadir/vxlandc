from pytest import fixture
import json


def load_test_data(path):
    with open(path) as data_file:
        data = json.load(data_file)
        return data

@fixture
def expected(request):
    return load_test_data(request.param)