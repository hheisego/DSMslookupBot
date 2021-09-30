import json
import re
import requests
import time
import datetime
from core_au import user, pwd, fixed_url, svr_url

start_time = time.perf_counter()

class newDSMlookup:
    # Set proper headers
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def expiryChecker(self, contractExp):

        try:

            contractExp = datetime.datetime.strptime(contractExp, "%m/%d/%Y")
            todaysDate = datetime.datetime.now()

            result = str((contractExp - todaysDate).days)

            return result

        except:

            return "\n Could not calculate the service remaining days..."

    def getDSMs(self, svr_number):

        final_url = svr_url + svr_number

        dsm = requests.get(final_url, auth=(user, pwd), headers=self.headers).json()["result"]

        return dsm

    def chorus(self, account_name):

        #previous query parameters: "%2Cu_record_number%2cu_cs_case_owner%2cu_offer_name%2Ccustomer%2cu_order_status%2cu_order_substatus%2cu_offer_type%2Cu_te_primary%2Cu_te_primary.email%2Cu_te_secondary%2Cu_te_secondary.email%2Cu_te_tertiary%2Cu_te_tertiary.email%2Cu_contract_number%2Cu_contract_term%2Cu_service_start_date%2Cu_service_end_date%2Cu_subscription_id%2Cu_web_order_id%2Cu_architecture%2Cu_covered_products%2Cu_covered_product%2Cu_product_status&sysparm_query=customerLIKE"
        final_url = fixed_url + "%2Cu_record_number%2cu_cs_case_owner%2cu_offer_name%2Ccustomer%2cu_order_status%2cu_order_substatus%2cu_offer_type%2Cu_contract_number%2Cu_contract_term%2Cu_service_start_date%2Cu_service_end_date%2Cu_subscription_id%2Cu_web_order_id%2Cu_architecture%2Cu_covered_products%2Cu_covered_product%2Cu_product_status&sysparm_query=customerLIKE" + account_name #+ '^u_order_status!=Expired^u_order_sub_status!=Inactive'  #"  # ^u_order_substatus!=Expired"

        # Do the HTTP request
        expert = requests.get(final_url, auth=(user, pwd), headers=self.headers).json()["result"]

        if len(expert) <= 0:

            print("se chinga porque no existe")

        else:

            # Validation Order Status Section ###
            status = ''

            for i in range(len(expert)):

                try:

                    if expert[i]['u_order_status'] == 'Expired':

                        del expert[i]
                        status += "Expired, "

                except:

                    print("No Expired")

                try:

                    if expert[i]['u_order_status'] == 'Cancelled':
                        del expert[i]
                        status += "Cancelled, "

                except:

                    print("No Cancelled")

                try:

                    if expert[i]['u_order_status'] == 'Inactive':
                        del expert[i]
                        status += "Inactive, "

                except:

                    print("No Inactive")



            if len(expert) <= 0:

                print(status + " Order(s)")

            else:

                customer = list(set(debug['customer'] for debug in expert))

                clean_dataset = []

                for cu in customer:

                    accounts = []
                    collab_products, security_info, inserted_values = [], [], []
                    collaboration = []
                    subscriptions = []
                    last_updates = []
                    weborders = []
                    contracts = []
                    offer_n = []
                    service_s, service_e = [], []

                    for data in expert:

                        if cu == data['customer']:

                            if data['u_architecture'] == 'Collaboration':

                                info = {}
                                info['Customer'] = data['customer']
                                info['service_start'] = data['u_service_start_date']
                                info['service_end'] = data['u_service_end_date']
                                info['order_status'] = data['u_order_substatus']

                                collaboration.append(info)
                                print(data['number'])
                                print(self.getDSMs(svr_number=data['number']))

                                for i in self.getDSMs(svr_number=data['number']):

                                    if i.get("u_role") == "TE Primary" and i.get('u_last_updated') is not None:

                                        ultima_modificacion = i.get('u_last_updated')[:i.get('u_last_updated').index(" ")]
                                        ultima_modificacion = datetime.datetime.strptime(ultima_modificacion, "%m/%d/%Y")

                                        last_updates.append(ultima_modificacion)


                                print("\nahi va la chida:\n")

                                ultima_modificacion = str(max(last_updates))
                                ultima_modificacion = ultima_modificacion[:ultima_modificacion.index(" ")]
                                ultima_modificacion = datetime.datetime.strptime(ultima_modificacion, "%Y-%m-%d")
                                ultima_modificacion = ('{0}/{1}/{2}'.format(ultima_modificacion.month, ultima_modificacion.day, ultima_modificacion.year))

                                print(ultima_modificacion)

                                for i in self.getDSMs(svr_number=data['number']):

                                    if i.get('u_last_updated') is not None and i.get('u_last_updated').find(ultima_modificacion) == True:

                                        print(i.get("u_technical_expert"))

            return "simon"


dsmlookup = newDSMlookup()

print(dsmlookup.chorus(account_name="t-mobile"))
print("\n\n")
print(time.perf_counter() - start_time, "seconds")