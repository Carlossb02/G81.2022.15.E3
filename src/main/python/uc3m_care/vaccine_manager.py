"""Vaccine manager"""
import json
import re
import uuid
from pathlib import Path

from datetime import datetime
from uc3m_care.vaccine_management_exception import VaccineManagementException
from uc3m_care.vaccine_patient_register import VaccinePatientRegister
from uc3m_care.vaccination_appoinment import VaccinationAppoinment

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

    #RF1

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
            data = json.load(file)
            data.append(vaccine_patient_register.__dict__())
            file.seek(0)
            json.dump(data, file, indent=2)

        return vaccine_patient_register.patient_system_id

    #RF2

    def generate_json (self, patient_id, phone_number):
        """Esta funcion de apoyo nos permite generar los ficheros JSON
        para la función get_vaccine_data() y devuelve su dirección"""

        patient={"PatientSystemID": patient_id, "ContactPhoneNumber": phone_number}
        path_file=self.json_collection + "/" + patient_id + ".json"

        with open(path_file, 'w', encoding="utf-8") as json_file:
            json.dump(patient, json_file, indent=2)

        return path_file

    def get_vaccine_date (self, input_file):

        path_exist=Path(input_file)
        if not path_exist:
            raise VaccineManagementException("File does not exist")

        if input_file[-5:]!=".json":
            raise VaccineManagementException("Invalid file type")

        with open(input_file, 'r', encoding="utf-8") as file:  # Leemos el fichero
            data = json.load(file)
            file.close()

        if list(data.keys())!=["PatientSystemID", "ContactPhoneNumber"]:
            raise VaccineManagementException("Invalid JSON structure")

        p_id=data["PatientSystemID"]

        if type(p_id)!=str or len(p_id)!=32:
            raise VaccineManagementException("Invalid PatientSystemID")

        p_phone=data["ContactPhoneNumber"]

        if type(p_phone)!=str or len(p_phone)!=9:
            raise VaccineManagementException("Invalid phone number")
        try:
            int(p_phone)
        except ValueError as error:
            raise VaccineManagementException("Invalid phone number") from error

        ##Buscamos en las solicitudes:
        with open(self.patient_registry, 'r', encoding="utf-8") as file: #Leemos el fichero
            solicitudes = json.load(file)
            file.close()

        found=False
        p_uuid=""

        for dict in solicitudes:
            if dict["patient_system_id"]==data["PatientSystemID"]:
                found=True
                p_uuid=dict["patient_id"]
                if dict["phone_number"]!=p_phone:
                    raise VaccineManagementException("Phone numbers are different")

        if not found:
            raise VaccineManagementException("This patient is not registered")

        date=VaccinationAppoinment(p_uuid, p_id, p_phone, 10)
        date_dict={"patient_id": date.patient_id, "phone_number": date.phone_number,
                   "vaccine_date": str(datetime.fromtimestamp(int(float(date.appoinment_date))))[0:10],"patient_system_id": date.patient_sys_id, "date_signature": date.vaccination_signature}

        print ("Test")
        with open(self.vaccination_appointments, "r+",
                  encoding="utf-8") as file:
            data = json.load(file)
            data.append(date_dict)
            file.seek(0)
            print("PRUEBA")
            json.dump(data, file, indent=2)

        return date.vaccination_signature

    
    
    
    
    def vaccine_patient (self, date_signature):
        #date_signature representa la firma obtenida en la funcion 2

        #Compruebo formato
        if date_signature == None or type(date_signature) != str or len(date_signature) != 64:
            raise VaccineManagementException("Invalid signature")
        
        #Abro el archivo json
        path_file = self.vaccination_appointments
        
        #Compruebo que no haya errores al abrir el archivo
        try:
            with open(path_file, 'r', encoding="utf-8") as file:
                data = json.load(file)
                file.close()
        except FileNotFoundError as ex:
            raise VaccineManagerException("Error while opening the file")
        except json.JSONDecodeError as ex:
            raise VaccineManagerException("Error while decoding JSON")
            

        #Compruebo que tiene el formato correcto (para cada diccionario)
        for n in data:
            if list(n.keys()) != ["patient_id", "phone_number", "vaccine_date", "patient_system_id", "date_signature"]:
                raise VaccineManagementException("Invalid appointments JSON format")

        #Compruebo si la firma es valida (si la firma se encuentra en el json)
        encontrado = False
        #Este indice nos indica en que indice esta la firma dentro del json (para luego comprobar su fecha)
        indice = 0
        for n in data:
            if n["date_signature"] == date_signature:
                encontrado = True
                break
            else:
                indice += 1

        #Si no la he encontrado, lanzo una excepcion
        if encontrado == False:
            raise VaccineManagementException("Invalid date_signature")


        #Si no hay excepcion, la firma está dentro, por lo que paso a comprobar la fecha
        actual = str(datetime.utcnow())
        if data[indice] != actual:
            raise VaccineManagementException("Invalid vaccine date")

        else:
            #Sitodo es correcto, registro vacunacion
            #Guardo en un json, el diccionario siguiente (con lo que nos piden: fecha de acceso y firma)
            towrite = {"Access_date": actual, "Key_value": date_signature}
            string = json.dumps(towrite)

            
        #Al abrir el archivo compruebo si da algun error
        try:    
            with open('registered_vaccinations.json', 'w') as outfile:
                json.dump(string, outfile)
                outfile.close()
                
                return True
            
        except FileNotFoundError as ex:
            raise VaccineManagerException("Error while opening the file")
        except json.JSONDecodeError as ex:
            raise VaccineManagerException("Error while decoding JSON")
            
            
            #-------COMPROBACIONES INTERNAS (ELIMINAR AL ENTREGAR)------------------------------------------------------------
            with open('registered_vaccinations.json', 'r') as file:
                datos = json.load(file)
                file.close()
            print("Firma --->", date_signature)
            print("Diccionario del json con la firma ----> ", data[indice])
            print("JSON de la Vacunacion registrada ----> ", datos)
            #-----------------------------------------------------------------------------------------------------------------
            
            









v=VaccineManager()
path=v.generate_json("fb545bec6cd4468c3c0736520a4328db", "123456789")

ruta= v.get_vaccine_date(path)
print(v.vaccine_patient(ruta))

