SQL = dict(
    check_601="""
    select md.prim, md.operationdatetime from mdlp_doc md where md.xmldoc like '%s' and md.numschema = 601""",
    check_SGTIN_doc="""
    select max(mp.cur_nalic) cur_nalic, max(cast(ms.expiration_date as date)) exp_date from mdlp_sgtin ms
    inner join mdlp_pos mp on mp.id_sgtin = ms.prim
    where ms.sgtin = '%s'
    group by ms.prim
    """
)
