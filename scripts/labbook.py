
"""
def make_results (in_dir, out_file="d:/merged_output.xls"):

    xls_files = glob.glob(in_dir + "*.xls")
    sheet_names = []
    merged_book = xlwt.Workbook()

    [sheet_names.append(os.path.basename(v)[:-4]) for k, v in enumerate(xls_files)]
    for k, xls_file in enumerate(xls_files):
    if len (sheet_names[k]) <= 31:
    book = xlrd.open_workbook(xls_file)
    ws = merged_book.add_sheet(sheet_names[k])
    for sheetx in range(book.nsheets):
    sheet = book.sheet_by_index(sheetx)
    for rx in range(sheet.nrows):
    for cx in range(sheet.ncols):
    ws.write(rx, cx, sheet.cell_value(rx, cx))
    else:
    print "File name too long: <%s.xls> (maximum is 31 chars) " % (sheet_names[k])
    print "File <%s.xls> is *not* included in the merged xls file." % (sheet_names[k])
    merged_book.save(out_file)

    print "---> Merged xls file written to %s using the following source files: " % (out_file)
    for k, v in enumerate(sheet_names):
    if len(v) <= 31: print "\t", str(k+1).zfill(3), "%s.xls" % (v)

"""