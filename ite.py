#!/usr/bin/env python3

from openpyxl import Workbook
import csv, sys

# FIXME
ORIGINAL_DATA_COL_RANGE = ('C', 'J')
DIFF_COL_RANGE = ('L', 'O')
MISSED_COL_RANGE = ('Q', 'T')

def extract(inpath):
	rows = []
	row = None

	with open(inpath, 'r') as infile:
		for line in infile:
			if should_skip(line):
				continue

			if is_new_row(line):
				if row:
					rows.append(row)
				row = []

			if row != None:
				row.append(line.strip())

	labels = rows[0]

	body = [row for row in rows if row != labels]

	return labels, body

def is_heading(line):
	# FIXME: This isn't good
	return (
		'Keyword' in line
		or 'Basic Sciences' in line
		or 'Clinical Sciences' in line
		or 'Clinical Subspecialties' in line
		or 'Special Problems' in line
		or 'Basic items' in line
		or 'Advanced items' in line
	)

def is_new_row(line):
	return (
		'(A)' in line
		or '(B)' in line
		or is_heading(line)
	)

def should_skip(line):
	return (
		not line
		or len(line.strip()) == 0
		or 'Page' in line
		or '#' in line
		or 'N=' in line
	)

def dump_csv(labels, body, outpath):
	rows = [
		labels,
		*body
	]

	with open(outpath, 'w') as outfile:
		writer = csv.writer(outfile)
		writer.writerows(rows)

def extract_sections(rows):
	sections = []
	heading = None
	subheading = None
	items = []

	for row in rows:
		if len(row) == 1:
			if not heading:
				heading = row[0]
			elif not subheading:
				subheading = row[0]
			elif items:
				try:
					sections.append(IteSection(heading, subheading, items))
					heading = row[0]
					subheading = None
					items = []
				except Exception as e:
					print(e, file=sys.stderr)
		else:
			items.append(row)

	try:
		sections.append(IteSection(heading, subheading, items))
	except Exception as e:
		print(e, file=sys.stderr)

	return sections

def parse_percentage(text):
	return float(text[:-1]) / 100

def format_percentage(num):
	return '{}%'.format(num * 100)

def get_xlsx_rows(sections):
	# TODO: Averages
	rows = []

	for section in sections:
		rows += section.get_xlsx_rows()
		rows.append([])

	rows.append([])

	return rows

def get_csv_rows(sections):
	rows = []
	items = []

	for section in sections:
		rows += section.get_csv_rows()
		rows.append([])
		items += section.items

	rows.append([])

	rows.append([
		'Overall averages',
		'',
		sum([item.cby_total for item in items])/len(items),
		sum([item.cby for item in items])/len(items),
		sum([item.ca1_total for item in items])/len(items),
		sum([item.ca1 for item in items])/len(items),
		sum([item.ca2_total for item in items])/len(items),
		sum([item.ca2 for item in items])/len(items),
		sum([item.ca3_total for item in items])/len(items),
		sum([item.ca3 for item in items])/len(items),
		'',
		sum([item.cby_diff for item in items])/len(items),
		sum([item.ca1_diff for item in items])/len(items),
		sum([item.ca2_diff for item in items])/len(items),
		sum([item.ca3_diff for item in items])/len(items),
		'',
		sum([item.cby_missed for item in items])/len(items),
		sum([item.ca1_missed for item in items])/len(items),
		sum([item.ca2_missed for item in items])/len(items),
		sum([item.ca3_missed for item in items])/len(items)
	])

	advanced_items = [item for item in items if item.item_type == 'A']
	basic_items = [item for item in items if item.item_type == 'B']

	rows.append([
		'Advanced averages',
		'',
		sum([item.cby_total for item in advanced_items])/len(advanced_items),
		sum([item.cby for item in advanced_items])/len(advanced_items),
		sum([item.ca1_total for item in advanced_items])/len(advanced_items),
		sum([item.ca1 for item in advanced_items])/len(advanced_items),
		sum([item.ca2_total for item in advanced_items])/len(advanced_items),
		sum([item.ca2 for item in advanced_items])/len(advanced_items),
		sum([item.ca3_total for item in advanced_items])/len(advanced_items),
		sum([item.ca3 for item in advanced_items])/len(advanced_items),
		'',
		sum([item.cby_diff for item in advanced_items])/len(advanced_items),
		sum([item.ca1_diff for item in advanced_items])/len(advanced_items),
		sum([item.ca2_diff for item in advanced_items])/len(advanced_items),
		sum([item.ca3_diff for item in advanced_items])/len(advanced_items),
		'',
		sum([item.cby_missed for item in advanced_items])/len(advanced_items),
		sum([item.ca1_missed for item in advanced_items])/len(advanced_items),
		sum([item.ca2_missed for item in advanced_items])/len(advanced_items),
		sum([item.ca3_missed for item in advanced_items])/len(advanced_items)
	])
	rows.append([
		'Basic averages',
		'',
		sum([item.cby_total for item in basic_items])/len(basic_items),
		sum([item.cby for item in basic_items])/len(basic_items),
		sum([item.ca1_total for item in basic_items])/len(basic_items),
		sum([item.ca1 for item in basic_items])/len(basic_items),
		sum([item.ca2_total for item in basic_items])/len(basic_items),
		sum([item.ca2 for item in basic_items])/len(basic_items),
		sum([item.ca3_total for item in basic_items])/len(basic_items),
		sum([item.ca3 for item in basic_items])/len(basic_items),
		'',
		sum([item.cby_diff for item in basic_items])/len(basic_items),
		sum([item.ca1_diff for item in basic_items])/len(basic_items),
		sum([item.ca2_diff for item in basic_items])/len(basic_items),
		sum([item.ca3_diff for item in basic_items])/len(basic_items),
		'',
		sum([item.cby_missed for item in basic_items])/len(basic_items),
		sum([item.ca1_missed for item in basic_items])/len(basic_items),
		sum([item.ca2_missed for item in basic_items])/len(basic_items),
		sum([item.ca3_missed for item in basic_items])/len(basic_items)
	])

	return rows

