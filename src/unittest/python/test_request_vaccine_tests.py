import hashlib
import json
from unittest import TestCase
from datetime import datetime
from freezegun import freeze_time
from pathlib import Path
from uc3m_care.vaccine_manager import VaccineManager
from uc3m_care.vaccine_management_exception import VaccineManagementException

class MyTestCase(TestCase):
    def setUp(self) -> None:
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
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.validate_uuid4("43831e01-cd0f-7b97-aa6d-c071b42129f0")
        self.assertEqual(exception.exception.message, "Invalid UUID format")

    def test_uuid_correcta(self):
        vaccine_manager = VaccineManager()
        self.assertEqual(vaccine_manager.validate_uuid4("43831e01-cd0f-4b97-aa6d-c071b42129f0"), True)


        ## TESTS request_vaccination_id()

    def test_edad_inferior(self):
        patient=self.patient_data.copy() #Ponemos .copy() para no modificar el original, ya que python hace paso por referencia
        patient["age"]=4
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid age")

    def test_edad_superior(self):
        patient=self.patient_data.copy()
        patient["age"]=150
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid age")

    def test_edad_no_numero(self):
        patient=self.patient_data.copy()
        patient["age"]="diez"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid age")

    def test_nombre_vacio(self):
        patient=self.patient_data.copy()
        patient["name_surname"]=""
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid name and surname")

    def test_nombre_largo(self):
        patient=self.patient_data.copy()
        patient["name_surname"]="Juan Pablo José Rodríguez Sánchez López"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid name and surname")

    def test_nombre_sin_apellido(self):
        patient=self.patient_data.copy()
        patient["name_surname"]="José"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid name and surname")

    def test_patientID_incorrecto(self):
        patient=self.patient_data.copy()
        patient["patient_id"]="43831e01-cd0f-2b97-za6d-c071b42129f0"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid UUID format")

    @freeze_time("2020-04-26")
    def test_registro_correcto(self):
        vaccine_manager = VaccineManager()
        patient = self.patient_data.copy()
        data={}
        #Borramos el Json para evitar errores
        with open(self.direccion, 'w') as file:
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()
            file.close()
        patient_id_test=vaccine_manager.request_vaccination_id(**patient)
        justnow = datetime.utcnow()
        time_stamp = datetime.timestamp(justnow)
        patient["time_stamp"] = time_stamp
        self.assertEqual(patient_id_test, hashlib.md5(json.dumps(patient).encode("utf-8")).hexdigest())
    
    def test_numerotelef_muycorto(self):
        #Esta comprobara que el numero de telefono no es demasiado corto
        patient = self.patient_data.copy()
        patient["phone_number"] = "624"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid phone number")
    
    
    def test_numerotelef_nonumero(self):
        #Esta comprobara que se da un numero de telefono y no cualquier cosa
        patient = self.patient_data.copy()
        patient["phone_number"] = "I23456789"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid phone number")
        
        
    def test_numerotelef_muylargo(self):
        #Comprueba que el numero de telefono no es muy largo
        patient = self.patient_data.copy()
        patient["phone_number"] = "6918237182461746"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid phone number")
    
    
    def test_tiporegistro_novalido(self):
        #Esta comprobara que se da o bien Family o Regular
        patient = self.patient_data.copy()
        patient["registration_type"] = "Premium"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid registration type")
        
    
    def test_tiporegistro_nostr(self):
        patient = self.patient_data.copy()
        patient["registration_type"] = 12
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid registration type")
        
    def test_guardado_correcto_json(self):

        #Vaciamos el JSON para evitar errores
        data={}
        with open(self.direccion, 'w') as file:
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()
            file.close()
        vaccine_manager=VaccineManager()
        vaccine_manager.request_vaccination_id(**self.patient_data)
        with open(self.direccion, 'r') as file: #Leemos el fichero
            data = json.load(file)
            file.close()
        self.assertEqual(data, self.patient_data)

    def test_hash_es_str(self):
        #Esta funcion simplemente comprueba que lo que devuelve el return de la funcion requestvaccine es una str
        patient = self.patient_data.copy()
        vaccine_manager = VaccineManager()
        hashprueba = vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(type(hashprueba), str, "Invalid hash type")


    def test_tamano_correcto_hash(self):
        #Esta funcion comprueba que el hash MD5 que devuelve el return de la funcion requestvaccinationid es de 32 digitos
        patient = self.patient_data.copy()
        vaccine_manager = VaccineManager()
        hashprueba = vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(len(hashprueba), 32, "Incorrect returned hash length")

    @freeze_time("2020-04-26")
    def test_comprobar_hash(self):
        #Esta funcion comprueba que el hash que devuelve el return de la funcion es el correcto
        #si se le introducen los mismos datos
        patient = self.patient_data.copy()
        vaccine_manager = VaccineManager()
        hashprueba = vaccine_manager.request_vaccination_id(**patient)
        #Utilizo para un hash los datos del self.patient
        hashcomprobar = vaccine_manager.request_vaccination_id(**self.patient_data)
        self.assertEqual(hashprueba, hashcomprobar, "Incorrect returned hash")


    
if __name__ == '__main__':
    unittest.main()
