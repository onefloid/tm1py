import configparser
import unittest
import uuid
from pathlib import Path

from Tests.Utils import generate_test_uuid
from TM1py import Dimension, Element, Hierarchy
from TM1py.Exceptions.Exceptions import TM1pyRestException
from TM1py.Objects import Cube, Rules
from TM1py.Services import TM1Service

from .Utils import skip_if_version_higher_or_equal_than, skip_if_version_lower_than


class TestCubeService(unittest.TestCase):
    tm1: TM1Service

    @classmethod
    def setUpClass(cls):
        """
        Establishes a connection to TM1 and defines unique names for the TM1 objects used across all tests
        """
        # Connection to TM1
        cls.config = configparser.ConfigParser()
        cls.config.read(Path(__file__).parent.joinpath("config.ini"))
        cls.tm1 = TM1Service(**cls.config["tm1srv01"])

        # Define unique names
        cls.test_uuid = generate_test_uuid()
        cls.prefix = "TM1py_Tests_Cube_"
        cls.cube_name = cls.prefix + "some_name_" + cls.test_uuid
        cls.cube_name_to_delete = cls.prefix + "Some_Other_Name_" + cls.test_uuid
        cls.control_cube_name = "}" + cls.prefix + "some_control_cube_name_" + cls.test_uuid
        cls.dimension_names = [
            cls.prefix + "dimension1_" + cls.test_uuid,
            cls.prefix + "dimension2_" + cls.test_uuid,
            cls.prefix + "dimension3_" + cls.test_uuid,
        ]
        # unique rule comment, so that rule searches only find cubes of this test run
        cls.rule_comment = "find_me_comment_" + cls.test_uuid

    @classmethod
    def tearDownClass(cls):
        cls.tm1.logout()

    def setUp(self):
        for dimension_name in self.dimension_names:
            elements = [Element("Element {}".format(str(j)), "Numeric") for j in range(1, 1001)]
            hierarchy = Hierarchy(dimension_name=dimension_name, name=dimension_name, elements=elements)
            dimension = Dimension(dimension_name, [hierarchy])
            self.tm1.dimensions.update_or_create(dimension)

        # Build Cube
        c = Cube(self.cube_name, dimensions=self.dimension_names, rules=Rules(""))
        if self.tm1.cubes.exists(c.name):
            self.tm1.cubes.delete(c.name)
        self.tm1.cubes.create(c)

        # Build Control Cube
        c = Cube(self.control_cube_name, dimensions=self.dimension_names, rules=Rules(""))
        if self.tm1.cubes.exists(c.name):
            self.tm1.cubes.delete(c.name)
        self.tm1.cubes.create(c)

    def test_get_cube(self):
        c = self.tm1.cubes.get(self.cube_name)
        self.assertIsInstance(c, Cube)
        self.assertEqual(c.dimensions, self.dimension_names)

        # other tests may create or delete cubes in parallel, so compare memberships instead of counts
        cube_names = {cube.name for cube in self.tm1.cubes.get_all()}
        control_cube_names = {cube.name for cube in self.tm1.cubes.get_control_cubes()}
        model_cube_names = {cube.name for cube in self.tm1.cubes.get_model_cubes()}
        self.assertFalse(control_cube_names & model_cube_names)
        self.assertIn(self.cube_name, cube_names)
        self.assertIn(self.cube_name, model_cube_names)
        self.assertIn(self.control_cube_name, cube_names)
        self.assertIn(self.control_cube_name, control_cube_names)

    def test_update_cube(self):
        c = self.tm1.cubes.get(self.cube_name)
        c.rules = Rules("SKIPCHECK;\nFEEDERS;")
        self.tm1.cubes.update(c)
        # test if rule was actually updated
        c = self.tm1.cubes.get(self.cube_name)
        self.assertEqual(c.rules.text, "SKIPCHECK;\nFEEDERS;")
        self.assertTrue(c.skipcheck)

    def test_get_control_cubes(self):
        control_cubes = self.tm1.cubes.get_control_cubes()
        self.assertGreater(len(control_cubes), 0)
        for cube in control_cubes:
            self.assertTrue(cube.name.startswith("}"))

    def test_get_model_cubes(self):
        model_cubes = self.tm1.cubes.get_model_cubes()
        self.assertGreater(len(model_cubes), 0)
        for cube in model_cubes:
            self.assertFalse(cube.name.startswith("}"))

    def test_get_dimension_names(self):
        dimension_names = self.tm1.cubes.get_dimension_names(self.cube_name)
        self.assertEqual(dimension_names, self.dimension_names)

    def test_get_random_intersection(self):
        intersection1 = self.tm1.cubes.get_random_intersection(cube_name=self.cube_name, unique_names=False)
        intersection2 = self.tm1.cubes.get_random_intersection(cube_name=self.cube_name, unique_names=False)
        self.assertNotEqual(intersection1, intersection2)
        intersection1 = self.tm1.cubes.get_random_intersection(cube_name=self.cube_name, unique_names=True)
        intersection2 = self.tm1.cubes.get_random_intersection(cube_name=self.cube_name, unique_names=True)
        self.assertNotEqual(intersection1, intersection2)

    def test_exists(self):
        self.assertTrue(self.tm1.cubes.exists(self.cube_name))
        self.assertFalse(self.tm1.cubes.exists(uuid.uuid4()))

    def test_create_delete_cube(self):
        cube_name = self.cube_name_to_delete
        # use own dimensions. Other dimensions may be deleted by tests running in parallel
        dimension_names = self.dimension_names[0:2]
        cube = Cube(cube_name, dimension_names)

        self.assertNotIn(cube_name, self.tm1.cubes.get_all_names())
        self.tm1.cubes.update_or_create(cube)
        self.assertIn(cube_name, self.tm1.cubes.get_all_names())
        self.assertEqual(self.tm1.cubes.get_dimension_names(cube_name), dimension_names)

        self.tm1.cubes.delete(cube_name)
        self.assertNotIn(cube_name, self.tm1.cubes.get_all_names())

    def test_get_all_names(self):
        # other tests may create or delete cubes in parallel, so compare memberships instead of counts
        cubes_with_rules = set(self.tm1.cubes.get_all_names_with_rules())
        cubes_without_rules = set(self.tm1.cubes.get_all_names_without_rules())
        self.assertFalse(cubes_with_rules & cubes_without_rules)
        self.assertIn(self.cube_name, self.tm1.cubes.get_all_names())
        self.assertIn(self.cube_name, cubes_without_rules)

        self.assertIn(self.control_cube_name, self.tm1.cubes.get_all_names())
        self.assertNotIn(self.control_cube_name, self.tm1.cubes.get_all_names(skip_control_cubes=True))

        cube_name = self.cube_name_to_delete
        dimension_names = self.dimension_names[0:2]
        cube = Cube(cube_name, dimension_names)
        self.tm1.cubes.update_or_create(cube)
        self.assertIn(cube_name, self.tm1.cubes.get_all_names_without_rules())
        self.assertNotIn(cube_name, self.tm1.cubes.get_all_names_with_rules())

        cube.rules = "SKIPCHECK"
        self.tm1.cubes.update(cube)
        self.assertIn(cube_name, self.tm1.cubes.get_all_names_with_rules())
        self.assertNotIn(cube_name, self.tm1.cubes.get_all_names_without_rules())

        self.tm1.cubes.delete(cube_name)

        cube = self.tm1.cubes.get(self.control_cube_name)
        cube.rules = "SKIPCHECK"
        self.tm1.cubes.update(cube)
        self.assertNotEqual(
            self.tm1.cubes.get_all_names_with_rules(), self.tm1.cubes.get_all_names_with_rules(skip_control_cubes=True)
        )
        self.assertNotEqual(
            self.tm1.cubes.get_all_names_without_rules(),
            self.tm1.cubes.get_all_names_without_rules(skip_control_cubes=True),
        )

    @skip_if_version_lower_than(version="11.4")
    def test_get_storage_dimension_order(self):
        dimensions = self.tm1.cubes.get_storage_dimension_order(cube_name=self.cube_name)
        self.assertEqual(dimensions, self.dimension_names)

    def test_search_for_dimension_happy_case(self):
        cube_names = self.tm1.cubes.search_for_dimension(self.dimension_names[0])
        self.assertEqual([self.cube_name, self.control_cube_name], cube_names)

    def test_search_for_dimension_no_match(self):
        cube_names = self.tm1.cubes.search_for_dimension("NotADimensionName")
        self.assertEqual([], cube_names)

    def test_search_for_dimension_case_insensitive(self):
        cube_names = self.tm1.cubes.search_for_dimension(self.dimension_names[1].upper())
        self.assertEqual([self.cube_name, self.control_cube_name], cube_names)

    def test_search_for_dimension_space_insensitive(self):
        cube_names = self.tm1.cubes.search_for_dimension(" " + self.dimension_names[2] + " ")
        self.assertEqual([self.cube_name, self.control_cube_name], cube_names)

    def test_search_for_dimension_substring_happy_case(self):
        cubes = self.tm1.cubes.search_for_dimension_substring(substring=self.dimension_names[0])
        self.assertEqual(
            {self.cube_name: [self.dimension_names[0]], self.control_cube_name: [self.dimension_names[0]]}, cubes
        )

    def test_search_for_dimension_substring_case_insensitive(self):
        cubes = self.tm1.cubes.search_for_dimension_substring(substring=self.dimension_names[1].upper())
        self.assertEqual(
            cubes, {self.cube_name: [self.dimension_names[1]], self.control_cube_name: [self.dimension_names[1]]}
        )

    def test_search_for_dimension_substring_space_insensitive(self):
        cubes = self.tm1.cubes.search_for_dimension_substring(substring=" " + self.dimension_names[2] + " ")
        self.assertEqual(
            cubes, {self.cube_name: [self.dimension_names[2]], self.control_cube_name: [self.dimension_names[2]]}
        )

    def test_search_for_dimension_substring_no_match(self):
        cubes = self.tm1.cubes.search_for_dimension_substring(substring="NotADimensionName")
        self.assertEqual({}, cubes)

    def test_search_for_dimension_substring_skip_control_cubes_true(self):
        cubes = self.tm1.cubes.search_for_dimension_substring(substring="}cubes", skip_control_cubes=True)
        self.assertEqual({}, cubes)

    @skip_if_version_higher_or_equal_than(version="12")
    def test_search_for_dimension_substring_skip_control_cubes_false_v11(self):
        cubes = self.tm1.cubes.search_for_dimension_substring(substring="}cubes", skip_control_cubes=False)
        self.assertEqual(cubes["}CubeProperties"], ["}Cubes"])

    @skip_if_version_lower_than(version="12")
    def test_search_for_dimension_substring_skip_control_cubes_false_v12(self):
        cubes = self.tm1.cubes.search_for_dimension_substring(substring="}cubes", skip_control_cubes=False)
        self.assertEqual(cubes["}CubeSecurity"], ["}Cubes"])

    def test_get_number_of_cubes(self):
        number_of_cubes = self.tm1.cubes.get_number_of_cubes()
        self.assertIsInstance(number_of_cubes, int)

    @skip_if_version_lower_than(version="11.4")
    def test_update_storage_dimension_order(self):
        self.tm1.cubes.update_storage_dimension_order(
            cube_name=self.cube_name, dimension_names=reversed(self.dimension_names)
        )
        dimensions = self.tm1.cubes.get_storage_dimension_order(self.cube_name)
        self.assertEqual(list(reversed(dimensions)), self.dimension_names)

    @skip_if_version_lower_than(version="11.6")
    @skip_if_version_higher_or_equal_than(version="12")
    def test_load(self):
        response = self.tm1.cubes.load(cube_name=self.cube_name)
        self.assertTrue(response.ok)

    @skip_if_version_lower_than(version="11.6")
    @skip_if_version_higher_or_equal_than(version="12")
    def test_unload(self):
        response = self.tm1.cubes.unload(cube_name=self.cube_name)
        self.assertTrue(response.ok)

    def test_lock(self):
        response = self.tm1.cubes.lock(cube_name=self.cube_name)
        self.assertTrue(response.ok)

    def test_unlock(self):
        self.tm1.cubes.lock(cube_name=self.cube_name)
        response = self.tm1.cubes.unlock(cube_name=self.cube_name)
        self.assertTrue(response.ok)

    def test_check_rules_without_errors(self):
        errors = self.tm1.cubes.check_rules(cube_name=self.cube_name)
        self.assertEqual(0, len(errors))

    def test_check_rules_with_errors(self):
        cube = self.tm1.cubes.get(cube_name=self.cube_name)
        cube.rules = "SKIPCHECK"
        self.tm1.cubes.update(cube)

        errors = self.tm1.cubes.check_rules(cube_name=self.cube_name)
        self.assertEqual(1, len(errors))

    def test_check_supplied_rules_without_errors(self):
        rules = "SKIPCHECK;"

        errors = self.tm1.cubes.check_rules(cube_name=self.cube_name, rules=rules)

        self.assertEqual(0, len(errors))

    def test_check_supplied_rules_with_errors(self):
        rules = "SKIPCHECK"

        errors = self.tm1.cubes.check_rules(cube_name=self.cube_name, rules=rules)

        self.assertEqual(1, len(errors))

    def test_check_supplied_invalid_rules_returns_api_validation_error(self):
        rules = "['Element'] = N: 1"  # Missing semicolon

        errors = self.tm1.cubes.check_rules(cube_name=self.cube_name, rules=rules)

        self.assertEqual(1, len(errors))
        self.assertEqual(1, errors[0]["LineNumber"])
        self.assertIn("Element", errors[0]["Message"])
        self.assertTrue(errors[0]["Message"])

    def test_check_supplied_rules_does_not_update_cube(self):
        rules = "SKIPCHECK;"

        self.tm1.cubes.check_rules(cube_name=self.cube_name, rules=rules)

        cube = self.tm1.cubes.get(cube_name=self.cube_name)
        self.assertFalse(cube.has_rules)

    def test_check_supplied_rules_object(self):
        errors = self.tm1.cubes.check_rules(cube_name=self.cube_name, rules=Rules("SKIPCHECK;"))

        self.assertEqual(0, len(errors))

    def test_check_supplied_rules_typing_error(self):
        self.assertRaises(
            ValueError, lambda: self.tm1.cubes.check_rules(cube_name=self.cube_name, rules=["SKIPCHECK;"])
        )

    def test_update_or_create_rules_str_happy_case(self):
        """
        Check if the rules: str will be updated or created on cube
        """
        rules = "#test_rules"
        self.tm1.cubes.update_or_create_rules(cube_name=self.cube_name, rules=rules)
        self.assertEqual(rules, self.tm1.cubes.get(cube_name=self.cube_name).rules.text)

    def test_update_or_create_rules_happy_case(self):
        """
        Check if the rules: Rules will be updated or created on cube
        """
        rules = Rules("#test_rules_update")
        self.tm1.cubes.update_or_create_rules(cube_name=self.cube_name, rules=rules)
        self.assertEqual(rules.text, self.tm1.cubes.get(cube_name=self.cube_name).rules.text)

    def test_update_or_create_rules_for_nonexistent_cube(self):
        """
        Check if the function will raise TM1pyRestException for an update on a nonexistent cube
        """
        nonexist_cube_name = "nonexist_cube"
        rules = "#test_rules"
        self.assertRaises(
            TM1pyRestException, lambda: self.tm1.cubes.update_or_create_rules(cube_name=nonexist_cube_name, rules=rules)
        )

    def test_update_or_create_rules_list_typing_error(self):
        """
        Check if the function will raise a ValueError for rules in list type
        """
        self.assertRaises(
            ValueError, lambda: self.tm1.cubes.update_or_create_rules(cube_name=self.cube_name, rules=["#list_rules"])
        )

    def test_update_or_create_rules_dict_typing_error(self):
        """
        Check if the function will raise a ValueError for rules in dict type
        """
        self.assertRaises(
            ValueError, lambda: self.tm1.cubes.update_or_create_rules(cube_name=self.cube_name, rules={"#dict_rules"})
        )

    def test_search_for_rule_substring_no_match(self):
        cubes = self.tm1.cubes.search_for_rule_substring(substring="find_nothing")
        self.assertEqual(0, len(cubes))

    def test_search_for_rule_substring_happy_case(self):
        cube = self.tm1.cubes.get(cube_name=self.cube_name)
        cube.rules = "SKIPCHECK;\n#" + self.rule_comment
        self.tm1.cubes.update(cube)

        cubes = self.tm1.cubes.search_for_rule_substring(substring=self.rule_comment)
        self.assertEqual([self.cube_name], [cube.name for cube in cubes])

    def test_search_for_rule_substring_skip_control_cubes_false(self):
        cube = self.tm1.cubes.get(self.control_cube_name)
        cube.rules = "SKIPCHECK;\n[]=N:1;\n#" + self.rule_comment + "\nFEEDERS;"
        self.tm1.cubes.update(cube)

        cubes = self.tm1.cubes.search_for_rule_substring(substring=self.rule_comment, skip_control_cubes=False)
        self.assertEqual([self.control_cube_name], [cube.name for cube in cubes])

    def test_search_for_rule_substring_space_insensitive(self):
        cube = self.tm1.cubes.get(self.cube_name)
        cube.rules = "SKIPCHECK;\n[]=N:2;\n#" + self.rule_comment + "\nFEEDERS;"
        self.tm1.cubes.update(cube)

        cubes = self.tm1.cubes.search_for_rule_substring(
            substring="find _me _COMMENT_" + self.test_uuid.upper(), skip_control_cubes=False
        )
        self.assertEqual([self.cube_name], [cube.name for cube in cubes])

    def test_search_for_rule_substring_skip_control_cubes_true(self):
        cube = self.tm1.cubes.get(self.control_cube_name)
        cube.rules = "SKIPCHECK;\n#" + self.rule_comment
        self.tm1.cubes.update(cube)

        cubes = self.tm1.cubes.search_for_rule_substring(substring=self.rule_comment, skip_control_cubes=True)
        self.assertEqual(0, len(cubes))

    def test_get_measure_dimension(self):
        measure_dimension = self.tm1.cubes.get_measure_dimension(self.cube_name)

        self.assertEqual(self.dimension_names[-1], measure_dimension)

    def test_set_and_get_measure_dimension(self):
        # assign a non-last dimension as the measures dimension
        self.tm1.cubes.set_measure_dimension(self.cube_name, self.dimension_names[0])

        measure_dimension = self.tm1.cubes.get_measure_dimension(self.cube_name)
        self.assertEqual(self.dimension_names[0], measure_dimension)

    def test_set_measure_dimension_invalid_dimension(self):
        with self.assertRaises(ValueError):
            self.tm1.cubes.set_measure_dimension(self.cube_name, "Not_A_Dimension_Of_The_Cube")

    def test_get_time_dimension_not_set(self):
        time_dimension = self.tm1.cubes.get_time_dimension(self.cube_name)
        self.assertIsNone(time_dimension)

    def test_set_and_get_time_dimension(self):
        self.tm1.cubes.set_time_dimension(self.cube_name, self.dimension_names[1])

        time_dimension = self.tm1.cubes.get_time_dimension(self.cube_name)
        self.assertEqual(self.dimension_names[1], time_dimension)

    def test_set_time_dimension_invalid_dimension(self):
        with self.assertRaises(ValueError):
            self.tm1.cubes.set_time_dimension(self.cube_name, "Not_A_Dimension_Of_The_Cube")

    def tearDown(self):
        for cube_name in (self.cube_name, self.control_cube_name, self.cube_name_to_delete):
            if self.tm1.cubes.exists(cube_name):
                self.tm1.cubes.delete(cube_name)
        for dimension_name in self.dimension_names:
            if self.tm1.dimensions.exists(dimension_name):
                self.tm1.dimensions.delete(dimension_name)


if __name__ == "__main__":
    unittest.main()
