SQL = dict(
    get_sale=
    """
        with PROD
        as (select
              extract(month from D.DATE_DOC_VN) M,
              extract(weekday from D.DATE_DOC_VN) WD,
              CASE
                WHEN A.EAN13 SIMILAR TO '[0-9]+' -- проверка на правильность заполнения EAN13, если не правильно, берем EAN13 из таблицы TOVAR, если и там не верно, берем из PREP
              and LEN(A.EAN13) = 13 and left(A.EAN13, 1) <> '2' and A.EAN13 <> '0000000000000' and (right(A.EAN13, 1) = right(10 - cast(right(((cast(substring(A.EAN13 from 12 for 1) as int) + -- расчет контольной суммы
              cast(substring(A.EAN13 from 10 for 1) as int) + cast(substring(A.EAN13 from 8 for 1) as int) + cast(substring(A.EAN13 from 6 for 1) as int) + cast(substring(A.EAN13 from 4 for 1) as int) + cast(substring(A.EAN13 from 2 for 1) as int)) * 3) + ((cast(substring(A.EAN13 from 11 for 1) as int) + cast(substring(A.EAN13 from 9 for 1) as int) + cast(substring(A.EAN13 from 7 for 1) as int) + cast(substring(A.EAN13 from 5 for 1) as int) + cast(substring(A.EAN13 from 3 for 1) as int) + cast(substring(A.EAN13 from 1 for 1) as int))), 1) as int), 1)) THEN A.EAN13
                else '-1'
              end EAN13,
        
              sum(P.SUM_REAL_DISCOUNT) SUM_REAL_DISCOUNT,
              sum(P.SUM_ROZN) SUM_ROZN,
              sum(P.SUM_OPT_NDS) SUM_OPT_NDS,
              cast(sum(P.KOL_ALL / A.KOL_RAZB) as numeric(16,2)) KOL_ALL
        
            from
              DOC D
            inner join POSDOC P on P.ID_DOC = D.ID_DOC
            inner join ARTIKUL A on A.ARTIKUL = P.ARTIKUL
            where D.DATE_DOC_VN >= '01.01.2020'
                  and D.ID_OPER = 23
            group by D.DATE_DOC_VN, A.EAN13, D.ID_DEPART)
        
        select
          P.* from
          PROD P
        where P.EAN13 <> -1    
    """

)
