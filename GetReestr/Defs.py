import datetime
import json
import sys


class Params:
    """ Чтение конфига """

    def __init__(self):
        # config_file = sys.argv[1]
        config_file = './get_reestr.prm'
        now = datetime.datetime.now()
        with open(config_file, 'r', encoding='UTF-8') as read_file:
            params = json.load(read_file)

        self.start_page = params['start_page']  # Start page on site

        self.tmp_path = params['tmp_path']
        self.md5_file = params['md5_file']
        self.copy_file = params['copy_file']

        self.zip_file = self.tmp_path + "FromSite" + now.strftime("%m_%d_%Y_%H_%M_%S") + ".zip"  # Temp zip from site
        self.xlsx_file = self.tmp_path + "FromSite" + now.strftime("%m_%d_%Y_%H_%M_%S") + ".xlsx"  # Temp XLS from site
        self.result_file = params['result_file']  # Result file
        self.result_tmp = self.tmp_path + now.strftime("%m_%d_%Y_%H_%M_%S") + ".csv"  # Temp result file

        self.send_by_email = params['send_by_email']  # EMail parametres
        self.emails = params['emails']  # EMail parametres
        self.file_parse_params = params["file_parse_params"]  # Параметры XLSX
