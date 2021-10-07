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
        reg = re.compile(pattern=r"(Sub\d{6}|\d{8}|\d{9})")
        result = re.findall(reg, str(sub_web_id))

        return result

    def chorus(self, account_name):

        #previous query parameters: %2Cu_contract_term "%2Cu_record_number%2cu_cs_case_owner%2cu_offer_name%2Ccustomer%2cu_order_status%2cu_order_substatus%2cu_offer_type%2Cu_te_primary%2Cu_te_primary.email%2Cu_te_secondary%2Cu_te_secondary.email%2Cu_te_tertiary%2Cu_te_tertiary.email%2Cu_contract_number%2Cu_contract_term%2Cu_service_start_date%2Cu_service_end_date%2Cu_subscription_id%2Cu_web_order_id%2Cu_architecture%2Cu_covered_products%2Cu_covered_product%2Cu_product_status&sysparm_query=customerLIKE"
        final_url = fixed_url + "%2Cparent_contract%2Cu_record_number%2cu_cs_case_owner%2cu_offer_name%2Ccustomer%2cu_order_status%2cu_order_substatus%2cu_offer_type%2Cu_contract_number%2Cu_service_start_date%2Cu_service_end_date%2Cu_subscription_id%2Cu_web_order_id%2Cu_architecture%2Cu_covered_products%2Cu_covered_product%2Cu_product_status&sysparm_query=customerLIKE" + account_name #+ '^u_order_status!=Expired^u_order_sub_status!=Inactive'  #"  # ^u_order_substatus!=Expired"

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
                        sproducts = []
                        srv_security = []
                        sdsms = {}
                        ccontract = []
                        scontract = []
                        scounter = 0

                        for data in expert:

                            if cu == data['customer']:

                                info.update({'customer': cu})

                                if data['u_architecture'] == 'Collaboration':

                                    # Web Order ID #
                                    if self.weborder(sub_web_id=data['u_web_order_id']) not in cweborder:
                                        cweborder.append(self.weborder(sub_web_id=data['u_web_order_id']))

                                    # Subscriptions #
                                    if self.weborder(sub_web_id=data['u_subscription_id']) not in csubscription:
                                        csubscription.append(self.weborder(sub_web_id=data['u_subscription_id']))

                                    # Contracts #
                                    if self.weborder(sub_web_id=data['u_contract_number']) not in ccontract:
                                        ccontract.append(self.weborder(sub_web_id=data['u_contract_number']))


                                    info['c_service_start'] = data['u_service_start_date']
                                    info['c_service_end'] = data['u_service_end_date']
                                    info['c_offer_type'] = data['u_offer_type']
                                    info['c_offer_name'] = data['u_offer_name']
                                    info['cproducts'] = data['u_covered_products']
                                    info['ccontracts'] = list(set(sum(ccontract, [])))
                                    info['csubscription'] = list(set(sum(csubscription, [])))
                                    info['cweborder'] = list(set(sum(cweborder, [])))



                                    #collab['weborders'] = inserted_values

                                    #info[data['u_architecture']] = collab

                                        #print("collab")


                                        #print(result)

                                        #inserted_values = inserted_values + self.weborder(weborderid=data['u_web_order_id'])
                                        #inserted_values.append(self.weborder(weborderid=data['u_web_order_id']))

                                elif data['u_architecture'] == 'Security' and data['parent_contract'] is not None:

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

                                    # Contracts #
                                    if self.weborder(sub_web_id=data['u_contract_number']) not in scontract:
                                        scontract.append(self.weborder(sub_web_id=data['u_contract_number']))

                                    #dsm = self.getDSMs(svr_number=data['number'])

                                    #for j in dsm:

                                    #    sdsms['coverage'] = {j.get('u_role') + ': ' + data['u_covered_product'] + ' -> ' + j.get('u_technical_expert.name') + ' ' + j.get('u_technical_expert.email')}

                                    #    if j.get('u_role') + ': ' + data['u_covered_product'] + ' -> ' + j.get('u_technical_expert.name') + ' ' + j.get('u_technical_expert.email') not in inserted_values:
                                    #        inserted_values.append(j.get('u_role') + ': ' + data['u_covered_product'] + ' -> ' + j.get('u_technical_expert.name') + ' ' + j.get('u_technical_expert.email'))

                                    #print(len(data['u_architecture']))
                                    print(scounter)


                                    if scounter == len(data['u_architecture']):

                                        print("ora putos")
                                        info['sdsms'] = inserted_values
                                        svr2product = dict(zip(srv_security, sproducts))
                                        info['sweborder'] = list(set(sum(sweborder, [])))
                                        info['ssubscription'] = list(set(sum(ssubscription, [])))
                                        info['scontracts'] = list(set(sum(scontract, [])))
                                        info['sproducts'] = svr2product

                                        scounter = 1

                                    scounter += 1



                                     #   print(time.perf_counter() - start_time, "seconds")

                                #container = dict(zip(srv_security, sproducts))
                                #print(container)

                        clean_dataset.append(info)

                    #inserted_values = sum(inserted_values, [])
                    #a= ("sobres perro: ".join(inserted_values))



                    return clean_dataset

dsmlookup = newDSMlookup()

print(dsmlookup.chorus(account_name="navy"))
print("\n\n")
print(time.perf_counter() - start_time, "seconds")






