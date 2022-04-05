"""Tests de la funcion get_vaccine_date()"""

import json
from unittest import TestCase
from pathlib import Path
from freezegun import freeze_time
from uc3m_care.vaccine_manager import VaccineManager
from uc3m_care.vaccine_management_exception import VaccineManagementException
from uc3m_care.vaccination_appoinment import VaccinationAppoinment

class MyTestCase(TestCase):
    """"Clase en la que se inicializan los tests"""
    @freeze_time("2020-04-26")
    def setUp(self) -> None:
        """"SetUp"""
        self.patient_data = {
            "patient_id": "43831e01-cd0f-4b97-aa6d-c071b42129f0",
            "name_surname": "Fernando Alonso",
            "registration_type": "Family",
            "phone_number": "123456789",
            "age": 20,
        }
        self.direccion=Path().home().resolve().__str__() + "/Desktop" + "/G81.2022.15.E3" + "/src/json"
        with open(self.direccion + "/db/patient_registry.json", 'r', encoding="utf-8") as file:
            data = json.load(file)
            file.close()

        found=False

        for dict in data:
            if dict["patient_id"]==self.patient_data["patient_id"]:
                found=True
                self.patient_system_id=dict["patient_system_id"]
        if not found:
            v_p=VaccineManager()
            self.patient_system_id=v_p.request_vaccination_id(**self.patient_data)


    def test_json_no_existe(self):
        """Se comprueba que si el json no existe, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(self.direccion + "/collection/estearchivonoexiste.json")
        self.assertEqual(exception.exception.message, "File does not exist")

    def test_no_es_json(self):
        """Se comprueba que si el fichero no es .json no existe, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(self.direccion + "/collection/estearchivonoesjson.txt")
        self.assertEqual(exception.exception.message, "Invalid file type")

    def test_path_no_str(self):
        """Se comprueba que si la dirreción no es un string, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(12345)
        self.assertEqual(exception.exception.message, "Invalid input type")

    def test_estructura_incorrecta_1(self):
        """Se comprueba que si las llaves del diccionario no son correctas, se lanza una excepción
        (Archivo test_estructura_incorrecta_1.json en json/collection)"""
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(self.direccion + "/collection/test_estructura_incorrecta_1.json")
        self.assertEqual(exception.exception.message, "Invalid JSON structure")

    def test_estructura_incorrecta_2(self):
        """Se comprueba que si hay más llaves de las necesarias, se lanza una excepción
        (Archivo test_estructura_incorrecta_2.json en json/collection)"""
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(self.direccion + "/collection/test_estructura_incorrecta_2.json")
        self.assertEqual(exception.exception.message, "Invalid JSON structure")

    def test_estructura_incorrecta_3(self):
        """Se comprueba que si hay menos llaves de las necesarias, se lanza una excepción
        (Archivo test_estructura_incorrecta_3.json en json/collection)"""
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(self.direccion + "/collection/test_estructura_incorrecta_3.json")
        self.assertEqual(exception.exception.message, "Invalid JSON structure")

    def test_patient_system_id_no_str(self):
        """Se comprueba que si el PatientSystemID es incorrecto, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        path=vaccine_manager.generate_json(1234434,"123456789")
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(path)
        self.assertEqual(exception.exception.message, "Invalid PatientSystemID")

    def test_patient_system_id_corto(self):
        """Se comprueba que si el PatientSystemID es demasiado corto, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        path=vaccine_manager.generate_json("abc","123456789")
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(path)
        self.assertEqual(exception.exception.message, "Invalid PatientSystemID")

    def test_patient_system_id_largo(self):
        """Se comprueba que si el PatientSystemID es demasiado largo, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        path=vaccine_manager.generate_json("abcd12343482sqaffeajs2384shdiwdjsadb","123456789")
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(path)
        self.assertEqual(exception.exception.message, "Invalid PatientSystemID")

    def test_phone_no_str(self):
        """Se comprueba que si el ContactPhoneNumber es incorrecto, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        path=vaccine_manager.generate_json("fb545bec6cd4468c3c0736520a4328db",123456789)
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(path)
        self.assertEqual(exception.exception.message, "Invalid ContactPhoneNumber")

    def test_phone_corto(self):
        """Se comprueba que si el ContactPhoneNumber es demasiado corto, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        path=vaccine_manager.generate_json("fb545bec6cd4468c3c0736520a4328db","12345678")
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(path)
        self.assertEqual(exception.exception.message, "Invalid ContactPhoneNumber")

    def test_phone_largo(self):
        """Se comprueba que si el ContactPhoneNumber es demasiado largo, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        path=vaccine_manager.generate_json("fb545bec6cd4468c3c0736520a4328db","1234567895")
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(path)
        self.assertEqual(exception.exception.message, "Invalid ContactPhoneNumber")

    def test_phone_no_numeros(self):
        """Se comprueba que si el ContactPhoneNumber no es un número, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        path=vaccine_manager.generate_json("fb545bec6cd4468c3c0736520a4328db","12345X789")
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(path)
        self.assertEqual(exception.exception.message, "Invalid ContactPhoneNumber")

    def test_paciente_no_registrado(self):
        """Se comprueba que si el paciente no está registrado, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        path=vaccine_manager.generate_json("hb545bec6cd4468c3c0736520a4328db","123456789")
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(path)
        self.assertEqual(exception.exception.message, "This patient is not registered")

    def test_paciente_numero_incorrecto(self):
        """Se comprueba que si el paciente está registrado pero su número es diferente, se lanza una excepción"""
        vaccine_manager = VaccineManager()
        path=vaccine_manager.generate_json(self.patient_system_id,"723456789")
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.get_vaccine_date(path)
        self.assertEqual(exception.exception.message, "Phone numbers are different")

    @freeze_time("2020-04-26")
    def test_vaccination_signature_correcta(self):
        """Se comprueba que si todos los datos son correctos, la vaccination_signature es correcta"""
        vaccine_manager = VaccineManager()
        signature=VaccinationAppoinment(self.patient_data["patient_id"], self.patient_system_id, "123456789", 10).vaccination_signature
        path=vaccine_manager.generate_json(self.patient_system_id,"123456789")
        signature_2=vaccine_manager.get_vaccine_date(path)
        self.assertEqual(signature, signature_2)

    @freeze_time("2020-04-26")
    def test_vaccination_json_correcto(self):
        """Se comprueba que si los datos son correctos, el json es correcto"""
        vaccine_manager = VaccineManager()
        path=vaccine_manager.generate_json(self.patient_system_id,"123456789")
        date_signature=vaccine_manager.get_vaccine_date(path)

        with open(self.direccion + "/db/vaccination_appointments.json", "r+",
                  encoding="utf-8") as file:
            data=json.load(file)
            found=False
            for dict in data:
                if dict==  {
    "patient_id": "43831e01-cd0f-4b97-aa6d-c071b42129f0",
    "phone_number": "123456789",
    "vaccine_date": "2020-05-06",
    "patient_system_id": self.patient_system_id,
    "date_signature": date_signature}:
                    found=True
                    break

        self.assertEqual(found, True)


if __name__ == '__main__':
    unittest.main()
