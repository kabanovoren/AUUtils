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


"""
Скрипт для Ефармы



  select g.NAME,
  cgg.NAME,
  p.NAME,
  c.NAME,
  b.CODE,
  gg.NAME 
  from goods g 
  inner join GOODS_2_GROUP  g2 on g2.ID_GOODS = g.ID_GOODS 
  inner join GOODS_GROUP gg on gg.ID_GOODS_GROUP = g2.ID_GOODS_GROUP 
  inner join BAR_CODE b on b.ID_GOODS = g.ID_GOODS 
  inner join PRODUCER p on p.ID_PRODUCER = g.ID_PRODUCER 
  inner join COUNTRY c on c.ID_COUNTRY = p.ID_COUNTRY
  left join CATEGORICAL_GROUPS_2_GOODS cg on cg.ID_GOODS_GLOBAL = g.ID_GOODS_GLOBAL 
  left join CATEGORICAL_GROUPS cgg on cgg.ID_CATEGORICAL_GROUPS_GLOBAL   = cg.ID_CATEGORICAL_GROUPS_GLOBAL  

  where gg.ID_PARENT_GROUP is null
  order by g.NAME 

"""

"""
Выполнение и процедура поиска значения в MS SQL


EXEC SearchAllTablesText 'Изделия медицинского назначения'
GO


CREATE PROC SearchAllTablesText
(
	@SearchStr nvarchar(100)
)
AS
BEGIN
	CREATE TABLE #Results (ColumnName nvarchar(370), ColumnValue nvarchar(3630))

	SET NOCOUNT ON

	DECLARE @TableName nvarchar(256), @ColumnName nvarchar(128), @SearchStr2 nvarchar(110)
	SET  @TableName = ''
	SET @SearchStr2 = QUOTENAME('%' + @SearchStr + '%','''')

	WHILE @TableName IS NOT NULL
	BEGIN
		SET @ColumnName = ''
		SET @TableName = 
		(
			SELECT MIN(QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME))
			FROM 	INFORMATION_SCHEMA.TABLES
			WHERE 		TABLE_TYPE = 'BASE TABLE'
				AND	QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME) > @TableName
				AND	OBJECTPROPERTY(
						OBJECT_ID(
							QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME)
							 ), 'IsMSShipped'
						       ) = 0
		)

		WHILE (@TableName IS NOT NULL) AND (@ColumnName IS NOT NULL)
		BEGIN
			SET @ColumnName =
			(
				SELECT MIN(QUOTENAME(COLUMN_NAME))
				FROM 	INFORMATION_SCHEMA.COLUMNS
				WHERE 		TABLE_SCHEMA	= PARSENAME(@TableName, 2)
					AND	TABLE_NAME	= PARSENAME(@TableName, 1)
					AND	DATA_TYPE IN ('char', 'varchar', 'nchar', 'nvarchar')
					AND	QUOTENAME(COLUMN_NAME) > @ColumnName
			)
	
			IF @ColumnName IS NOT NULL
			BEGIN
				INSERT INTO #Results
				EXEC
				(
					'SELECT ''' + @TableName + '.' + @ColumnName + ''', LEFT(' + @ColumnName + ', 3630) 
					FROM ' + @TableName + ' (NOLOCK) ' +
					' WHERE ' + @ColumnName + ' LIKE ' + @SearchStr2
				)
			END
		END	
	END

	SELECT ColumnName, ColumnValue FROM #Results
END
"""