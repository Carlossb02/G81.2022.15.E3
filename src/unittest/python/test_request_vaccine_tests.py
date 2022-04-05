"""Tests de la funcion request_vaccination_id"""

import hashlib
import json
from unittest import TestCase
from datetime import datetime
from pathlib import Path
from freezegun import freeze_time
from uc3m_care.vaccine_manager import VaccineManager
from uc3m_care.vaccine_management_exception import VaccineManagementException

class MyTestCase(TestCase):
    """"Clase en la que se inicializan los tests"""

    def setUp(self) -> None:
        """"SetUp"""
        self.patient_data = {
            "patient_id": "43831e01-cd0f-4b97-aa6d-c071b42129f0",
            "name_surname": "Fernando Alonso",
            "registration_type": "Family",
            "phone_number": "123456789",
            "age": 20,
        }
        self.direccion=Path().home().resolve().__str__() + "/Desktop" + "/G81.2022.15.E3" + "/src/json/db/patient_registry.json"

        # TESTS validate_uuid4()

    def test_uuid_incorrecta(self):
        """Se comprueba que validate_uuid4() lanza una excepción
        en caso de que la uuid4 no sea correcta"""
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.validate_uuid4("43831e01-cd0f-7b97-aa6d-c071b42129f0")
        self.assertEqual(exception.exception.message, "Invalid UUID format")

    def test_uuid_correcta(self):
        """Se comprueba que validate_uuid4() devuelve True si la
        uuid4 es correcta"""
        vaccine_manager = VaccineManager()
        self.assertEqual(vaccine_manager.validate_uuid4("43831e01-cd0f-4b97-aa6d-c071b42129f0"), True)


        # TESTS request_vaccination_id()

    def test_edad_inferior(self):
        """Se comprueba que se devuelve una excepción si la edad es menor que 6"""
        patient=self.patient_data.copy() #Ponemos .copy() para no modificar el original, ya que python hace paso por referencia
        patient["age"]=4
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid age")

    def test_edad_superior(self):
        """Se comprueba que se devuelve una excepción si la edad es mayor que 120"""
        patient=self.patient_data.copy()
        patient["age"]=150
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid age")

    def test_edad_no_numero(self):
        """Se comprueba que se devuelve una excepción si la edad no es un número"""
        patient=self.patient_data.copy()
        patient["age"]="diez"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid age")

    def test_edad_no_int(self):
        """Se comprueba que se devuelve una excepción si la edad no es un número entero"""
        patient=self.patient_data.copy()
        patient["age"]=float(23.2)
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid age")

    def test_nombre_vacio(self):
        """Se comprueba que se devuelve una excepción si el nombre es una string vacía"""
        patient=self.patient_data.copy()
        patient["name_surname"]=""
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid name and surname")

    def test_nombre_largo(self):
        """Se comprueba que se devuelve una excepción si el nombre tiene más de 30 caracteres"""
        patient=self.patient_data.copy()
        patient["name_surname"]="Juan Pablo José Rodríguez Sánchez López"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid name and surname")

    def test_nombre_sin_apellido(self):
        """Se comprueba que se devuelve una excepción si el nombre no incluye al menos dos palabras"""
        patient=self.patient_data.copy()
        patient["name_surname"]="José"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid name and surname")

    def test_nombre_nostring(self):
        """Se comprueba que se devuelve una excepción si el nombre no es una string"""
        patient=self.patient_data.copy()
        patient["name_surname"]=1234567
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid name and surname")

    def test_patient_id_nostring(self):
        """Se comprueba que se devuelve una excepción si la id del paciente no es una string"""
        patient=self.patient_data.copy()
        patient["patient_id"]=382843292
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid patient ID")

    def test_patient_id_incorrecto(self):
        """Se comprueba que se devuelve una excepción si la id del paciente no es correcta"""
        patient=self.patient_data.copy()
        patient["patient_id"]="43831e01-cd0f-2b97-za6d-c071b42129f0"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid patient ID")

    @freeze_time("2020-04-26")
    def test_registro_correcto(self):
        """Se comprueba que la función devuelve el md5 si las entradas son correctas"""
        vaccine_manager = VaccineManager()
        patient = self.patient_data.copy()
        patient_id_test=vaccine_manager.request_vaccination_id(**patient)
        justnow = datetime.utcnow()
        time_stamp = datetime.timestamp(justnow)
        patient["time_stamp"] = time_stamp
        self.assertEqual(patient_id_test, hashlib.md5(json.dumps(patient).encode("utf-8")).hexdigest())

    def test_numerotelef_muycorto(self):
        """Se comprueba que si el número es demasiado corto, se lanza una excepción"""
        patient = self.patient_data.copy()
        patient["phone_number"] = "624"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid phone number")

    def test_numerotelef_nonumero(self):
        """Se comprueba que en caso de que el 'phone_number' no sea un número, se lance una excepción"""
        patient = self.patient_data.copy()
        patient["phone_number"] = "I23456789"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid phone number")

    def test_numerotelef_muylargo(self):
        """Se comprueba que en caso de que el número de telefono sea demasiado largo, se lanza una excepción"""
        patient = self.patient_data.copy()
        patient["phone_number"] = "6918237182461746"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid phone number")

    def test_tiporegistro_novalido(self):
        """Se comprueba que el registro deba ser correcto o se lanza una excepción"""
        patient = self.patient_data.copy()
        patient["registration_type"] = "Premium"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid registration type")

    def test_tiporegistro_nostr(self):
        """Se comprueba que el registro es una string o se lanza una excepción"""
        patient = self.patient_data.copy()
        patient["registration_type"] = 12
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid registration type")

    def test_guardado_correcto_json(self):
        """Se comprueba que los datos guardados en el Json son correctos"""
        with open(self.direccion, 'r', encoding="utf-8") as file: #Leemos el fichero
            data = json.load(file)
            file.close()
        found=False
        for dict in data:
            del dict["time_stamp"]
            del dict["patient_system_id"]
            if dict==self.patient_data:
                found=True
        self.assertEqual(found, True)

    def test_hash_es_str(self):
        """Esta funcion simplemente comprueba que lo que devuelve el return de la funcion requestvaccine es una str"""
        patient = self.patient_data.copy()
        vaccine_manager = VaccineManager()
        hashprueba = vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(type(hashprueba), str, "Invalid hash type")

    def test_tamanocorrectohash(self):
        """Esta funcion comprueba que el hash MD5 que devuelve el return de la funcion requestvaccinationid es de 32 digitos"""
        patient = self.patient_data.copy()
        vaccine_manager = VaccineManager()
        hashprueba = vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(len(hashprueba), 32, "Incorrect returned hash length")

    @freeze_time("2020-04-26")
    def test_comprobarhash(self):
        """Esta funcion comprueba que el hash que devuelve el return de la funcion es el correcto
        introduciendo los mismos datos"""
        patient = self.patient_data.copy()
        vaccine_manager = VaccineManager()
        hashprueba = vaccine_manager.request_vaccination_id(**patient)
        #Utilizo para un hash los datos del self.patient
        hashcomprobar = vaccine_manager.request_vaccination_id(**self.patient_data)
        self.assertEqual(hashprueba, hashcomprobar, "Incorrect returned hash")

    @freeze_time("2020-04-26")
    def test_comprobarhash_distinto(self):
        """Esta funcion comprueba que el hash que devuelve el return de la funcion es el distinto
        introduciendo distintos datos"""
        patient = self.patient_data.copy()
        patient["age"]=32
        vaccine_manager = VaccineManager()
        hashprueba = vaccine_manager.request_vaccination_id(**patient)
        #Utilizo para un hash los datos del self.patient
        hashcomprobar = vaccine_manager.request_vaccination_id(**self.patient_data)
        self.assertNotEqual(hashprueba, hashcomprobar, "Incorrect returned hash")

if __name__ == '__main__':
    unittest.main()
