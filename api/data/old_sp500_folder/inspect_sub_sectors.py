
import csv
with open('S&P500-Sub_sectors.csv') as csv_file:
	reader = csv.DictReader(csv_file)
	for row in reader:
		if '"' in row:
			breakpoint()
