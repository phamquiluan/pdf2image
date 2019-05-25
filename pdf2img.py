import os
import re
import platform

from subprocess import Popen, PIPE


def _get_command_path(command):
    if platform.system() == 'Windows':
        command = command + '.exe'
    return command


def _pdf_info(pdf_path):
    command = [_get_command_path("pdfinfo"), pdf_path]
    proc = Popen(command, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()

    page_count = int(re.search(r'Pages:\s+(\d+)',
                      out.decode("utf8", "ignore")).group(1))
    
    pdf_info = []
    for i in range(page_count):
        cmd = [_get_command_path("pdfinfo"), '-f', str(i + 1), '-l', str(i + 1), pdf_path]
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        # Page size: 792 x 1224 pts
        page_size = re.search('Page.*size:\s+([\d\.x\s]+)', out.decode("utf8", "ignore")).group(1).split('x')
        pdf_info.append((str(i+1), list(map(float, page_size))))

    return pdf_info


def cvt_pdf_2_image(file_path='./data/input.pdf',
                    path_out='debug', thread_num=6):
    """
    file_path: path of pdf file
    path_out: path out of image(s)
    thread_num: number of thread
    output is jpeg file
    """
    assert 'pdf' in file_path
    base_name = file_path.split('/')[-1][:-4]
    page_info = _pdf_info(file_path)

    large_page = [(pnum, psize) for (pnum, psize) in page_info if psize[0] > 3000]
    small_page = [(pnum, psize) for (pnum, psize) in page_info if psize[0] <= 3000]

    processes = []
    proc_cnt = 0
    
    for page_num, page_size in small_page:
        # print(os.path.join(path_out, base_name + '_' + str(page_num)))
        command = [_get_command_path("pdftoppm"), "-cropbox", "-jpeg", 
                   "-singlefile", "-r", "300", "-f", page_num, "-l", page_num,
                   file_path, os.path.join(path_out, str(int(page_num) - 1))]
        processes.append((page_num, Popen(command, stdout=PIPE, stderr=PIPE)))
        proc_cnt += 1
        if proc_cnt == thread_num:
            for page_num, proc in processes:
                proc.wait()
            proc_cnt = 0
            processes = []

    for page_num, page_size in large_page:
        # print(os.path.join(path_out, base_name + '_' + str(page_num)))
        command = [_get_command_path("pdftoppm"), "-cropbox", "-jpeg",
                   "-singlefile", "-r", "150", "-f", page_num, "-l", page_num,
                   file_path, os.path.join(path_out, str(int(page_num) - 1))]
        processes.append((page_num, Popen(command, stdout=PIPE, stderr=PIPE)))
        proc_cnt += 1
        if proc_cnt == thread_num:
            for page_num, proc in processes:
                proc.wait()
            proc_cnt = 0
            processes = []
    
    for page_num, proc in processes:
        proc.wait()



if __name__ == "__main__":
    for d, _ , files in os.walk('../Projects/siemens/data/GED0005/MA371'):
        for f in files:
            pdf_path = os.path.join(d, f)
            print(pdf_path)
            # print(_pdf_info(pdf_path))
            cvt_pdf_2_image(pdf_path)

            break
