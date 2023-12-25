SQL = dict(
    check_SGTIN="""
    with CHECK_SGTIN
as (select
      '%s' SGTIN,
      max(MD.PRIM) ID_DOC_MDLP_DOC,
      max(cast(MD.OPERATIONDATETIME as date)) OPERATIONDATETIME,
      null CUR_NALIC,
      null id_doc,
      null check_id,
      null id_oper,
      null xmldoc_id_doc,
      null xmldoc_check_id,
      null date_doc_vn 
       from
      MDLP_DOC MD
    where MD.XMLDOC like '%s'
          and MD.NUMSCHEMA = 601
    group by 1

    union all
    select
      '%s' SGTIN,
      null ID_DOC_MDLP_DOC,
      null OPERATIONDATETIME,
      max(MP.CUR_NALIC) CUR_NALIC,
      list(d.id_doc) id_doc,
      list(ck.check_id) check_id,
      list(d.id_oper) id_oper,
      list(md2.xmldoc) xmldoc_id_doc,
      list(md.xmldoc) xmldoc_check_id,
      max(d.date_doc_vn) date_doc_vn

       from
      MDLP_SGTIN MS
    inner join MDLP_POS MP on MP.ID_SGTIN = MS.PRIM
    inner join doc d on d.id_doc = mp.id_doc
    inner join check_kkm ck on ck.check_id = mp.id_check
    left join mdlp_doc md on md.id_check_kkm = mp.id_check and md.id_check_kkm > 0
    left join mdlp_doc md2 on md2.id_doc = mp.id_doc and md2.iddoc >0
    where MS.SGTIN = '%s'
    group by 1)

select
  SGTIN,
  max(ID_DOC_MDLP_DOC) ID_DOC_MDLP_DOC,
  max(OPERATIONDATETIME) OPERATIONDATE,
  max(CUR_NALIC) CUR_NALIC,
  max(id_doc) id_doc,
  max(check_id) check_id,
  max(id_oper) id_oper,
  max(xmldoc_id_doc) xmldoc_id_doc,
  max(xmldoc_check_id) xmldoc_check_id,
  max(date_doc_vn) date_doc_vn 
   from
  CHECK_SGTIN
group by 1""",
    get_cost="""
    select first 1
  cast(A.CENA_OPT_NDS as numeric(16,2)) cena_opt_nds,
  cast(A.CENA_OPT_NDS - A.CENA_OPT as numeric(16,2)) VAT from
  ARTIKUL A
inner join MDLP_GTIN MG on MG.PRIM = A.ID_GTIN
where MG.GTIN = '%s'
order by A.ARTIKUL desc  
    """,
    get_depart="select short_client||'['||id_client||']' from client where automation_depart = 1",
    get_client="select short_client||'['||id_client||']' from client where automation_depart <> 1 order by short_client",
    get_oper="select distinct o.short_oper||'['||o.id_oper||']' from oper o inner join doc d on d.id_oper = o.id_oper order by o.id_oper ",

    ins_upd_sgtin=
    """update or insert into MDLP_SGTIN (SGTIN, DETAIL_LEVEL, ID_GROUP) values ('%s', 0, 7) matching (SGTIN)""",
    upd_mdlp_doc_14="""update mdlp_doc m set m.nextstart = current_time where m.numschema = 14""",
    select_sgtin_info="""
    select
  MS.SGTIN SGTIN,
  case
    when MS.SGTIN_STATUS = 'marked' then 'Ожидает выпуска'
    when MS.SGTIN_STATUS = 'lp_sampled' then 'Отобран образец'
    when MS.SGTIN_STATUS = 'moved_for_disposal' then 'Передан на уничтожение'
    when MS.SGTIN_STATUS = 'disposed' then 'Уничтожен'
    when MS.SGTIN_STATUS = 'out_of_circulation' then 'Выведен из оборота'
    when MS.SGTIN_STATUS = 'transfered_to_owner' then 'Ожидает подтверждения получения собственником'
    when MS.SGTIN_STATUS = 'shipped' then 'Отгружен в РФ'
    when MS.SGTIN_STATUS = 'arrived' then 'Ввезен на территорию РФ'
    when MS.SGTIN_STATUS = 'declared' then 'Задекларирован'
    when MS.SGTIN_STATUS = 'in_circulation' then 'В обороте'
    when MS.SGTIN_STATUS = 'in_realization' then 'Отгружен'
    when MS.SGTIN_STATUS = 'paused_circulation' then 'Оборот приостановлен'
    when MS.SGTIN_STATUS = 'in_sale' then 'Продан в розницу'
    when MS.SGTIN_STATUS = 'in_discount_prescription_sale' then 'Отпущен по льготному рецепту'
    when MS.SGTIN_STATUS = 'in_medical_use' then 'Выдан для медицинского применения'
    when MS.SGTIN_STATUS = 'relabeled' then 'Перемаркирован'
    when MS.SGTIN_STATUS = 'reexported' then 'Реэкспорт'
    when MS.SGTIN_STATUS = 'released_contract' then 'Ожидает передачи собственнику'
    when MS.SGTIN_STATUS = 'released_foreign' then 'для типа эмиссии 3 Ожидает отгрузки в РФ  для типа эмиссии 4 Маркирован в ЗТК'
    when MS.SGTIN_STATUS = 'moved_to_unregistered' then 'Отгружен на незарегистрированное место деятельности'
    when MS.SGTIN_STATUS = 'expired' then 'Срок годности истек'
    when MS.SGTIN_STATUS = 'change_owner' then 'Ожидает подтверждения смены собственника'
    when MS.SGTIN_STATUS = 'change_owner_state_gov' then 'Ожидает подтверждения получения новым владельцем'
    when MS.SGTIN_STATUS = 'confirm_return_paused' then 'Ожидает подтверждения возврата приостановленных лекарственных препаратов'
    when MS.SGTIN_STATUS = 'experiment_outbound' then 'Выведен из оборота (накопленный в рамках эксперимента '
    when MS.SGTIN_STATUS = 'in_partial_medical_use' then 'Частично выдан для медицинского применения'
    when MS.SGTIN_STATUS = 'in_partial_sale' then 'Частично продан в розницу'
    when MS.SGTIN_STATUS = 'in_partial_discount_prescription_sale' then 'Частично отпущен по льготному рецепту'
    when MS.SGTIN_STATUS = 'moved_to_eeu' then 'Отгружен в ЕАЭС'
    when MS.SGTIN_STATUS = 'moved_to_warehouse' then 'Принят на склад из ЗТК'
    when MS.SGTIN_STATUS = 'emission' then 'Эмитирован'
    when MS.SGTIN_STATUS = 'ofd_retail_error' then 'Продан в розницу с отклонением от требований в части выбытия ЛП'
    when MS.SGTIN_STATUS = 'ofd_discount_prescription_error' then 'Отпущен по льготному рецепту (ККТ  с отклонением от требований в части выбытия ЛП'
    when MS.SGTIN_STATUS = 'transferred_for_release' then 'Ожидает подтверждения получения собственником до ввода в оборот'
    when MS.SGTIN_STATUS = 'waiting_for_release' then 'Ожидает ввода в оборот собственником'
    when MS.SGTIN_STATUS = 'emitted' then 'Эмитирован'
    when MS.SGTIN_STATUS = 'marked_not_paid' then 'Ожидает выпуска  не оплачен'
    when MS.SGTIN_STATUS = 'released_foreign_not_paid' then 'для типа эмиссии 3 Ожидает отгрузки в РФ  не оплачен. для типа эмиссии 4 Маркирован в ЗТК  не оплачен'
    when MS.SGTIN_STATUS = 'expired_not_paid' then 'Истек срок ожидания оплаты'
    when MS.SGTIN_STATUS = 'emitted_paid' then 'Эмитирован  готов к использованию'
    when MS.SGTIN_STATUS = 'discount_prescription_error' then 'Отпущен по льготному рецепту с отклонением оттребований в части выбытия ЛП'
    when MS.SGTIN_STATUS = 'med_care_error' then 'Отпущен для медицинского применения с отклонением от требований в части выбытия ЛП'
    when MS.SGTIN_STATUS = 'declared_warehouse' then 'Принят на склад из ЗТК'
    when MS.SGTIN_STATUS = 'transferred_to_customs' then 'Передан для маркировки в ЗТК'
    when MS.SGTIN_STATUS = 'transferred_to_importer' then 'Ожидает подтверждения импортером'
    when MS.SGTIN_STATUS = 'in_arbitration' then 'В арбитраже'
    when MS.SGTIN_STATUS = 'waiting_confirmation' then 'Ожидает подтверждения'
    when MS.SGTIN_STATUS = 'transfer_to_production' then 'Ожидает подтверждения возврата'
    when MS.SGTIN_STATUS = 'waiting_change_property' then 'Ожидает подтверждения корректировки'
    when MS.SGTIN_STATUS = 'eliminated' then 'Не использован'
    when MS.SGTIN_STATUS = 'transferred_to_agent' then 'Отгружен по агентскому договору'
    when MS.SGTIN_STATUS = 'awaiting_return_confirmation' then 'Ожидает подтверждения возврата иностранного ЛП'
    when MS.SGTIN_STATUS = 'dispensing_by_document' then 'Выдан по документам'
    when MS.SGTIN_STATUS = 'in_partial_dispensing_by_document' then 'Частично выдан по документам'
    when MS.SGTIN_STATUS = 'ooc_part_sale' then 'Частичная продажа  остаток списан'
    when MS.SGTIN_STATUS = 'ooc_part_prescription_sale' then 'Частичный отпуск по ЛР  остаток списан'
    when MS.SGTIN_STATUS = 'ooc_part_medical_use' then 'Частичное медицинское применение  остаток списан'
    when MS.SGTIN_STATUS = 'ooc_part_dispensing_by_doc' then 'Частично выдан по документам  остаток списан'
    when MS.SGTIN_STATUS = 'in_partial_ooc' then 'Частично выведен из оборота'
    else MS.SGTIN_STATUS
  end "Статус",
  MS.SYS_ID "Место деятельности",
  MS.STATUS_DATE "Дата последней операции",
  cast(MS.EXPIRATION_DATE as date) "Срок годности",
  MS.BATCH "Серия",
  MS.DATE_LOAD "Дата загрузки информации"
 from
  MDLP_SGTIN MS
where MS.SGTIN = '%s'  
    """,
    get_sgtin_status="""select count(*) from mdlp_sgtin ms where ms.detail_level = 0 and prim > 0 and ms.sgtin <> 
    '' and ms.id_group = 7 """

)
