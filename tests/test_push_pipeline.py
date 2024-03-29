from src.push_pipeline import *
from inspect import getgeneratorlocals


# @pytest.mark.skip
def test_header_extract(test_sink):
    with file_readers(data_package) as readers:
        headers = header_extract((test_sink, test_sink))
        row_cycler = cycle_rows(headers)
        row_cycler.send(readers)
        header_rows = getgeneratorlocals(test_sink)['ml']
        # print('26:', 'header_rows ''='' ', header_rows)
        assert header_rows[0][0][0] == 'car'
        assert header_rows[0][1][0] == 'employer'
        assert header_rows[0][2][0] == 'summons_number'
        assert len(header_rows[0]) == 5
        test_sink.send('clear')


# @pytest.mark.skip
def test_gen_field_names(test_sink):
    with file_readers(data_package) as readers:
        field_names_gen = gen_field_names(test_sink)
        field_names_gen.send(tuple(input_data[1] for input_data, output_data in
                                   data_package))  # send class_names
        headers = header_extract((field_names_gen, field_names_gen))
        cycle_rows(headers).send(readers)
        dummy_nt = getgeneratorlocals(test_sink)['ml'][0]
        print(dummy_nt)
        data_fields = getgeneratorlocals(test_sink)['ml'][0]
        assert len(data_fields) == len(tuple
                                       (input_data[1]
                                        for input_data, output_data
                                        in data_package))
        print(data_fields)
        attrs = ['car', 'employer', 'summons_number', 'ssn', 'ssn']
        assert len(attrs) == len(data_fields)
        for i in range(len(data_fields)):
            assert getattr(data_fields[i], attrs[i])
            print(' ')
            print(dir(data_fields[i]))
            print(' ')


# @pytest.mark.skip
def test_file_readers(test_sink):
    with file_readers(data_package) as readers:
        # check the first element in each files header row:
        assert (next(readers[0])[0]) == 'Car'
        assert (next(readers[1])[0]) == 'employer'
        assert (next(readers[2])[0]) == 'Summons Number'
        assert (next(readers[3])[0]) == 'ssn'
        assert (next(readers[4])[0]) == 'ssn'
        data_rows = []
        for _ in range(len(readers)):
            try:
                while True:
                    data_rows.append(next(readers[_]))
            except StopIteration:
                continue
            except IndexError:
                break
        assert len(data_rows) == 4406


# @pytest.mark.skip
def test_cycle_rows(test_sink):
    row_cycler = cycle_rows(test_sink)
    ml = getgeneratorlocals(test_sink)['ml']
    with file_readers(data_package) as readers:
        row_cycler.send(readers)
        assert len(getgeneratorlocals(test_sink)['ml'][0]) == 5
        assert getgeneratorlocals(test_sink)['ml'][0][0][0] == 'Car'
        assert getgeneratorlocals(test_sink)['ml'][0][4][0] == 'ssn'
        test_sink.send('clear')
        try:
            row_cycler.send(test_sink)
        except StopIteration:
            pass
        assert len(ml) == 1000
    test_sink.send('clear')


# @pytest.mark.skip
def test_row_key_gen(test_sink, sample_reader_rows):
    # cars.csv
    test_key0 = (str, float, int, float, float, float, float, int, str)
    # nyc_parking_tickets_extract.csv
    test_key1 = (int, str, str, str, str, int, str, str, str)
    # update_status.csv
    test_key2 = (str, str, str)
    unpacked_test_keys = [*chain(test_key0, test_key1, test_key2)]
    f_idxs = (0, 2, 4)
    test_sink_tuple = (test_sink, test_sink)

    def check_key(row_keys, ref_keys):
        for value, ref in list(zip(row_keys, ref_keys)):
            return ref(value)

    gen_row_key = row_key_gen(test_sink_tuple)
    gen_row_key.send(sample_reader_rows(f_idxs))
    parsed_key0 = getgeneratorlocals(test_sink)['ml'][1]
    assert check_key(parsed_key0, unpacked_test_keys)
    test_sink.send('clear')


# @pytest.mark.skip
def test_date_key_gen(test_sink, sample_reader_rows, get_test_date,
                      date_tester):
    # so we create a file index of 2, 4, 4
    f_idxs = (2, 4, 4)
    # for each test run, the test sink key is ml, so 3 ml keys
    sink_keys = tuple('ml' for _ in range(3))
    # date format type 0, then 1, then 1 again
    date_key_idxs = (0, 1, 1)
    sink_idxs = ((2, 4), (2, 10), (2, 11))
    raw_date_strs = ('10/5/2016', '2016-01-24T21:19:30Z',
                     '2017-10-07T00:14:42Z')
    date_tester(test_sink, sample_reader_rows(f_idxs),
                get_test_date, key_names=sink_keys,
                date_format_key_idxs=date_key_idxs,
                access_idxs=sink_idxs, date_strs=raw_date_strs)
    print(getgeneratorlocals(test_sink)['ml'])
    test_sink.send('clear')


