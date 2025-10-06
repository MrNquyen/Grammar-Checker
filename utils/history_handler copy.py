import os
import sqlite3 
from icecream import ic

class ConversationHistory:
    def __init__(self, name="history", save_dir="save"):
        self.name = name
        self.save_dir = save_dir
        self.create_connection()

    #-- BUILD
    def create_connection(self):
        history_db_path = os.path.join(self.save_dir, "database", f"{self.name}.db")
        self.connection = sqlite3.connect(history_db_path, check_same_thread=False, timeout=10)
        self.connection.execute("PRAGMA journal_mode=WAL;")
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        # -- Conversation table
        CREATE_CONVERSATION_TABLE_QUERY = """
            CREATE TABLE IF NOT EXISTS CONVERSATION (
                ConversationID TEXT PRIMARY KEY,
                dateCreate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                name TEXT
            );
        """
        self.cursor.execute(CREATE_CONVERSATION_TABLE_QUERY)
        self.connection.commit()

        # -- History table
        CREATE_HISTORY_TABLE_QUERY = """
            CREATE TABLE IF NOT EXISTS HISTORY (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ConversationID TEXT NOT NULL,
                systemMessage TEXT,
                userMessage TEXT,
                FOREIGN KEY (ConversationID) REFERENCES CONVERSATION(ConversationID) ON DELETE CASCADE
            );
        """
        self.cursor.execute(CREATE_HISTORY_TABLE_QUERY)
        self.connection.commit()
        
        # -- File Controller table
        CREATE_FILE_MANAGER_QUERY = """
            CREATE TABLE IF NOT EXISTS FILE_MANAGER (
                FileName TEXT PRIMARY KEY NOT NULL,
                FilePath TEXT NOT NULL,
                type TEXT
            );
        """
        self.cursor.execute(CREATE_FILE_MANAGER_QUERY)
        self.connection.commit()
        
        # -- File Controller table
        CREATE_SUBSET_MANAGER_QUERY = """
            CREATE TABLE IF NOT EXISTS SUBSET_MANAGER (
                FileName TEXT PRIMARY KEY NOT NULL,
                FilePath TEXT NOT NULL,
                type TEXT
            );
        """
        self.cursor.execute(CREATE_FILE_MANAGER_QUERY)
        self.connection.commit()


    # ADD AND GET
    def get_table_len(self, table_name):
        GET_LEN_QUERY = f"""
            SELECT COUNT(*)
            FROM {table_name}
        """
        return self.cursor.execute(GET_LEN_QUERY).fetchone()


    def add_conversation(self, conversation_id, user_message, system_message):
        id = self.get_table_len(table_name="HISTORY")[0] + 1
        INSERT_QUERY = f"""
            INSERT INTO HISTORY (ID, ConversationID, systemMessage, userMessage)
            VALUES ({id}, '{conversation_id}', '{system_message}', '{user_message}');
        """
        self.cursor.execute(INSERT_QUERY)
        self.connection.commit()


    def add_file(self, file_name, file_path, file_type):
        ADD_FILE_QUERY = f"""
            INSERT INTO FILE_MANAGER (FileName, FilePath, type)
            VALUES ('{file_name}', '{file_path}', '{file_type}');
        """

        UPDATE_FILE_QUERY = f"""
            UPDATE FILE_MANAGER 
            SET FilePath = '{file_path}' 
            WHERE FileName = '{file_name}'"
        """

        GET_FILE_QUERY = f"""
            SELECT FileName, FilePath, type
            FROM FILE_MANAGER
            WHERE FileName = '{file_name}'
        """

        row = self.cursor.execute(GET_FILE_QUERY).fetchone()
        self.connection.commit()

        if row:
            if row[1] != file_path:
                self.cursor.execute(UPDATE_FILE_QUERY)
        else:
            self.cursor.execute(ADD_FILE_QUERY)
        self.connection.commit()


    def create_new_conversation(self, conversation_id, timestamp, conversation_name):
        CREATE_CONVERSATION_QUERY = f"""
            INSERT INTO CONVERSATION (ConversationID, dateCreate, name)
            VALUES ('{conversation_id}', '{timestamp}', '{conversation_name}');
        """
        self.cursor.execute(CREATE_CONVERSATION_QUERY)
        self.connection.commit()

    
    def delete_conversation(self, conversation_id):
        DELETE_CONVERSATION_QUERY = f"""
            DELETE FROM CONVERSATION
            WHERE ConversationID = '{conversation_id}'
        """
        self.cursor.execute(DELETE_CONVERSATION_QUERY)
        self.connection.commit()

        DELETE_HISTORY_QUERY = f"""
            DELETE FROM HISTORY
            WHERE ConversationID = '{conversation_id}'
        """
        self.cursor.execute(DELETE_HISTORY_QUERY)
        self.connection.commit()


    def rename_conversation(self, conversation_id, new_name):
        RENAME_CONVERSATION_QUERY = F"""
            UPDATE CONVERSATION
            SET name = '{new_name}'
            WHERE ConversationID = '{conversation_id}'
        """
        self.cursor.execute(RENAME_CONVERSATION_QUERY)
        self.connection.commit()


    def get_conversation_history(self, conversation_id):
        GET_HISTORY_QUERY = f"""
            SELECT systemMessage, userMessage
            FROM HISTORY AS HIS 
            WHERE HIS.ConversationID = '{conversation_id}'
            ORDER BY ID ASC
        """
        rows = self.cursor.execute(GET_HISTORY_QUERY).fetchall()
        return rows


    def get_all_existing_conversation_info(self):
        GET_ALL_CONVERSATION_IDS = """                                      
            SELECT DISTINCT ConversationID, dateCreate, name
            FROM CONVERSATION
        """
        conversation_ids = self.cursor.execute(GET_ALL_CONVERSATION_IDS).fetchall()
        return conversation_ids


    def get_all_existing_files_info(self):
        GET_ALL_EXISTING_FILE_INFO = """                                      
            SELECT DISTINCT FileName, FilePath, type
            FROM FILE_MANAGER
        """
        existing_files_info = self.cursor.execute(GET_ALL_EXISTING_FILE_INFO).fetchall()
        return existing_files_info


    def get_conversation_name(self, conversation_id):
        GET_ALL_CONVERSATION_IDS = f"""                                      
            SELECT name
            FROM CONVERSATION
            WHERE ConversationID = '{conversation_id}'
        """
        conversation_ids = self.cursor.execute(GET_ALL_CONVERSATION_IDS).fetchone()
        return conversation_ids[0]

        


