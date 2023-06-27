# coding=utf8
# Copyright (c) 2021 GVF
# Author: Chenglin (Niko) Lu
# Version: V2.0.0
"""GDB Package

GDB Package is a bridge that handles database connections.

Update History:
    V1.0.0: Comes with working GMySQLConnector and GLog
    V1.1.0: Reopen sql_data param.
    V2.0.0: Removal of quite mode, GLog, now collects errors as list for better accuracy.

    APIs:

    class GMySQLConnector():

        constructor(dict CONFIG)          -Init a connector with CONFIG

        ---ACCESSORS---
        dict example_config()             -Get a example CONFIG
        dict get_config()                 -Get CONFIG
        void set_config()                 -Set CONFIG

        ---AUTO MODE---
        dict query(String sql_line, String sql_data=Null)                   - Query DB
        dict write(String sql_line, String sql_data=Null)                   - Write DB
        dict write_multiple_times(String sql_line, String list_of_sql_data) - Write DB Multiple Values
        dict write_transaction(String list_of_sql_line)                     - Write DB as Transaction

        ---MANUAL MODE---
        Boolean start()                   -Start Connection
        Boolean execute()                 -Execute SQL statements
        Boolean fetch()                   -Fetch Query Results
        Boolean commit()                  -Commit changes to database
        Boolean rollback()                -Discard changes
        Boolean close()                   -Close Connection
"""
import traceback
import mysql.connector


