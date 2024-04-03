##################################################################################
#  You can add your actions in this file or create any other file in this folder #
##################################################################################

from rasa_sdk import Action
from rasa_sdk.events import SlotSet, ReminderScheduled, ConversationPaused, ConversationResumed, FollowupAction, Restarted, ReminderScheduled, ActiveLoop
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
from rasa_sdk.types import DomainDict
import requests
import logging
from datetime import datetime


class searchService(Action):
    def name(self):
        return 'action_search_service'
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict):
        service = tracker.get_slot('servicio') or tracker.get_slot('id_servicio')
        if not service:
            dispatcher.utter_message(text='Por favor selecciona el estudio de tu interes :)')
            return [FollowupAction('action_list_studies')]
        url = ''
        if tracker.get_slot('servicio'):
            url =f'https://server-production-c354.up.railway.app/medical-studies/searchMedStudy?name={service}'
        elif tracker.get_slot('id_servicio'):
            url = f'https://server-production-c354.up.railway.app/medical-studies/searchById/{service}'   
        token = 'e073ced94b8dfd0ef3e088070da07562b93a4e4af5dc3c5e74ba05c0e9a70868'
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                data = data[0]
            if not data: 
                dispatcher.utter_message(text='Actualmente no contamos con ese servicio')
                return []
            dispatcher.utter_message(text= str(data['description']))
            dispatcher.utter_message(text=f"El precio del estudio en nuestras clinicas es de ${str(data['price'])} MXN")
            buttons = [
            {"payload": f"'/responder{{\"respuesta\":\"{str(data['info']['proceed'])}\"}}'".replace("'", ""), "title": "Como es el procedimiento?", "type": "postback"},
            {"payload": f"'/responder{{\"respuesta\":\"{str(data['info']['risks'])}\"}}'".replace("'", ""), "title": "Que tan seguro es el estudio?", "type": "postback"},
            {"payload": f"'/responder{{\"respuesta\":\"{str(data['info']['preparation'])}\"}}'".replace("'", ""), "title": "Debo prepararme de alguna manera?", "type": "postback"}, 
            {"payload": f"'/responder{{\"respuesta\":\"{str(data['info']['duration'])}\"}}'".replace("'", ""), "title": "Cual es la duracion  del estudio?", "type": "postback"},  
            ]
            dispatcher.utter_message(text='Deseas saber mas?', buttons=buttons)
            return []
        
class anwerQuickFAQ(Action):
    def name(self):
        return 'action_quick_questions'
    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: DomainDict):
        answer = tracker.get_slot('respuesta')
        dispatcher.utter_message(text=answer)
        return[]

class listStudies(Action):

    def name(self):
        return 'action_list_studies'

    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: DomainDict):
        url = 'https://server-production-c354.up.railway.app/medical-studies/list'
        token = 'e073ced94b8dfd0ef3e088070da07562b93a4e4af5dc3c5e74ba05c0e9a70868'
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                dispatcher.utter_message(text='Por el momento estoy teniendo dificultades paa revisar nustro sistema, por favor intentelo mas tarde') 
                return []
            template = self.get_template(data)
            dispatcher.utter_message(json_message=template)
        return []
        
    def get_template(self, data):
        elements =[]
        for study in data[:min(len(data), len(data))]:
            payload = f"'/info_servicio{{\"id_servicio\":\"{study['_id']}\"}}'".replace("'", "")
            element = {
                            "title": str(study['name']),
                            "image_url": str(study['image']),
                            "buttons":[
                                {
                                    "title": "Mas información",
                                    "type": "postback",
                                    "payload": payload
                                },
                            ]
                        }
            elements.append(element)
        template = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements 
                }
            }
        }
        return template  
    

class ResetSearch(Action):

    def name(self):
        return 'action_reset_consulta'

    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: DomainDict):
        return [SlotSet('codigo', None), SlotSet('key', None), SlotSet('key_type', None)]

class SendImage(Action):
    def name(self):
        return 'action_send_image'
    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: DomainDict):
        image_path = 'https://www.migobierno.com/sites/default/files/styles/full_width/public/2019-10/Salud-Digna.jpeg?itok=6PuuVTR7'
        dispatcher.utter_message(image=image_path)
        return[]

