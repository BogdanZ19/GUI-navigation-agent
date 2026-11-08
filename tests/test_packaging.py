from importlib.metadata import requires, entry_points

def get_requirements():
    return requires("gui_agent")


def dependency_exists(dependency: str, **kwargs):
    is_dev_dep = kwargs.get("is_dev_dep", None)
    requirements = get_requirements()
    
    if (is_dev_dep):
        return any(f"{dependency}>=" in d and 'extra == "dev"' in d for d in requirements)     
    
    return any(f"{dependency}>=" in d for d in requirements) 


def test_requirements_exist():
    assert requires("gui-agent") is not None


def test_entry_point_exists():
    assert entry_points(name="gui-agent")["gui-agent"].value == "gui_agent.cli:main"


def test_dep_exists_mss():
    assert dependency_exists("mss")


def test_dep_exists_pywin():
    assert dependency_exists("pywin32")


def test_dep_exists_pytest():
    assert dependency_exists("pytest", is_dev_dep = True)
