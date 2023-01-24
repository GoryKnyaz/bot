import psycopg2


def reading_my_table_from(filename_of_commands):
    table = []
    with open(filename_of_commands, encoding="utf8") as txt_file:
        for line in txt_file.readlines():
            if line[-1] == '\n':
                line = line[0:len(line) - 1]
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

    def __init__(self):
        self.conn = None
        self.user = ''
        self.password = ''
        self.dbname = ''
        self.is_authorized = False

    def __del__(self):
        if self.conn is not None:
            self.conn.close()
        self.conn = None
        self.user = ''
        self.password = ''
        self.dbname = ''
        self.is_authorized = False

    def create_my_table_from(self, filename_of_commands, table_mass):
        with open(filename_of_commands, encoding="utf8") as txt_file:
            self.execute_command(''.join([line for line in txt_file.readlines()]))
        command = 'insert into public."regextable" values '
        for row in table_mass[1:]:
            command += '(' + ''.join([col + (', ' if col is not row[-1] else
                                             ('),' if row is not table_mass[-1] else ')')) for col in row])
        self.execute_command(f'{command};')

    def authorization(self, user, password):
        try:
            self.conn = psycopg2.connect(
                f"user='{user}' password='{password}' "
                f"host='127.0.0.1' port='5432' dbname='postgres'")
            self.conn.autocommit = True
            self.user = user
            self.password = password
            self.dbname = "postgres"
            self.is_authorized = True
            return True
        except psycopg2.DatabaseError:
            return False

    def execute_command(self, command):
        with self.conn.cursor() as cur:
            try:
                cur.execute(command)
                output = cur.fetchall()
                return [[str(desc[0]) for desc in cur.description]] + \
                       [[str(element) for row in output for element in row]]
            except psycopg2.Error:
                self.conn.rollback()
                return 'Error'

    def parsing_by(self, element_string, element_value):
        with self.conn.cursor() as cur:
            try:
                cur.execute(f'select * from public."regextable" where {element_string} = {element_value};')
                output = cur.fetchall()
                return [[str(desc[0]) for desc in cur.description]] + \
                       [[str(element) for row in output for element in row]]
            except psycopg2.Error:
                self.conn.rollback()
                return 'Error'

    def create_default_table(self):
        def_table = reading_my_table_from('regex_table/regextable.txt')
        table = self.execute_command('select * from public."regextable";')
        if table == 'Error':
            self.create_my_table_from('regex_table/creating_regextable.txt', def_table)
        elif def_table != table:
            self.execute_command('drop table public."regextable"')
            self.create_my_table_from('regex_table/creating_regextable.txt', def_table)
