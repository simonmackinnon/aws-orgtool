import boto3
import json
import logging
import sys, getopt
import webbrowser
from graphviz import Digraph
import string
import os

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, filename='orgtool.log')
logger = logging.getLogger('oustructure')

def visualize_organization_diagrams(file,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    logger.info(f'Import Json file: {file}')    
    f = open(file,)
    data = json.load(f)

    csvfile = 'organizations.csv'
    if os.path.exists(csvfile):
        print("Remove old CSV File.")
        os.remove(csvfile)

    csvfile = open(csvfile,"w")
    csv = """##
## Example CSV import. Use ## for comments and # for configuration. Paste CSV below.
## The following names are reserved and should not be used (or ignored):
## id, tooltip, placeholder(s), link and label (see below)
##
#
#
# label: %ou%<br><i style="color:black;fontSize=8"> %scps% </i><br>
## Node style (placeholders are replaced once).
## Default is the current style for nodes.
#
# style: label;image=%image%;whiteSpace=wrap;html=1;rounded=1;fillColor=#fff;strokeColor=#545B64;
#
## Parent style for nodes with child nodes (placeholders are replaced once).
#
# parentstyle: swimlane;whiteSpace=wrap;html=1;childLayout=stackLayout;horizontal=1;horizontalStack=0;resizeParent=1;resizeLast=0;collapsible=1;
#
## Optional column name that contains a reference to a named style in styles.
## Default is the current style for nodes.
#
# stylename: -
#
## JSON for named styles of the form {"name": "style", "name": "style"} where style is a cell style with
## placeholders that are replaced once.
#
# styles: -
#
## JSON for variables in styles of the form {"name": "value", "name": "value"} where name is a string
## that will replace a placeholder in a style.
#
# vars: -
#
## Optional column name that contains a reference to a named label in labels.
## Default is the current label.
#
# labelname: -
#
## JSON for named labels of the form {"name": "label", "name": "label"} where label is a cell label with
## placeholders.
#
# labels: -
#
## Uses the given column name as the identity for cells (updates existing cells).
## Default is no identity (empty value or -).
#
# identity: -
#
## Uses the given column name as the parent reference for cells. Default is no parent (empty or -).
## The identity above is used for resolving the reference so it must be specified.
#
# parent: -
#
## Adds a prefix to the identity of cells to make sure they do not collide with existing cells (whose
## IDs are numbers from 0..n, sometimes with a GUID prefix in the context of realtime collaboration).
## Default is csvimport-.
#
# namespace: csvimport-
#
## Connections between rows ("from": source colum, "to": target column).
## Label, style and invert are optional. Defaults are '', current style and false.
## If placeholders are used in the style, they are replaced with data from the source.
## An optional placeholders can be set to target to use data from the target instead.
## In addition to label, an optional fromlabel and tolabel can be used to name the column
## that contains the text for the label in the edges source or target (invert ignored).
## The label is concatenated in the form fromlabel + label + tolabel if all are defined.
## Additional labels can be added by using an optional labels array with entries of the
## form {"label": string, "x": number, "y": number, "dx": number, "dy": number} where
## x is from -1 to 1 along the edge, y is orthogonal, and dx/dy are offsets in pixels.
## The target column may contain a comma-separated list of values.
## Multiple connect entries are allowed.
#
# connect: {"from": "refs", "to": "id", "style": "edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;elbow=vertical;startArrow=none;endFill=1;strokeColor=#545B64;rounded=0;"}
#
## Node x-coordinate. Possible value is a column name. Default is empty. Layouts will
## override this value.
#
# left: 
#
## Node y-coordinate. Possible value is a column name. Default is empty. Layouts will
## override this value.
#
# top: 
#
## Node width. Possible value is a number (in px), auto or an @ sign followed by a column
## name that contains the value for the width. Default is auto.
#
# width: auto
#
## Node height. Possible value is a number (in px), auto or an @ sign followed by a column
## name that contains the value for the height. Default is auto.
#
# height: auto
#
## Padding for autosize. Default is 0.
#
# padding: 0
#
## Comma-separated list of ignored columns for metadata. (These can be
## used for connections and styles but will not be added as metadata.)
#
#
## Column to be renamed to link attribute (used as link).
#
# ignore: id,image,refs
#
## Spacing between nodes. Default is 40.
#
# nodespacing: 40
#
## Spacing between levels of hierarchical layouts. Default is 100.
#
# levelspacing: 100
#
## Spacing between parallel edges. Default is 40. Use 0 to disable.
#
# edgespacing: 10
#
## Name or JSON of layout. Possible values are auto, none, verticaltree, horizontaltree,
## verticalflow, horizontalflow, organic, circle or a JSON string as used in Layout, Apply.
## Default is auto.
#
# layout: verticalflow
#
## ---- CSV below this line. First line are column names."""
    root_id = org.list_roots()['Roots'][0]['Id']
    csv += f"\nid,ou,scps,refs,image\n{root_id},'ManagementAccount',,,https://raw.githubusercontent.com/daknhh/aws-orgtool/68de9477ed0fa9ac3dda1beea938b7453d44480e/static/AWS-Organizations_Management-Account.svg"
    for firstlevel in data['Ous']:
        scps = ""
        if(firstlevel['SCPs'] != []):
            scps += "Attached SCPs: "
            for scp in firstlevel['SCPs']:
                scps += f"{scp['Name']} "
        csv += f"\n{firstlevel['Id']},{firstlevel['Name']},{scps},{root_id},https://raw.githubusercontent.com/daknhh/aws-orgtool/68de9477ed0fa9ac3dda1beea938b7453d44480e/static/AWS-Organizations_Organizational-Unit.svg"
        if firstlevel['Children'] == 'No-Children':
            logger.info(f"{firstlevel['Name']} has no No-Children")
        else:
            for secondlevel in firstlevel['Children']:
                scps = ""
                if(secondlevel['SCPs'] != []):
                    scps += "Attached SCPs: "
                    for scp in secondlevel['SCPs']:
                        scps += f"{scp['Name']} "
                csv += f"\n{secondlevel['Id']},{secondlevel['Name']},{scps},{firstlevel['Id']},https://raw.githubusercontent.com/daknhh/aws-orgtool/68de9477ed0fa9ac3dda1beea938b7453d44480e/static/AWS-Organizations_Organizational-Unit.svg"
                if secondlevel['Children'] == 'No-Children':
                    logger.info(f"{secondlevel['Name']} has no No-Children")
                else:
                    for thirdlevel in secondlevel['Children']:
                        scps = ""
                        if(thirdlevel['SCPs'] != []):
                            scps += "Attached SCPs: "
                            for scp in thirdlevel['SCPs']:
                                scps += f"{scp['Name']} "
                        csv += f"\n{thirdlevel['Id']},{thirdlevel['Name']},{scps},{secondlevel['Id']},https://raw.githubusercontent.com/daknhh/aws-orgtool/68de9477ed0fa9ac3dda1beea938b7453d44480e/static/AWS-Organizations_Organizational-Unit.svg"
                        if thirdlevel['Children'] == 'No-Children':
                            logger.info(f"{thirdlevel['Name']} has no No-Children")
                        else:
                            for fourlevel in thirdlevel['Children']:
                                scps = ""
                                if(fourlevel['SCPs'] != []):
                                    scps += "Attached SCPs: "
                                    for scp in fourlevel['SCPs']:
                                        scps += f"{scp['Name']} "
                                csv += f"\n{fourlevel['Id']},{fourlevel['Name']},{scps},{thirdlevel['Id']},https://raw.githubusercontent.com/daknhh/aws-orgtool/68de9477ed0fa9ac3dda1beea938b7453d44480e/static/AWS-Organizations_Organizational-Unit.svg"
                                if fourlevel['Children'] == 'No-Children':
                                    logger.info(f"{fourlevel['Name']} has no No-Children")
                                else:
                                    for fivelevel in fourlevel['Children']:
                                        scps = ""
                                        if(fivelevel['SCPs'] != []):
                                            scps += "Attached SCPs: "
                                            for scp in fivelevel['SCPs']:
                                                scps += f"{scp['Name']} "
                                        csv += f"\n{fivelevel['Id']},{fivelevel['Name']},{scps},{fourlevel['Id']},https://raw.githubusercontent.com/daknhh/aws-orgtool/68de9477ed0fa9ac3dda1beea938b7453d44480e/static/AWS-Organizations_Organizational-Unit.svg"
    csvfile.write(csv)
    csvfile.close

def visualize_organization_graphviz(file,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    logger.info(f'Import Json file: {file}')    
    f = open(file,)
    data = json.load(f)
    dot = Digraph(comment='Organization',edge_attr={'arrowhead':'none'})
    root_id = org.list_roots()['Roots'][0]['Id']
    dot.node('O', f"Organization: \n{root_id}")
    for firstlevel in data['Ous']:
        dot.node(f"{firstlevel['Id']}", f"{firstlevel['Name']}",shape='box')
        dot.edge(f"O",f"{firstlevel['Id']}")
        if firstlevel['Children'] == 'No-Children':
            logger.info(f"{firstlevel['Name']} has no No-Children")
        else:
            for secondlevel in firstlevel['Children']:
                dot.node(f"{secondlevel['Id']}", f"{secondlevel['Name']}",shape='box')
                dot.edge(f"{firstlevel['Id']}",f"{secondlevel['Id']}")
                if secondlevel['Children'] == 'No-Children':
                    logger.info(f"{secondlevel['Name']} has no No-Children")
                else:
                    for thirdlevel in secondlevel['Children']:
                        dot.node(f"{thirdlevel['Id']}", f"{thirdlevel['Name']}",shape='box')
                        dot.edge(f"{secondlevel['Id']}", f"{thirdlevel['Id']}")
                        if thirdlevel['Children'] == 'No-Children':
                            logger.info(f"{thirdlevel['Name']} has no No-Children")
                        else:
                            for fourlevel in thirdlevel['Children']:
                                dot.node(f"{fourlevel['Id']}", f"{fourlevel['Name']}",shape='box')
                                dot.edge(f"{fourlevel['Id']}", f"{thirdlevel['Id']}")
                                if fourlevel['Children'] == 'No-Children':
                                    logger.info(f"{fourlevel['Name']} has no No-Children")
                                else:
                                    for fivelevel in fourlevel['Children']:
                                        logger.info(f"{fourlevel['Name']} has no No-Children")
                                        dot.node(f"{fivelevel['Id']}", f"{fivelevel['Name']}",shape='box')
                                        dot.edge(f"{fourlevel['Id']}", f"{fivelevel['Id']}")
    dot.graph_attr['nodesep']='1.0'
    #print(dot.source)
    dot.render('organization.gv', view=True,format='png')
    f.close() 
    
    

def export_policies(file,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    response = org.list_policies(
    Filter='SERVICE_CONTROL_POLICY'
    )
    logger.info(f'Inititalize Dict for SCPs')
    policies = {}

    for scp in response['Policies']:
        contentfile = f"scps/{scp['Name']}.json"
        
        responsepolicy = org.describe_policy(
            PolicyId=scp['Id']
            )
        content = responsepolicy['Policy']['Content']
        scpcontent = open(contentfile, "w")
        json.dump(content, scpcontent, indent = 6)
        scpcontent.close()
        logger.info(f'Created SCP Content File: {contentfile} in scps directory 🗂.')
        print(f'Created SCP Content File: {contentfile} in scps directory 🗂.')
        policies.setdefault('Scps', []).append({'Id': scp['Id'],'Name': scp['Name'],'Description': scp['Description'],'ContentFile':contentfile})
        logger.info(f'Add SCP {scp} to policies Dict.')
        print(f"Add SCP {scp['Name']} to policies Dict.")
    out_file = open(file, "w") 
    json.dump(policies, out_file, indent = 6) 
    out_file.close()
    logger.info(f'Created SCPs File: {file}.')
    print("\n************************")
    print(f'SCPs have been written to File: {file} 🗃.')

def import_policies(file,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    logger.info(f'Import Json file: {file}')    
    f = open(file,)
    data = json.load(f) 
    print("\n************************")
    print("\nImport-SCPs:")

    for scp in data['Scps']:
        print(f"- {scp['Name']}")
        f = open(scp['ContentFile'],)
        print(f"  - Import Json file: {scp['ContentFile']}.")
        logger.info(f"Import Json file: {scp['ContentFile']}.")  
        data = json.load(f)
        try:
            response = org.create_policy(
            Content=data,
            Description=scp['Description'],
            Name=scp['Name'],
            Type='SERVICE_CONTROL_POLICY'
            )
            logger.info(f"Created SCP with Name: {scp['Name']} - Id: {response['Policy']['PolicySummary']['Id']}.") 
            print(f"✅ Created SCP with Name: {scp['Name']} - Id: {response['Policy']['PolicySummary']['Id']}. \n\n") 
        except org.exceptions.DuplicatePolicyException:
            logger.info(f"SCP with Name: {scp['Name']} - already exist.") 
            print(f"ℹ SCP with Name: {scp['Name']} - already exist. \n\n") 
    print("\n************************")
    print(f'✅ SCPs have been imported.')

def validate_policies(file,profile):
    session = boto3.Session(profile_name=profile,region_name='us-east-1')
    accessanalyzer = session.client('accessanalyzer')
    logger.info(f'Load Json file: {file}')    
    f = open(file,)
    data = json.load(f) 
    print("\n************************")
    print("Validate Policies \n")

    for scp in data['Scps']:
        print(f"\n------------------------------------------")
        print(f"🔍 Findings for: \n{scp['Name']} SCP \n\n")
        logger.info(f"Validate SCP with Name: {scp['Name']}") 
        response = accessanalyzer.validate_policy(
        locale='EN',
        policyDocument=scp['ContentFile'],
        policyType='SERVICE_CONTROL_POLICY'
        )
        for finding in response['findings']:
            if finding['findingDetails'] == 'Fix the JSON syntax error at index 0 line 1 column 0.':
                break
            else: 
                if finding['findingType'] == 'ERROR':
                    findingtype = '❗️'
                if finding['findingType'] == 'SECURITY_WARNING':
                    findingtype = '🚨'
                if finding['findingType'] == 'WARNING':
                    findingtype = '⚠️'
                if finding['findingType'] == 'SUGGESTION':
                    findingtype = '💡'
                print(f"{findingtype}{finding['findingType']}")
                print(f"Details: {finding['findingDetails']}")
                print(f"Code: {finding['issueCode']}")
                print(f"🔗 Learn more: \x1b]8;;{finding['learnMoreLink']}\aCtrl+Click here\x1b]8;;\a \n")
                logger.info(f"Finding in {scp['Name']} - Type:{finding['findingType']} - Details:{finding['findingDetails']} - Code:{finding['issueCode']} - Learn more:{finding['learnMoreLink']}")
                 
def get_ou_stucture(parent_id,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    paginator = org.get_paginator('list_organizational_units_for_parent')
    page_iterator = paginator.paginate(ParentId=parent_id)
    ous = {}
    ou_secondlevel = {}
    ou_thirdlevel = {}
    ou_fivelevel = {}
    ou_sixlevel = {}
    ou_sevenlevel = {}
    print("\n************************")
    print("\nOrganization-Structure: ")
    print("%s" % (parent_id))

    for page in page_iterator:
        for ou in page['OrganizationalUnits']:
            logger.info(f'Inititalize Dict for {ou}')
            ous.setdefault('Ous', []).append({'Id': ou['Id'],'Name': ou['Name'],'Children': {}})
    for idx, ou in enumerate(ous['Ous']):
        page_iterator = paginator.paginate(ParentId=ou['Id'])
        logger.info(f'Check {ou} for Children')
        for page in page_iterator:
            scp = get_scpforou(ou['Id'],profile)
            if page['OrganizationalUnits'] == []:
                ou_secondlevel = {'Children':'No-Children'}
                print(" - %s" % (ou['Name']))
            else:
                print(" - %s" % (ou['Name']))
                for ou_2l in page['OrganizationalUnits']:   
                    print(" - - %s" % (ou_2l['Name']))
                    ou_secondlevel.setdefault('Children', []).append({'Id': ou_2l['Id'],'Name': ou_2l['Name'],'SCP': scp,'Children': {}})       
            ous['Ous'][idx] = {'Id': ou['Id'],'Name': ou['Name'],'SCPs': scp['SCPs'],'Children':ou_secondlevel['Children']}
            if ou_secondlevel == 'No-Children':
                ou_secondlevel = {}
            else:
                ou_secondlevel.clear()

            if ous['Ous'][idx]['Children'] == 'No-Children':
                logger.info('No-Children') 
            else:
                for idx2, ou3 in enumerate(ous['Ous'][idx]['Children']):
                    scp = get_scpforou(ou3['Id'],profile)
                    page_iterator2 = paginator.paginate(ParentId=ou3['Id'])
                    logger.info(f'Check {ou3} for Children')
                    for page in page_iterator2:
                        if page['OrganizationalUnits'] == []:
                            ou_thirdlevel = {'Children':'No-Children'}
                            logger.info(f'No-Children')
                            print(" - - - %s" % (ou3['Name']))
                        else:
                            logger.info(page['OrganizationalUnits'])
                            print(" - - - %s" % (ou3['Name']))
                            for ou_3l in page['OrganizationalUnits']:
                                print(" - - - - %s" % (ou_3l['Name']))
                                ou_thirdlevel.setdefault('Children', []).append({'Id': ou_3l['Id'],'Name': ou_3l['Name'],'Children': {}})       
                        ous['Ous'][idx]['Children'][idx2] = {'Id': ou3['Id'],'Name': ou3['Name'],'SCPs': scp['SCPs'],'Children':ou_thirdlevel['Children']}
                        if ou_thirdlevel == {'Children':'No-Children'}:
                            ou_thirdlevel = {}
                        else:
                            ou_thirdlevel.clear()
                        
                        if ous['Ous'][idx]['Children'][idx2]['Children'] == 'No-Children':
                            logger.info('No-Children')
                        else:
                            for idx3, ou4 in enumerate(ous['Ous'][idx]['Children'][idx2]['Children']):
                                scp = get_scpforou(ou4['Id'],profile)
                                page_iterator3 = paginator.paginate(ParentId=ou4['Id'])
                                logger.info(f'Check {ou4} for Children')
                                for page in page_iterator3:
                                    if page['OrganizationalUnits'] == []:
                                        ou_fivelevel = {'Children':'No-Children'}
                                        logger.info(f'No-Children')
                                        print(" - - - - - %s" % (ou4['Name']))
                                    else:
                                        logger.info(page['OrganizationalUnits'])
                                        print(" - - - - - %s" % (ou4['Name']))
                                        for ou_4l in page['OrganizationalUnits']:
                                            print(" - - - - - - %s" % (ou_4l['Name']))
                                            ou_fivelevel.setdefault('Children', []).append({'Id': ou_4l['Id'],'Name': ou_4l['Name'],'Children': {}})
                                    ous['Ous'][idx]['Children'][idx2]['Children'][idx3] = {'Id': ou4['Id'],'Name': ou4['Name'],'SCPs': scp['SCPs'],'Children':ou_fivelevel['Children']}                      
                                    if ou_fivelevel == {'Children':'No-Children'}:
                                        ou_fivelevel = {}
                                    else:
                                        ou_fivelevel.clear()
                                    
                                    if ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'] == 'No-Children':
                                        logger.info('No-Children')
                                    else:
                                        for idx4, ou5 in enumerate(ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children']):
                                            scp = get_scpforou(ou5['Id'],profile)
                                            page_iterator4 = paginator.paginate(ParentId=ou5['Id'])
                                            logger.info(f'Check {ou5} for Children')
                                            for page in page_iterator4:
                                                if page['OrganizationalUnits'] == []:
                                                    ou_sixlevel = {'Children':'No-Children'}
                                                    logger.info(f'No-Children')
                                                    print(" - - - - - %s" % (ou5['Name']))
                                                else:
                                                    logger.info(page['OrganizationalUnits'])
                                                    print(" - - - - - %s" % (ou5['Name']))
                                                    for ou_5l in page['OrganizationalUnits']:
                                                        print(" - - - - - - %s" % (ou_5l['Name']))
                                                        ou_sixlevel.setdefault('Children', []).append({'Id': ou_5l['Id'],'Name': ou_5l['Name'],'Children': {}})
                                                ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4] = {'Id': ou5['Id'],'Name': ou5['Name'],'SCPs': scp['SCPs'],'Children':ou_sixlevel['Children']}                      
                                                if ou_sixlevel == {'Children':'No-Children'}:
                                                    ou_sixlevel = {}
                                                else:
                                                    ou_sixlevel.clear()
                                            if ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4]['Children'] == 'No-Children':
                                                logger.info('No-Children')
                                            else:
                                                for idx5, ou6 in enumerate(ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4]['Children']):
                                                    scp = get_scpforou(ou6['Id'],profile)
                                                    page_iterator5 = paginator.paginate(ParentId=ou6['Id'])
                                                    logger.info(f'Check {ou6} for Children')
                                                    for page in page_iterator5:
                                                        if page['OrganizationalUnits'] == []:
                                                            ou_sevenlevel = {'Children':'No-Children'}
                                                            logger.info(f'No-Children')
                                                            print(" - - - - - - %s" % (ou6['Name']))
                                                        else:
                                                            logger.info(page['OrganizationalUnits'])
                                                            print(" - - - - - - %s" % (ou6['Name']))
                                                            for ou_6l in page['OrganizationalUnits']:
                                                                print(" - - - - - - - %s" % (ou_6l['Name']))
                                                                ou_sevenlevel.setdefault('Children', []).append({'Id': ou_6l['Id'],'Name': ou_6l['Name'],'Children': {'Children':'No-Children'}})
                                                        ous['Ous'][idx]['Children'][idx2]['Children'][idx3]['Children'][idx4]['Children'][idx5] = {'Id': ou6['Id'],'Name': ou6['Name'],'SCPs': scp['SCPs'],'Children':ou_sevenlevel['Children']}                      
                                                        if ou_sevenlevel == {'Children':'No-Children'}:
                                                            ou_sevenlevel = {}
                                                        else:
                                                            ou_sevenlevel.clear()    
    return ous

def export_structure(file,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    root_id = org.list_roots()['Roots'][0]['Id']
    logger.info('Query first level OUs')
    ous= get_ou_stucture(root_id,profile)
    out_file = open(file, "w") 
    json.dump(ous, out_file, indent = 6) 
    out_file.close()
    print("\n************************")
    logger.info(f'\n Write Ous to file: {file}')
    print(f'Ous have been written to {file}.')

def get_scpforou(ou_id,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    response = org.list_policies_for_target(
        TargetId=ou_id,
        Filter='SERVICE_CONTROL_POLICY',
    )
    scp = {}
    scp.setdefault('SCPs',[])
    for policy in response['Policies']:
        if policy['Name'] == 'FullAWSAccess':
            logger.info(f'\n AWS SCP Found: FullAWSAccess')
        else:
            scp.setdefault('SCPs',[]).append({'Name': policy['Name']})    
    return scp

def get_all_scps(profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    response = org.list_policies(
    Filter='SERVICE_CONTROL_POLICY',
    )
    allscps = ""
    for Scp in response['Policies']:
        allscps += f"\"{Scp['Name']}\": \"{Scp['Id']}\","
        #allscps.setdefault('SCPs', []).append({Scp['Name']: Scp['Id']})
    allscps = allscps[:-1]
    allscpsstring = "{" + allscps + "}" 
    convertedDict = json.loads(allscpsstring)
    return convertedDict

def attach_policies(file,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    scps_in_org = get_all_scps(profile)
    logger.info(f'Import Json file: {file}')    
    f = open(file,)
    data = json.load(f) 
    
    root_id = org.list_roots()['Roots'][0]['Id']
    print("\n************************")
    print("\nAttach-SCPs:")
    for firstlevel in data['Ous']: 
        firstlevelname = firstlevel['Name']
        firstlevelou_id = get_ou_id_by_name(firstlevelname,root_id,profile)
        if(firstlevel['SCPs'] == []):
            logger.info(f'No SCP to attach for: {firstlevelou_id} - {firstlevelname} in {root_id}')
            print(f'\nℹ️ No SCPs for OU: {firstlevelname}.')         
        else:
            print(f'\nattaching SCPs to OU {firstlevelname}:') 
            for scp in firstlevel['SCPs']:
                policyid = scps_in_org.get(scp['Name'])                
                try:
                    response = org.attach_policy(
                    PolicyId=policyid,
                    TargetId=firstlevelou_id,
                    )
                    logger.info(f'Attached: {policyid} to {firstlevelou_id}')
                    print(f"✅ {scp['Name']} - {policyid}")
                except org.exceptions.DuplicatePolicyAttachmentException:
                    logger.info(f'Already attached: {policyid} to {firstlevelou_id}')
                    print(f"✅ {scp['Name']} - {policyid}")

            if firstlevel['Children'] == 'No-Children':
                logger.info(f'{firstlevelname} has no No-Children')        
            else:
                for secondlevel in firstlevel['Children']:
                    secondlevelname = secondlevel['Name']
                    secondlevelou_id = get_ou_id_by_name(secondlevelname,firstlevelou_id,profile)
                    if(secondlevel['SCPs'] == []):
                        logger.info(f'No SCP to attach for: {secondlevelou_id} - {secondlevelname} in {firstlevelou_id}')
                        print(f'\nℹ️ No SCPs for OU: {secondlevelname}.')         
                    else:
                        print(f'\nattaching SCPs to OU {secondlevelname}:') 
                        for scp in secondlevel['SCPs']:
                            policyid = scps_in_org.get(scp['Name'])                
                            try:
                                response = org.attach_policy(
                                PolicyId=policyid,
                                TargetId=secondlevelou_id,
                                )
                                logger.info(f'Attached: {policyid} to {secondlevelou_id}')
                                print(f"✅ {scp['Name']} - {policyid}")
                            except org.exceptions.DuplicatePolicyAttachmentException:
                                logger.info(f'Already attached: {policyid} to {secondlevelou_id}')
                                print(f"✅ {scp['Name']} - {policyid}")        
                        if secondlevel['Children'] == 'No-Children':
                            logger.info(f'{secondlevelname} has no No-Children')
                        else:
                            for thirdlevel in secondlevel['Children']:
                                thirdlevelname = thirdlevel['Name']
                                thirdlevelou_id = get_ou_id_by_name(thirdlevelname,secondlevelou_id,profile)
                                if(thirdlevel['SCPs'] == []):
                                    logger.info(f'No SCPs to attach for: {thirdlevelou_id} - {thirdlevelname} in {secondlevelou_id}')
                                    print(f'\nℹ️ No SCPs for OU: {thirdlevelname}.')         
                                else:
                                    print(f'\nattaching SCPs to OU {thirdlevelname}:') 
                                    for scp in thirdlevel['SCPs']:
                                        policyid = scps_in_org.get(scp['Name'])                
                                        try:
                                            response = org.attach_policy(
                                            PolicyId=policyid,
                                            TargetId=thirdlevelou_id,
                                            )
                                            logger.info(f'Attached: {policyid} to {thirdlevelou_id}')
                                            print(f"✅ {scp['Name']} - {policyid}")
                                        except org.exceptions.DuplicatePolicyAttachmentException:
                                            logger.info(f'Already attached: {policyid} to {thirdlevelou_id}')
                                            print(f"✅ {scp['Name']} - {policyid}")

                                if thirdlevel['Children'] == 'No-Children':
                                    logger.info(f'{thirdlevelname} has no No-Children')
                                else:
                                    for fourlevel in thirdlevel['Children']:
                                        fourlevelname = thirdlevel['Name']
                                        fourlevelou_id = get_ou_id_by_name(fourlevelname,thirdlevelou_id,profile)
                                        if(fourlevel['SCPs'] == []):
                                            logger.info(f'No SCPs to attach for: {fourlevelou_id} - {fourlevelname} in {thirdlevelou_id}')
                                            print(f'\nℹ️ No SCPs for OU: {fourlevelname}.')         
                                        else:
                                            print(f'\nattaching SCPs to OU {fourlevelname}:') 
                                            for scp in fourlevel['SCPs']:
                                                policyid = scps_in_org.get(scp['Name'])                
                                                try:
                                                    response = org.attach_policy(
                                                    PolicyId=policyid,
                                                    TargetId=fourlevelou_id,
                                                    )
                                                    logger.info(f'Attached: {policyid} to {fourlevelou_id}')
                                                    print(f"✅ {scp['Name']} - {policyid}")
                                                except org.exceptions.DuplicatePolicyAttachmentException:
                                                    logger.info(f'Already attached: {policyid} to {fourlevelou_id}')
                                                    print(f"✅ {scp['Name']} - {policyid}")
                                        if fourlevel['Children'] == 'No-Children':
                                            logger.info(f'{fourlevelname} has no No-Children')
                                        else:
                                            for fivelevel in fourlevel['Children']:
                                                fivelevelname = fivelevel['Name']
                                                fivelevelou_id = get_ou_id_by_name(fivelevelname,fourlevelou_id,profile)
                                                if(fivelevel['SCPs'] == []):
                                                    logger.info(f'No SCPs to attach for: {fivelevelou_id} - {fivelevelname} in {fourlevelou_id}')
                                                    print(f'\nℹ️ No SCPs for OU: {fivelevelname}.')         
                                                else:
                                                    print(f'\nattaching SCPs to OU {fourlevelname}:') 
                                                    for scp in fivelevel['SCPs']:
                                                        policyid = scps_in_org.get(scp['Name'])                
                                                        try:
                                                            response = org.attach_policy(
                                                            PolicyId=policyid,
                                                            TargetId=fivelevelou_id,
                                                            )
                                                            logger.info(f'Attached: {policyid} to {fivelevelou_id}')
                                                            print(f"✅ {scp['Name']} - {policyid}")
                                                        except org.exceptions.DuplicatePolicyAttachmentException:
                                                            logger.info(f'Already attached: {policyid} to {fivelevelou_id}')
                                                            print(f"✅ {scp['Name']} - {policyid}")

def get_ou_id_by_name(name,parent_id,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    paginator = org.get_paginator('list_organizational_units_for_parent')
    page_iterator = paginator.paginate(ParentId=parent_id)
    session = boto3.Session(profile_name=profile)
    search_key = name
    logger.info(f'Search for OuID by name: {name}')
    for page in page_iterator:
        for ou in page['OrganizationalUnits']:
            for (key, value) in ou.items():
                    if value == search_key:
                            res = ou['Id']
                            logger.info(f'Got OuID: {res}')
    return(res)

def import_structure(file,profile):
    session = boto3.Session(profile_name=profile)
    org = session.client('organizations')
    logger.info(f'Import Json file: {file}')    
    f = open(file,)
    data = json.load(f) 
    
    root_id = org.list_roots()['Roots'][0]['Id']
    print("\n************************")
    print("\nOrganization-Structure: ")
    print(f'{root_id}')
    for firstlevel in data['Ous']: 
        try:
            response = org.create_organizational_unit(
            ParentId=root_id,
            Name=firstlevel['Name']
            )
            firstlevelou_id = response['OrganizationalUnit']['Id']
            firstlevelname= firstlevel['Name']
            logger.info(f'Created OU: {firstlevelou_id} - {firstlevelname} in {root_id}')
            print(f' - {firstlevelname}')
        except (org.exceptions.DuplicateOrganizationalUnitException):
            logger.info('OU already exist')
            firstlevelname = firstlevel['Name']
            print(f' - {firstlevelname}')
            firstlevelou_id = get_ou_id_by_name(firstlevel['Name'],root_id,profile)  
        if firstlevel['Children'] == 'No-Children':
            logger.info(f'{firstlevelname} has no No-Children')
        else:
            for secondlevel in firstlevel['Children']:
                try:
                    response2 = org.create_organizational_unit(
                    ParentId=firstlevelou_id,
                    Name=secondlevel['Name']
                    )
                    secondlevelou_id = response2['OrganizationalUnit']['Id']
                    secondlevelname = secondlevel['Name']
                    logger.info(f'Created OU: {secondlevelname} with Id: {secondlevelou_id} {firstlevelname} in {firstlevelou_id}')
                    print(f' - - {secondlevelname}')
                except (org.exceptions.DuplicateOrganizationalUnitException):
                    secondlevelname = secondlevel['Name']
                    print(f' - - {secondlevelname}')
                    secondlevelou_id = get_ou_id_by_name(secondlevel['Name'],firstlevelou_id,profile)

                if secondlevel['Children'] == 'No-Children':
                    logger.info(f'{secondlevelname} has no No-Children')
                else:
                    for thirdlevel in secondlevel['Children']:
                        try:
                            response3 = org.create_organizational_unit(
                            ParentId=secondlevelou_id,
                            Name=thirdlevel['Name']
                            )
                            thirdlevellevelou_id = response3['OrganizationalUnit']['Id']
                            thirdlevelname = thirdlevel['Name']
                            logger.info(f'Created OU: {thirdlevelname} with Id: {thirdlevellevelou_id} {secondlevelname} in {secondlevelou_id}')
                            print(f' - - - {thirdlevelname}')
                        except (org.exceptions.DuplicateOrganizationalUnitException):
                            thirdlevelname = thirdlevel['Name']
                            print(f' - - - {thirdlevelname}')
                            thirdlevellevelou_id = get_ou_id_by_name(thirdlevel['Name'],secondlevelou_id,profile)

                        if thirdlevel['Children'] == 'No-Children':
                            logger.info(f'{thirdlevelname} has no No-Children')
                        else:
                            for fourlevel in thirdlevel['Children']:
                                try:
                                    response4 = org.create_organizational_unit(
                                    ParentId=thirdlevellevelou_id,
                                    Name=fourlevel['Name']
                                    )
                                    fourlevelou_id = response4['OrganizationalUnit']['Id']
                                    fourlevelname = fourlevel['Name']
                                    logger.info(f'Created OU: {fourlevelname} with Id: {fourlevelou_id} in {thirdlevellevelou_id}')
                                    print(f' - - - - {fourlevelname}')
                                except (org.exceptions.DuplicateOrganizationalUnitException):
                                    fourlevelname = fourlevel['Name']
                                    print(f' - - - - {fourlevelname}')
                                    fourlevelou_id = get_ou_id_by_name(fourlevel['Name'],thirdlevellevelou_id,profile)
                            
                            if fourlevel['Children'] == 'No-Children':
                                logger.info(f'{fourlevelname} has no No-Children')
                            else:
                                for fivelevel in fourlevel['Children']:
                                    try:
                                        response5 = org.create_organizational_unit(
                                        ParentId=fourlevelou_id,
                                        Name=fivelevel['Name']
                                        )
                                        fivelevelou_id = response5['OrganizationalUnit']['Id']
                                        fivelevelname = fivelevel['Name']
                                        logger.info(f'Created OU: {fivelevelname} with Id: {fivelevelou_id} in {thirdlevellevelou_id}')
                                        print(f' - - - - - {fivelevelname}')
                                    except (org.exceptions.DuplicateOrganizationalUnitException):
                                        fivelevelname = fivelevel['Name']
                                        print(f' - - - - - {fivelevelname}')
                                        fivelevelou_id = get_ou_id_by_name(fivelevel['Name'],fourlevelou_id,profile)

    f.close() 
    logger.info(f'\n OU Structure has been imported.')
    logger.info(f'\n********************************')

def main(argv):
    print('------------------------------------------------------------------------------')
    print('ORGTOOL for exporting and importing AWS organizations structure to / from Json')
    print('------------------------------------------------------------------------------')
    try:
        opts, args = getopt.getopt(argv,"hu:f:p:",["u=","f=","p="])
    except getopt.GetoptError:
        print('Usage:')
        print('Export: orgtool.py -u export -f <file.json> -p AWSPROFILE')
        print('Export SCPs: orgtool.py -u export-scps -p AWSPROFILE')
        print('Import: orgtool.py -u import -f <file.json> -p AWSPROFILE')
        print('Import SCPs: orgtool.py -u import-scps -f <file.json> -p AWSPROFILE')
        print('Validate SCPs: orgtool.py -u validate-scps -f <file.json> -p AWSPROFILE')
        print('Visualize Organization: orgtool.py -u visualize-organization-graphviz -f <file.json> -p AWSPROFILE')
        print('Visualize Organization: orgtool.py -u visualize-organization-diagrams -f <file.json> -p AWSPROFILE')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage:')
            print('Export: orgtool.py -u export -f <file.json> -p AWSPROFILE')
            print('Export SCPs: orgtool.py -u export-scps -f <file.json> -p AWSPROFILE')
            print('Import: orgtool.py -u import -f <file.json> -p AWSPROFILE')
            print('Import SCPs: orgtool.py -u import-scps -f <file.json> -p AWSPROFILE')
            print('Validate SCPs: orgtool.py -u validate-scps -f <file.json> -p AWSPROFILE')
            print('Attach SCPs: orgtool.py -u attach-scps -f <file.json> -p AWSPROFILE')
            print('Visualize Organization: orgtool.py -u visualize-organization-graphviz -f <file.json> -p AWSPROFILE')
            print('Visualize Organization: orgtool.py -u visualize-organization-diagrams -f <file.json> -p AWSPROFILE')
            sys.exit()
        elif opt in ("-u", "--usage"):
            print(f'Current usage: {arg}')
            logger.info(f'Usage:{arg}')
            usage = arg
        elif opt in ("-f", "--file"):
            print(f'File {arg}')
            logger.info(f'File:{arg}')
            file = arg
        elif opt in ("-p", "--profile"):
            print(f'Profile {arg}')
            logger.info(f'Profile:{arg}')
            profile = arg
    if usage == 'export':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: Export OUs to Json')
        export_structure(file,profile)
    elif usage == 'import':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: Import OUs from Json')
        import_structure(file,profile)
    elif usage == 'export-scps':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: Export Scps to Json')
        export_policies(file,profile)
    elif usage == 'import-scps':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: Import Scps from Json')
        import_policies(file,profile)
    elif usage == 'validate-scps':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: Validate Scps from Json')
        validate_policies(file,profile)
    elif usage == 'attach-scps':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: Validate Scps from Json')
        attach_policies(file,profile)
    elif usage == 'visualize-organization-graphviz':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: visualize Organization with graphviz from Json')
        visualize_organization_graphviz(file,profile)
    elif usage == 'visualize-organization-diagrams':
        logger.info('---------------------------------------------------')
        logger.info('NEW REQUEST: visualize Organization with diagrams.net from Json')
        visualize_organization_diagrams(file,profile)
    print('ℹ️: logs can be found in orgtool.log')

if __name__ == "__main__":
   main(sys.argv[1:])

