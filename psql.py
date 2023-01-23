import psycopg2


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

    def connect_database(self, dbname):
        try:
            new_conn = psycopg2.connect(
                f"user='{self.user}' password='{self.password}' host='127.0.0.1' port='5432' "
                f"dbname='{dbname}'")
            self.conn.close()
            self.conn = new_conn
            self.conn.autocommit = True
            self.dbname = dbname
            return True
        except psycopg2.DatabaseError:
            return False

    def execute_command(self, command):
        with self.conn.cursor() as cur:
            try:
                cur.execute(command)
                output = cur.fetchall()
                return (''.join([str(desc[0]) for desc in cur.description]) +
                        ''.join([str(element) for row in output for element in row]))
            except psycopg2.DataError:
                self.conn.rollback()
                return 'Wrong command'

    def create_default_table(self):
        pass
