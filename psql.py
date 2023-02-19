import psycopg2


def reading_my_table_from(filename_of_commands):
    """
    A function to process from file its content.
    :param filename_of_commands: the path where the file with data is stored.
    :type filename_of_commands: str

    :rtype:List(List(str))
    :return: the array of data from file.
    """
    table = []
    with open(filename_of_commands, encoding="utf8") as txt_file:
        for line in txt_file.readlines():
            if line[-1] == '\n':
                line = line[:len(line) - 1]
            index = 0
            row_table = []
            start_quotes = line.find('\'')
            if start_quotes == -1:
                row_table += (line[index:].split(' '))
            else:
                row_table += (line[:start_quotes].split(' '))[:1]
            while start_quotes != -1:
                index = start_quotes
                line = line[index + 1:]
                start_quotes = line.find('\'')
                row_table.append('\'' + line[:start_quotes] + '\'')
                line = line[start_quotes + 1:]
                start_quotes = line.find('\'')
            table.append(row_table)
    return table


class PSQL:
    """
    This is the class required to interact with PostgreSQL.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.conn = None
        self.user = ''
        self.password = ''
        self.dbname = ''
        self.is_authorized = False

    def __del__(self):
        """
        Destructor.
        """
        if self.conn is not None:
            self.conn.close()
        self.conn = None
        self.user = ''
        self.password = ''
        self.dbname = ''
        self.is_authorized = False

    def create_my_table_from(self, filename_of_commands, table_mass):
        """
        A function that creates a  table from a file with SQL code and array of data.
        :param filename_of_commands: the path where the file with SQL code is stored.
        :type filename_of_commands: str
        :param table_mass: the array of data required to fill the table.
        :type table_mass: List(str)
        """
        with open(filename_of_commands, encoding="utf8") as txt_file:
            self.execute_command(''.join([line for line in txt_file.readlines()]))
        command = 'insert into public."regextable" values '
        for row in table_mass[1:]:
            command += '(' + ''.join([col + (', ' if col is not row[-1] else
                                             ('),' if row is not table_mass[-1] else ')')) for col in row])
        self.execute_command(f'{command};')

    def create_my_database(self, name_of_database):
        """
        A function that creates a  table from a file with SQL code and array of data.
        :param name_of_database: the path where the file with SQL code is stored.
        :type name_of_database: str
        """
        self.execute_command(f"CREATE DATABASE \"{name_of_database}\" "
                             "WITH "
                             "OWNER = postgres "
                             "ENCODING = 'UTF8' "
                             "LC_COLLATE = 'Russian_Russia.1251' "
                             "LC_CTYPE = 'Russian_Russia.1251' "
                             "TABLESPACE = pg_default "
                             "CONNECTION LIMIT = -1 "
                             "IS_TEMPLATE = False;")

    def authorization(self, user, password, dbname="postgres"):
        """
        A function enter in PostgreSQL system by login and password.
        :param user: name of user in PostgreSQL.
        :type user: str
        :param password: password of user in PostgreSQL.
        :type password: str
        :param dbname:
        :type dbname: str

        :rtype: bool
        :return: True if authorization was successful, otherwise False.
        """
        try:
            self.conn = psycopg2.connect(
                f"user='{user}' password='{password}' "
                f"host='127.0.0.1' port='5432' dbname='{dbname}'")
            self.conn.autocommit = True
            self.user = user
            self.password = password
            self.dbname = dbname
            self.is_authorized = True
        except psycopg2.DatabaseError:
            return False
        return True

    def execute_command(self, command):
        """
        A function that executes an SQL command and prints the output, if any.
        :param command: SQL string command.
        :type command: str

        :rtype: List(List(str))
        :return: the output array from SQL command.
        """
        with self.conn.cursor() as cur:
            try:
                cur.execute(command)
                output = cur.fetchall()
            except psycopg2.Error:
                self.conn.rollback()
                return []
            return [[str(desc[0]) for desc in cur.description], [str(element) for row in output for element in row]]

    def parsing_by(self, element_string, element_value):
        """
        A function that performs parsing on a specific field in a table.
        :param str element_string: the string with name for parsing.
        :type element_string: str
        :param str element_value: the string to find.
        :type element_value: str

        :rtype: List(List(str))
        :return: the output array by parsing.
        """
        with self.conn.cursor() as cur:
            try:
                cur.execute(f'select * from public."regextable" where {element_string} = \'{element_value}\';')
                output = cur.fetchall()
            except psycopg2.Error:
                self.conn.rollback()
                return []
            return [[str(desc[0]) for desc in cur.description], [str(element) for row in output for element in row]]

    def create_default_database(self):
        """
        A function that creates a default table from a SQL code file and a file with content.
        """
        self.authorization("postgres", "1111")
        db = self.execute_command("select datname from pg_database WHERE datname = 'TGServer'")
        if not len(db[1]):
            self.create_my_database("TGServer")
        self.authorization("postgres", "1111", "TGServer")
        def_table = reading_my_table_from('regex_table/regextable.txt')
        table = self.execute_command('select * from public."regextable";')
        if not table:
            self.create_my_table_from('regex_table/creating_regextable.txt', def_table)
        elif def_table != table:
            self.execute_command('drop table public."regextable"')
            self.create_my_table_from('regex_table/creating_regextable.txt', def_table)
