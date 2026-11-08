from importlib.metadata import requires, entry_points

import pytest

def get_requirements():
    return requires("gui_agent")


def dependency_exists(dependency: str, is_dev_dep: bool = False) -> bool:
    requirements = get_requirements()
    prefix = f"{dependency}>="
    if (is_dev_dep):
        return any(d.startswith(prefix) and 'extra == "dev"' in d for d in requirements)     
    
    return any(d.startswith(prefix) for d in requirements) 


def test_requirements_exist():
    assert requires("gui-agent") is not None


def test_entry_point_exists():
    assert entry_points(name="gui-agent")["gui-agent"].value == "gui_agent.cli:main"


def test_dep_exists_mss():
    assert dependency_exists("mss")


def test_dep_exists_pywin():
    assert dependency_exists("pywin32")


def test_dep_exists_pytest():
    assert dependency_exists("pytest", is_dev_dep=True)
    
def test_dep_missing_numpy():
    assert not dependency_exists("numpy")


def test_partial_name_is_not_a_dep():
    assert not dependency_exists("ss")


def test_mss_is_not_a_dev_dep():
    assert not dependency_exists("mss", is_dev_dep=True)


def test_typo_in_keyword_raises():
    with pytest.raises(TypeError):
        dependency_exists("mss", is_dev=True)
