SQL = dict(
    delete_farmgroup="""
    delete from farmgroup where id_farmgroup > 0""",
    delete_prep="""
    delete from prep where id_prep > 0""",
    delete_firm="""
    delete from firm where id_firm > 0""",
    delete_country="""
    delete from country where id_country > 0""",
    delete_tovar="""
    delete from tovar where id_tovar > 0""",
    delete_prep_vat="""
    delete from prep_vat""",
    delete_group_name_link="""
    delete from group_name_link where prim > 0""",
    update_firm="""
    update firm set id_country=0 where id_firm=0""",
    farmgroup="""
    update or insert into farmgroup (name_farmgroup) values ('%s') matching(name_farmgroup) returning id_farmgroup""",
    cs4="""
    update or insert into custom_sprav4 (name_cs4) values ('%s') matching(name_cs4) returning id_cs4""",
    country="""
    update or insert into country (name_country) values ('%s') matching(name_country) returning id_country""",
    firm="""
    update or insert into firm (name_firm, id_country, otech_firm) values ('%s', %s, %s) matching(name_firm) returning id_firm""",
    prep="""
    update or insert into prep (name_prep, id_cs4, id_farmgroup, code1) values ('%s', %s, %s, '%s') matching(name_prep) returning id_prep""",
    tovar="""
    update or insert into tovar (ean13, id_prep, id_firm) values ('%s', %s, %s) matching(ean13, id_prep, id_firm) """,
)
