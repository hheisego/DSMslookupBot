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

        try:
            dsm = requests.get(final_url, auth=(user, pwd), headers=self.headers).json()["result"]

            return dsm

        except:

            dsm = [{'u_technical_expert.name': 'Try Again', 'u_role': 'could not', 'u_technical_expert.user_name': 'fetch details'}]

            print("vuelve a intentar en unos segundos")

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
                    final_output = ''
                    clean_dataset = []
                    #print(expert)
                    for cu in customer:

                        inserted_values = []
                        collab_coverage = []
                        info = {}
                        csubscription = []
                        ssubscription = []
                        sweborder = []
                        cweborder = []
                        sproducts = []
                        srv_security = []
                        sdsms = {}
                        cdsms = {}
                        ccontract = []
                        scontract = []
                        spas = []
                        #scounter = 1

                        for data in expert:
                            print(data)
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
                                    info['c_covered_products'] = data['u_covered_products']
                                    info['cpas'] = data['u_cs_case_owner']

                                    # GET DSMS block #
                                    dsm = self.getDSMs(svr_number=data['number'])

                                    for j in dsm:

                                        if j.get('u_technical_expert.name') and j.get('u_technical_expert.user_name'):

                                            collab_dsm = j.get('u_technical_expert.name') + ' (' + j.get('u_technical_expert.user_name') + ')'

                                        else:

                                           collab_dsm = " N/A "

                                        # print(j.get('u_role') + ' ' + data['u_covered_product'] + ' ' + j.get('u_technical_expert.name') + ' ' + j.get('u_technical_expert.user_name'))
                                        cdsms['coverage'] = {j.get('u_role') + ': ' + collab_dsm}

                                        if j.get('u_role') + ': ' + collab_dsm not in collab_coverage:
                                            collab_coverage.append(j.get('u_role') + ': ' + collab_dsm)

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

                                    # PAS / SOM #
                                    if data['u_cs_case_owner'] and data['u_cs_case_owner'] not in spas:
                                        spas.append(data['u_cs_case_owner'])

                                    info['s_offer_name'] = data['u_offer_name'] # each product has different this should be on the dsms block

                                    # GET DSMS block #
                                    dsm = self.getDSMs(svr_number=data['number'])

                                    for j in dsm:
                                        off_name = '_(N/A)_'

                                        if data['u_offer_name'] and 'Premium' in data['u_offer_name']:

                                            off_name = '_(P)_'

                                        elif data['u_offer_name'] and 'Enhance' in data['u_offer_name']:

                                            off_name = '_(E)_'

                                        if j.get('u_technical_expert.name') and j.get('u_technical_expert.user_name'):

                                            security_dsm = j.get('u_technical_expert.name') + ' (' + j.get('u_technical_expert.user_name') + ')' + ' ' + off_name

                                        else:

                                            security_dsm = " N/A "

                                        #print(j.get('u_role') + ' ' + data['u_covered_product'] + ' ' + j.get('u_technical_expert.name') + ' ' + j.get('u_technical_expert.user_name'))
                                        sdsms['coverage'] = {j.get('u_role') + ': ' + data['u_covered_product'] + ' -> ' + security_dsm}

                                        if j.get('u_role') + ': ' + data['u_covered_product'] + ' -> ' + security_dsm not in inserted_values:

                                            inserted_values.append(j.get('u_role') + ': ' + data['u_covered_product'] + ' -> ' + security_dsm)

                                #elif data['u_architecture'] == 'Security' and data['parent_contract'] is None:

                                    info['s_service_start'] = data['u_service_start_date']
                                    info['s_service_end'] = data['u_service_end_date']
                                    info['s_offer_type'] = data['u_offer_type']

                                    #if scounter == len(data['u_architecture']):
                        if sweborder or ssubscription or scontract:

                            info['sdsms'] = inserted_values
                            #svr2product = dict(zip(srv_security, sproducts))
                            info['sweborder'] = list(set(sum(sweborder, [])))
                            info['ssubscription'] = list(set(sum(ssubscription, [])))
                            info['scontracts'] = list(set(sum(scontract, [])))
                            info['spas'] = (", ".join(spas))
                            #info['sproducts'] = svr2product

                        if ccontract or csubscription or cweborder:

                            info['cdsms'] = collab_coverage
                            info['ccontracts'] = list(set(sum(ccontract, [])))
                            info['csubscription'] = list(set(sum(csubscription, [])))
                            info['cweborder'] = list(set(sum(cweborder, [])))

                        clean_dataset.append(info)

                    # result block the output#
                    print(clean_dataset)
                    for each in clean_dataset:

                        final_output += '--------------------\nAccount: ' + each['customer']

                        if each.get('ccontracts') or each.get('csubscription') or each.get('cweborder') or each.get('c_offer_name'):

                            final_output += '\n\nCollaboration:\n'

                            for tes in each['cdsms']:
                                final_output += '\n' + tes

                            if each['cpas']:
                                final_output += '\nPAS: ' + each['cpas']

                            if each['c_covered_products']:
                                final_output += '\nCovered Product(s): ' + each['c_covered_products'].replace("Webex",
                                                                                                              "WBX")

                            if each['c_offer_name'] and each['c_offer_type']:
                                final_output += '\nOffer: ' + each['c_offer_name'] + ' ' + each['c_offer_type']

                            if each['cweborder']:
                                final_output += '\nWeb Order(s): ' + (", ".join(each['cweborder']))

                            if each['csubscription']:
                                final_output += '\nSubcription(s): ' + (", ".join(each['csubscription']))

                            if each['ccontracts']:
                                final_output += '\nContract(s): ' + (", ".join(each['ccontracts']))

                            if each['c_service_start'] and each['c_service_end']:
                                final_output += '\nService Duration: ' + each['c_service_start'] + ' - ' + each[
                                    'c_service_end'] + ' -> Days Left: ' + self.expiryChecker(contractExp=each['c_service_end'])

                        if each.get('scontracts') or each.get('ssubscription') or each.get('sweborder'):

                            final_output += '\n\nSecurity:\n'

                            for tes in each['sdsms']:
                                final_output += '\n' + tes

                            if each['spas']:
                                final_output += '\nPAS: ' + each['spas']

                            if each['s_offer_name'] and each['s_offer_type']:
                                final_output += '\nOffer: ' + each['s_offer_name'] + ' ' + each['s_offer_type']

                            if each['sweborder']:
                                final_output += '\nWeb Order(s): ' + (", ".join(each['sweborder']))

                            if each['ssubscription']:
                                final_output += '\nSubcription(s): ' + (", ".join(each['ssubscription']))

                            if each['scontracts']:
                                final_output += '\nContract(s): ' + (", ".join(each['scontracts']))

                            if each['s_service_start'] and each['s_service_end']:
                                final_output += '\nService Duration: ' + each['s_service_start'] + ' - ' + each[
                                    's_service_end'] + ' -> Days Left: ' + self.expiryChecker(contractExp=each['s_service_end'])

                        final_output += '\n--------------------\n'

                    return final_output

dsmlookup = newDSMlookup()

print(dsmlookup.chorus(account_name="metlife"))
print("\n\n")
print(time.perf_counter() - start_time, "seconds")