class ValidateDate(Action):

    def name(self):
        return 'validate_fecha_form'
    def limpiar_cadena(self, cadena):
        meses = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }
        cadena = cadena.replace("/", " ")
        cadena = cadena.replace("-", " ")
        palabras = cadena.split()
        palabras_filtradas = []
        for palabra in palabras:
            if palabra.isdigit():
                palabras_filtradas.append(palabra)
            elif palabra.lower() in meses:
                numero_mes = meses[palabra.lower()]
                palabras_filtradas.append(str(numero_mes))
        cadena_limpia = ' '.join(palabras_filtradas)

        return cadena_limpia

    def validar_y_formatear_fecha(self, fecha_str):
        try:
            partes_fecha = fecha_str.split()
            dia = int(partes_fecha[0])
            mes = int(partes_fecha[1])
            año = int(partes_fecha[2])
            fecha = datetime(año, mes, dia)
            return fecha.strftime("%Y%m%d")  # Formatea la fecha como desees
        except (ValueError, IndexError, KeyError):
            return None

    def run(self, dispatcher, tracker, domain):
        fecha = tracker.get_slot('date')
        logger.debug(f'Validando Fecha {fecha}')
        fecha = self.limpiar_cadena(fecha) 
        logger.debug(f'Validando Fecha {fecha}')
        fecha_formateada = self.validar_y_formatear_fecha(fecha)
        if fecha_formateada:
            return[SlotSet('date',fecha_formateada)]
        if not fecha_formateada:
            dispatcher.utter_message('La fecha ingresada, no es valida por favor ingrese fecha por dia, mes y año')
            return[SlotSet('date',fecha_formateada), ActiveLoop('Fecha_form')]

class GetStudy(Action):

    def name(self):
        return 'action_get_consulta'

    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: DomainDict):
        name = str(tracker.get_slot('name'))
        date= str(tracker.get_slot('date'))
        url = f'https://a401-2806-261-417-5512-6590-e2e0-186b-8ce8.ngrok-free.app/tools/find'
        json_data = {
    "Expand": True,
    "Query": {
        "PatientID": "*VSX*",
        "PatientName": f"*{name}*",
        "PatientBirthDate": f"{date}"
    },
    "Level": "Study"
}

        response = requests.post(url, json=json_data)
        if response.status_code == 200:
            data = response.json()
            if not data:
                buttons = [
                {"payload": '/consultar_resultados', "title": "Intentar de nuevo", "type": "postback"},
                {"payload": '/continuar_resultados{"name": null}', "title": "Modificar Nombre", "type": "postback"},
                {"payload": '/continuar_resultados{"date": null}', "title": "Modificar Fecha de Nacimiento", "type": "postback"},
                {"payload": '/continuar_resultados{"study_id": null}', "title": "Modificar ID de estudio", "type": "postback"},  
                {"payload": '/servicios', "title": "Aun no me realizo un estudio, que servicios tienene disponibles?", "type": "postback"},   
                ]
                dispatcher.utter_message(text="""No ha sido encontrado en nuestros registros, por favor verifique los datos de consulta""", quick_replies = buttons)
                return[]
            template = self.get_template(data)
            dispatcher.utter_message(json_message=template)
        return []
        
    def get_template(self, data):
        elements =[]
        for study in data[:min(len(data), 5)]:
            payload = f"'/listar_archivos{{\"id_estudio\":\"{study['ID']}\"}}'".replace("'", "")
            url = f"https://e3ee-2806-103e-29-32ce-f85b-921f-a941-c924.ngrok-free.app/stone-webviewer/index.html?study={study['StudyInstanceUID']}"
            element = {
                            "title": str(study['MainDicomTags']["StudyDescription"]),
                            "buttons":[
                                {
                                    "title": "Consultar",
                                    "type": "postback",
                                    "payload": payload
                                },
                                {
                                    "title": "Compartir con su Medico",
                                    "type": "web_url",
                                    "payload": str(url)
                                },
                            ]
                        }
            elements.append(element)
        template = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements 
                }
            }
        }
        return template  


class ListFiles(Action):
    def name(self):
        return 'action_list_files'
    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: DomainDict):
        files = tracker.get_slot('id_estudio')
        logger.debug({files})
        return[]