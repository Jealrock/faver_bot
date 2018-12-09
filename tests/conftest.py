import pytest
from .factories import *

@pytest.fixture
def init_tables(request):
    create_tables()

    def finalize():
        drop_tables()

    request.addfinalizer(finalize)
