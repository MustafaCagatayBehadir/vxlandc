import json
from pathlib import Path
from nsoapi import NsoRestconfCall
from pytest import mark
import json


class VxlandcTests:
    """
    A Test Class for NSO package l1access
    """

    payload_path = Path.cwd() / "tests" / "test_00_vxlandc" / "payload"
    expected_path = Path.cwd() / "tests" / "test_00_vxlandc" / "expected"
    nso = NsoRestconfCall()

    @classmethod
    def setup_class(cls):
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_site_config.json",
            path="",
            params="",
        )

    @mark.parametrize('expected, path', [(expected_path / 'ref_001_site.json', 'vxlandc-core:vxlandc')], indirect=['expected'])
    def test_001_site(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_002_resource_pools.json',
         'vxlandc-core:vxlandc/sites-operations/resource-pools/create-site-resource-pools',
         'resource-allocator:resource-pools'),
    ], indirect=['expected'])
    def test_002_resource_pools(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_002_input.json', path=post_path, params='', action=True)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 200
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected
