import os
import sqlite3, hashlib
from icecream import ic
from utils.excel_utils import convert_coor_to_cell_string
import json

class HistoryHandler:
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
        # -- File Information
        CREATE_FILE_INFORMATION_QUERY = """
            CREATE TABLE IF NOT EXISTS FILE (
                fileId INT PRIMARY KEY,
                localPath TEXT,
                localPathHash TEXT,
                onlineUrl TEXT,
                sheetnames TEXT,
                iframe TEXT,
                type TEXT
            );
        """
        self.cursor.execute(CREATE_FILE_INFORMATION_QUERY)
        self.connection.commit()

        # -- Error Correction History 
        CREATE_HISTORY_CORRECTION_QUERY = """
            CREATE TABLE IF NOT EXISTS ERROR_CORRECTION (
                fileId INT,
                sheetName TEXT,
                rowIndex INT,
                colIndex INT,
                oldValue TEXT,
                newValue TEXT,

                PRIMARY KEY (fileId, sheetName, rowIndex, colIndex),
                FOREIGN KEY (fileId) REFERENCES FILE(fileId) ON DELETE CASCADE
            );
        """
        self.cursor.execute(CREATE_HISTORY_CORRECTION_QUERY)
        self.connection.commit()


    # ADD AND GET
    def get_table_len(self, table_name):
        GET_LEN_QUERY = f"""
            SELECT COUNT(*)
            FROM {table_name}
        """
        return self.cursor.execute(GET_LEN_QUERY).fetchone()[0]


    # FILE INFORMATION
    def get_all_current_files(self):
        GET_ALL_CURRENT_LOCAL_FILES_QUERY = """
            SELECT localPath
            FROM FILE
        """
        all_files = self.cursor.execute(GET_ALL_CURRENT_LOCAL_FILES_QUERY).fetchall()
        all_files = [file_tuple[0] for file_tuple in all_files]
        return all_files


    def get_file_id(self, local_path):
        local_path_hash = make_hash(local_path)
        GET_FILE_ID_QUERY = f"""
            SELECT fileID
            FROM FILE
            WHERE localPathHash = '{local_path_hash}'
        """
        file_id = self.cursor.execute(GET_FILE_ID_QUERY).fetchone()
        if file_id:
            file_id = file_id[0]
        return file_id


    def get_file_information(self, local_path):
        local_path_hash = make_hash(local_path)
        GET_FILE_INFORMATION = f"""
            SELECT fileId, localPath, localPathHash, onlineUrl, sheetnames, iframe, type
            FROM FILE
            WHERE localPathHash = '{local_path_hash}'
        """
        row = self.cursor.execute(GET_FILE_INFORMATION).fetchone()
        file_id, local_path, local_path_hash, online_url, sheetnames, iframe, file_type = row
        sheetnames = json.loads(sheetnames)
        return {
            "file_id": file_id,
            "local_path": local_path,
            "local_path_hash": local_path_hash,
            "online_url": online_url,
            "sheetnames": sheetnames,
            "iframe": iframe,
            "file_type": file_type,
        }



    def get_sheetnames(self, local_path):
        local_path_hash = make_hash(local_path)
        GET_SHEETNAMES = f"""
            SELECT sheetnames 
            FROM FILE
            WHERE localPathHash = '{local_path_hash}'
        """
        row = self.cursor.execute(GET_SHEETNAMES).fetchone()
        sheetnames = json.loads(row[0])
        return sheetnames


    def add_file_information(self, local_path: str, online_url: str, iframe: str, sheetnames: list):
        file_type = local_path.split(".")[-1]
        local_path_hash = make_hash(local_path)

        #~ Clear the exist record if exists
        self.delete_file_information(local_path)
        #~ Insert new to database
        table_length = self.get_table_len(table_name="FILE")
        ic(f"Add one file {table_length + 1}")
        ADD_FILE_INFORMATION_QUERY = """
            INSERT INTO FILE (fileId, localPath, localPathHash, onlineUrl, sheetnames, iframe, type)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """

        self.cursor.execute(
            ADD_FILE_INFORMATION_QUERY,
            (
                table_length + 1,
                local_path,
                local_path_hash,
                online_url,
                json.dumps(sheetnames),  # safe, no quote issues
                iframe,
                file_type
            )
        )
        self.connection.commit()

    
    def delete_file_information(self, local_path):
        file_id = self.get_file_id(local_path)
        ic(f"Delete file {file_id}")
        DELETE_FILE_INFORMATION_QUERY = f"""
            DELETE FROM FILE
            WHERE fileID = '{file_id}'
        """
        self.cursor.execute(DELETE_FILE_INFORMATION_QUERY)
        self.connection.commit()

        self.delete_correction_history(file_id)


    # ERROR CORRECTION HISTORY
    def add_correction_history(self, file_id, sheet_name, coordinates, old_value, new_value):
        row_index, col_index = coordinates
        ic(f"Add history file_id: {file_id} - sheet_name: {sheet_name} - coordinates: {coordinates}")

        # Add new
        ADD_CORRECTION_HISTORY_QUERY = """
            INSERT INTO ERROR_CORRECTION
            (fileId, sheetName, rowIndex, colIndex, oldValue, newValue)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        self.cursor.execute(
            ADD_CORRECTION_HISTORY_QUERY,
            (file_id, sheet_name, row_index, col_index, old_value, new_value)
        )
        self.connection.commit()


    def delete_correction_history(self, file_id):
        DELETE_CORRECTION_HISTORY_QUERY = f"""
            DELETE FROM ERROR_CORRECTION
            WHERE fileID = '{file_id}'
        """
        self.cursor.execute(DELETE_CORRECTION_HISTORY_QUERY)
        self.connection.commit() 


    def get_correction_history_info(self, local_path, sheet_name):
        local_path_hash = make_hash(local_path)
        GET_CORRECTION_HISTORY_QUERY = f"""
            SELECT oldValue, newValue, rowIndex, colIndex
            FROM FILE, ERROR_CORRECTION
            WHERE FILE.localPathHash = '{local_path_hash}' AND ERROR_CORRECTION.sheetName = '{sheet_name}'
        """

        rows = self.cursor.execute(GET_CORRECTION_HISTORY_QUERY).fetchall()
        if rows:
            return [
                {
                    "old_value": row[0],
                    "new_value": row[1],
                    "coordinates": (row[2], row[3]),
                    "cell": convert_coor_to_cell_string(row[2], row[3])
                }
                for row in rows
            ]
        return []


# UTILS
def make_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


