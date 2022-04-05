"""Test setup for the Python unittest module."""
import json
from pathlib import Path
from shutil import rmtree


class TestUtils:
    """Test setup for the Python unittest module."""
    project_path = Path().home().resolve().__str__() + "/Desktop" + "/G81.2022.15.E3"
    json_store = project_path + "/src/json/db"
    json_collection = project_path + "/src/json/collection"

    patient_registry = json_store + "/patient_registry.json"
    vaccination_appointments = json_store + "/vaccination_appointments.json"
    vaccination_administration = json_store + "/vaccine_administration.json"

    @classmethod
    def setup_folders(cls):
        """Create folders for testing."""
        Path(cls.json_store).mkdir(parents=True, exist_ok=True)
        Path(cls.json_collection).mkdir(parents=True, exist_ok=True)
        Path(cls.patient_registry) \
            .touch(mode=0o777, exist_ok=True)
        Path(cls.vaccination_appointments) \
            .touch(mode=0o777, exist_ok=True)
        Path(cls.vaccination_administration) \
            .touch(mode=0o777, exist_ok=True)

        cls.clear_json_file(cls.patient_registry)
        cls.clear_json_file(cls.vaccination_appointments)
        cls.clear_json_file(cls.vaccination_administration)

    @classmethod
    def cleanup_all_folders(cls):
        """Cleanup folders for testing."""
        rmtree(cls.json_store)

    @classmethod
    def add_element_to_json_file(cls, path, new_elem: dict):
        with open(path, "r+", encoding="utf-8") as file:
            data = json.load(file)
            data.append(new_elem)
            file.seek(0)
            json.dump(data, file, indent=2)

    @classmethod
    def read_json_file(cls, path):
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    @classmethod
    def clear_json_file(cls, path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump([], file)
