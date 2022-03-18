"""Vaccine manager"""
import json
import re
import uuid
from pathlib import Path

from uc3m_care.vaccine_management_exception import VaccineManagementException
from uc3m_care.vaccine_patient_register import VaccinePatientRegister


class VaccineManager:
    """Class for providing the methods for managing the vaccination process"""
    project_path = Path().home().resolve().__str__() + "/Desktop" + "/G81.2022.15.E3"
    json_store = project_path + "/src/json/db"
    json_collection = project_path + "/src/json/collection"

    patient_registry = json_store + "/patient_registry.json"
    vaccination_appointments = json_store + "/vaccination_appointments.json"
    vaccination_administration = json_store + "/vaccine_administration.json"

    def __init__(self) -> None:
        self.__uuid4_rule = re.compile(r'^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB]'
                                       r'[0-9A-F]{3}-[0-9A-F]{12}$',
                                       re.IGNORECASE)

    def validate_uuid4(self, guid: str) -> bool:
        """
        Validates the GUID
        :param guid: GUID to validate (str)
        :return: True if the GUID is valid, False otherwise (bool)
        :raises: VaccineManagementException: If the GUID is not valid
        """
        try:
            uuid.UUID(guid)
            match = self.__uuid4_rule.fullmatch(guid)
            if not match:
                raise VaccineManagementException("Invalid UUID format")
        except ValueError as error:
            raise VaccineManagementException("Invalid UUID format") from error
        return True

    def request_vaccination_id(self, patient_id: str, registration_type: str,
                               name_surname: str, phone_number: str,
                               age: int) -> str:
        """
        Requests the vaccination ID
        :param patient_id:
        :param registration_type:
        :param name_surname:
        :param phone_number:
        :param age:
        :return MD5 hash of the patient ID (str)
        """
        if type(patient_id)!=str:
            raise VaccineManagementException("Invalid patient ID")
        try:
            self.validate_uuid4(patient_id)
        except VaccineManagementException as error:
            raise VaccineManagementException("Invalid patient ID") from error

        if registration_type not in ["Regular", "Family"]:
            raise VaccineManagementException("Invalid registration type")

        if name_surname == "" or type(name_surname)!=str:
            raise VaccineManagementException("Invalid name and surname")
        if len(name_surname) > 30:
            raise VaccineManagementException("Invalid name and surname")

        split_name_surname = name_surname.split(" ")
        if len(split_name_surname) < 2:
            raise VaccineManagementException("Invalid name and surname")

        if len(phone_number) != 9:
            raise VaccineManagementException("Invalid phone number")

        try:
            int(phone_number)
        except ValueError as error:
            raise VaccineManagementException("Invalid phone number") from error

        try:
            int_age = int(age)
        except ValueError as error:
            raise VaccineManagementException("Invalid age") from error

        if int_age < 6 or int_age > 125 or type(age)!=int:
            raise VaccineManagementException("Invalid age")

        vaccine_patient_register = VaccinePatientRegister(patient_id=patient_id, full_name=name_surname,
                                                          phone_number=phone_number,
                                                          age=age, registration_type=registration_type)

        with open(self.patient_registry, "r+",
                  encoding="utf-8") as file:
            file.seek(0)
            json.dump({
            "patient_id": patient_id, "name_surname": name_surname,
            "registration_type": registration_type,
            "phone_number": phone_number, "age": age,}, file, indent=2)

        return vaccine_patient_register.patient_system_id
