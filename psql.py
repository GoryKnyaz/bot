import psycopg2


def reading_my_table_from(filename_of_commands):
    """
    A function to process from file its content.
    :param filename_of_commands: the path where the file with data is stored.
    :return List(List(str)): the array of data from file.
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
        :param str filename_of_commands: the path where the file with SQL code is stored.
        :param List(str) table_mass: the array of data required to fill the table.
        """
        with open(filename_of_commands, encoding="utf8") as txt_file:
            self.execute_command(''.join([line for line in txt_file.readlines()]))
        command = 'insert into public."regextable" values '
        for row in table_mass[1:]:
            command += '(' + ''.join([col + (', ' if col is not row[-1] else
                                             ('),' if row is not table_mass[-1] else ')')) for col in row])
        self.execute_command(f'{command};')

    def authorization(self, user, password):
        """
        A function enter in PostgreSQL system by login and password.
        :param str user: name of user in PostgreSQL.
        :param str password: password of user in PostgreSQL.
        :return bool: True if authorization was successful, otherwise False.
        """
        try:
            self.conn = psycopg2.connect(
                f"user='{user}' password='{password}' "
                f"host='127.0.0.1' port='5432' dbname='postgres'")
            self.conn.autocommit = True
            self.user = user
            self.password = password
            self.dbname = "postgres"
            self.is_authorized = True
        except psycopg2.DatabaseError:
            return False
        return True

    def execute_command(self, command):
        """
        A function that executes an SQL command and prints the output, if any.
        :param str command: SQL string command.
        :return List(List(str)): the output array from SQL command.
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
        :param str element_value: the string to find.
        :return List(List(str)): the output array by parsing.
        """
        with self.conn.cursor() as cur:
            try:
                cur.execute(f'select * from public."regextable" where {element_string} = \'{element_value}\';')
                output = cur.fetchall()
            except psycopg2.Error:
                self.conn.rollback()
                return []
            return [[str(desc[0]) for desc in cur.description], [str(element) for row in output for element in row]]

    def create_default_table(self):
        """
        A function that creates a default table from a SQL code file and a file with content.
        """
        def_table = reading_my_table_from('regex_table/regextable.txt')
        table = self.execute_command('select * from public."regextable";')
        if not table:
            self.create_my_table_from('regex_table/creating_regextable.txt', def_table)
        elif def_table != table:
            self.execute_command('drop table public."regextable"')
            self.create_my_table_from('regex_table/creating_regextable.txt', def_table)
