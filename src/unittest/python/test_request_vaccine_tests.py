import hashlib
import json
from unittest import TestCase, main, mock
from datetime import datetime
from freezegun import freeze_time

from test_utils import TestUtils
from uc3m_care.vaccine_manager import VaccineManager
from uc3m_care.vaccine_management_exception import VaccineManagementException
from uc3m_care.vaccine_patient_register import VaccinePatientRegister



class MyTestCase(TestCase):
    def setUp(self) -> None:
        self.patient_data = {
            "patient_id": "43831e01-cd0f-4b97-aa6d-c071b42129f0",
            "name_surname": "Fernando Alonso",
            "registration_type": "Family",
            "phone_number": "123456789",
            "age": 20,
        }
    def test_edad_inferior( self ):
        patient=self.patient_data.copy() #Ponemos .copy() para no modificar el original, ya que python hace paso por referencia
        patient["age"]=4
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid age")

    def test_edad_superior( self ):
        patient=self.patient_data.copy()
        patient["age"]=150
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid age")

    def test_edad_no_numero( self ):
        patient=self.patient_data.copy()
        patient["age"]="diez"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid age")

    def test_nombre_vacio( self ):
        patient=self.patient_data.copy()
        patient["name_surname"]=""
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid name and surname")

    def test_nombre_largo( self ):
        patient=self.patient_data.copy()
        patient["name_surname"]="Juan Pablo José Rodríguez Sánchez López"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid name and surname")

    def test_nombre_sin_apellido( self ):
        patient=self.patient_data.copy()
        patient["name_surname"]="José"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid name and surname")

    def test_UUID_incorrecta( self ):
        patient=self.patient_data.copy()
        patient["patient_id"]="43831e01-cd0f-2b97-za6d-c071b42129f0"
        vaccine_manager = VaccineManager()
        with self.assertRaises(VaccineManagementException) as exception:
            vaccine_manager.request_vaccination_id(**patient)
        self.assertEqual(exception.exception.message, "Invalid UUID format")

    @freeze_time("2020-04-26")
    def test_registro_correcto( self ):
        vaccine_manager = VaccineManager()
        patient = self.patient_data.copy()
        patient_id_test=vaccine_manager.request_vaccination_id(**patient)
        justnow = datetime.utcnow()
        time_stamp = datetime.timestamp(justnow)
        patient["time_stamp"] = time_stamp
        self.assertEqual(patient_id_test, hashlib.md5(json.dumps(patient).encode("utf-8")).hexdigest())
        
    
    def numerotelef_muycorto( self ):
        #Esta comprobara que el numero de telefono no es demasiado corto
        patient = self.patient_data.copy()
        patient["phone_number"] = 624
        
        
        
        
    
    def numerotelef_nonumero( self ):
        #Esta comprobara que se da un numero de telefono y no cualquier cosa
        patient = self.patient_data.copy()
        patient["phone_number"] = "Pedro sanchez"
        
        
        
        
        
    def numerotelef_muylargo( self ):
        #Comprueba que el numero de telefono no es muy largo
        patient = self.patient_data.copy()
        patient["phone_number"] = 6918237182461746

        
        
        
        
if __name__ == '__main__':
    unittest.main()
