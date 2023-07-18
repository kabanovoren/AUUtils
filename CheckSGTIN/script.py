SQL = dict(
    ins_upd_sgtin=
        """update or insert into MDLP_SGTIN (SGTIN, DETAIL_LEVEL)
values (:SGTIN, 0)
matching (SGTIN)

"""
)