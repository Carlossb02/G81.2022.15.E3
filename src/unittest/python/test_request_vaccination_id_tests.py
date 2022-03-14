"""
Test module
"""
import hashlib
import json
from unittest import TestCase, main, mock
from datetime import datetime
from freezegun import freeze_time

from test_utils import TestUtils
from uc3m_care.vaccine_manager import VaccineManager
from uc3m_care.vaccine_management_exception import VaccineManagementException


class TestRequestVaccinationId(TestCase):
    """
    Test class for the RequestVaccinationId Function.
    """

    def setUp(self) -> None:
        self.patient_data = {
            "patient_id": "43831e01-cd0f-4b97-aa6d-c071b42129f0",
            "name_surname": "Christoph Hartmann",
            "registration_type": "Family",
            "phone_number": "123456789",
            "age": 20,
        }

    @classmethod
    def setUpClass(cls) -> None:
        TestUtils.setup_folders()

    @classmethod
    def tearDownClass(cls) -> None:
        TestUtils.cleanup_all_folders()

    # mock datetime
    @freeze_time("2020-04-26")
    def test_ok(self, ):
        vaccine_manager = VaccineManager()
        value = vaccine_manager.request_vaccination_id(**self.patient_data)

        justnow = datetime.utcnow()
        time_stamp = datetime.timestamp(justnow)
        self.patient_data["time_stamp"] = time_stamp

        hashed_patient = hashlib.md5(json.dumps(self.patient_data).encode("utf-8")).hexdigest()
        self.assertEqual(hashed_patient, value)

        found_file = False
        patient_registry_data = TestUtils.read_json_file(TestUtils.patient_registry)
        for patient in patient_registry_data:
            if patient["patient_id"] == self.patient_data["patient_id"]:
                found_file = True
        self.assertTrue(found_file)

    def test_wrong_uuid_not_v4(self):
        vaccine_manager = VaccineManager()
        patient_data = self.patient_data
        patient_data["patient_id"] = "43831e01-cd0f-7b97-aa6d-c071b42129f0"
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient_data)
        self.assertEqual(exception.exception.message, "Invalid UUID format")


if __name__ == '__main__':
    main()
