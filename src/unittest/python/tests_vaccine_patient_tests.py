import unittest
import json
from unittest import TestCase
from datetime import datetime
from pathlib import Path
from freezegun import freeze_time
from uc3m_care.vaccine_manager import VaccineManager
from uc3m_care.vaccine_management_exception import VaccineManagementException




class MyTestCase(unittest.TestCase):
    def setUp(self):
        #Creo dos paths utiles para mis comprobaciones con los jsons
        self.pathappointments = Path().home().resolve().__str__() + "/Desktop" + "/G81.2022.15.E3" + "/src/json/db/vaccination_appointments.json"
        self.pathregisteredvacc = Path().home().resolve().__str__() + "/Desktop" + "/G81.2022.15.E3" + "/src/json/db/registered_vaccinations.json"


    def test_firma_None(self):
        #Comprueba la excepcion 1
        v = VaccineManager()
        path = v.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        #Obtengo la firma
        firma = None
        with self.assertRaises(VaccineManagementException) as exception:
            result = v.vaccine_patient(firma)
        self.assertEqual(exception.exception.message, "Invalid signature")


    def test_firma_int(self):
        #Comprueba en el caso de un int(excepcion 1)
        v = VaccineManager()
        path = v.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        firma = 152463
        with self.assertRaises(VaccineManagementException) as exception:
            result = v.vaccine_patient(firma)
        self.assertEqual(exception.exception.message, "Invalid signature")



    def test_firma_63caracteres(self):
        v = VaccineManager()
        path = v.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        firma63car = "1ff628e1c47df266e40d6cd5ec67f3b41b0daaa9d756d03020ccef032f2f627"

        #Compruebo que la firma dara excepcion si tiene 63 caracteres en vez de 64
        with self.assertRaises(VaccineManagementException) as exception:
            result = v.vaccine_patient(firma63car)
        self.assertEqual(exception.exception.message, "Invalid signature")


    def test_comprobar_json_registered_vaccinations(self):
        #Compruebo si el json esta creado o no
        v = VaccineManager()
        path = v.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        firma = v.get_vaccine_date(path)

        try:
            p = open(self.pathregisteredvacc, 'r')
            p.close()
            encontrado = True

        except FileExistsError as ex:
            encontrado = False
        self.assertEqual(encontrado, True, "JSON no existe")


    def test_comprobar_json_appoinments(self):
        #Compruebo si el json appoinments esta creado o no
        v = VaccineManager()
        path = v.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        firma = v.get_vaccine_date(path)

        try:
            p = open(self.pathappointments, 'r')
            p.close()
            encontrado = True

        except FileExistsError as ex:
            encontrado = False
        self.assertEqual(encontrado, True, "JSON no existe")


    def test_no_encontrada_firma(self):
        #Se comprueba con una firma que no está en el JSON
        v = VaccineManager()
        path = v.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        firma = v.get_vaccine_date(path)
        firmaincorrecta = "1ff628e1c47df266e40d6cd5ec67f3b41b0daaa9d756d03020ccef032f2f6272"

        #Pongo otra firma (para comprobar una incorrecta)
        with self.assertRaises(VaccineManagementException) as exception:
            result = v.vaccine_patient(firmaincorrecta)
        self.assertEqual(exception.exception.message, "Invalid date_signature")


    def test_funcion_correcta(self):
        #Comprueba el caso correcto
        v = VaccineManager()
        path = v.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        firma = v.get_vaccine_date(path)
        result = v.vaccine_patient(firma)

        self.assertEqual(result, True, "Funcion incorrecta")


    def test_comprobar_formato_JSON(self):
        #Compruebo  la excepcion de si el formato del json no es el correcto
        v = VaccineManager()
        path = v.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")
        firma = v.get_vaccine_date(path)
        result = v.vaccine_patient(firma)
        with open(self.pathregisteredvacc, "r", encoding= "utf-8") as file:
            copia = json.load(file)
            correcto = True
            for n in copia:
                print(n)
                if list(n.keys()) != ["Access_date", "Key_value"]:
                    correcto = False
                    break
            self.assertEqual(correcto, True, "Formato JSON incorrecto")















if __name__ == '__main__':
    unittest.main()