def dump_section_csv(sections, outpath):
	with open(outpath, 'w') as outfile:
		writer = csv.writer(outfile)
		writer.writerows(get_csv_rows(sections))

def dump_section_xlsx(sections, outpath):
	wb = Workbook(write_only=True)
	ws = wb.create_sheet()
	for row in get_xlsx_rows(sections):
		ws.append(row)

	wb.save(outpath)

def main():
	labels, body = extract('/home/mischka/Downloads/ite and basic stuff/ITE_ProgramItem_156002.txt')

	# dump_csv(labels, body, './output/2017-ite.csv')
	sections = extract_sections(body)
	dump_section_csv(sections, './output/2017-ite-sections.csv')
	dump_section_xlsx(sections, './output/2017-ite-sections.xlsx')


class IteSection(object):
	HEADINGS = [
		'',
		'% total CBY',
		'% our CBY',
		'% total CA-1',
		'% our CA-1',
		'% total CA-2',
		'% our CA-2',
		'% total CA-3',
		'% our CA-3',
		'',
		'CBY',
		'CA-1',
		'CA-2',
		'CA-3',
		'',
		'CBY',
		'CA-1',
		'CA-2',
		'CA-3'
	]

	def __init__(self, heading, subheading, items):
		self.heading = heading
		self.subheading = subheading
		self.items = [IteItem(item) for item in items]


	def get_csv_rows(self):
		return [
			[
				self.heading,
				*self.HEADINGS
			],
			*[item.get_csv_row() for item in self.items]
		]

	def get_xlsx_rows(self):
		return [
			[
				self.heading,
				*self.HEADINGS
			],
			*[item.get_xlsx_row() for item in self.items]
		]

	def __repr__(self):
		return 'IteSection(heading={}, subheading={}, items={})'.format(
			self.heading,
			self.subheading,
			self.items
		)

class IteItem(object):

	def __init__(self, row):
		self.keyword = row[0]
		(
			self.ca3_total,
			self.ca3,
			self.ca2_total,
			self.ca2,
			self.ca1_total,
			self.ca1,
			self.cby_total,
			self.cby
		) = [parse_percentage(cell) for cell in row[1:]]

		self.item_type = 'A' if '(A)' in self.keyword else 'B'

	@property
	def cby_diff(self):
		return self.cby - self.cby_total

	@property
	def ca1_diff(self):
		return self.ca1 - self.ca1_total

	@property
	def ca2_diff(self):
		return self.ca2 - self.ca2_total

	@property
	def ca3_diff(self):
		return self.ca3 - self.ca3_total

	@property
	def cby_missed(self):
		return 1 - self.cby

	@property
	def ca1_missed(self):
		return 1 - self.ca1

	@property
	def ca2_missed(self):
		return 1 - self.ca2

	@property
	def ca3_missed(self):
		return 1 - self.ca3

	def get_csv_row(self):
		return [
			self.keyword,
			'',
			self.cby_total,
			self.cby,
			self.ca1_total,
			self.ca1,
			self.ca2_total,
			self.ca2,
			self.ca3_total,
			self.ca3,
			'',
			self.cby_diff,
			self.ca1_diff,
			self.ca2_diff,
			self.ca3_diff,
			'',
			self.cby_missed,
			self.ca1_missed,
			self.ca2_missed,
			self.ca3_missed
		]

	def get_xlsx_row(self):
		return [
			self.keyword,
			'',
			self.cby_total,
			self.cby,
			self.ca1_total,
			self.ca1,
			self.ca2_total,
			self.ca2,
			self.ca3_total,
			self.ca3,
			'',
			'=(RC[-8] - RC[-9])',
			'=(RC[-7] - RC[-8])',
			'=(RC[-6] - RC[-7])',
			'=(RC[-5] - RC[-6])',
			'',
			'=(1 - R[0]C[-13])',
			'=(1 - R[0]C[-12])',
			'=(1 - R[0]C[-11])',
			'=(1 - R[0]C[-10])'
		]

	def __repr__(self):
		return (
			'IteItem(keyword={}, ca3_total={}, ca3={}, ca2_total={}, ca2={}, '
			'ca1_total={}, ca1={}, cby_total={}, cby={})'
		).format(
			self.keyword,
			self.ca3_total,
			self.ca3,
			self.ca2_total,
			self.ca2,
			self.ca1_total,
			self.ca1,
			self.cby_total,
			self.cby
		)

if __name__ == '__main__':
	main()
