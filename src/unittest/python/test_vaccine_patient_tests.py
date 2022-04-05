"""Importamos lo necesario"""
import unittest
import json
from pathlib import Path
from uc3m_care.vaccine_manager import VaccineManager
from uc3m_care.vaccine_management_exception import VaccineManagementException




class MyTestCase(unittest.TestCase):
    """Clase de pruebas"""
    def setUp(self):
        """Añadimos los paths necesarios"""
        self.pathappointments = Path().home().resolve().__str__() + "/Desktop" + "/G81.2022.15.E3" + "/src/json/db/vaccination_appointments.json"
        self.pathregisteredvacc = Path().home().resolve().__str__() + "/Desktop" + "/G81.2022.15.E3" + "/src/json/db/registered_vaccinations.json"


    def test_firma_none(self):
        """Comprobamos caso de firma None"""
        v_test = VaccineManager()
        #Obtengo la firma
        firma = None
        with self.assertRaises(VaccineManagementException) as exception:
            v_test.vaccine_patient(firma)
        self.assertEqual(exception.exception.message, "Invalid signature")


    def test_firma_int(self):
        """Comprobamos la firma si es int"""
        v_test = VaccineManager()
        firma = 152463
        with self.assertRaises(VaccineManagementException) as exception:
            v_test.vaccine_patient(firma)
        self.assertEqual(exception.exception.message, "Invalid signature")



    def test_firma_63caracteres(self):
        """Comprueba con firma 63 caracteres"""
        v_test = VaccineManager()
        firma63car = "1ff628e1c47df266e40d6cd5ec67f3b41b0daaa9d756d03020ccef032f2f627"

        #Compruebo que la firma dara excepcion si tiene 63 caracteres en vez de 64
        with self.assertRaises(VaccineManagementException) as exception:
            v_test.vaccine_patient(firma63car)
        self.assertEqual(exception.exception.message, "Invalid signature")


    def test_comprobar_json_registered_vaccinations(self):
        """Compruebo si el json esta creado o no"""
        v_test = VaccineManager()
        path = v_test.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        v_test.get_vaccine_date(path)

        try:
            with open(self.pathregisteredvacc, 'r', encoding='utf-8') as file:
                file.close()
                encontrado = True

        except FileExistsError:
            encontrado = False
        self.assertEqual(encontrado, True, "JSON no existe")


    def test_comprobar_json_appoinments(self):
        """Compruebo si el json appoinments esta creado o no"""
        v_test = VaccineManager()
        path = v_test.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        v_test.get_vaccine_date(path)

        try:
            with open(self.pathappointments, 'r', encoding='utf-8') as file:
                file.close()
                encontrado = True

        except FileExistsError:
            encontrado = False
        self.assertEqual(encontrado, True, "JSON no existe")


    def test_no_encontrada_firma(self):
        """Se comprueba con una firma que no está en el JSON"""
        v_test= VaccineManager()
        path = v_test.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        v_test.get_vaccine_date(path)
        firmaincorrecta = "1ff628e1c47df266e40d6cd5ec67f3b41b0daaa9d756d03020ccef032f2f6272"

        #Pongo otra firma (para comprobar una incorrecta)
        with self.assertRaises(VaccineManagementException) as exception:
            v_test.vaccine_patient(firmaincorrecta)
        self.assertEqual(exception.exception.message, "Invalid date_signature")


    def test_funcion_correcta(self):
        """Comprueba el caso correcto"""
        v_test = VaccineManager()
        path = v_test.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        firma = v_test.get_vaccine_date(path)
        result = v_test.vaccine_patient(firma)

        self.assertEqual(result, True, "Funcion incorrecta")


    def test_comprobar_formato_json(self):
        """Compruebo  la excepcion de si el formato del json no es el correcto"""
        v_test = VaccineManager()
        path = v_test.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        firma = v_test.get_vaccine_date(path)
        v_test.vaccine_patient(firma)
        with open(self.pathregisteredvacc, "r", encoding= "utf-8") as file:
            copia = json.load(file)
            correcto = True
            for n_dict in copia:
                if list(n_dict.keys()) != ["Access_date", "Key_value"]:
                    correcto = False
                    break
            self.assertEqual(correcto, True, "Formato JSON incorrecto")


if __name__ == '__main__':
    unittest.main()
