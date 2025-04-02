
from app.utils.utils_dls import extract_data, extract_DLS
from tests import samples
import pytest
import pandas as pd


@pytest.fixture
def extract_dls_instance():
    return extract_DLS('/mock/path')

def test_show_report(extract_dls_instance):
    extract_dls_instance.recap = "Mock Recap"
    assert extract_dls_instance.show_report() == "Mock Recap"

def test_show_ready(extract_dls_instance):
    extract_dls_instance.data_ready = "Mock Data Ready"
    assert extract_dls_instance.show_ready() == "Mock Data Ready"

def test_extract_data():
    out= pd.DataFrame()
    for i in range(2):
        data_out = extract_data(samples.sample_DLS_in)
        out = pd.concat([out,data_out],axis=1)
    assert out.shape == (24,2)

def test_generate_report():
    test_my_class = extract_DLS("")
    test_my_class.all_data = pd.concat([pd.Series(samples.sample_DLS_out) for i in range(2)], axis=1)
    test_my_class.generate_report()
    assert any(test_my_class.show_report())
    