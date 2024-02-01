import xml.etree.ElementTree as ET
import xmlschema
import json
from xml.etree.ElementTree import ElementTree
import itertools


def create_xml(detail_data, subject_id):
    """Создание xml"""
    schema = 'xsd/documents.xsd'
    schema = xmlschema.XMLSchema(schema)
    xml_docs = []
    for doc in detail_data:
        sgtin = doc['sales']['union']['detail']['sgtin']
        detail = {'@action_id': 511, 'subject_id': subject_id}
        detail.update(doc)
        header = {'retail_sale': detail}
        data = {'@version': '1.37'}
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
        list_sgtin = itertools.zip_longest(part, sgtins, costs, vat_values, fillvalue=None)
        for part, sgtin, cost, vat_value in list_sgtin:
            if part is None:
                continue
            if part.text != '1':
                data = {"operation_date": operation_date,
                        "sales": {"union": {"detail": {
                            "sgtin": sgtin.text, "cost": cost.text, "vat_value": vat_value.text,
                            "sold_part": part.text},
                            "sale_docs": {"doc_type": 1,
                                          "doc_number": doc_number, "doc_date": doc_date}}}}
            else:
                data = {"operation_date": operation_date,
                        "sales": {"union": {"detail": {
                            "sgtin": sgtin.text, "cost": cost.text, "vat_value": vat_value.text},
                            "sale_docs": {"doc_type": 1,
                                          "doc_number": doc_number, "doc_date": doc_date}}}}
            docs_json.append(data)
    return docs_json


def insert_into_fdb(con, sgtins_doc):
    for sgtin, doc in sgtins_doc:
        con.execute(f"insert into mdlp_sgtin (sgtin, id_group, state_sgtin) values('{sgtin}', 7, 10)")
        ElementTree(doc).write(f'out/511.xml', encoding="UTF-8", xml_declaration=True)
        f = open(f'out/511.xml', 'rb')
        con.execute(f"insert into mdlp_doc (state, numschema, xmldoc, id_check_kkm) values(?,?,?,?)", ('NONE', 511, f, 1,))
        f.close()
    con.transaction.commit()


def delete_data(con):
    con.execute("delete from mdlp_doc where prim > 0")
    con.execute("delete from mdlp_pos where prim > 0")
    con.execute("delete from mdlp_sgtin where prim > 0")
    con.execute("SET GENERATOR GEN_MDLP_DOC TO 0")
    con.execute("SET GENERATOR GEN_MDLP_SGTIN TO 0")
    try:
        con.execute("""
         INSERT INTO CHECK_KKM (CHECK_ID, ID_DEPART)
            select first 1
             1,
            C.ID_CLIENT from
             CLIENT C
            where C.AUTOMATION_DEPART = 1
        """)
    except Exception as ex:
        print(f"Запись уже существует {ex}")

    con.execute("""
        CREATE OR ALTER TRIGGER MDLP_SGTIN_UPDATE_DOC FOR MDLP_SGTIN
        ACTIVE BEFORE UPDATE POSITION 0
        AS
        begin
         if (new.SGTIN_STATUS = 'in_partial_sale' or (new.SGTIN_STATUS = 'in_circulation') and
         old.STATE_SGTIN = 10) then
        begin
         update MDLP_DOC MD
         set MD.STATE = 'XMLREADY',
         MD.LAST_STATE = 'NONE'
         where MD.PRIM = new.PRIM and MD.STATE = 'NONE';
        end
        end
    """)
    con.execute("""
        CREATE OR ALTER TRIGGER MDLP_DOC_BU0 FOR MDLP_DOC
        ACTIVE BEFORE UPDATE POSITION 0
        AS
        begin
          if (new.STATE = 'GETKIZINFO') then
          begin
            new.STATE = 'SUCCESS';
            update MDLP_SGTIN MS
            set MS.DETAIL_LEVEL = 0,
                MS.ID_GROUP = 7,
                MS.IS_GISMT = 0
            where MS.PRIM = new.PRIM;
          end
        end
    """)
    con.execute("""
        CREATE OR ALTER trigger mdlp_sgtin_biu10 for mdlp_sgtin
        inactive before insert or update position 10
        AS
        DECLARE VARIABLE ID_GRP INTEGER;
        BEGIN
          IF (NEW.ID_GTIN > 0) THEN BEGIN
            SELECT ID_GROUP FROM MDLP_GTIN WHERE PRIM=NEW.ID_GTIN INTO :ID_GRP;
            IF (NEW.ID_GROUP <> ID_GRP) THEN BEGIN
              IF (ID_GRP = 7) THEN BEGIN
                NEW.IS_GISMT = 0;
              END ELSE BEGIN
                NEW.IS_GISMT = 1;
             END
             NEW.ID_GROUP = :ID_GRP;
            END
          END
        END
    """)
    con.transaction.commit()


def main():
    # schema = xmlschema.XMLSchema("xsd/documents.xsd")
    # print(schema.to_dict('D:/Python/AUUtils/TMP/511/511.XML'))
    file = 'D:/Python/AUUtils/TMP/511/test_2.xml'
    detail_json = open_file1C(file)
    # for sgtin in detail_json:
    #     print(f"{sgtin['sales']['union']['detail']['sgtin']}\n")

    # print(detail_json)
    sgtin_doc = create_xml(detail_json, '00000000000289')
    print(sgtin_doc)
    # 30.07.2022 Версия XSD-схем: 1.38
    # 20.11.2021 Версия XSD-схем: 1.37


if __name__ == '__main__':
    main()
