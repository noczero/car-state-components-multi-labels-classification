import csv
import os


class ImageToTextAnnotationsBuilder:
    def __init__(self,
                 source_path='datasets/annotations.csv',
                 output_path='datasets/image_to_text_annotations.csv'
                 ):
        """
        Initializes the ImageToTextAnnotationsBuilder.

        Args:
            source_path (str): Path to the source CSV file.
            output_path (str): Path where the processed CSV file will be saved.
        """
        self.csv_annotations_source_path = source_path
        self.output_csv_path = output_path
        self.output_header = ['filename', 'text']

    def _extract_and_process_data(self):
        """
        Reads the source CSV, extracts relevant data, and processes it.

        Returns:
            list: A list of dictionaries, where each dictionary has 'filename' and 'text' keys.
                  Returns an empty list if the source file is not found, crucial columns are
                  missing in the header, or another error occurs.
        """
        processed_data = []
        try:
            with open(self.csv_annotations_source_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for i, row in enumerate(reader):
                    print(row)
                    filename = row.get('filename')

                    front_left_label = 'open' if row.get('front_left') == '1' else 'closed'
                    front_right_label = 'open' if row.get('front_right') == '1' else 'closed'
                    rear_left_label = 'open' if row.get('rear_left') == '1' else 'closed'
                    rear_right_label = 'open' if row.get('rear_right') == '1' else 'closed'
                    hood_label = 'open' if row.get('hood') == '1' else 'closed'

                    text_content = f"""
                            The front left door is {front_left_label}, 
                            the front right door is {front_right_label}, 
                            the rear left door is {rear_left_label}, 
                            the rear right door is {rear_right_label}, 
                            and the hood is {hood_label}.
                    """

                    processed_data.append({'filename': filename.strip(), 'text': text_content.strip()})

        except FileNotFoundError:
            print(f"Error: Source CSV file not found at {self.csv_annotations_source_path}")
            return []
        except Exception as e:
            print(f"An error occurred while reading or processing the source CSV: {e}")
            return []

        return processed_data

    def _write_processed_csv(self, data_to_write):
        """
        Writes the processed data to the output CSV file.

        Args:
            data_to_write (list): A list of dictionaries to write to the CSV.
                                  Each dictionary should have 'filename' and 'text' keys.
        """
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(self.output_csv_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")

            with open(self.output_csv_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.output_header)
                writer.writeheader()
                writer.writerows(data_to_write)
            print(f"Successfully wrote processed data to {self.output_csv_path}")
        except IOError as e:
            print(
                f"Error: Could not write to output CSV file at {self.output_csv_path}. Check permissions or path. Details: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during CSV writing: {e}")

    def build(self):
        """
        Orchestrates the reading of the source CSV, processing the data,
        and writing it to a new CSV file.
        """
        print(f"Starting annotation processing...")
        print(f"Source CSV: {self.csv_annotations_source_path}")
        print(f"Output CSV: {self.output_csv_path}")

        processed_data = self._extract_and_process_data()
        self._write_processed_csv(processed_data)



if __name__ == '__main__':
    image_to_text_annotations_builder = ImageToTextAnnotationsBuilder()
    image_to_text_annotations_builder.build()