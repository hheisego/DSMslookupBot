import json
import re
import requests
import time
import datetime
from core_au import user, pwd, fixed_url, svr_url

#Static Variables#
#reg = re.compile(pattern=r"(\d{8})")

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

        final_url = svr_url + svr_number + '^u_end_date=^u_role!='

        dsm = requests.get(final_url, auth=(user, pwd), headers=self.headers).json()["result"]

        return dsm

    def weborder(self, sub_web_id):

        #reg = re.compile(pattern=r"(\d{8})")
        reg = re.compile(pattern=r"(Sub\d{6}|\d{8})")
        result = re.findall(reg, str(sub_web_id))

        return result

    def chorus(self, account_name):

        #previous query parameters: "%2Cu_record_number%2cu_cs_case_owner%2cu_offer_name%2Ccustomer%2cu_order_status%2cu_order_substatus%2cu_offer_type%2Cu_te_primary%2Cu_te_primary.email%2Cu_te_secondary%2Cu_te_secondary.email%2Cu_te_tertiary%2Cu_te_tertiary.email%2Cu_contract_number%2Cu_contract_term%2Cu_service_start_date%2Cu_service_end_date%2Cu_subscription_id%2Cu_web_order_id%2Cu_architecture%2Cu_covered_products%2Cu_covered_product%2Cu_product_status&sysparm_query=customerLIKE"
        final_url = fixed_url + "%2Cu_record_number%2cu_cs_case_owner%2cu_offer_name%2Ccustomer%2cu_order_status%2cu_order_substatus%2cu_offer_type%2Cu_contract_number%2Cu_contract_term%2Cu_service_start_date%2Cu_service_end_date%2Cu_subscription_id%2Cu_web_order_id%2Cu_architecture%2Cu_covered_products%2Cu_covered_product%2Cu_product_status&sysparm_query=customerLIKE" + account_name #+ '^u_order_status!=Expired^u_order_sub_status!=Inactive'  #"  # ^u_order_substatus!=Expired"

        # Do the HTTP request
        expert = requests.get(final_url, auth=(user, pwd), headers=self.headers)

        if expert.status_code != 200:

            print("vuelve a intentar por fa")

        else:

            expert = expert.json()["result"]

            if len(expert) <= 0:

                print("se chinga porque no existe")

            else:

                # Validation Order Status Section ###
                status = ''

                for i in range(len(expert)):

                    try:

                        if expert[i]['u_order_status'] == 'Expired':
                            del expert[i]
                            status += " || Expired Contract || "

                    except:

                        status += "No Expired Orders, "

                    try:

                        if expert[i]['u_order_status'] == 'Cancelled':
                            del expert[i]
                            status += " || Cancelled Contract || "

                    except:

                        status += "No Cancelled Orders, "

                    try:

                        if expert[i]['u_order_status'] == 'Inactive':
                            del expert[i]
                            status += " || Inactive Contract || "

                    except:

                        status += "No Inactive Orders."

                if len(expert) <= 0:

                    print(status + " Please reach out the account team")

                else:

                    customer = list(set(debug['customer'] for debug in expert))

                    clean_dataset = []
                    print(expert)
                    for cu in customer:

                        inserted_values = []
                        info = {}
                        csubscription = []
                        ssubscription = []
                        sweborder = []
                        cweborder = []
                        cproducts = []
                        sproducts = []
                        srv_security = []
                        sdsms = []
                        csstart = []

                        for data in expert:

                            if cu == data['customer']:

                                if data['u_architecture'] == 'Collaboration':

                                    # Web Order ID #
                                    if self.weborder(sub_web_id=data['u_web_order_id']) not in cweborder:
                                        cweborder.append(self.weborder(sub_web_id=data['u_web_order_id']))

                                    # Subscriptions #
                                    if self.weborder(sub_web_id=data['u_subscription_id']) not in csubscription:
                                        csubscription.append(self.weborder(sub_web_id=data['u_subscription_id']))

                                    # Covered Products #
                                    if data['u_covered_products'] and data['u_covered_products'] not in cproducts:
                                        cproducts.append(data['u_covered_products'])

                                    elif data['u_covered_product'] and data['u_covered_product'] not in cproducts:
                                        cproducts.append(data['u_covered_product'])

                                    if data['u_service_start_date'] and data['u_service_start_date'] not in csstart:
                                        csstart.append(data['u_service_start_date'])

                                        print(data['u_service_start_date'])

                                    #collab['weborders'] = inserted_values

                                    #info[data['u_architecture']] = collab

                                        #print("collab")


                                        #print(result)

                                        #inserted_values = inserted_values + self.weborder(weborderid=data['u_web_order_id'])
                                        #inserted_values.append(self.weborder(weborderid=data['u_web_order_id']))

                                elif data['u_architecture'] == 'Security':

                                    # Web Order ID #
                                    if self.weborder(sub_web_id=data['u_web_order_id']) not in sweborder:
                                        sweborder.append(self.weborder(sub_web_id=data['u_web_order_id']))

                                    # Subscriptions #
                                    if self.weborder(sub_web_id=data['u_subscription_id']) not in ssubscription:
                                        ssubscription.append(self.weborder(sub_web_id=data['u_subscription_id']))

                                    # Covered Products #
                                    if data['u_covered_product'] and data['u_covered_product'] not in sproducts:
                                        sproducts.append(data['u_covered_product'])

                                    # SRV_Number #
                                    if data['number'] and data['number'] not in srv_security:
                                        srv_security.append(data['number'])
                                        dsm = self.getDSMs(svr_number=data['number'])

                                        for j in dsm:
                                            #print(j.get('u_technical_expert.email'))
                                            sdsms.append(j.get('u_technical_expert.email'))

                                    #customer_info = {data['customer']: info}
                                    #accounts[data['customer']] = info
                                    #clean_dataset.append({data['customer']: info})

                                container = dict(zip(sproducts, sdsms))
                                #print(container)
                        info.update({'customer': cu})
                        info['cweborder'] = list(set(sum(cweborder, [])))
                        info['sweborder'] = list(set(sum(sweborder, [])))
                        info['ssubscription'] = list(set(sum(ssubscription, [])))
                        info['csubscription'] = list(set(sum(csubscription, [])))
                        info['cproducts'] = list(set(cproducts))

                        clean_dataset.append(info)
                                    #print(time.perf_counter() - start_time, "seconds")

                                    # getting damn DSM 1 ### lets check how to move this block to a method

                                    #for i in self.getDSMs(svr_number=data['number']):

                                    #    print(i.get("u_role"))

                                #if data['u_architecture'] == 'Security':

                                #    print(data)

                    #inserted_values = sum(inserted_values, [])
                    #a= ("sobres perro: ".join(inserted_values))



                    return clean_dataset

dsmlookup = newDSMlookup()

print(dsmlookup.chorus(account_name="t-mobile"))
print("\n\n")
print(time.perf_counter() - start_time, "seconds")






