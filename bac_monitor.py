import serial
import time
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BACMonitor")


class GDoc:
    def __init__(self, auth_file="auth.json"):
        self.creds_path = auth_file
        self.service = None
        self.sheets = None
        self._connect()

    def _connect(self):
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.creds_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
            self.service = build("sheets", "v4", credentials=creds)
            self.sheets = self.service.spreadsheets()
            logger.info("Connected to Google Sheets API.")
        except Exception as e:
            logger.error("Failed to connect to Google Sheets.", exc_info=e)
            raise e

    @staticmethod
    def a1(sheet_name, cell):
        return f"{sheet_name}!{cell}"

    def write_cell(self, spreadsheet_id, sheet_name, cell, value):
        try:
            self.sheets.values().update(spreadsheetId=spreadsheet_id, range=self.a1(sheet_name, cell),
                                        valueInputOption="RAW", body={"values": [[value]]}).execute()
            logger.info(f"Wrote {value} to {cell}")
            return True
        except Exception as e:
            logger.error("Failed to write cell", exc_info=e)
            return False


class BACMonitor:
    def __init__(self, serial_port: str, baudrate: int, gdoc: GDoc, spreadsheet_id: str, sheet_name: str,
                 status_cell: str = "A1", bac_cell: str = "B1", threshold: float = 0.08, write_interval: float = 3.0):
        self.ser = serial.Serial(serial_port, baudrate, timeout=1)
        self.gdoc = gdoc
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.status_cell = status_cell
        self.bac_cell = bac_cell
        self.threshold = threshold
        self.write_interval = write_interval  # seconds between writes to Google Sheets
        self.last_status = None
        self.last_write_time = 0.0  # track last write to GSheet

    @staticmethod
    def parse_bac(line: str):
        if line.startswith("BAC:"):
            try:
                return float(line.strip().split(":")[1])
            except ValueError:
                logger.warning(f"Failed to parse BAC from line: {line}")
        return None

    def run(self):
        logger.info("Starting BAC monitoring (logging every read, writing every 3 seconds)...")
        while True:
            try:
                line = self.ser.readline().decode("utf-8").strip()
                if not line:
                    continue

                # Log every line read from serial
                logger.info(f"Serial: {line}")

                bac = self.parse_bac(line)
                if bac is not None:
                    status = bac > self.threshold

                    # Only write to Google Sheets if 3 seconds have passed
                    current_time = time.time()
                    if current_time - self.last_write_time >= self.write_interval:
                        self.gdoc.write_cell(self.spreadsheet_id, self.sheet_name,
                                             self.status_cell, "TRUE" if status else "FALSE")
                        self.gdoc.write_cell(self.spreadsheet_id, self.sheet_name,
                                             self.bac_cell, f"{bac:.3f}")
                        self.last_write_time = current_time

                        logger.info(f"Wrote to GSheet: BAC={bac:.3f} -> {status}")

            except KeyboardInterrupt:
                logger.info("Stopping BAC monitoring.")
                break

            except Exception as e:
                logger.error("Error in monitoring loop", exc_info=e)
                time.sleep(1)


if __name__ == "__main__":
    SERIAL_PORT = "/dev/cu.usbserial-A10LUX7S"
    BAUDRATE = 9600
    SPREADSHEET_ID = "1DssTz5DSLgyxIs7y6BJwHJHkm81YY98XnBYnmNwhPkw"
    SHEET_NAME = "S.P.I.N.S."
    STATUS_CELL = "A1"
    BAC_CELL = "B1"

    gdoc = GDoc(auth_file="auth.json")
    monitor = BACMonitor(SERIAL_PORT, BAUDRATE, gdoc, SPREADSHEET_ID, SHEET_NAME,
                         STATUS_CELL, BAC_CELL)
    monitor.run()
