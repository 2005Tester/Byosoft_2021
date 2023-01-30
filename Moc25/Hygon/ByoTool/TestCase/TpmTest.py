# -*- encoding=utf8 -*-
from ByoTool.Config import *
from ByoTool.BaseLib import *


@core.test_case(('5301', '[TC5301]TPM', 'TPM'))
def tpm():
    """
        Name:   TPM测试

        Steps:  1.设置TPM为FTPM,关闭TPM State
                2.关闭Platform Hierarchy
                3.关闭'Platform Hierarchy', 'Storage Hierarchy', 'Endorsement Hierarchy', 'PH Randomization'
                4.依次修改PPI,Rev,重启进SetUp检查是否为修改的值
                5.全选PCR Bank,POST显示，ESC,F12是否正常
                6.依次修改所有能设置的PCR Bank,POST显示，ESC,F12是否正常
                7.设置TPM为DTPM,关闭TPM State
                8.关闭Platform Hierarchy
                9.关闭'Platform Hierarchy', 'Storage Hierarchy', 'Endorsement Hierarchy', 'PH Randomization'
                10.依次修改PPI,Rev,重启进SetUp检查是否为修改的值
                11.全选PCR Bank,POST显示，ESC,F12是否正常
                12.依次修改所有能设置的PCR Bank,POST显示，ESC,F12是否正常

        Result: 1.关闭TPM State,底下所有选项自动隐藏，SetUp显示FTPM信息
                2.'Storage Hierarchy', 'Endorsement Hierarchy', 'PH Randomization'置灰
                3.正常启动
                4.修改成功
                5.POST显示全部PCR BANK，ESC继续启动，F12重启
                6.POST显示设置的PCR BANK，ESC继续启动，F12重启
                7.关闭TPM State,底下所有选项自动隐藏，SetUp显示DTPM信息
                8.'Storage Hierarchy', 'Endorsement Hierarchy', 'PH Randomization'置灰
                9.正常启动
                10.修改成功
                11.POST显示全部PCR BANK，ESC继续启动，F12重启
                12.POST显示设置的PCR BANK，ESC继续启动，F12重启
        """
    try:
        count = 0
        wrong_msg = []
        base_time = 10
        logging.info('FTPM测试...............................................................................')
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SET_FTPM, 18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        start = time.time()
        if not SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            BmcLib.init_sut()
            assert SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE)
        spent = time.time() - start
        SetUpLib.send_key(SutConfig.Msg.SETUP_KEY)
        if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN):
            assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.CLOSE_TPM_STATE, 18)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.DOWN)
        result1 = SetUpLib.get_data(1)
        SetUpLib.send_key(Key.DOWN)
        if result1 == SetUpLib.get_data(1):
            logging.info('TPM State 设为关闭，自动隐藏选项')
        else:
            stylelog.fail('TPM State 设为关闭，没有自动隐藏选项')
            wrong_msg.append('TPM State 设为关闭，没有自动隐藏选项')
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_SECURITY)
        # SetUpLib.send_key(Key.RIGHT)
        # time.sleep(1)
        # SetUpLib.send_key(Key.LEFT)
        # if re.search('TPM Version *{0}'.format(SutConfig.Sec.FTPM_MSG), SetUpLib.get_data(2)):
        #     logging.info('TPM State设为关闭，SetUp下显示{0}'.format(SutConfig.Sec.FTPM_MSG))
        # else:
        #     stylelog.fail('TPM State设为关闭，SetUp下没有显示{0}'.format(SutConfig.Sec.FTPM_MSG))
        #     wrong_msg.append('TPM State设为关闭，SetUp下没有显示{0}'.format(SutConfig.Sec.FTPM_MSG))
        #     count += 1
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_TPM_STATE, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.TPM_LIST[0]: 'Disabled'}], 18)
        if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.TPM_LIST[1]], 5) and not SetUpLib.locate_option(Key.UP, [
            SutConfig.Sec.TPM_LIST[2]], 5) and not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.TPM_LIST[3]], 5):
            logging.info(
                f'关闭{SutConfig.Sec.TPM_LIST[0]},{SutConfig.Sec.TPM_LIST[1]}和{SutConfig.Sec.TPM_LIST[2]}和{SutConfig.Sec.TPM_LIST[3]}都置灰')
        else:
            logging.info(
                f'关闭{SutConfig.Sec.TPM_LIST[0]},{SutConfig.Sec.TPM_LIST[1]}、{SutConfig.Sec.TPM_LIST[2]}、{SutConfig.Sec.TPM_LIST[3]}没有置灰')
            wrong_msg.append(
                f'关闭{SutConfig.Sec.TPM_LIST[0]},{SutConfig.Sec.TPM_LIST[1]}、{SutConfig.Sec.TPM_LIST[2]}、{SutConfig.Sec.TPM_LIST[3]}没有置灰')
            count += 1
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.TPM_LIST[0]: 'Enabled'}], 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.TPM_LIST[1]: 'Disabled'}], 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.TPM_LIST[2]: 'Disabled'}], 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.TPM_LIST[3]: 'Disabled'}], 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.UP, [{SutConfig.Sec.TPM_LIST[0]: 'Disabled'}], 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            SetUpLib.send_key(SutConfig.Msg.SETUP_KEY)
            if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN):
                logging.info(f'{SutConfig.Sec.TPM_LIST}都关闭，正常启动')
        else:
            stylelog.fail(f'{SutConfig.Sec.TPM_LIST}都关闭，没有启动')
            wrong_msg.append(f'{SutConfig.Sec.TPM_LIST}都关闭，没有启动')
            count += 1
            assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(2)
        # rev=re.findall('Current Rev of TPM2 ACPI Table *(Rev \d)',data)
        ppi = re.findall('Current PPI Version *([\d\.]+)', data)
        hard_support = re.findall('TPM2 Hardware Supported Hash Algorithm *([A-Z\_\d ,]+)BIOS', data)[0].replace(' ',
                                                                                                                 '').split(
            ',')
        bios_support = re.findall('BIOS Supported Hash Algorithm *([A-Z\_\d ,]+)TPM', data)[0].replace(' ', '').split(
            ',')
        # assert SetUpLib.locate_option(Key.DOWN,[SutConfig.Sec.REV_NAME],25,delay=2)
        # rev_support=SetUpLib.get_value_list()
        # rev_support.remove(rev[0])
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.PPI_NAME], 25, delay=2)
        ppi_support = SetUpLib.get_value_list()
        ppi_support.remove(ppi[0])
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.ENTER)
        for i in range(0, len(ppi_support)):
            # for i in range(0,max([len(ppi_support),len(rev_support)])):
            # if i < len(rev_support):
            #     assert SetUpLib.enter_menu_change_value(Key.DOWN,[{SutConfig.Sec.REV_NAME:rev_support[i]}],18)
            if i < len(ppi_support):
                assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.PPI_NAME: ppi_support[i]}], 18)
            time.sleep(1)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(5)
            assert SetUpLib.boot_to_setup()
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            data = SetUpLib.get_data(2)
            # if i < len(rev_support):
            #     if re.search(f'Current Rev of TPM2 ACPI Table *{rev_support[i]}',data) :
            #         logging.info(f'修改{SutConfig.Sec.REV_NAME}为{rev_support[i]}，成功')
            #     else:
            #         stylelog.fail(f'修改{SutConfig.Sec.REV_NAME}为{rev_support[i]}，失败')
            #         wrong_msg.append(f'修改{SutConfig.Sec.REV_NAME}为{rev_support[i]}，失败')
            #         count+=1
            if i < len(ppi_support):
                if re.search(f'Current PPI Version *{ppi_support[i]}', data):
                    logging.info(f'修改{SutConfig.Sec.PPI_NAME}为{ppi_support[i]}成功')
                else:
                    stylelog.fail(f'修改{SutConfig.Sec.PPI_NAME}为{ppi_support[i]}失败')
                    wrong_msg.append(f'修改{SutConfig.Sec.PPI_NAME}为{ppi_support[i]}失败')
                    count += 1
        SetUpLib.send_key(Key.UP)
        data = SetUpLib.get_data(2)
        all_support = [i for i in hard_support if i in bios_support]
        for i in all_support:
            if re.search(f'\[ \] *PCR Bank: {i}', data):
                assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {i}'], 25, delay=2)
                time.sleep(1)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(2)
        assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {all_support[0]}'], 25, delay=2)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if len(all_support) > 1:
            if SetUpLib.wait_message(f"{SutConfig.Sec.PCR_BANK_MSG}{', '.join(all_support)}", 300):
                logging.info('全选PCR BANK,启动时显示全部PCR BANK')
                SetUpLib.send_key(Key.F12)
                start = time.time()
                if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                    end = time.time()
                    spent_time = end - start
                    if abs(spent_time - spent) < base_time:
                        logging.info('F12后重启')
                    else:
                        stylelog.fail('F12没有重启')
                        count += 1
                    time.sleep(1)
                    SetUpLib.send_key(Key.DEL)
                    if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 90):
                        assert SetUpLib.boot_to_setup()
                else:
                    stylelog.fail('F12后宕机')
                    count += 1
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('全选PCR BANK,启动时没有显示全部PCR BANK')
                wrong_msg.append('全选PCR BANK,启动时没有显示全部PCR BANK')
                count += 1
                assert SetUpLib.boot_to_setup()
        else:
            assert SetUpLib.boot_to_setup()

        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.UP)
        data = SetUpLib.get_data(2)
        if all(re.search(f'\[X\] *PCR Bank: {i}', data) for i in all_support):
            logging.info('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
        else:
            stylelog.fail('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
            wrong_msg.append('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
            count += 1
        if len(all_support) > 1:
            for i in all_support:
                SetUpLib.send_key(Key.ESC)
                time.sleep(2)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                SetUpLib.send_key(Key.UP)
                data = SetUpLib.get_data(2)
                for m in all_support:
                    if re.search(f'\[ \] *PCR Bank: {m}', data):
                        assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {m}'], 25, delay=2)
                        time.sleep(1)
                        SetUpLib.send_key(Key.ENTER)
                        time.sleep(2)

                for j in all_support:
                    if j != i:
                        assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {j}'], 25, delay=2)
                        time.sleep(1)
                        SetUpLib.send_key(Key.ENTER)
                        time.sleep(1)
                time.sleep(1)
                SetUpLib.send_keys(Key.SAVE_RESET)
                time.sleep(5)
                if SetUpLib.wait_message(f"{SutConfig.Sec.PCR_BANK_MSG}{i}", 300):
                    logging.info(f'选择PCR Bank 为{i},启动时显示{i}')
                    SetUpLib.send_key(Key.F12)
                    start = time.time()
                    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                        end = time.time()
                        spent_time = end - start
                        if abs(spent_time - spent) < base_time:
                            logging.info('F12后重启')
                        else:
                            stylelog.fail('F12没有重启')
                            count += 1
                        time.sleep(1)
                        SetUpLib.send_key(SutConfig.Msg.SETUP_KEY)
                        if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 90):
                            assert SetUpLib.boot_to_setup()
                    else:
                        stylelog.fail('F12后宕机')
                        count += 1
                        assert SetUpLib.boot_to_setup()
                else:
                    stylelog.fail(f'选择PCR Bank 为{i},启动时没有显示{i}')
                    wrong_msg.append(f'选择PCR Bank 为{i},启动时没有显示{i}')
                    count += 1
                    assert SetUpLib.boot_to_setup()

                assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
                time.sleep(1)
                SetUpLib.send_key(Key.UP)
                data = SetUpLib.get_data(2)
                if re.search(f'Active PCR Banks *{i}', data):
                    logging.info(f'选择PCR Bank 为{i},SetUp下显示正常')
                else:
                    stylelog.fail(f'选择PCR Bank 为{i},SetUp下显示异常')
                    wrong_msg.append(f'选择PCR Bank 为{i},SetUp下显示异常')
                    count += 1
        for i in SutConfig.Sec.CHANGE_TPM_VALUE:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [{'TPM2 Operation': i}], 18)
            time.sleep(2)
            SetUpLib.send_keys(Key.SAVE_RESET)
            if SetUpLib.wait_message(SutConfig.Sec.ESC_MSG):
                time.sleep(1)
                SetUpLib.send_key(Key.ESC)
                start = time.time()
                if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                    end = time.time()
                    spent_time = end - start
                    if abs(spent_time - spent) > base_time:
                        logging.info('ESC后继续启动')
                    else:
                        stylelog.fail('ESC没有继续启动')
                        count += 1
                    time.sleep(1)
                    SetUpLib.send_key(SutConfig.Msg.SETUP_KEY)
                    if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 90):
                        assert SetUpLib.boot_to_setup()
                else:
                    stylelog.fail('ESC后宕机')
                    count += 1
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sec.ESC_MSG))
                wrong_msg.append('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sec.ESC_MSG))
                count += 1
                BmcLib.init_sut()
                assert SetUpLib.boot_with_hotkey_only(SutConfig.Msg.SETUP_KEY, SutConfig.Msg.PAGE_MAIN, 200, SutConfig.Msg.POST_MESSAGE)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
            SetUpLib.send_key(Key.ENTER)
            if re.search('No Action', SetUpLib.get_data(3)):
                logging.info('一次启动后,TPM2操作变为无动作')
            else:
                stylelog.fail('一次启动后,TPM2操作没有变为无动作')
                wrong_msg.append('一次启动后,TPM2操作没有变为无动作')
                count += 1
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [{'TPM2 Operation': i}], 18)
            time.sleep(2)
            SetUpLib.send_keys(Key.SAVE_RESET)
            if SetUpLib.wait_message(SutConfig.Sec.ESC_MSG):
                time.sleep(1)
                SetUpLib.send_key(Key.F12)
                start = time.time()
                if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                    end = time.time()
                    spent_time = end - start
                    if abs(spent_time - spent) < base_time:
                        logging.info('F12后重启')
                    else:
                        stylelog.fail('F12没有重启')
                        count += 1
                    time.sleep(1)
                    SetUpLib.send_key(SutConfig.Msg.SETUP_KEY)
                    if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 90):
                        assert SetUpLib.boot_to_setup()
                else:
                    stylelog.fail('F12后宕机')
                    count += 1
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sec.ESC_MSG))
                wrong_msg.append('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sec.ESC_MSG))
                count += 1
                assert SetUpLib.boot_to_setup()
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
            SetUpLib.send_key(Key.ENTER)
            if re.search('No Action', SetUpLib.get_data(3)):
                logging.info('一次启动后,TPM2操作变为无动作')
            else:
                stylelog.fail('一次启动后,TPM2操作没有变为无动作')
                wrong_msg.append('一次启动后,TPM2操作没有变为无动作')
                count += 13

        logging.info('DTPM测试...............................................................................')
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.SET_DTPM, 18)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.CLOSE_TPM_STATE, 18)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.DOWN)
        result1 = SetUpLib.get_data(1)
        SetUpLib.send_key(Key.DOWN)
        if result1 == SetUpLib.get_data(1):
            logging.info('TPM State 设为关闭，自动隐藏选项')
        else:
            stylelog.fail('TPM State 设为关闭，没有自动隐藏选项')
            wrong_msg.append('TPM State 设为关闭，没有自动隐藏选项')
            count += 1
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        assert SetUpLib.boot_to_setup()
        assert SetUpLib.boot_to_page(SutConfig.Msg.PAGE_SECURITY)
        # SetUpLib.send_key(Key.RIGHT)
        # time.sleep(1)
        # SetUpLib.send_key(Key.LEFT)
        # if re.search('TPM Version *{0}'.format(SutConfig.Sec.DTPM_MSG), SetUpLib.get_data(2)):
        #     logging.info('TPM State设为关闭，SetUp下显示{0}'.format(SutConfig.Sec.DTPM_MSG))
        # else:
        #     stylelog.fail('TPM State设为关闭，SetUp下没有显示{0}'.format(SutConfig.Sec.DTPM_MSG))
        #     wrong_msg.append('TPM State设为关闭，SetUp下没有显示{0}'.format(SutConfig.Sec.DTPM_MSG))
        #     count += 1
        assert SetUpLib.enter_menu_change_value(Key.DOWN, SutConfig.Sec.OPEN_TPM_STATE, 18)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.TPM_LIST[0]: 'Disabled'}], 18)
        if not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.TPM_LIST[1]], 5) and not SetUpLib.locate_option(Key.UP, [
            SutConfig.Sec.TPM_LIST[2]], 5) and not SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.TPM_LIST[3]], 5):
            logging.info(
                f'关闭{SutConfig.Sec.TPM_LIST[0]},{SutConfig.Sec.TPM_LIST[1]}和{SutConfig.Sec.TPM_LIST[2]}和{SutConfig.Sec.TPM_LIST[3]}都置灰')
        else:
            logging.info(
                f'关闭{SutConfig.Sec.TPM_LIST[0]},{SutConfig.Sec.TPM_LIST[1]}、{SutConfig.Sec.TPM_LIST[2]}、{SutConfig.Sec.TPM_LIST[3]}没有置灰')
            wrong_msg.append(
                f'关闭{SutConfig.Sec.TPM_LIST[0]},{SutConfig.Sec.TPM_LIST[1]}、{SutConfig.Sec.TPM_LIST[2]}、{SutConfig.Sec.TPM_LIST[3]}没有置灰')
            count += 1
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.TPM_LIST[0]: 'Enabled'}], 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.TPM_LIST[1]: 'Disabled'}], 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.TPM_LIST[2]: 'Disabled'}], 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.TPM_LIST[3]: 'Disabled'}], 18)
        time.sleep(1)
        assert SetUpLib.enter_menu_change_value(Key.UP, [{SutConfig.Sec.TPM_LIST[0]: 'Disabled'}], 18)
        time.sleep(1)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
            SetUpLib.send_key(SutConfig.Msg.SETUP_KEY)
            if SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN):
                logging.info(f'{SutConfig.Sec.TPM_LIST}都关闭，正常启动')
        else:
            stylelog.fail(f'{SutConfig.Sec.TPM_LIST}都关闭，没有启动')
            wrong_msg.append(f'{SutConfig.Sec.TPM_LIST}都关闭，没有启动')
            count += 1
            assert SetUpLib.boot_to_setup()
        assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        data = SetUpLib.get_data(2)
        rev = re.findall('Current Rev of TPM2 ACPI Table *(Rev \d)', data)
        ppi = re.findall('Current PPI Version *([\d\.]+)', data)
        hard_support = re.findall('TPM2 Hardware Supported Hash Algorithm *([A-Z\_\d ,]+)BIOS', data)[0].replace(' ',
                                                                                                                 '').split(
            ',')
        bios_support = re.findall('BIOS Supported Hash Algorithm *([A-Z\_\d ,]+)TPM', data)[0].replace(' ', '').split(
            ',')
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.REV_NAME], 25, delay=2)
        rev_support = SetUpLib.get_value_list()
        rev_support.remove(rev[0])
        assert SetUpLib.locate_option(Key.DOWN, [SutConfig.Sec.PPI_NAME], 25, delay=2)
        ppi_support = SetUpLib.get_value_list()
        ppi_support.remove(ppi[0])
        time.sleep(1)
        SetUpLib.send_key(Key.ESC)
        SetUpLib.clean_buffer()
        SetUpLib.send_key(Key.ENTER)
        for i in range(0, max([len(ppi_support), len(rev_support)])):
            if i < len(rev_support):
                assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.REV_NAME: rev_support[i]}], 18)
            if i < len(ppi_support):
                assert SetUpLib.enter_menu_change_value(Key.DOWN, [{SutConfig.Sec.PPI_NAME: ppi_support[i]}], 18)
            time.sleep(1)
            SetUpLib.send_keys(Key.SAVE_RESET)
            time.sleep(5)
            assert SetUpLib.boot_to_setup()
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
            time.sleep(1)
            SetUpLib.send_key(Key.ENTER)
            data = SetUpLib.get_data(2)
            if i < len(rev_support):
                if re.search(f'Current Rev of TPM2 ACPI Table *{rev_support[i]}', data):
                    logging.info(f'修改{SutConfig.Sec.REV_NAME}为{rev_support[i]}，成功')
                else:
                    stylelog.fail(f'修改{SutConfig.Sec.REV_NAME}为{rev_support[i]}，失败')
                    wrong_msg.append(f'修改{SutConfig.Sec.REV_NAME}为{rev_support[i]}，失败')
                    count += 1
            if i < len(ppi_support):
                if re.search(f'Current PPI Version *{ppi_support[i]}', data):
                    logging.info(f'修改{SutConfig.Sec.PPI_NAME}为{ppi_support[i]}成功')
                else:
                    stylelog.fail(f'修改{SutConfig.Sec.PPI_NAME}为{ppi_support[i]}失败')
                    wrong_msg.append(f'修改{SutConfig.Sec.PPI_NAME}为{ppi_support[i]}失败')
                    count += 1
        SetUpLib.send_key(Key.UP)
        data = SetUpLib.get_data(2)
        all_support = [i for i in hard_support if i in bios_support]
        for i in all_support:
            if re.search(f'\[ \] *PCR Bank: {i}', data):
                assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {i}'], 25, delay=2)
                SetUpLib.clean_buffer()
                SetUpLib.send_key(Key.ENTER)
                time.sleep(2)
        assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {all_support[0]}'], 25, delay=2)
        time.sleep(1)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_key(Key.ENTER)
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        if len(all_support) > 1:
            if SetUpLib.wait_message(f"{SutConfig.Sec.PCR_BANK_MSG}{', '.join(all_support)}", 300):
                logging.info('全选PCR BANK,启动时显示全部PCR BANK')
                SetUpLib.send_key(Key.F12)
                start = time.time()
                if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                    end = time.time()
                    spent_time = end - start
                    if abs(spent_time - spent) < base_time:
                        logging.info('F12后重启')
                    else:
                        stylelog.fail('F12没有重启')
                        count += 1
                    time.sleep(1)
                    SetUpLib.send_key(SutConfig.Msg.SETUP_KEY)
                    if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 90):
                        assert SetUpLib.boot_to_setup()
                else:
                    stylelog.fail('F12后宕机')
                    count += 1
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('全选PCR BANK,启动时没有显示全部PCR BANK')
                wrong_msg.append('全选PCR BANK,启动时没有显示全部PCR BANK')
                count += 1
                assert SetUpLib.boot_to_setup()
        else:
            assert SetUpLib.boot_to_setup()
        assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
        time.sleep(1)
        SetUpLib.send_key(Key.UP)
        data = SetUpLib.get_data(2)
        if all(re.search(f'\[X\] *PCR Bank: {i}', data) for i in all_support):
            logging.info('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
        else:
            stylelog.fail('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
            wrong_msg.append('全选PCR BANK,重启进SetUp,SetUp显示全部PCR BANK')
            count += 1
        if len(all_support) > 1:
            for i in all_support:
                SetUpLib.send_key(Key.ESC)
                time.sleep(2)
                SetUpLib.send_key(Key.ENTER)
                time.sleep(1)
                SetUpLib.send_key(Key.UP)
                data = SetUpLib.get_data(2)
                for m in all_support:
                    if re.search(f'\[ \] *PCR Bank: {m}', data):
                        assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {m}'], 25, delay=2)
                        time.sleep(1)
                        SetUpLib.send_key(Key.ENTER)
                        time.sleep(2)

                for j in all_support:
                    if j != i:
                        assert SetUpLib.locate_option(Key.DOWN, [f'PCR Bank: {j}'], 25, delay=2)
                        time.sleep(1)
                        SetUpLib.send_key(Key.ENTER)
                        time.sleep(1)
                time.sleep(1)
                SetUpLib.send_keys(Key.SAVE_RESET)
                time.sleep(5)
                if SetUpLib.wait_message(f"{SutConfig.Sec.PCR_BANK_MSG}{i}", 300):
                    logging.info(f'选择PCR Bank 为{i},启动时显示{i}')
                    SetUpLib.send_key(Key.F12)
                    start = time.time()
                    if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                        end = time.time()
                        spent_time = end - start
                        if abs(spent_time - spent) < base_time:
                            logging.info('F12后重启')
                        else:
                            stylelog.fail('F12没有重启')
                            count += 1
                        time.sleep(1)
                        SetUpLib.send_key(SutConfig.Msg.SETUP_KEY)
                        if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 90):
                            assert SetUpLib.boot_to_setup()
                    else:
                        stylelog.fail('F12后宕机')
                        count += 1
                        assert SetUpLib.boot_to_setup()
                else:
                    stylelog.fail(f'选择PCR Bank 为{i},启动时没有显示{i}')
                    wrong_msg.append(f'选择PCR Bank 为{i},启动时没有显示{i}')
                    count += 1
                    BmcLib.init_sut()
                    assert SetUpLib.boot_with_hotkey_only(SutConfig.Msg.SETUP_KEY, SutConfig.Msg.PAGE_MAIN, 200,
                                                          SutConfig.Msg.POST_MESSAGE)
                assert SetUpLib.enter_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
                time.sleep(1)
                SetUpLib.send_key(Key.UP)
                data = SetUpLib.get_data(2)
                if re.search(f'Active PCR Banks *{i}', data):
                    logging.info(f'选择PCR Bank 为{i},SetUp下显示正常')
                else:
                    stylelog.fail(f'选择PCR Bank 为{i},SetUp下显示异常')
                    wrong_msg.append(f'选择PCR Bank 为{i},SetUp下显示异常')
                    count += 1
        for i in SutConfig.Sec.CHANGE_TPM_VALUE:
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [{'TPM2 Operation': i}], 18)
            time.sleep(2)
            SetUpLib.send_keys(Key.SAVE_RESET)
            if SetUpLib.wait_message(SutConfig.Sec.ESC_MSG):
                time.sleep(1)
                SetUpLib.send_key(Key.ESC)
                start = time.time()
                if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                    end = time.time()
                    spent_time = end - start
                    if abs(spent_time - spent) > base_time:
                        logging.info('ESC后继续启动')
                    else:
                        stylelog.fail('ESC没有继续启动')
                        count += 1
                    time.sleep(1)
                    SetUpLib.send_key(SutConfig.Msg.SETUP_KEY)
                    if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 90):
                        assert SetUpLib.boot_to_setup()
                else:
                    stylelog.fail('ESC后宕机')
                    count += 1
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sec.ESC_MSG))
                wrong_msg.append('修改{0}，启动时没有显示{1}'.format(i, SutConfig.Sec.ESC_MSG))
                count += 1
                BmcLib.init_sut()
                assert SetUpLib.boot_with_hotkey_only(SutConfig.Msg.SETUP_KEY, SutConfig.Msg.PAGE_MAIN, 200, SutConfig.Msg.POST_MESSAGE)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
            SetUpLib.send_key(Key.ENTER)
            if re.search('No Action', SetUpLib.get_data(3)):
                logging.info('一次启动后,TPM2操作变为无动作')
            else:
                stylelog.fail('一次启动后,TPM2操作没有变为无动作')
                wrong_msg.append('一次启动后,TPM2操作没有变为无动作')
                count += 1
            assert SetUpLib.enter_menu_change_value(Key.DOWN, [{'TPM2 Operation': i}], 18)
            time.sleep(2)
            SetUpLib.send_keys(Key.SAVE_RESET)
            if SetUpLib.wait_message(SutConfig.Sec.ESC_MSG):
                time.sleep(1)
                SetUpLib.send_key(Key.F12)
                start = time.time()
                if SetUpLib.wait_message(SutConfig.Msg.POST_MESSAGE):
                    end = time.time()
                    spent_time = end - start
                    if abs(spent_time - spent) < base_time:
                        logging.info('F12后重启')
                    else:
                        stylelog.fail('F12没有重启')
                        count += 1
                    time.sleep(1)
                    SetUpLib.send_key(SutConfig.Msg.SETUP_KEY)
                    if not SetUpLib.wait_message(SutConfig.Msg.PAGE_MAIN, 90):
                        assert SetUpLib.boot_to_setup()
                else:
                    stylelog.fail('F12后宕机')
                    count += 1
                    assert SetUpLib.boot_to_setup()
            else:
                stylelog.fail('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sec.ESC_MSG))
                wrong_msg.append('修改{0},启动时没有显示{1}'.format(i, SutConfig.Sec.ESC_MSG))
                count += 1
                BmcLib.init_sut()
                assert SetUpLib.boot_with_hotkey_only(SutConfig.Msg.SETUP_KEY, SutConfig.Msg.PAGE_MAIN, 200, SutConfig.Msg.POST_MESSAGE)
            assert SetUpLib.locate_menu(Key.DOWN, SutConfig.Sec.LOC_TCG2, 18)
            SetUpLib.send_key(Key.ENTER)
            if re.search('No Action', SetUpLib.get_data(3)):
                logging.info('一次启动后,TPM2操作变为无动作')
            else:
                stylelog.fail('一次启动后,TPM2操作没有变为无动作')
                wrong_msg.append('一次启动后,TPM2操作没有变为无动作')
                count += 1
        time.sleep(2)
        SetUpLib.send_keys(Key.SAVE_RESET)
        time.sleep(5)
        if count == 0:
            return True
        else:
            for i in wrong_msg:
                stylelog.fail(i)
            return
    except Exception as e:
        logging.error(e)
        return core.Status.Fail
