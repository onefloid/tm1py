import configparser
import unittest
from pathlib import Path

from Tests.Utils import generate_test_uuid
from TM1py import TM1Service
from TM1py.Exceptions import TM1pyVersionException

from .Utils import (
    skip_if_version_higher_or_equal_than,
    skip_if_version_lower_than,
    verify_version,
)


class TestFileService(unittest.TestCase):
    tm1: TM1Service

    @classmethod
    def setUpClass(cls) -> None:
        """
        Establishes a connection to TM1 and defines unique file and folder names for this test run
        """
        cls.config = configparser.ConfigParser()
        cls.config.read(Path(__file__).parent.joinpath("config.ini"))
        cls.tm1 = TM1Service(**cls.config["tm1srv01"])

        cls.test_uuid = generate_test_uuid()
        cls.FILE_NAME1 = "TM1py_unittest_" + cls.test_uuid + "_file1"
        cls.FILE_NAME2 = "TM1py_unittest_" + cls.test_uuid + "_file2"
        cls.FILE_NAME3 = "TM1py_unittest_" + cls.test_uuid + "_file3"

        cls.ROOT_FOLDER = "TM1py_unittest_" + cls.test_uuid
        cls.FILE_NAME1_IN_FOLDER = Path(cls.ROOT_FOLDER) / "Tests" / cls.FILE_NAME1
        cls.FILE_NAME2_IN_FOLDER = Path(cls.ROOT_FOLDER) / "Tests" / cls.FILE_NAME2

        cls.FOLDER_NAME1 = "TM1py_unittest_folder1_" + cls.test_uuid
        cls.NESTED_FOLDER_PATH = Path("TM1py_unittest_folder2_" + cls.test_uuid) / "subfolder_a" / "subfolder_b"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tm1.logout()

    def setUp(self) -> None:
        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as file:
            self.tm1.files.update_or_create(self.FILE_NAME1, file.read())

        if self.tm1.files.exists(self.FILE_NAME2):
            self.tm1.files.delete(self.FILE_NAME2)

        if self.tm1.files.exists(self.FILE_NAME3):
            self.tm1.files.delete(self.FILE_NAME3)

        if verify_version(required_version="12", version=self.tm1.version):
            self.setUpV12()

    @skip_if_version_lower_than(version="12")
    def setUpV12(self):
        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as file:
            self.tm1.files.update_or_create(self.FILE_NAME1_IN_FOLDER, file.read())

        if self.tm1.files.exists(self.FILE_NAME2_IN_FOLDER):
            self.tm1.files.delete(self.FILE_NAME2_IN_FOLDER)

        if self.tm1.files.exists(self.FOLDER_NAME1):
            self.tm1.files.delete(self.FOLDER_NAME1)

        if self.tm1.files.exists(self.NESTED_FOLDER_PATH.parts[0]):
            self.tm1.files.delete(self.NESTED_FOLDER_PATH.parts[0])

    def run_create_get(self, mpu, max_mb_per_part=None, max_workers=1):
        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            self.tm1.files.update_or_create(
                self.FILE_NAME1,
                original_file.read(),
                multi_part_upload=mpu,
                max_mb_per_part=max_mb_per_part,
                max_workers=max_workers,
            )

            created_file = self.tm1.files.get(self.FILE_NAME1)
        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            self.assertEqual(original_file.read(), created_file)

    @skip_if_version_lower_than(version="11.4")
    def test_create_get(self):
        self.run_create_get(mpu=False)

    @skip_if_version_lower_than(version="12")
    def test_create_get_empty_file_with_mpu(self):
        self.tm1.files.update_or_create(
            self.FILE_NAME3, b"", multi_part_upload=True, max_mb_per_part=200, max_workers=1
        )

        created_file = self.tm1.files.get(self.FILE_NAME3)
        self.assertEqual(b"", created_file)

    @skip_if_version_lower_than(version="12")
    def test_create_get_with_mpu_1_byte_per_part(self):
        self.run_create_get(mpu=True, max_mb_per_part=1 / (1024 * 1024))

    @skip_if_version_lower_than(version="12")
    def test_create_get_with_mpu_1_byte_per_part_10_max_workers(self):
        self.run_create_get(mpu=True, max_mb_per_part=1 / (1024 * 1024), max_workers=10)

    @skip_if_version_lower_than(version="12")
    def test_create_get_with_mpu_200_megabyte_per_part(self):
        self.run_create_get(mpu=True, max_mb_per_part=200)

    @skip_if_version_lower_than(version="12")
    def test_create_get_in_folder(self):
        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            self.tm1.files.update_or_create(self.FILE_NAME1_IN_FOLDER, original_file.read())

            created_file = self.tm1.files.get(self.FILE_NAME1_IN_FOLDER)

        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            self.assertEqual(original_file.read(), created_file)

    @skip_if_version_lower_than(version="12")
    def test_create_get_in_folder_with_mpu(self):
        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            self.tm1.files.update_or_create(
                self.FILE_NAME1_IN_FOLDER, original_file.read(), mpu=True, max_mb_per_part=1 / (1024 * 1024)
            )

            created_file = self.tm1.files.get(self.FILE_NAME1_IN_FOLDER)

        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            self.assertEqual(original_file.read(), created_file)

    @skip_if_version_lower_than(version="11.4")
    @skip_if_version_higher_or_equal_than(version="12")
    def test_create_in_folder_exception(self):
        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            with self.assertRaises(TM1pyVersionException) as e:
                self.tm1.files.update_or_create(self.FILE_NAME1_IN_FOLDER, original_file.read())
            self.assertEqual(
                str(e.exception),
                "'Subfolder' feature of function 'FileService.create' requires TM1 server version >= '12'",
            )

    @skip_if_version_lower_than(version="11.4")
    def test_update_get(self):
        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            self.tm1.files.update(self.FILE_NAME1, original_file.read())

            created_file = self.tm1.files.get(self.FILE_NAME1)

        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            self.assertEqual(original_file.read(), created_file)

    @skip_if_version_lower_than(version="12")
    def test_update_get_in_folder(self):
        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            self.tm1.files.update(self.FILE_NAME1_IN_FOLDER, original_file.read())

            created_file = self.tm1.files.get(self.FILE_NAME1_IN_FOLDER)

        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            self.assertEqual(original_file.read(), created_file)

    @skip_if_version_lower_than(version="11.4")
    @skip_if_version_higher_or_equal_than(version="12")
    def test_update_in_folder_exception(self):
        with open(Path(__file__).parent.joinpath("resources", "file.csv"), "rb") as original_file:
            with self.assertRaises(TM1pyVersionException) as e:
                self.tm1.files.update(self.FILE_NAME1_IN_FOLDER, original_file.read())
            self.assertEqual(
                str(e.exception),
                "'Subfolder' feature of function 'FileService.update' requires TM1 server version >= '12'",
            )

    @skip_if_version_lower_than(version="11.4")
    def test_get_all_names(self):
        result = self.tm1.files.get_all_names()
        self.assertIn(self.FILE_NAME1, result)

    @skip_if_version_lower_than(version="12")
    def test_get_all_names_in_folder(self):
        result = self.tm1.files.get_all_names(path=self.FILE_NAME1_IN_FOLDER.parent)
        self.assertIn(self.FILE_NAME1, result)

    @skip_if_version_lower_than(version="11.4")
    def test_search_string_in_name__name_startswith(self):
        result = self.tm1.files.search_string_in_name(name_startswith=self.FILE_NAME1)
        self.assertEqual([self.FILE_NAME1], result)

    @skip_if_version_lower_than(version="12")
    def test_search_string_in_name__name_startswith_in_folder(self):
        result = self.tm1.files.search_string_in_name(
            name_startswith=self.FILE_NAME1, path=self.FILE_NAME1_IN_FOLDER.parent
        )
        self.assertEqual([self.FILE_NAME1], result)

    @skip_if_version_lower_than(version="11.4")
    @skip_if_version_higher_or_equal_than(version="12")
    def test_search_string_in_name__name_startswith_in_folder_exception(self):
        with self.assertRaises(TM1pyVersionException) as e:
            self.tm1.files.search_string_in_name(name_startswith=self.FILE_NAME1, path=self.FILE_NAME1_IN_FOLDER.parent)
            self.assertEqual(
                str(e.exception),
                "'Subfolder' feature of function 'FileService.search_string_in_name' requires TM1 server version >= '12'",
            )

    @skip_if_version_lower_than(version="11.4")
    def test_search_string_in_name__name_startswith_not_existing(self):
        result = self.tm1.files.search_string_in_name(name_startswith="not_the_file_im_looking_for")
        self.assertEqual([], result)

    @skip_if_version_lower_than(version="11.4")
    def test_search_string_in_name__name_contains_both_existing(self):
        result = self.tm1.files.search_string_in_name(name_contains=[self.test_uuid, "file1"])
        self.assertEqual([self.FILE_NAME1], result)

    @skip_if_version_lower_than(version="11.4")
    def test_search_string_in_name__name_contains_mixed_existing_and(self):
        result = self.tm1.files.search_string_in_name(name_contains=[self.FILE_NAME1[:5], "NotFound"])
        self.assertEqual([], result)

    @skip_if_version_lower_than(version="11.4")
    def test_search_string_in_name__name_contains_mixed_existing_or(self):
        result = self.tm1.files.search_string_in_name(
            name_contains=[self.FILE_NAME1, "NotFound"], name_contains_operator="OR"
        )
        self.assertEqual([self.FILE_NAME1], result)

    @skip_if_version_lower_than(version="11.4")
    def test_delete_exists(self):
        self.assertTrue(self.tm1.files.exists(self.FILE_NAME1))

        self.tm1.files.delete(self.FILE_NAME1)

        self.assertFalse(self.tm1.files.exists(self.FILE_NAME1))

    @skip_if_version_lower_than(version="12")
    def test_delete_exists_in_folder(self):
        self.assertTrue(self.tm1.files.exists(self.FILE_NAME1_IN_FOLDER))

        self.tm1.files.delete(self.FILE_NAME1_IN_FOLDER)

        self.assertFalse(self.tm1.files.exists(self.FILE_NAME1_IN_FOLDER))

    @skip_if_version_lower_than(version="11.4")
    @skip_if_version_higher_or_equal_than(version="12")
    def test_delete_in_folder_exception(self):
        with self.assertRaises(TM1pyVersionException) as e:
            self.tm1.files.delete(self.FILE_NAME1_IN_FOLDER)
            self.assertEqual(
                str(e.exception),
                "'Subfolder' feature of function 'FileService.delete' requires TM1 server version >= '12'",
            )

    @skip_if_version_lower_than(version="12")
    def test_create_folder_with_str(self):
        self.tm1.files.create_folder(self.FOLDER_NAME1)

        result = self.tm1.files.get_all_names()
        self.assertIn(self.FOLDER_NAME1, result)

    @skip_if_version_lower_than(version="12")
    def test_create_folder_with_path(self):
        self.tm1.files.create_folder(Path(self.FOLDER_NAME1))

        result = self.tm1.files.get_all_names()
        self.assertIn(self.FOLDER_NAME1, result)

    @skip_if_version_lower_than(version="12")
    def test_create_folder_idempotent(self):
        self.tm1.files.create_folder(self.FOLDER_NAME1)
        self.tm1.files.create_folder(self.FOLDER_NAME1)

        result = self.tm1.files.get_all_names()
        self.assertIn(self.FOLDER_NAME1, result)

    @skip_if_version_lower_than(version="12")
    def test_create_folder_nested(self):
        self.tm1.files.create_folder(self.NESTED_FOLDER_PATH)

        result = self.tm1.files.get_all_names(path=self.NESTED_FOLDER_PATH.parent)
        self.assertIn(self.NESTED_FOLDER_PATH.name, result)

    def tearDown(self) -> None:
        if self.tm1.files.exists(self.FILE_NAME1):
            self.tm1.files.delete(self.FILE_NAME1)
        if self.tm1.files.exists(self.FILE_NAME2):
            self.tm1.files.delete(self.FILE_NAME2)
        if self.tm1.files.exists(self.FILE_NAME3):
            self.tm1.files.delete(self.FILE_NAME3)
        if self.tm1.files.exists(self.FILE_NAME1_IN_FOLDER):
            self.tm1.files.delete(self.FILE_NAME1_IN_FOLDER)
        if self.tm1.files.exists(self.FILE_NAME2_IN_FOLDER):
            self.tm1.files.delete(self.FILE_NAME2_IN_FOLDER)
        if self.tm1.files.exists(self.FOLDER_NAME1):
            self.tm1.files.delete(self.FOLDER_NAME1)
        if self.tm1.files.exists(self.NESTED_FOLDER_PATH.parts[0]):
            self.tm1.files.delete(self.NESTED_FOLDER_PATH.parts[0])
        if verify_version(required_version="12", version=self.tm1.version):
            if self.tm1.files.exists(self.ROOT_FOLDER):
                self.tm1.files.delete(self.ROOT_FOLDER)
