def test_host_modules_are_inert_precollection_stubs() -> None:
    from pathlib import Path
    import sys

    import comfy
    import folder_paths
    import nodes
    import server
    import __init__ as root_init

    assert root_init.__lf_nodes_test_stub__ is True
    assert comfy.__lf_nodes_test_stub__ is True
    assert folder_paths.__lf_nodes_test_stub__ is True
    assert nodes.__lf_nodes_test_stub__ is True
    assert server.__lf_nodes_test_stub__ is True

    lf_root = Path(__file__).resolve().parents[3]
    comfy_root = lf_root.parents[1].resolve()
    resolved_sys_path = {
        Path(entry).resolve()
        for entry in sys.path
        if entry
    }
    assert comfy_root not in resolved_sys_path