class GMySQLConnector(object):
    """ Tutorial

    # Init
    conn = GMySQLConnector(connection_config={
        'user': 'DB_USERNAME',
        'password': 'DB_PASSWORD',
        'host': 'DB_IP',
        'database': 'DB_NAME'
    })

    # Query
    query_result = conn.query(sql_line='SELECT * FROM my_table WHERE id=1 AND name="Niko"')
    query_result = conn.query(sql_line='SELECT * FROM my_table WHERE id=%s AND name=%s',
                              sql_data=[1, "Niko"])

    # Write
    query_result = conn.write(sql_line='INSERT INTO my_table(id, name) VALUES (Null, "Niko")')
    query_result = conn.write(sql_line='INSERT INTO my_table(id, name) VALUES (%s, %s)',
                              sql_data=[None, "Niko"])

    # write_multiple_times
    query_result = conn.write_multiple_times(sql_line='INSERT INTO my_table(id, name) VALUES (%s, %s)',
                                             list_of_sql_data=[[None, "Niko"],
                                                               [None, "Charlie"],
                                                               [None, "Sam"]])

    # write_transaction
    query_result = conn.write_transaction(list_of_sql_lines=[
        ['INSERT INTO my_table(id, name) VALUES (%s, %s)', [None, "Niko"]],
        ['INSERT INTO credit(id, name) VALUES (%s, %s)', [None, "Niko"]],
    ])
    """

    @staticmethod
    def example_config():
        """This function returns a example/template CONFIG

        Returns:
            A template config dictionary

        """
        return {
            'user': None,
            'password': None,
            'host': None,
            'database': None,
        }

    def __init__(self, connection_config=None):
        """This is the constructor that you will use.

        Args:
            dict connection_config: the config, you can require from example_config()
        """

        self.config = None
        self.conn = None
        self.cursor = None
        self.quiet_mode = False
        self.set_config(connection_config)

    def get_config(self):
        """Regular Getter

        Returns: dict CONFIG

        """
        return self.config

    def set_config(self, config):
        """Regular Setter

        Args:
            dict config: you can require one from example_config()

        """
        if config:
            self.config = config
        else:
            self.config = self.example_config()

    def query(self, sql_line, sql_data=None):
        """Feed in the READ-ONLY SQL Line, SQL Data Hand back the result. Easy.

        Args:
            str sql_line: where you usually put the sql query line

        Returns:
            Dict = {
                "result": List<dict>,
                "errors": List<str>
            }
        """
        connection = None
        cursor = None
        result = None
        errors = []

        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_line, sql_data)
            result = cursor.fetchall()
        except:
            errors.append(traceback.format_exc())
        finally:
            try:
                cursor.close()
            except Exception as e:
                errors.append(traceback.format_exc())
            try:
                connection.close()
            except Exception as e:
                errors.append(traceback.format_exc())

        return {
            "result": result,
            "errors": errors
        }

    def write(self, sql_line, sql_data=None):
        """Feed in one WRITE-ONLY SQL line, boom, easy

        Args:
            str sql_line: One SQL line that WRITE into database
            list sql_data: Data adapts to sql_line

        Returns:
            Dict = {
                "result": List<dict>,
                "errors": List<str>
            }
        """
        connection = None
        cursor = None
        result = None
        errors = []

        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_line, sql_data)
            connection.commit()
            result = True
        except:
            errors.append(traceback.format_exc())
        finally:
            try:
                cursor.close()
            except Exception as e:
                errors.append(traceback.format_exc())
            try:
                connection.close()
            except Exception as e:
                errors.append(traceback.format_exc())

        return {
            "result": result,
            "errors": errors
        }

    def write_multiple_times(self, sql_line, list_of_sql_data):
        """Feed in one WRITE-ONLY SQL line, and a list of sql_data

        Args:
            str sql_line: One SQL line that WRITE into database
            list sql_data: Data adapts to sql_line

        Returns:
            Dict = {
                "result": List<dict>,
                "errors": List<str>
            }
        """
        connection = None
        cursor = None
        result = None
        errors = []

        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor(dictionary=True)
            cursor.executemany(sql_line, list_of_sql_data)
            connection.commit()
            result = True
        except:
            errors.append(traceback.format_exc())
        finally:
            try:
                cursor.close()
            except Exception as e:
                errors.append(traceback.format_exc())
            try:
                connection.close()
            except Exception as e:
                errors.append(traceback.format_exc())

        return {
            "result": result,
            "errors": errors
        }

    def write_transaction(self, list_of_sql_lines):
        """Feed in a list of WRITE-ONLY SQL lines, On Error Auto Rollback

        Args:
            list list_of_sql_lines: SQL lines that WRITE into database
            list list_of_sql_data: SQL Data that adapts to sql_lines

        Returns:
            Dict = {
                "result": List<dict>,
                "errors": List<str>
            }
        """
        connection = None
        cursor = None
        result = None
        errors = []

        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor(dictionary=True)
            for sql_execution_obj in list_of_sql_lines:
                if isinstance(sql_execution_obj, str):
                    sql_line = sql_execution_obj
                    sql_data = None
                elif isinstance(sql_execution_obj, list) and len(sql_execution_obj) == 2:
                    sql_line = sql_execution_obj[0]
                    sql_data = sql_execution_obj[1]
                else:
                    raise ValueError('SQL line must a String or [sql_line, sql_data]')
                cursor.execute(sql_line, sql_data)
            connection.commit()
            result = True
        except:
            errors.append(traceback.format_exc())
            try:
                connection.rollback()
            except Exception as e:
                errors.append(traceback.format_exc())
        finally:
            try:
                cursor.close()
            except Exception as e:
                errors.append(traceback.format_exc())
            try:
                connection.close()
            except Exception as e:
                errors.append(traceback.format_exc())

        return {
            "result": result,
            "errors": errors
        }

    def start(self):
        """Manually Starting the Connection

        You shouldn't be using this unless you really know what you are doing.

        Returns:
            Boolean: True if success, False if any of them failed.

        """
        return_value = False

        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor(dictionary=True)
            return_value = True
        except mysql.connector.Error as e:
            self.error_display("GDB.MySQL.start => SQL ERROR\n{}".format(e))
        except Exception as e:
            self.error_display("GDB.MySQL.start => PYTHON ERROR\n{}".format(e))

        return return_value

    def execute(self, sql_line, sql_data=None):
        """Manually Executing SQL

        You shouldn't be using this unless you really know what you are doing.

        Args:
            sql_line: str SQL line or SQL Template
            sql_data: list/dict that holds data

        Returns:
            boolean: True if success, False if failed

        """
        return_value = False

        try:
            self.cursor.execute(sql_line, sql_data)
            return_value = True
        except mysql.connector.Error as e:
            self.error_display("GDB.MySQL.execute => SQL ERROR\n{}".format(e))
        except Exception as e:
            self.error_display("GDB.MySQL.execute => PYTHON ERROR\n{}".format(e))

        return return_value

    def fetch(self):
        """Manually Fetching Query Result

        You shouldn't be using this unless you really know what you are doing.

        Returns:
            dict: if success
            False: if failed

        """
        return_value = False

        try:
            return_value = self.cursor.fetchall()
        except mysql.connector.Error as e:
            self.error_display("GDB.MySQL.fetch => SQL ERROR\n{}".format(e))
        except Exception as e:
            self.error_display("GDB.MySQL.fetch => PYTHON ERROR\n{}".format(e))

        return return_value

    def commit(self):
        """Manually Commit Changes to Database

        You shouldn't be using this unless you really know what you are doing.

        Returns:
            boolean: True if success, False if failed

        """
        return_value = False

        try:
            self.conn.commit()
            return_value = True
        except mysql.connector.Error as e:
            self.error_display("GDB.MySQL.commit => SQL ERROR\n{}".format(e))
        except Exception as e:
            self.error_display("GDB.MySQL.commit => PYTHON ERROR\n{}".format(e))

        return return_value

    def rollback(self):
        """Manually Rollback

        You shouldn't be using this unless you really know what you are doing.

        Returns:
            boolean: True if success, False if failed

        """
        return_value = False

        try:
            self.conn.rollback()
            return_value = True
        except mysql.connector.Error as e:
            self.error_display("GDB.MySQL.rollback => SQL ERROR\n{}".format(e))
        except Exception as e:
            self.error_display("GDB.MySQL.rollback => PYTHON ERROR\n{}".format(e))

        return return_value

    def close(self):
        """Manually Closing the connection

        You shouldn't be using this unless you really know what you are doing.

        Returns:
            boolean: True if success, False if failed

        """
        return_value = False

        try:
            if self.conn:
                self.conn.close()
                self.conn = None
            self.cursor = None
            return_value = True
        except mysql.connector.Error as e:
            self.error_display("GDB.MySQL.rollback => SQL ERROR\n{}".format(e))
        except Exception as e:
            self.error_display("GDB.MySQL.rollback => PYTHON ERROR\n{}".format(e))

        return return_value
