# core/excel_exporter.py

import os
import logging
from typing import List, Dict, Any
import pandas as pd
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)

class ExcelExporter:
    """
    Handles the conversion of a list of dictionaries into a clean Excel file.
    """

    @staticmethod
    def save_to_excel(data: List[Dict[str, Any]], filepath: str) -> bool:
        """
        Saves the extracted data to an Excel file.
        
        :param data: List of dictionaries (e.g., [{"invoice": "123", "amount": 100}, ...])
        :param filepath: The destination path for the .xlsx file.
        :return: True if successful, False otherwise.
        """
        if not data:
            logger.warning("No data to export.")
            return False

        try:
            # 1. Convert list of dicts to DataFrame.
            # Pandas automatically aligns keys and fills missing values with NaN.
            df = pd.DataFrame(data)

            # 2. Ensure the directory exists
            output_dir = os.path.dirname(os.path.abspath(filepath))
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 3. Export to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Extracted Data')
                
                # 4. Auto-adjust column widths for better UX
                worksheet = writer.sheets['Extracted Data']
                for i, col in enumerate(df.columns):
                    col_name_len = len(str(col))
                    
                    # Безопасный подсчет длины: принудительно делаем строку из любого значения
                    try:
                        max_val_len = df[col].apply(lambda x: len(str(x))).max()
                        if pd.isna(max_val_len): # Если колонка пустая
                            max_val_len = 0
                    except Exception:
                        max_val_len = 0
                        
                    column_len = max(col_name_len, int(max_val_len)) + 2
                    worksheet.column_dimensions[get_column_letter(i + 1)].width = column_len

            logger.info(f"Successfully saved {len(data)} rows to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save Excel file: {e}")
            return False


# ==========================================
# TEST BLOCK (Run this file directly to test)
# ==========================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("--- Testing Excel Exporter ---")
    
    mock_data = [
        {
            "invoice_number": "INV-001",
            "date": "2023-10-25",
            "sender": "Acme Corp",
            "amount": 5450.00,
            "tax": 450.00
        },
        {
            "invoice_number": "INV-002",
            "date": "2023-10-26",
            "sender": "Globex Inc",
            "amount": 1200.50,
        },
        {
            "invoice_number": "INV-003",
            "date": "2023-10-27",
            "sender": "Initech",
            "tax": 100.00
        }
    ]
    
    output_path = "test_invoices_report.xlsx"
    
    success = ExcelExporter.save_to_excel(mock_data, output_path)
    
    if success:
        print(f"\n✅ Success! Open the file to verify: {os.path.abspath(output_path)}")
    else:
        print("\n❌ Failed to export data.")