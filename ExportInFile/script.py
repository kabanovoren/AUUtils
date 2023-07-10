import Service.fdb_service as service

SQL = dict(
    get_depart="select short_client||'['||id_client||']' from client where automation_depart = 1",

    get_nalic_evotor="""
    select
     '' uuid,
    pr.name_prep,
    0 name_group,
    a.artikul kod,
    '' kod_group,
    '' ed_izmer,
    a.cena_rozn * a.kol_razb cena_rozn,
    a.cena_opt_nds * a.kol_razb cena_opt_nds,
    n.kol_all/a.kol_razb kol,
    a.artikul,
    'normal' tip,
    a.nacen_opt_nds nds,
    a.ean13,
    '' opis,
    '' kod_prod,
    '' krep,
    '' wol,
    '' alk,
    1 kpprod,
    '' rasp_prod
    from nalic n 
    inner join artikul a on a.artikul = n.artikul
    inner join prep pr on pr.id_prep = a.id_prep
    inner join firm f on f.id_firm = a.id_firm
    where n.id_depart = %s """
)

#
# def get_depart():
#     result = []
#     id_client = []
#     con = service.fdb_au()
#     list_depart = con.execute("select id_client, short_client from client where automation_depart = 1").fetchall()
#     for depart in list_depart:
#         result.append(depart[1])
#         id_client.append(depart[0])
#     service.disconnect_fdb(con)
#     return result, id_client

def main():
    print(SQL["get_depart"])
    service.get_name_file(__file__)
    # print(get_depart())

if __name__ == '__main__':
    main()
