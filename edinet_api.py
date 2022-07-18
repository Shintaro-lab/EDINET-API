# -*- coding: utf-8 -*-
"""
Created on Sun Jul 10 20:27:58 2022

@author: shintaro
"""

import datetime
import json
import os
import requests
import sys

### variable

##dir_path
TMP_DIR = r'C:\Users\shintaro\Documents\edinet_api\tmp'

##list
PDF_RECEIVED_LIST = 'pdf_old.json'
XBRL_RECEIVED_LIST = 'xbrl_old.json'
DOWNLOAD_ERROL_LIST = 'error.json'
LIST_FILE_FOR_DEBUG = 'listfile_for_debug.json'
FILTERED_LIST_FILE_FOR_DEBUG = 'filtered_listfile_for_debug.json'
DOWNLOAD_LOG_FILE_FOR_DEBUG = 'download_logfile_for_debug.json'

PDF_RECEIVED_LIST_PATH = os.path.join(TMP_DIR,PDF_RECEIVED_LIST)
XBRL_RECEIVED_LIST_PATH = os.path.join(TMP_DIR,XBRL_RECEIVED_LIST)
DOWNLOAD_ERROL_LIST_PATH = os.path.join(TMP_DIR,DOWNLOAD_ERROL_LIST)
LIST_FILE_FOR_DEBUG_PATH = os.path.join(TMP_DIR,LIST_FILE_FOR_DEBUG)
FILTERED_LIST_FILE_FOR_DEBUG_PATH = os.path.join(TMP_DIR,FILTERED_LIST_FILE_FOR_DEBUG)
DOWNLOAD_LOG_FILE_FOR_DEBUG_PATH = os.path.join(TMP_DIR,DOWNLOAD_LOG_FILE_FOR_DEBUG)

##url
LIST_URL = 'https://disclosure.edinet-fsa.go.jp/api/v1/documents.json'
DOWNLOAD_URL = 'https://disclosure.edinet-fsa.go.jp/api/v1/documents/'

##for RESTRICT NUMBER OF DOWNLOAD
MAX_DOWNLOAD_NUM = 100

def main():
    print("start download!")
    
    init()
    target_date_list = makeDateList(from_date,to_date)
    
    log_rotaion_num = 0
    download_num = 0
    
    for target_date in target_date_list:
        pdf_receive_list["date"] = target_date
        
        download(LIST_URL, {'date':target_date,'type': 2}, LIST_FILE_FOR_DEBUG_PATH + str(log_rotaion_num), 1)
        with open(LIST_FILE_FOR_DEBUG_PATH + str(log_rotaion_num), 'r', encoding='utf-8') as f:
            no_filter_list = json.load(f)
            
            if no_filter_list["metadata"]["status"] != "200":
                print("cannot get data from API!")
                sys.exit(1)
        
        filterTargetData(LIST_FILE_FOR_DEBUG_PATH + str(log_rotaion_num), target_date, FILTERED_LIST_FILE_FOR_DEBUG_PATH + str(log_rotaion_num))
        
        with open(FILTERED_LIST_FILE_FOR_DEBUG_PATH + str(log_rotaion_num), 'r', encoding='utf-8') as f:
            filtered_list = json.load(f)
            
            for i in filtered_list:
                if download_num >= MAX_DOWNLOAD_NUM:
                    break
                
                if i["pdfFlag"] == "1":
                    if searchList(i["docID"],pdf_receive_list["docIDLists"]):
                        pass
                    else:
                        response = download(DOWNLOAD_URL + i["docID"], {'type': 2}, DOWNLOAD_LOG_FILE_FOR_DEBUG_PATH, 0)
                        

                        if response.status_code != 200:
                            print("cannot download file from API!")
                            #append error list
                        else:

                            convertBinaryToFile(response, i["docID"], ".pdf")
                            pdf_receive_list["docIDLists"].append(i["docID"])
                            
                            download_num += 1                       
                        
        
        if download_num >= MAX_DOWNLOAD_NUM:
            break
        
        if target_date_list.index(target_date)+1 != len(target_date_list):
            rotationList(pdf_receive_list, os.path.join(TMP_DIR,PDF_RECEIVED_LIST + target_date))
            
            pdf_receive_list["docIDLists"] = [] 

        log_rotaion_num += 1
        
        if log_rotaion_num >=3:
            log_rotaion_num = 0
    
    #for debug
    with open(PDF_RECEIVED_LIST_PATH, 'w', encoding='utf-8') as f:
        json.dump(pdf_receive_list, f, ensure_ascii=False, indent=2)
    print("end download!")  
    
def init():
    ### variable
    ##date
    global target_date
    global today
    global from_date
    global to_date
    global target_date_list
    
    ##variable for containing json file value
    global pdf_receive_list
    global xbrl_receive_list
    global download_error_list
    global no_filter_list
    global filtered_list
    
    ##log rotation number
    global log_rotaion_num
    
    # set_today
    dt_now = datetime.datetime.now()
    today = dt_now.strftime('%Y-%m-%d')
    
    #set pdf_receive_list
    if os.path.exists(PDF_RECEIVED_LIST_PATH):
        pdf_receive_list = json.load(open(PDF_RECEIVED_LIST_PATH, 'r'))
    else:
        with open(PDF_RECEIVED_LIST_PATH, 'w', encoding='utf-8') as f:
            json.dump({"date":today,"docIDLists":[]}, f, ensure_ascii=False, indent=2)
        pdf_receive_list = json.load(open(PDF_RECEIVED_LIST_PATH, 'r'))

    #set date
    from_date = pdf_receive_list["date"]
    to_date = today
    target_date = from_date
    
def download(url:str, parameter:dict, json_path:str, write_json_flag:int):
    
    response = requests.get(url, params=parameter)
    
    if write_json_flag == 1:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)
    else:
        pass   
    
    return response
    
def makeDateList(start_date:str, end_date:str):
    strdt = datetime.datetime.strptime(start_date,"%Y-%m-%d")
    enddt = datetime.datetime.strptime(end_date,"%Y-%m-%d")
    
    days_num = (enddt - strdt).days + 1
    
    date_list =[]
    
    for i in range(days_num):
        date_list.append((strdt + datetime.timedelta(days=i)).strftime('%Y-%m-%d'))
    
    return date_list

def filterTargetData(before_list_path:str, t_date:str, after_list_path:str):
    with open(before_list_path, 'r', encoding='utf-8') as f:
        before_list = json.load(f)
    after_array = []
    
    for i in before_list["results"]:
        if i["docTypeCode"] in ["120","130","140","150","160","170"] \
        and i["submitDateTime"][0:10] == t_date \
        and i["withdrawalStatus"] == "0" and i["disclosureStatus"] == "0":
            after_array.append(i)
    
    with open(after_list_path, 'w', encoding='utf-8') as f:
        json.dump(after_array, f, ensure_ascii=False, indent=2)

def searchList(targetWord:str, targetList:str):
    if (targetList.count(targetWord)>0):
        return True
    else:
        return False

def convertBinaryToFile(response:str, ID:str, extension:str):
    download_file_name = ID + extension
    download_file_path = os.path.join(TMP_DIR, download_file_name)
    
    with open(download_file_path, 'wb') as binary:
        binary.write(response.content)
        
def rotationList(content_list:list, after_file_path:str):
    
    with open(after_file_path, 'w', encoding='utf-8') as f:
        json.dump(content_list, f, ensure_ascii=False, indent=2)
    

if __name__ == "__main__":
    main()