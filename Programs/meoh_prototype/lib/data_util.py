import csv
import os


class DataWriter:

    def __init__(self, filename, fieldnames):
        self.filename = filename
        self.fieldnames = fieldnames
        self.create_directory()
        self.precision = {}

        # Write header if file does not exist
        with open(self.filename, 'a') as f:
            if os.stat(self.filename).st_size == 0:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def set_precision(self, field, precision):
        self.precision[field] = precision

    def write_data(self, data):
        dataw = data.copy()
        with open(self.filename, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            for field in self.precision:
                dataw[field] = self.precision[field].format(dataw[field])
            writer.writerow(dataw)

    def create_directory(self):
        path = os.path.dirname(os.path.abspath(self.filename))
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
