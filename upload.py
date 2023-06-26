import pathlib
import argparse
import subprocess

def upload_app_main():

    # Parse command line arguments
    description ='upload Micropython code to microcontroller using ampy'
    parser = argparse.ArgumentParser(description=description)
    
    port_help = 'device port, e.g. /dev/ttyACM0, COM1, etc.' 
    parser.add_argument('-p', '--port', type=str, help=port_help, required=True)
    conf_help = 'optional configuration file'
    parser.add_argument('-c', '--conf', type=str, help=conf_help, required=False)
    
    args = parser.parse_args()
    src_file_list = get_src_list()
    num_files = len(src_file_list)
    conf_file = get_conf_file(args)

    print()
    print(f'port: {args.port}')
    if conf_file is not None:
        print(f'conf: {args.conf}')
    print()

    # Upload source files
    print('uploading firmware ... ')
    for i, src_file in enumerate(src_file_list):
        cmd_list = ['ampy', '-p', args.port, 'put', src_file]
        print(f'  {i+1}/{num_files}: {src_file}')
        subprocess.run(cmd_list)
    print()

    print('uploading configuration file ... ')
    if conf_file is not None:
        cmd_list = ['ampy', '-p', args.port, 'put', conf_file]
        print(f'  {conf_file}')
        subprocess.run(cmd_list)
    print()


def get_src_list():
    """ Get list of *.py files in src sub-directory """
    src_dir = pathlib.Path(pathlib.Path.cwd(), 'src')
    src_files = src_dir.glob('*.py')
    return list(src_files)


def get_conf_file(args):
    """ Get configuration file if it exists """
    conf_file = None 
    if args.conf is not None:
        conf_path = pathlib.Path(args.conf)
        if conf_path.exists():
            conf_file = conf_path.absolute()
        else:
            print('error: conf file does not exist')
            exit(0)
    return conf_file

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    upload_app_main()








