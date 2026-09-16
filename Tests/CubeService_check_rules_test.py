import unittest
from unittest.mock import MagicMock

from TM1py.Objects import Rules
from TM1py.Services.CubeService import CubeService


class TestCubeServiceCheckRules(unittest.TestCase):
    def setUp(self):
        self.rest = MagicMock()
        response = MagicMock()
        response.json.return_value = {"value": []}
        self.rest.POST.return_value = response
        self.service = CubeService(self.rest)

    def test_check_existing_rules_sends_empty_payload(self):
        self.service.check_rules(cube_name="Sales")

        self.rest.POST.assert_called_once_with("/Cubes('Sales')/tm1.CheckRules")

    def test_check_supplied_rules_sends_rules_payload(self):
        self.service.check_rules(cube_name="Sales", rules="SKIPCHECK;")

        self.rest.POST.assert_called_once_with("/Cubes('Sales')/tm1.CheckRules", data='{"Rules": "SKIPCHECK;"}')

    def test_check_supplied_rules_object_sends_rules_payload(self):
        self.service.check_rules(cube_name="Sales", rules=Rules("SKIPCHECK;"))

        self.rest.POST.assert_called_once_with("/Cubes('Sales')/tm1.CheckRules", data='{"Rules": "SKIPCHECK;"}')

    def test_check_supplied_rules_returns_errors(self):
        errors = [{"Message": "Rule is invalid"}]
        self.rest.POST.return_value.json.return_value = {"value": errors}

        result = self.service.check_rules(cube_name="Sales", rules="SKIPCHECK")

        self.assertEqual(errors, result)

    def test_check_supplied_rules_rejects_invalid_type(self):
        with self.assertRaises(ValueError):
            self.service.check_rules(cube_name="Sales", rules=["SKIPCHECK;"])


if __name__ == "__main__":
    unittest.main()
