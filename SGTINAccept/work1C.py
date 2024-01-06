import xml.etree.ElementTree as ET
import xmlschema
import json
from xml.etree.ElementTree import ElementTree

def create_xml(detail_data):
    """Создание xml"""
    schema = 'xsd/documents.xsd'
    schema = xmlschema.XMLSchema(schema)
    xml_docs = []
    for doc in detail_data:
        sgtin = doc['sales']['union']['detail']['sgtin']
        detail = {'@action_id': 511, 'subject_id': '00000000274039'}
        detail.update(doc)
        header = {'retail_sale': detail}
        data = {'@version': '1.38'}
        data.update(header)
        data = json.dumps(data)
        xml = xmlschema.from_json(data, schema=schema, preserve_root=True)
        xml_docs.append([sgtin, xml])
    return xml_docs
        # ElementTree(xml).write(
        #     f'out/511.xml',
        #     encoding="UTF-8", xml_declaration=True)


def open_file1C(file):
    tree = ET.parse(file)
    document = tree.getroot()
    docs_json = []
    for docs in document:
        operation_date = docs.find("operation_date").text
        sales = docs.find("sales")
        union = sales.find("union")
        detail = union.find("detail")
        sgtins = detail.findall("sgtin")
        costs = detail.findall("cost")
        vat_values = detail.findall("vat_value")
        sale_docs = union.find("sale_docs")
        doc_number = sale_docs.find("doc_number").text
        doc_date = sale_docs.find("doc_date").text
        part = detail.findall("part")

        # Чеки если содержат продажу распаковки и целую, то целая не включается в список, что-то нужно переделать.
        if len(part) > 0:
            list_sgtin = zip(sgtins, costs, vat_values, part)
            for sgtin, cost, vat_value, part in list_sgtin:
                data = {"operation_date": operation_date,
                           "sales": { "union" :{ "detail" : {
                           "sgtin": sgtin.text, "cost": cost.text, "vat_value": vat_value.text, "sold_part": part.text},
                               "sale_docs":{ "doc_type" : 1,
                           "doc_number": doc_number, "doc_date": doc_date}}}}
                docs_json.append(data)
        else:
            list_sgtin = zip(sgtins, costs, vat_values)
            for sgtin, cost, vat_value in list_sgtin:
                data = {"operation_date": operation_date,
                        "sales": {"union": {"detail": {
                            "sgtin": sgtin.text, "cost": cost.text, "vat_value": vat_value.text},
                            "sale_docs": {"doc_type": 1,
                                          "doc_number": doc_number, "doc_date": doc_date}}}}
                docs_json.append(data)
    return docs_json


def insert_into_fdb(con, sgtins_doc):

    for sgtin, doc in sgtins_doc:
        con.execute(f"insert into mdlp_sgtin (sgtin, id_group) values('{sgtin}', 7)")
        ElementTree(doc).write(f'out/511.xml', encoding="UTF-8", xml_declaration=True)
        f = open(f'out/511.xml', 'rb')
        con.execute(f"insert into mdlp_doc (state, numschema, xmldoc) values(?,?,?)", ('None', 511, f,))
        f.close()
    con.transaction.commit()

def delete_data(con):
    con.execute("delete from mdlp_doc where prim > 0")
    con.execute("delete from mdlp_pos where prim > 0")
    con.execute("delete from mdlp_sgtin where prim > 0")
    con.execute("SET GENERATOR GEN_MDLP_DOC TO 0")
    con.execute("SET GENERATOR GEN_MDLP_SGTIN TO 0")
    con.transaction.commit()

def main():
    # schema = xmlschema.XMLSchema("xsd/documents.xsd")
    # print(schema.to_dict('D:/Python/AUUtils/TMP/511/511.XML'))
    file = 'D:/Python/AUUtils/TMP/511/test_2.xml'
    detail_json = open_file1C(file)
    # for sgtin in detail_json:
    #     print(f"{sgtin['sales']['union']['detail']['sgtin']}\n")

    # print(detail_json)
    sgtin_doc = create_xml(detail_json)
    print(sgtin_doc)
    # 30.07.2022 Версия XSD-схем: 1.38
    # 20.11.2021 Версия XSD-схем: 1.37


if __name__ == '__main__':
    main()
