import Database as d

def main():
    con = d.Database()
    print(con.execute("select * from oper").fetchall())
    con.disconnect()
    # con.disconnect()


if __name__ == '__main__':
    main()