# @pytest.mark.skip
def test_date_lambda_parser(test_sink):
    dk2 = '%Y-%m-%dT%H:%M:%SZ'
    dk1 = '%m/%d/%Y'
    date_str1 = '10/5/2016'
    date_str2 = '2016-01-24T21:19:30Z'
    dkeys = (dk1, dk2)
    date_func1 = (lambda v: datetime.strptime(v, dkeys[0]))
    date_func2 = (lambda v: datetime.strptime(v, dkeys[1]))

    assert date_func1(date_str1).day == 5
    assert date_func1(date_str1).month == 10
    assert date_func1(date_str1).year == 2016

    assert date_func2(date_str2).day == 24
    assert date_func2(date_str2).month == 1
    assert date_func2(date_str2).year == 2016
    test_sink.send('clear')


# @pytest.mark.skip
def test_data_parser(test_sink):
    ml = getgeneratorlocals(test_sink)['ml']
    for i in range(len(date_keys)):
        with file_readers(data_package) as readers:

            # CONSTANTS:
            nt_class_names = [data[0][1] for data in data_package]
            
            # DECLARE --> From the bottom up stack
            parse_data = data_parser(test_sink)
            date_key = date_key_gen(parse_data)
            row_key = row_key_gen((parse_data, date_key))
            field_name_gen = gen_field_names(parse_data)
            headers = header_extract((field_name_gen, test_sink))
            row_cycler = cycle_rows(headers)

            # SEND PREREQUISITES FIRST
            field_name_gen.send(nt_class_names)
            date_key.send(date_keys)
            row_cycler.send(readers)

            # SEND DATA:
            while True:
                try:
                    row_cycler.send((date_key, row_key))
                except StopIteration:
                    break
    print(*ml, sep='\n\n\n')
    print(len(ml))
    assert (len(ml)) == 2002
    # raise


# @pytest.mark.skip
def test_broadcast(test_sink):
    ml = getgeneratorlocals(test_sink)['ml']
    with file_readers(data_package) as readers:

        # CONSTANTS:
        nt_class_names = [data[0][1] for data in data_package]
        output_package = [data[1] for data in data_package]

        # DECLARE --> From the bottom up stack
        broadcaster = broadcast(test_sink)
        parse_data = data_parser(broadcaster)
        date_key = date_key_gen(parse_data)
        row_key = row_key_gen((parse_data, date_key))
        field_name_gen = gen_field_names(parse_data)
        headers = header_extract((field_name_gen, field_name_gen))
        row_cycler = cycle_rows(headers)

        # SEND PREREQUISITES FIRST
        field_name_gen.send(nt_class_names)
        date_key.send((date_keys[0], date_keys[1]))
        row_cycler.send(readers)
        broadcaster.send(output_package)
        # writer.send(output_dir)

        # SEND DATA:
        try:
            row_cycler.send((date_key, row_key))
        except StopIteration:
            pass
    # total rows of all files * 3 constant:
    assert(len(ml)) == 13218


# @pytest.mark.skip
def test_filter_data(test_sink):
    ml = getgeneratorlocals(test_sink)['ml']
    with file_readers(data_package) as readers:

        # CONSTANTS:
        nt_class_names = [data[0][1] for data in data_package]
        output_package = [data[1] for data in data_package]

        # DECLARE --> From the bottom up stack
        data_filter = filter_data(test_sink)
        broadcaster = broadcast(data_filter)
        parse_data = data_parser(broadcaster)
        date_key = date_key_gen(parse_data)
        row_key = row_key_gen((parse_data, date_key))
        field_name_gen = gen_field_names(parse_data)
        headers = header_extract((field_name_gen, field_name_gen))
        row_cycler = cycle_rows(headers)

        # SEND PREREQUISITES FIRST
        field_name_gen.send(nt_class_names)
        date_key.send((date_keys[1], date_keys[1]))
        row_cycler.send(readers)
        broadcaster.send(output_package)

        # SEND DATA:
        try:
            row_cycler.send((date_key, row_key))
        except StopIteration:
            pass
    print(*ml, sep='\n')
    print(len(ml))


# @pytest.mark.skip
def test_save_data():
    header_rows = [('test_headers', 'test_headers', 'test_headers')]
    writer = save_data()
    writer.send(output_dir)
    writer.send(header_rows)
    # test create and write
    writer.send('test_file')
    writer.send(['this is a test line'])
    writer.send(0)
    # test append file
    writer.send('test_file')
    writer.send(['this is a test line'])
    writer.send(0)

    os.chdir('output_data')
    try:
        with open('test_file.csv') as tf:
            assert next(tf) == "test_headers,test_headers,test_headers\n"
            assert next(tf) == 'this is a test line\n'
    finally:
        os.remove('test_file.csv')
        os.chdir('..')
